#!/usr/bin/env python3
"""Prepare and assemble externally rendered image sections; never call an image API."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

def rect(value, width, height):
    if len(value)!=4 or any(int(v)!=v for v in value): raise ValueError('Rectangle requires four integer coordinates')
    x0,y0,x1,y1=map(int,value)
    if not (0<=x0<x1<=width and 0<=y0<y1<=height): raise ValueError(f'Rectangle outside canvas: {value}')
    return x0,y0,x1,y1

def load_plan(path):
    path=Path(path).resolve(); p=json.loads(path.read_text())
    if p.get('artifact_kind','job_plan')!='job_plan':raise ValueError('Bind a job plan; a method manifest is a reusable procedure, not a job')
    from jsonschema import Draft202012Validator
    schema=json.loads((Path(__file__).resolve().parent.parent/'references/job.schema.json').read_text())
    errors=sorted(Draft202012Validator(schema).iter_errors(p),key=lambda e:str(list(e.path)))
    if errors:raise ValueError('Invalid job plan at '+('/'.join(map(str,errors[0].path)) or 'root')+': '+errors[0].message)
    if p.get('binding_status','bound')!='bound':raise ValueError('Fill the job template and set binding_status to bound before preparation')
    if not isinstance(p.get('source'),str) or not p['source']:raise ValueError('Job requires a source image path')
    if not p.get('sections'):raise ValueError('Job requires at least one mapped section')
    intent=p.get('intent','upscale_only');corrections=p.get('corrections',[])
    if intent not in ['upscale_only','upscale_with_corrections']:raise ValueError('Unknown job intent')
    if corrections and intent=='upscale_only':raise ValueError('upscale_only jobs cannot include content corrections')
    if intent=='upscale_with_corrections' and not corrections:raise ValueError('List the requested corrections explicitly')
    source=Path(p['source']);source=source if source.is_absolute() else path.parent/source
    image=Image.open(source).convert('RGBA')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if p.get('source_sha256') and p['source_sha256']!=digest: raise ValueError('Source digest changed')
    seen=set()
    for s in p['sections']:
        if s['id'] in seen: raise ValueError('Duplicate section id')
        seen.add(s['id'])
        if not s['id'] or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in s['id']): raise ValueError('Unsafe section id')
        if ('box' in s)==('cells' in s):raise ValueError('Section requires exactly one of box or cells')
        if 'cells' in s:
            if not s['cells'] or s.get('columns',2)<1:raise ValueError('Atlas requires cells and a positive column count')
            if any(v<9 for v in s.get('cell_size',[320,384])):raise ValueError('Atlas cell dimensions must be at least nine pixels')
            for c in s['cells']:rect(c['box'],*image.size)
        else:rect(s['box'],*image.size)
    for c in corrections:
        if not isinstance(c,dict) or not c.get('id') or not c.get('instruction') or not c.get('section_ids'):raise ValueError('Each correction requires id, instruction and section_ids')
        if not set(c['section_ids']).issubset(seen):raise ValueError('Correction targets an unknown section')
    for r in p.get('protected_rects',[]):rect(r,*image.size)
    return p,image,digest

def section_contract(p,digest,s):
    keys=['id','box','cells','columns','cell_size','preview_long_edge','invariants','context_references','prompt_overrides']
    corrections=[c for c in p.get('corrections',[]) if s['id'] in c['section_ids']]
    value={'source_sha256':digest,'context_references':p.get('context_references',[]),'corrections':corrections,'section':{k:s[k] for k in keys if k in s}}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def render_contract(p,digest):
    value={'source_sha256':digest,'intent':p.get('intent','upscale_only'),'sections':[{s['id']:section_contract(p,digest,s)} for s in p['sections']]}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def prepare(plan_path,directory):
    p,source,digest=load_plan(plan_path);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    has_alpha=source.getchannel('A').getextrema()!=(255,255)
    mode='RGBA' if has_alpha else 'RGB'
    manifest={'artifact_kind':'render_records','protocol_version':'1.1','source_sha256':digest,'source_size':list(source.size),'source_has_alpha':has_alpha,'render_contract_sha256':render_contract(p,digest),'intent':p.get('intent','upscale_only'),'sections':[]}
    records_path=directory/'render-records.json';previous={}
    if records_path.exists():
        previous=json.loads(records_path.read_text())
        if previous.get('render_contract_sha256')!=manifest['render_contract_sha256']:
            history=directory/'render-records-history';history.mkdir(exist_ok=True)
            old_hash=hashlib.sha256(records_path.read_bytes()).hexdigest()
            (history/(old_hash+'.json')).write_text(json.dumps(previous,indent=2))
    previous_sections={s['id']:s for s in previous.get('sections',[])}
    for s in p['sections']:
        entry={'id':s['id'],'render_contract_sha256':section_contract(p,digest,s),'invariants':s.get('invariants',[]),'requested_corrections':[c for c in p.get('corrections',[]) if s['id'] in c['section_ids']],'accepted':False}
        old=previous_sections.get(s['id'],{})
        if old.get('render_contract_sha256')==entry['render_contract_sha256']:
            entry.update({k:old[k] for k in ['render','accepted','review'] if k in old})
        elif old.get('render'):
            entry['previous_render']=old['render']
        if 'cells' in s:
            columns=s.get('columns',2);cw,ch=s.get('cell_size',[320,384]);rows=(len(s['cells'])+columns-1)//columns
            canvas=Image.new(mode,(cw*columns,ch*rows),(0,0,0,0) if has_alpha else p.get('atlas_background','#00101f'))
            placements=[]
            for i,c in enumerate(s['cells']):
                im=source.crop(c['box']).convert(mode)
                im=ImageOps.contain(im,(cw-8,ch-8),Image.Resampling.LANCZOS)
                x=(i%columns)*cw+(cw-im.width)//2;y=(i//columns)*ch+(ch-im.height)//2
                canvas.paste(im,(x,y))
                placements.append({'box':c['box'],'atlas_box':[x,y,x+im.width,y+im.height],'name':c.get('name',str(i))})
            entry.update({'cells':placements,'input_size':list(canvas.size)})
        else:
            canvas=source.crop(s['box']).convert(mode)
            factor=min(s.get('preview_long_edge',1536)/max(canvas.size),4)
            canvas=canvas.resize(tuple(max(1,round(v*factor)) for v in canvas.size),Image.Resampling.LANCZOS)
            entry.update({'box':s['box'],'input_size':list(canvas.size)})
        filename=directory/(s['id']+'_input.png');canvas.save(filename)
        entry['input']=str(filename.resolve());manifest['sections'].append(entry)
    records_path.write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'render_records':str((directory/'render-records.json').resolve()),'sections':len(manifest['sections'])}))

def register(source,generated,scale,max_shift=8):
    """Estimate bounded source-to-render flow; leave pixels untouched when alignment is disabled."""
    import cv2
    w,h=source.size
    # Work at 2x source resolution for small features, cap very large input sections.
    f=min(2.,1200/max(w,h));size=(max(16,round(w*f)),max(16,round(h*f)))
    a=np.asarray(source.resize(size,Image.Resampling.LANCZOS).convert('RGB'))
    b=np.asarray(generated.resize(size,Image.Resampling.LANCZOS).convert('RGB'))
    clahe=cv2.createCLAHE(clipLimit=2.,tileGridSize=(8,8))
    a=clahe.apply(cv2.cvtColor(a,cv2.COLOR_RGB2GRAY));b=clahe.apply(cv2.cvtColor(b,cv2.COLOR_RGB2GRAY))
    flow=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(a,b,None)
    flow=cv2.GaussianBlur(flow,(0,0),max(.6,1.5*f))
    norm=np.linalg.norm(flow,axis=2);limit=max_shift*f
    clipped=float(np.mean(norm>limit))
    flow*=np.minimum(1.,limit/np.maximum(norm,1e-6))[:,:,None]
    ow,oh=w*scale,h*scale
    flow=cv2.resize(flow,(ow,oh))*np.array([ow/size[0],oh/size[1]],np.float32)
    xx,yy=np.meshgrid(np.arange(ow,dtype=np.float32),np.arange(oh,dtype=np.float32))
    original=np.asarray(generated.resize((ow,oh),Image.Resampling.LANCZOS).convert('RGB'))
    warped=cv2.remap(original,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    return Image.fromarray(warped),{'flow_clipped_fraction':clipped,'max_shift_source_px':max_shift}

def feather(size,pixels):
    w,h=size
    if pixels<=0:return Image.new('L',size,255)
    yy,xx=np.mgrid[:h,:w]
    distance=np.minimum.reduce([xx+.5,w-xx-.5,yy+.5,h-yy-.5])
    a=np.clip(distance/pixels,0,1);a=a*a*(3-2*a)
    return Image.fromarray(np.round(a*255).astype('uint8'))

def assemble(plan_path,directory,output,scale=4,align=True):
    if scale<1:raise ValueError('Scale must be a positive integer')
    p,source,digest=load_plan(plan_path);directory=Path(directory)
    manifest=json.loads((directory/'render-records.json').read_text())
    if manifest['source_sha256']!=digest:raise ValueError('Prepared crops do not match the current source')
    if manifest.get('render_contract_sha256')!=render_contract(p,digest):raise ValueError('Render contract changed; prepare and review the affected renders again')
    if p.get('target',{}).get('scale',scale)!=scale:raise ValueError('Requested scale conflicts with the bound job target')
    accepted={x['id']:x for x in manifest['sections']}
    base=source.resize((source.width*scale,source.height*scale),Image.Resampling.LANCZOS)
    result=base.convert('RGB');metrics=[];mask_total=Image.new('L',result.size,0)
    for s in p['sections']:
        m=accepted[s['id']]
        if m.get('render_contract_sha256')!=section_contract(p,digest,s):raise ValueError('Section render contract changed: '+s['id'])
        if not m.get('accepted'):raise ValueError('Section has not passed visual structure review: '+s['id'])
        rendered=Path(m['render']);rendered=rendered if rendered.is_absolute() else directory/rendered
        rendered=Image.open(rendered).convert('RGBA')
        iw,ih=m['input_size'];rw,rh=rendered.size
        items=m.get('cells',[{'box':m.get('box'),'atlas_box':[0,0,iw,ih]}])
        for cell in items:
            box=cell['box'];x0,y0,x1,y1=box
            r=cell['atlas_box'];rb=(round(r[0]*rw/iw),round(r[1]*rh/ih),round(r[2]*rw/iw),round(r[3]*rh/ih))
            tile=rendered.crop(rb);reference=source.crop(box).convert('RGB')
            size=((x1-x0)*scale,(y1-y0)*scale);tile=tile.resize(size,Image.Resampling.LANCZOS).convert('RGB')
            requested_corrections=[c for c in p.get('corrections',[]) if s['id'] in c['section_ids']]
            registration_enabled=align and s.get('align',not requested_corrections)
            info={'section':s['id'],'box':box,'render_size':list(rendered.size),'correction_ids':[c['id'] for c in requested_corrections],'registration_applied':bool(registration_enabled)}
            if registration_enabled:tile,extra=register(reference,tile,scale,s.get('max_shift',8));info.update(extra)
            # Match broad illumination, retaining generated fine structure.
            sigma=12*scale;strength=s.get('color_match',0 if requested_corrections else .45)
            info['color_match_strength']=strength
            if strength:
                low_source=np.asarray(reference.resize(size,Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(sigma)),dtype=np.float32)
                low_render=np.asarray(tile.filter(ImageFilter.GaussianBlur(sigma)),dtype=np.float32)
                a=np.asarray(tile,dtype=np.float32)+strength*(low_source-low_render)
                tile=Image.fromarray(np.round(np.clip(a,0,255)).astype('uint8'))
            mask=feather(size,s.get('feather',5 if 'cells' in s else 12)*scale)
            dest=(x0*scale,y0*scale)
            if s.get('edit_polygons'):
                custom=Image.new('L',size,0);d=ImageDraw.Draw(custom)
                for polygon in s['edit_polygons']:
                    d.polygon([((x-x0)*scale,(y-y0)*scale) for x,y in polygon],fill=255)
                custom=custom.filter(ImageFilter.GaussianBlur(2*scale))
                mask=Image.fromarray((np.asarray(mask,dtype=np.uint16)*np.asarray(custom,dtype=np.uint16)//255).astype('uint8'))
            result.paste(tile,dest,mask);mask_total.paste(mask,dest,mask)
            info['source_mae_after_downsample']=float(np.abs(np.asarray(tile.resize(reference.size,Image.Resampling.LANCZOS),dtype=np.float32)-np.asarray(reference,dtype=np.float32)).mean())
            metrics.append(info)
    # Protected typography always wins, copied from the deterministic baseline.
    for r in p.get('protected_rects',[]):
        box=tuple(v*scale for v in r);result.paste(base.crop(box).convert('RGB'),box[:2])
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    if source.getchannel('A').getextrema()!=(255,255):result.putalpha(base.getchannel('A'))
    result.save(output)
    sidecar={'artifact_kind':'assembly_report','protocol_version':'1.1','source_sha256':digest,'render_contract_sha256':render_contract(p,digest),'intent':p.get('intent','upscale_only'),'corrections':p.get('corrections',[]),'scale':scale,'size':list(result.size),'sections':metrics,'protected_rects':p.get('protected_rects',[])}
    output.with_suffix('.json').write_text(json.dumps(sidecar,indent=2))
    preview=result.copy().resize((min(1600,result.width),round(result.height*min(1600,result.width)/result.width)),Image.Resampling.LANCZOS)
    if result.mode=='RGBA':preview.save(output.with_name(output.stem+'_preview.png'))
    else:preview.save(output.with_name(output.stem+'_preview.jpg'),quality=94)
    print(json.dumps({'output':str(output.resolve()),'sections':len(p['sections']),'regions':len(metrics),'size':list(result.size)}))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare');a.add_argument('plan');a.add_argument('directory')
    a=sub.add_parser('assemble');a.add_argument('plan');a.add_argument('directory');a.add_argument('output');a.add_argument('--scale',type=int,default=4);a.add_argument('--no-align',action='store_true')
    args=parser.parse_args()
    if args.command=='prepare':prepare(args.plan,args.directory)
    else:assemble(args.plan,args.directory,args.output,args.scale,not args.no_align)

if __name__=='__main__':main()
