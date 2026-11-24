# MOSAIC Upscaling

**Model-Orchestrated Semantic Amplification via Image Compositing**  
*Render locally. Preserve globally.*

Originating concept: **Shepherdess**, 23 November 2026. Developed collaboratively with Tachikoma (AI assistant). Independent research.

MOSAIC separates regional generative rendering from authority over the final image. Semantic crops and detail atlases are generated externally, reviewed for structure, and registered and composited onto a deterministic source master. A declarative protocol records the job, generation contracts, review decisions and assembly metadata.

## Research release v0.2

- [Research manuscript (LaTeX)](paper/MOSAIC_v0.2.tex). The compiled PDF is pending upload.
- Original protocol 1.1 files: [workflow](Generative_Upscaling_Workflow.md), [schema](references/job.schema.json), [executor](scripts/sections.py) and [agent skill](SKILL.md).
- [Original setup instructions](ORIGINAL_README.md).
- [Synthetic tests](tests/test_executor.py) and [recorded results](tests/results.txt).

The original executor is unchanged. This release establishes five expected behavior checks and reproduces three known defects. It does not establish superiority in generative quality. The external image editor is not included.

## Reproduce checks

Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python tests/test_executor.py
```

The eight tests include three explicit defect-reproduction tests. The passing suite does not imply those defects have been corrected. See the manuscript for their interpretation.

## Cite

Shepherdess (2026). *MOSAIC: Model-Orchestrated Semantic Amplification via Image Compositing: Source-Authoritative Generative Super-Resolution with Black-Box Image Editors*. Research preprint v0.2, 24 November 2026. DOI pending publication.

See `CITATION.cff`.

## License

MOSAIC is source-available under the [MOSAIC Personal Use and Commercial Licensing Agreement (MPCLA-1.0)](LICENSE.md). Personal, noncommercial use and independent noncommercial research are free. Commercial use, organizational commercial R&D, derivative development, redistribution and native AI-platform integration require separate written permission and paid licensing under the agreement. Ordinary user configurations and generated artwork are not derivative software. Personal use through third-party AI tools is permitted subject to the agreement.

Commercial licensing: contact [ShepherdessAnne](https://github.com/ShepherdessAnne). The full license controls; this summary does not grant additional rights.

