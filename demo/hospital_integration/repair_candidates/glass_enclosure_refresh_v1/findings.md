# Glass enclosure refresh — actual hospital reference candidate

User authorized a thinner, more transparent enclosure with cleaner corners, preserving footprints, openings and collision. The review uses the actual hospital with the Foundation wall candidate. No production/staged files or approval states are modified.

## Visual changes

- Main glazing alpha is **56/255 (22%)**, down from the original primary 150/255 (59%). A quiet cool tint lets the original floor and objects remain visible. Repeated reflection markings were removed along with the repeated panel posts.
- Back horizontal rails are two pixels high. Side rails are one pixel wide and no longer restart with a four-pixel crossbar at each 32px tile boundary. Front run ends retain two-pixel vertical termination rails around the unchanged opening.
- Existing corner views own the back enclosure ends. Their inner side rails begin below the back pane's lower rail, eliminating short protrusions into the pane. The original transparent exterior outline remains unchanged.
- Opaque samples across the 22 rendered placements decrease from **5,752 to 2,348 (59.2%)**. This is a placement-weighted measure, not a count of logical assets.

Codex inspected furnished, unobstructed and behind-figure Godot views. The enclosure now reads as lightweight glazing around the examination area rather than a second solid-wall system. Equipment is visible through the tint and the repeated heavy divisions are gone. Its boundary is intentionally subtle; visual acceptance is still pending. Foreground solid-wall visibility remains a separate unresolved issue.

## Boundaries and provenance

`hospital_glass_review.gd` deterministically draws material/frame regions within each existing glass sprite's nonzero-alpha support. The candidate preserves native canvas sizes and all transparent exterior pixels, grid anchors, placement transforms, sort order, opening widths and collision. No rotation, resampling, blur, external artwork or new topology is introduced. `mapping.json` records each candidate, original source/hash and unchanged placement declaration.

There are 22 placement-specific review textures corresponding to the existing four logical glass parents, not 22 new assets. Run-start front framing is explicitly placement-dependent; the candidate is not yet a production-ready exclusive-view package. Alpha/frame regions intentionally differ from the old approved technical contracts, so those contracts would need an explicit revision and validation before staging/promotion. Original pending files and their historical QA remain unchanged.

## Review and verification

Open `../../hospital_glass_review.tscn`, press F6. O toggles original/candidate glass; H toggles the wall candidate. Other existing hospital controls remain. Candidate textures are generated from the local originals at startup; the review flag also saves the textures and mapping.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/hospital_glass_run.log res://hospital_glass_review.tscn --quit-after 600 -- --hospital-glass-review
```

Require **HOSPITAL_GLASS_REVIEW_PASS** and **HOSPITAL_SMOKE_PASS**. Checks cover all support masks and fixed transforms, frame reduction, O restore, behind/inside/front poses, the actual hospital route, door collision and exact source-over pane transmission/figure sorting. The existing smoke now obtains its reference pane sample through a default method; this scene overrides it with the candidate's actual RGBA. Default startup still samples the original texture and was separately smoke-tested successfully. This does not relax either compositing assertion.

The independent Foundation review and production startup remain intact. Inventory stays **224 manifest / 220 approved / 4 pending**; no reference candidate is promoted.

Final checks: candidate review and candidate/default **HOSPITAL_SMOKE_PASS**; focused integration **10 passed in 0.33s**; full suite once **379 passed in 58.56s**. Existing SHA-256 baseline: **3,533 protected files unchanged**, including production, metadata, local reference downloads and all five user-owned demo files. Git inspection confirms prior candidate artifacts unchanged. `git diff --check` passed.
