# Generative Section Upscaling — Complete Reusable Package

Extract the entire ZIP and keep its directory structure intact. All supporting scripts, schemas, templates, and references used by SKILL.md are included.

## Start here

- SKILL.md: instructions for an AI or agent running the method.
- Generative_Upscaling_Workflow.md: the generic workflow brief.
- Generative_Upscaling_Method_Manifest.json: the portable method, with its embedded job schema.
- Generative_Upscaling_Job_Template.json: a blank per-image job.
- scripts/sections.py: section preparation and final compositing.
- references/: the helper schema, method manifest, coordinate format, prompt template, construction review, and optional historical case.
- assets/: the skill's blank job template and icon.
- agents/openai.yaml: agent display metadata.

## Python setup

Use Python 3.10 or newer. From the extracted package directory:

```bash
python -m pip install -r requirements.txt
```

Pillow, NumPy, and jsonschema support preparation and assembly. OpenCV supplies optional registration; use --no-align to disable registration.

## Run a job

Copy the blank job template to job.json. Fill in the source image path, target scale, section rectangles or atlas cells, invariants, and protected regions; then set binding_status to bound. Source paths are resolved relative to job.json.

```bash
python scripts/sections.py prepare job.json sections
```

Edit the prepared inputs with the image generator, using the full source as context. Inspect the generated outputs. In sections/render-records.json, set each accepted section's render path and accepted=true. Relative render paths resolve from the sections directory.

```bash
python scripts/sections.py assemble job.json sections final.png --scale 4
```

Match --scale to the bound job's target.scale. The helper performs preparation and compositing; section generation is performed with the image editor described in the workflow.

The optional historical case is background only. Derive the current image's design rules from its own source and references.
