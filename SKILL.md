---
name: upscale-images-by-sections
description: Upscale complex images with generative editing of overlapping semantic sections, fixed source coordinates, construction review, alignment, and protected typography. Use when whole-image enlargement loses small detail, tiled or console-style upscaling is requested, or a reusable generative upscaling workflow is needed. Default to source-preserving enlargement; keep separately requested content corrections explicit and traceable.
---

# Upscale Images by Sections

Read the image-independent [method manifest](references/method-manifest.json). Bind the current image through the [job template](assets/job-template.json); validate its structure with [the job schema](references/job.schema.json).

## Keep the artifacts separate

- **Method manifest:** reusable procedure, defaults, roles and acceptance rules. Keep image names, dimensions, coordinates, canon, render paths and measurements out of it.
- **Job plan:** per-image source, target, section map, protected content, invariants and requested corrections.
- **Render records:** prepared inputs, actual outputs, inspection decisions and render-contract identity.
- **Assembly report:** dimensions, alignment measurements and verification for one completed job.

Deliver the method manifest when the user asks for a reusable manifest. Supply a run record only when the user requests that record or a reproducible case.

## Bind scope before rendering

Default to `intent: upscale_only` and `corrections: []`. Preserve the current source's content, layout, proportions, materials and relationships. Derive invariants from that source; never copy content rules from another image or the case reference.

When the user requests a design or content correction, select `upscale_with_corrections`. Record each exact requested change, its id and target section ids. Apply only those assigned changes. Record corrections separately from generated surface detail so a later inspection can trace their origin. Use existing authorization; do not introduce a new confirmation step for a correction the user already requested.

## Execute

1. Resolve the authoritative source, identity/version and digest. Set the requested final scale in the bound job.
2. Map complete semantic sections with overlapping context. Keep connected parts together. Map typography and other content that must be restored separately.
3. Define current-image component counts, attachment paths, silhouette, orientation, palette and materials as section invariants. Read [construction review](references/construction-review.md).
4. Set `binding_status: bound` after filling the template. Run:
   `python scripts/sections.py prepare JOB.json SECTION_DIRECTORY`
   Read [the coordinate and record format](references/plan-format.md).
5. Inspect each local input. Use the native image editor with the section as edit target and full source as context. Preserve aspect, geometry and atlas order. Include only the job's applicable corrections. Use [the prompt template](references/prompt-template.md). Measure actual output dimensions.
6. Compare each render with its source at matched scale. Review connections, components, identity and geometry before finish. Re-render omissions or unexplained changes. Do not conceal a failed construction check by blending source pixels back in.
7. Record its render path and `accepted: true` in `SECTION_DIRECTORY/render-records.json` only after inspection.
8. Assemble:
   `python scripts/sections.py assemble JOB.json SECTION_DIRECTORY FINAL.png --scale SCALE`
   Match SCALE to the job target. Use bounded alignment, broad illumination matching and feathering; inspect the result. Disable alignment per section or with `--no-align` when unnecessary.
9. Inspect full composition, critical close-ups, boundaries, protected pixels, alpha and each requested correction. Retain the job plan, render records and assembly report when requested.
10. Persist the final image and requested portable workflow files. Report measured dimensions and relevant changes.

Use Pillow and NumPy for deterministic preparation/compositing, jsonschema for job validation, and OpenCV only for registration. Keep generation in the native editor. Run no paid service or external API merely because it appears here.

## Track changes

Preparation stores a digest of source content, section geometry, input layout, invariants, references and correction instructions. Assembly refuses records for a changed render contract. Re-prepare and review affected sections after such changes. Preparation retains accepted outputs for unchanged section contracts and archives previous records. Assembly-only changes such as feathering or protected overlays may be adjusted without silently changing the generation instructions.

Separate sharpness, source consistency and construction. Low downsampling error and attractive detail do not establish correct structure. Describe synthesized microdetail as generated information.

Read [the optional case reference](references/neon-night-case.md) only for the history of the console-budget analogy and its construction-review lesson; do not import that case's content into a new job.


For sections with assigned corrections, the helper defaults source-based registration and color matching to off. Set `align: true` or a nonzero `color_match` only when matching to the original source will preserve the requested change. The assembly report records the applied settings and correction ids.
