# Generative Section Upscaling

An image-independent workflow developed by Shepherdess and Tachikoma. Use it to give important parts of a complex image the full resolution budget of a generative editor, then assemble those parts back into the original layout.

## Portable artifacts

| Artifact | Contents | Lifetime |
|---|---|---|
| Method manifest | Procedure, defaults, reference roles and acceptance rules | Reuse across images |
| Job plan | Source, target scale, mapped sections, protected regions, invariants and optional corrections | Bind for one image |
| Render records | Input coordinates, source/contract digests, render paths and inspection decisions | Record one job |
| Assembly report | Output dimensions, alignment settings, corrections and verification | Record one output |

Give another AI `Generative_Upscaling_Method_Manifest.json` to explain the method. Copy `Generative_Upscaling_Job_Template.json` when starting an image. Fill the source, target and sections; set `binding_status` to `bound` before execution. The standalone method manifest embeds the job schema for use outside this skill.

## Default intent

Use `intent: upscale_only` and `corrections: []`. Preserve the current source's layout, proportions, content, palette, material character, component counts and physical relationships. Derive all content-specific invariants from that image.

When the user requests a design or content change, select `intent: upscale_with_corrections`. Give each requested change an id, exact instruction and target `section_ids`. Keep it separate from unchanged-source invariants. Include only the changes assigned to the section being rendered.

Keep prior outputs so a later comparison can trace differences. Do not infer that an intervention caused an artifact without comparing the relevant versions.

## Procedure

1. Resolve the authoritative source and requested output. Record source identity, digest and dimensions.
2. Map complete semantic sections with surrounding context and overlap. Keep connected parts together. Use cell atlases for related small details when useful.
3. Protect typography and any content requiring exact preservation. Record current-image invariants and optional explicitly requested corrections in the job.
4. Prepare immutable section inputs and atlas mappings. Record a digest of the rendering contract.
5. Generate each section using its crop as edit target and the full source as context. Preserve exact framing and relationships while increasing detail. Measure actual returned dimensions.
6. Inspect each result at matched scale. Check construction, counts, attachments, identity and geometry before judging surface finish. Re-render failed sections or make narrowly scoped repairs.
7. Mark a render accepted only after inspecting it. Invalidate affected acceptance records when source content, crop geometry, atlas layout, invariants, references or requested correction instructions change.
8. Map accepted outputs back to the source coordinates. Use bounded registration, broad illumination matching and feathered overlap where appropriate. On corrected sections, source-based registration and color matching default to off so they do not undo requested changes.
9. Restore protected content last. Inspect seams, rigid connections, dimensions, alpha, protected pixels and every requested correction in the assembled result.
10. Save the image and requested per-job records. Keep this portable method manifest independent of those records.

## Generic editing prompt

> Image 1 is the edit target; Image 2 is the full source for context. Produce a faithful high-resolution restoration of Image 1 only. Preserve its exact aspect ratio, crop boundaries, layout, pose, proportions, silhouette, palette, material shading, component counts and connections. Resolve finer material and surface detail while preserving these current-image invariants: [job invariants]. Keep atlas order and blank padding unchanged. Apply only these explicitly assigned corrections, if any: [job correction ids and instructions]. Preserve protected content for separate compositing. Add no unrequested content or design changes.

Use additional references only for an identified current-job requirement. Record their role. Keep any character, product, scene or engineering constraints in the job inputs.

## Compositing and scale

Use integer source-pixel rectangles `[left, top, right, bottom]`, with exclusive right and bottom. Retain exact atlas placement rectangles so returned cells can be extracted even when the generator chooses a different output size.

Measure local linear allocation as `actual_render_width / source_section_width`. Record returned pixel counts, overlap, atlas padding and repair passes. Obtain generator limits at runtime rather than assuming a universal fixed resolution.

Conservative starting settings are a guard band around 10% of section dimensions, bounded displacement around 8 source pixels, low-frequency color matching strength 0.45, a broad illumination radius around 12 source pixels, and feathering around 12 source pixels for large sections or 2–5 for small cells. Tune these to the current image. Check rigid geometry after alignment and disable warping when it changes construction.

Re-preparation retains render paths and acceptance for unchanged section contracts and archives earlier records. Changed sections require a new review.

Keep assembly settings separate from rendering instructions. Feathering and protected overlays can be adjusted without silently changing which source content was generated. Record applied registration, matching strength and correction ids in the assembly report.

## Execution with the installed helper

The **Upscale Images by Sections** skill includes the generic manifest, job template, JSON schema, preparation/compositing script and review instructions.

```bash
python scripts/sections.py prepare JOB.json SECTION_DIRECTORY
# Generate the prepared inputs with the native image editor.
# Inspect each output, then set its render path and accepted=true
# in SECTION_DIRECTORY/render-records.json.
python scripts/sections.py assemble JOB.json SECTION_DIRECTORY FINAL.png --scale SCALE
```

Set the same positive integer scale in the current helper's job target and command. Use `--no-align` or per-section `align: false` when registration is unnecessary. Image generation stays in the native editor; preparation and reconstruction use deterministic image operations. The helper requires Pillow, NumPy and jsonschema; OpenCV is optional for registration. Prepared preview magnification is independent of the requested final scale and can be tuned with `preview_long_edge`.

## Acceptance

Accept a result after inspecting both structure and finish. Verify component connections, orientation, silhouette, content, protected pixels and requested changes. Treat source-downsampling error as a consistency measurement. Describe synthesized microdetail as generated information, and retain the actual procedure and parameters used.
