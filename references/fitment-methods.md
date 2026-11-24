# Fitment methods — the 2026-11-24 experiments

Which deterministic (or deterministic-plus-learned) upscale should build the
MOSAIC master — the *fitment* the semantic tiles are then cut from? All runs
below are on the same source (the hisui Neon Night sheet, 1170×780 → 3510×2340
at 3×), measured and judged the same day. Shepherdess's verdicts govern;
gradient-energy figures are a proxy only, never the verdict.

## Standing decisions (her rulings, 2026-11-24)

- **Default fitment: the SGSR hybrid** — SGSR 1 reconstruction blended through
  NIS's own edge gate (m = Σw of the NIS directional edge weights):
  Y = (1 − m)·SGSR1 + m·NIS, no shaping. It is the best non-Waifu fitment
  **as a detail map for the AI tile stage**.
- **For direct human viewing, plain SGSR 1** was the best all-around
  non-Waifu performer. A fitment has two consumers — human eyes and the AI
  detail map — and they crown different winners; state the consumer when
  stating the best.
- **Fitment choice gate:** the operator asks the user *fast or best?*
  Fast = SGSR hybrid (seconds). Best = the Waifu tier (below). Waifu is
  optional by design and never the silent default: seconds on a local GPU,
  ~196 s per sheet under software Vulkan on a cloud CPU-only host.

## Results by method

| Method | What ran | Outcome |
|---|---|---|
| Lanczos | Classical baseline | The deterministic reference everything is compared against. |
| FSR 1 | Software port of AMD EASU + RCAS | Her verdict: "just looked identical" to Lanczos. Not adopted. |
| FSR 3 SR | Temporal core ported with synthetic history (72 jittered frames, zero motion vectors, flat depth) | Converged, still Lanczos-class (+2% proxy). **Temporal route closed for stills**: a temporal upscaler's extra detail is new scene samples; a bitmap can only be resampled. |
| NIS | NVIDIA scaler, full port from its SDK | Looks best of the spatial kernels, most artifacts (proxy 0.04398). **Out-of-spec note:** NIS's own config rejects upscale beyond 2× (kScale < 0.5); the 3× run is out-of-spec, while a 1.5× finishing step is in-spec (kScale 0.667). |
| SGSR 1 | Qualcomm's open shader, faithfully ported | Clean at every size (proxy 0.03389); best all-around for human eyes. |
| SGSR hybrid | SGSR 1 blended through NIS's edge gate | NIS's gate is leaky on this content (mask mean 0.54; only 38.4% of pixels fully closed — the closed flats are pure SGSR, exactly where NIS artifacts would live). Zoomed: hybrid blend best overall except text (SGSR wins text); hybrid-sharpen worst, because of text. At viewing size the ranking scrambles: hybrid-sharpen best. |
| Anime4K | Official GLSL Mode A via libplacebo on software Vulkan (×2 + Lanczos 1.5×) | Proxy 0.03669. |
| Waifu2x | Official ncnn-vulkan, cunet, no-denoise (×2 + finish) | **Her verdict: best overall.** With finishes: zoomed winner Waifu + Lanczos + NVSharpen (0.04606); regular-size winner Waifu + NIS 1.5× (0.04742). Waifu pass: 196 s on software Vulkan here; seconds on a real GPU. |

Whole-image spatial proxy for the record: NIS 0.04398 · FSR 1 0.03671 ·
SGSR 1 0.03389 · Lanczos 0.03180 · Catmull-Rom 0.02979 · bilinear 0.02788 ·
Mitchell 0.02648.

## Verdict discipline (standing laws from these experiments)

1. Comparison boards are 100% crops — maximum scrutiny. State the display
   size when stating a winner; rankings scramble between zoomed and
   viewing sizes, and both are true.
2. State the consumer (human eyes vs AI detail map) when stating the best.
3. Process integrity: every chain was re-run from its stated inputs — the
   Waifu chains reproduce bit-exactly, every finishing pass is last, and
   viewing-size boards are display copies made after the fact, never fed
   into any chain. No passes after zooming.

Full run records live with the experiment folders (fsr1_test/, fsr3_test/,
spatial_comparison/) in the 2026-11-24 hisui run archive.
