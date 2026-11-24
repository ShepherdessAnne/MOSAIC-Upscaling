# Generic native-edit prompt

Assign roles: Image 1 is the prepared edit target, Image 2 is full-source context, and any additional image is an explicitly identified current-job reference.

For the default source-preserving mode, use:

> Produce a faithful high-resolution restoration of Image 1 only. Preserve exact aspect ratio, crop boundaries, layout, pose, proportions, silhouette, palette, material shading and attachments. Use Image 2 for context. Resolve finer material and surface detail while preserving these current-source invariants: [job invariants]. Keep atlas order and blank padding unchanged. Preserve protected content for separate compositing. Add no unrequested design or content changes.

Only in `upscale_with_corrections` mode, append:

> Apply only these explicitly requested changes assigned to this section: [correction ids and instructions]. Preserve all other source content.

Keep observed source structure separate from requested revisions. Derive object-specific checks from the current source and job; never insert a previous character's anatomy, equipment, palette or lore into another image.

For asymmetric or occluded parts, preserve those properties. For an atlas, state the cell order. For a local repair, name the affected area and composite only the reviewed repair into the accepted region. Inspect and record the tool's actual returned dimensions.

