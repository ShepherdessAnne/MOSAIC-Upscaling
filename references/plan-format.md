# Job plans and render records

Copy `assets/job-template.json` to the job's working directory. Set the source path, target scale, sections and protected regions, then set `binding_status: bound`. Resolve relative source paths against the job file's directory.

Use integer source-pixel rectangles `[left, top, right, bottom]`, with exclusive right and bottom. Set exactly one of `box` or `cells` on each section. Use `columns` and `cell_size` to lay out cell atlases. Name section ids with lowercase letters, digits, underscores or hyphens.

Set `align: false` per section to disable registration. Set `color_match: 0` to disable illumination matching. Measure feather widths and maximum displacements in source pixels. Use optional `edit_polygons` in absolute source coordinates to restrict a non-atlas region's editable area. Protected rectangles are restored last.

## Scope

Default to `intent: upscale_only` with an empty `corrections` list.

For explicitly requested changes, set `intent: upscale_with_corrections` and list objects containing:

- `id`: stable change identifier.
- `instruction`: the exact requested change.
- `section_ids`: nonempty list of existing target sections.

Keep current-source invariants on sections. Keep revisions or new design instructions in corrections. The prepare step copies only the corrections assigned to each section into its render record.

## Records

Preparation writes `render-records.json`, including the source and render-contract digests, input sizes, atlas mappings, requested corrections and unaccepted section entries. After inspection, set each section's `render` path and `accepted: true`. Relative render paths resolve against the section directory.

Changing source bytes, section geometry, atlas layout, invariants, references or correction instructions invalidates those records. Re-prepare and review affected sections after changing the render contract. Existing reviews and render paths survive for unchanged section contracts; prior records are archived. Protected overlays, feathering, color matching and alignment settings are assembly controls and can be tuned independently.

Assembly writes a PNG, preview and JSON assembly report. Opaque previews use JPEG; transparent previews retain alpha as PNG. Preparation retains RGBA. Ask the native editor to preserve transparency where applicable. The current helper uses positive integer output scales; supply the same scale in the job target and CLI.

Preparation and assembly enforce `references/job.schema.json` through jsonschema. Execution additionally checks actual image bounds, duplicate ids, correction targets, source digest, acceptance records and render-contract identity.


For sections with assigned corrections, the helper defaults source-based registration and color matching to off. Set `align: true` or a nonzero `color_match` only when matching to the original source will preserve the requested change. The assembly report records the applied settings and correction ids.

Prepared inputs are cut from the fitment: `prepare()` standard-upscales the whole source once at the job's uniform target scale and cuts every section tile from that master, so a box section's prepared size is its box multiplied by the target scale, and every section arrives at the same scale. (Before 2026-11-24, preparation cropped the low-res source first and resized each crop separately, capped at a 1536-pixel long edge — handing sections different effective scales at the same nominal target. The `preview_long_edge` section key is retained in the render contract for compatibility but no longer sizes inputs.) Actual prepared sizes are recorded.
