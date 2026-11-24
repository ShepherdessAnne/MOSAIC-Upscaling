# v0.2.0 research release candidate

Manuscript v0.2; executor protocol 1.1, unchanged from the supplied package.

- Formalized declarative protocol, atlas sampling density, review and correction handling, implemented sequential compositor and cache reuse.
- Added eight synthetic tests; five expected behaviors and three reproduced defects.
- Added citation metadata. Publication date in the citation file is a draft; update it if the release is published on another day.
- Added MPCLA-1.0 custom source-available licensing terms to this release candidate.
- Next: confirm licensing terms and public author name, publish repository and tag, archive with Zenodo, add DOI to citation metadata. Keep private source art and credentials out of the repository.

Known defects: overlap order dependence, atlas background omitted from render contract, accepted bytes can change after review. Additional roadmap in paper. No real generative benchmark or optical-flow validation included.
