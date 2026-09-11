# Outer foreground cutaway review

The full-height review wall hid the figure near the south perimeter. This completed reference candidate renders that boundary as a 12 px face with the existing 8 px ground-strip cap, instead of a 44 px face. All source artwork, topology, anchors and foot-contact collision are unchanged. Presentation is opaque native pixels, with no transparency fade or character overlay.

Open `../../foreground_visibility_review.tscn` and press F6. C compares full/cutaway foreground; H compares original/candidate architecture. WASD, E door and zoom controls remain. Default F5 startup is unchanged. Glass remains excluded from this review and parked separately.

## Implementation scope

- Only the eight ground rows y=408..415 get new textures. Their image rows 0..31 are transparent; rows 32..44 are opaque for the connected strip x=24..711. No resampling of the Foundation finish.
- North, side and internal patient-room wall rows reuse the exact original texture objects. The south-facing ends of the tall side walls remain visible above the lowered front cap; the low cap meets both footprints without a hole.
- Internal patient-room wall/door-header occlusion remains full height and is outside this outer-boundary correction. Final whole-wall review must assess it before production promotion; this result does not claim that every interior occlusion case has been resolved.
- No production asset, approval, manifest entry or user-owned project configuration changes. New rendering scripts are reference implementation, not new logical assets.

## Visual inspection and practical checks

Codex inspected before/after, overview and both corner positions in Godot captures. The head and torso remain readable close to the front boundary; the low strip still reads as a wall. The exposed tall side ends are an intentional section-cut presentation rather than disconnected wall footprints. This restores the documented low-front convention after the full-height reference experiment. Human visual approval remains pending.

`before_godot.png` and `after_godot.png` compare the same figure position `(112,400)`. The former hides the torso; the latter reveals it. Five edge captures place the figure at x=42,112,352,528,694 and y=408, directly against the collision boundary. The review samples actual viewport head/torso colors at each position and attempts to move through the wall; movement is blocked in every case.

The review also checks opaque cutaway alpha, unchanged non-front textures, all four added connection contacts, closed/open door passage, the existing hospital walkthrough, C/H toggles and continued glass exclusion. Initial test-only failures came from an exact floating-point position assertion and closing the door before the walkthrough crossed it; the final checks use the existing movement tolerance and the correct door state. No collision rule was weakened.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/foreground_run.log res://foreground_visibility_review.tscn --quit-after 300 -- --foreground-visibility-review
```

Require `FOREGROUND_VISIBILITY_PASS`. Focused existing integration tests: **10 passed in 0.55s**. Full-suite result recorded after completion below.

Final verification: **379 passed in 100.47s**, Godot **FOREGROUND_VISIBILITY_PASS**, and **5,687 existing non-task files unchanged** by hash. Inventory remains **224 / 220 approved / 4 pending**. Only new review files, demo README and project state are included in this task.
