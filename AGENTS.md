# RastalR Modern Hospital & Emergency Services

## Non-negotiable production rules

- Build on a 32 px logical grid. Store the footprint in metadata; do not infer it from the PNG canvas.
- Camera: rectangular-grid RPG oblique. Ground remains axis aligned; depth recedes upward; horizontal and vertical edges remain horizontal and vertical. Freestanding assets default to `bottom_center`; architecture uses grid anchors.
- Scale against an invisible adult reference of about 26 x 46 px.
- Style is **RastalR Everyday Pixel / Warm Clinical Pixel Art**: crisp clusters, hard edges, no anti-aliasing, blur, fake high-resolution downscaling, heavy dithering, or noisy AI texture.
- Use dark navy-charcoal outlines (`#182331`, `#273746`; sparingly `#111923`), strongest at exterior silhouettes. Never default to pure black.
- All lighting comes from upper-left. Directional variants are independently authored; never rotate a rendered sprite to create direction.
- Keep recurring colors controlled (roughly 40–60): warm ivory, cool steel/slate, muted teal and surgical green, restrained wood/lavender/yellow, and small emergency red-orange/amber accents.
- Use small contact shadows only. Do not bake broad cast shadows. Final PNGs require true transparent backgrounds.
- Screens use abstract graphics only. Sign text and pictograms are separate deterministic assets; no AI-generated readable text, brands, or protected medical/emergency marks.

## Architecture

- Architecture is deterministic and geometry-first. Never use AI to define topology, grid alignment, footprints, or openings.
- The topology uses a 32 px tile, 8 px centered wall strip, connection region x/y 12–19, approximately 44 px physical wall height, and 8 px cap.
- North/back walls are full faces; east/west walls are shallow camera-aware boundaries; south/front walls are low cutaways. Doors, windows, and glass use the same grid anchors.
- Treat `references/camera/rastalr_camera_reference_v1.png` and `references/architecture/` as authoritative.

## Workflow and data

- Never bulk-generate art without explicit instruction. Work in coherent asset families; pilot batches are 12–24 assets.
- Preserve the approval path: `source/generated` -> `staging/pending` -> technical QA -> human visual QA -> `staging/approved` -> `assets/<category>`.
- Do not overwrite approved artwork automatically. Rejected work stays traceable in `staging/rejected`.
- Filenames are deterministic, lowercase snake_case, and human readable. No generic export names.
- Every entry in `metadata/manifest.json` needs a reuse scope (`hospital_only` or `everyday_world_common`), logical footprint, anchor, source path, status, and QA information.
- Count only unique, meaningfully useful assets. Do not count export formats, scales, sheets, frames, trivial recolors, or near-identical variants separately.

## Review bar

Technical QA supplements, never replaces, visual review. Check silhouette, scale, camera, upper-left light, pixel density, outline/palette consistency, gameplay usefulness, meaningful distinction, clean alpha, and modularity.

## Git workflow

This repository uses GitHub as the canonical project repository.

After every successfully completed user-requested task that modifies repository files:

- inspect `git status`
- run the relevant automated tests/QA required by the task
- do not commit failed, incomplete, or experimental work unless the user explicitly requests it
- commit all intended changes from that task with a concise descriptive commit message
- push the completed commit to `origin` on the current branch
- never force-push
- never rewrite or amend existing published commits unless explicitly instructed
- never commit `.rar` repository snapshots or temporary transfer archives
- leave the worktree clean when the task is finished
- report the resulting commit SHA in the final response
