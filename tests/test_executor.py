"""Reproduce synthetic compositor checks; no image-generation service is used."""
import copy, hashlib, json, tempfile, unittest, sys, io, contextlib
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import sections as m

class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name); self.records=self.d/'renders'; self.job=self.d/'job.json'
        y,x=np.indices((32,48)); self.src=Image.fromarray(np.stack([x*4,y*6,(x+y)*3,80+x*3],axis=-1).astype('uint8'),'RGBA'); self.src.save(self.d/'source.png')
        self.p={'artifact_kind':'job_plan','protocol':'generative_section_upscaling','protocol_version':'1.1','binding_status':'bound','intent':'upscale_only','source':'source.png','target':{'scale':2},'sections':[{'id':'a','box':[4,4,32,28],'feather':0,'color_match':0},{'id':'b','cells':[{'box':[20,8,44,30]}],'columns':1,'cell_size':[64,64],'feather':0,'color_match':0}],'corrections':[],'protected_rects':[[12,12,24,20]]}
    def prep(self):
        self.job.write_text(json.dumps(self.p));
        with contextlib.redirect_stdout(io.StringIO()): m.prepare(self.job,self.records)
        return json.loads((self.records/'render-records.json').read_text())
    def accept(self, r):
        for e in r['sections']:
            f=self.records/(e['id']+'.png'); Image.new('RGB',tuple(e['input_size']),(240,20,30) if e['id']=='a' else (20,230,50)).save(f); e.update(render=f.name,accepted=True)
        (self.records/'render-records.json').write_text(json.dumps(r))
    def assemble(self):
        with contextlib.redirect_stdout(io.StringIO()): m.assemble(self.job,self.records,self.d/'out.png',2,False)
        return np.array(Image.open(self.d/'out.png'))
    def test_protection_alpha_and_dimensions(self):
        self.accept(self.prep()); o=self.assemble(); b=np.array(self.src.resize((96,64),Image.Resampling.LANCZOS)); self.assertEqual(o.shape,(64,96,4)); np.testing.assert_array_equal(o[24:40,24:48],b[24:40,24:48]); np.testing.assert_array_equal(o[:,:,3],b[:,:,3]); self.assertFalse(np.array_equal(o[:,:,:3],b[:,:,:3])); np.testing.assert_array_equal(o[:8],b[:8])
    def test_cache_reuse_selective_invalidation(self):
        self.accept(self.prep()); r=self.prep(); self.assertTrue(all(e['accepted'] for e in r['sections'])); self.p['sections'][0]['invariants']=['new constraint']; r=self.prep(); self.assertFalse(r['sections'][0]['accepted']); self.assertTrue(r['sections'][1]['accepted']); self.assertTrue(list((self.records/'render-records-history').glob('*.json')))
    def test_unaccepted_blocks_assembly(self):
        self.prep(); self.assertRaisesRegex(ValueError,'not passed',self.assemble)
    def test_assembly_change_reuses_renders(self):
        self.accept(self.prep()); self.p['sections'][0]['feather']=2; self.assertTrue(all(e['accepted'] for e in self.prep()['sections']))
    def test_overlap_order_dependence_observed(self):
        self.accept(self.prep()); a=self.assemble(); self.p['sections'].reverse(); self.accept(self.prep()); b=self.assemble(); self.assertFalse(np.array_equal(a,b))
    def test_atlas_background_hash_omission_observed(self):
        self.src.convert('RGB').save(self.d/'source.png'); r=self.prep(); self.p['atlas_background']='#ffffff'; q=self.prep(); self.assertEqual(r['render_contract_sha256'],q['render_contract_sha256'])
    def test_accepted_file_mutation_observed(self):
        r=self.prep(); self.accept(r); a=self.assemble(); Image.new('RGB',tuple(r['sections'][0]['input_size']),(0,0,255)).save(self.records/'a.png'); b=self.assemble(); self.assertFalse(np.array_equal(a,b))
    def test_prepare_cuts_tiles_from_fitment(self):
        # Regression (2026-11-24): tiles must be cut from the whole-source
        # fitment at the job's uniform target scale (2x here), not cropped
        # from the low-res source and resized per-section under a 1536 cap.
        r=self.prep()
        a=[e for e in r['sections'] if e['id']=='a'][0]
        self.assertEqual(a['input_size'],[56,48])  # box 28x24 at uniform 2x
        fitment=self.src.resize((96,64),Image.Resampling.LANCZOS).crop((8,8,64,56))
        prepared=Image.open(a['input'])
        np.testing.assert_array_equal(np.array(prepared),np.array(fitment))
        # Crop-first preparation differs from the fitment at the tile edges;
        # the prepared input must be the fitment's pixels, not the crop's.
        crop_first=self.src.crop((4,4,32,28)).resize((56,48),Image.Resampling.LANCZOS)
        self.assertFalse(np.array_equal(np.array(prepared),np.array(crop_first)))
    def test_corrections_default_disable_matching(self):
        self.p['intent']='upscale_with_corrections'; self.p['corrections']=[{'id':'c','instruction':'change color','section_ids':['a']}]; del self.p['sections'][0]['color_match']; self.accept(self.prep()); self.assemble(); report=json.loads((self.d/'out.json').read_text()); self.assertEqual(report['sections'][0]['color_match_strength'],0)

if __name__=='__main__': unittest.main(verbosity=2)
