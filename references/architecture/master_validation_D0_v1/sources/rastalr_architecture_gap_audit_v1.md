# RastalR Architecture Gap Audit

**Date:** 10 September 2026  
**Repository snapshot:** `RastalRahl/Hospital` at `a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be`  
**Status:** Proposed continuation for review. Not an approved batch or an ingestion instruction.

## 1. Executive decision

Continue with Windows, Glass and Low Partitions (D), then Interior Structural and Vertical-Circulation Elements (E). Budget 15 clearly described new logical assets, rather than inventing 17 pieces to force an approximate total of 45. This would put Architecture at 43 if all 15 prove useful and distinct; keep the remaining planning headroom for connection/orientation needs demonstrated by actual layouts. The count is a consequence of scope, not a reason to add art.

Before producing D1 artwork, perform a small D0 geometry/alpha/validation-contract task. The audit found that at least one earlier validator writes geometry pass claims as constants. Correct the evidence standard before expanding to glass, not after generating another family. Existing production approvals and artwork remain unchanged.

## 2. What is actually approved

| Group | Logical assets | Coverage |
|---|---:|---|
| Plain floors | 4 | One material family, four variants |
| Alternate floors | 4 | One material family, four variants |
| Back walls | 4 | 32x52 native straight-wall variants |
| Side walls | 4 | Two left and two right; 20x32 native |
| Front cutaways | 4 | 32x20 native variants |
| Doors and openings | 8 | C1-C8; 32x52, 64x52, or 96x52 main carriers |
| **Architecture** | **28** | **20 foundation + 8 opening states** |

Batch 12 also has five implementation components. They are not five extra logical assets. The project-wide reported and recorded approval state is 220 logical assets, all approved, zero awaiting human review. This audit did not independently rerun the complete automated suite or reapprove every image.

The catalogue also already includes straight/corner/folded privacy curtains, a mobile privacy screen, and multiple reception counters. New D work must be fixed architecture, not recatalogued versions of those props.

## 3. What the original plan does and does not establish

The committed `architecture_master_plan_v1.json` inspected defines A1, A2, B, canonical geometry, and the master/extract/reconstruct approval flow. It does not contain an itemized D/E asset list. The broad D/E labels in the chat should therefore be treated as planning intent, not a recovered locked scope. The approximate 45-asset target does not establish exactly 17 named obligations.

## 4. Proposed Master D: Windows, Glass and Low Partitions

Sizes below are proposals unless explicitly identified as an existing reference. They do not authorize a change to approved geometry.

| Unit | Proposed logical asset | Footprint | Purpose / constraint |
|---|---|---|---|
| D1 | `hospital_glass_partition_back_01` | 1x1 tiles | Make a genuinely transparent, repeatable divider from the canonical 28 px glass-partition reference. Reference dimensions exist; repeat joins, support points, and alpha contract still require validation. |
| D2 | `hospital_glass_partition_left_01` | 1x1 tiles | Allow glass partitions to turn into a depth-running wall on the left. Derive camera-aware geometry from topology; do not rotate the back-facing PNG. |
| D3 | `hospital_glass_partition_right_01` | 1x1 tiles | Provide the separately rendered right-side boundary with consistent upper-left light. Derive geometry and lighting independently; no automatic mirrored artwork. |
| D4 | `hospital_glass_partition_front_cutaway_01` | 1x1 tiles | Close a glass enclosure on its foreground side without hiding the room. Define reduced-height presentation explicitly; do not assume the full-height/back sprite applies. |
| D5 | `hospital_observation_window_01` | 2x1 tiles | A sealed viewing window in a solid clinical wall; not a door. Proposed two-cell back-wall carrier; frame and glass are separate alpha roles. No baked second room. |
| D6 | `hospital_patient_room_window_01` | 2x1 tiles | An exterior-facing sash-and-sill window, visibly different from an interior observation pane. Proposed two-cell carrier. Make any daylight/background insert optional rather than part of modular geometry. |
| D7 | `hospital_service_hatch_01` | 2x1 tiles | A wall opening with a transfer sill for a pharmacy/reception counter. Not another freestanding reception desk. Determine protruding sill envelope and reuse existing counters where appropriate. |
| D8 | `hospital_low_partition_back_01` | 1x1 tiles | A visibly lower, permanent divider for a nurses station or waiting zone. Height requires a new explicit contract; do not silently replace canonical full-height walls. |
| D9 | `hospital_low_partition_left_01` | 1x1 tiles | Turn a low solid divider into the depth axis. Conditional on a genuinely distinct rendered module. Reuse existing parts if the derived presentation is identical. |
| D10 | `hospital_low_partition_right_01` | 1x1 tiles | Complete low-divider enclosures with the corresponding right-side presentation. Conditional on a genuinely distinct rendered module. No duplicate inventory for an identical existing part. |

D1 starts from the existing 32x28 glass reference. Architecture v2 explicitly describes glass partitions as 28 px transparent partitions. That must not silently become another full-height 52 px opaque wall. D2-D4 need camera-aware geometry derived from the same topology; their PNGs are not rotations of D1.

For D5-D7, the proposed 64x52 carrier spans two existing back-wall cells. The frame/sill is opaque; the viewing or serving aperture has an explicit, separately documented material/alpha role. A room behind the window should come from the level, not an AI-painted room permanently embedded in every window.

For D8-D10, lower height is the functional difference. Do not catalogue a new low-wall direction when an existing approved module gives exactly the required result. The ordinary front cutaway should be reused where appropriate rather than renamed as an eleventh D asset.

## 5. Proposed Master E: Interior Structure and Vertical Circulation

| Unit | Proposed logical asset | Proposed footprint | Purpose / constraint |
|---|---|---|---|
| E1 | `hospital_structural_column_01` | 1x1 tiles | Provide a freestanding structural support and a deliberate visual termination where useful. Does not substitute for proving ordinary wall junctions. Grid anchor and wall-height relation must be explicit. |
| E2 | `hospital_elevator_closed_01` | 2x1 tiles | Provide a recognizable vertical-circulation entrance with an elevator-specific surround and call control. Not C6 relabeled. Any text/display glyphs are deterministic; carrier size is proposed, not validated. |
| E3 | `hospital_elevator_open_01` | 2x1 tiles | The matching open-cabin state of E2. Preserve E2 frame and origin. Cabin backing is a declared visual component, not evidence of engine functionality. |
| E4 | `hospital_stairs_up_01` | 2x3 tiles | Allow a layout to communicate access to an upper floor. Footprint is provisional. Requires a new elevation/landing scaffold, collision guidance, and camera proof. |
| E5 | `hospital_stairs_down_01` | 2x3 tiles | A distinct descending/stairwell view for access to a lower floor. Not a flipped ascending image. Opening, edge protection, landings, and draw order require validation. |

These are proposed interior-system additions, not a claim that the pack already includes multi-storey gameplay. Elevator states need the same carrier, frame and origin; stairs need a new elevation/landing contract. No rotated finished sprites, guessed rise/run, or generated architecture drifting into a different camera.

## 6. Integration work that is not automatically extra inventory

### Ends, corners and junctions
The canonical topology calls for N/E/S/W, ends, corners, T junctions and crosses. The existence of masks or a rectangular room reconstruction is not itself evidence that every final-art junction is usable. Build small L/T/cross and connected-room layouts with approved modules first. Record shared contact regions and rendering order. Add a cap, mask or visual adapter only when an actual uncovered case proves it necessary. Technical masks and duplicated exports are not new marketed assets.

### Opening direction coverage
Current C1-C8 artwork is the back-wall-facing family. Do not advertise all-direction door coverage or create 24 additional orientations automatically. First test whether a minimal side/front opening adapter and the existing cutaway system satisfy the intended scenes. Any new artwork must go through an explicit future scope/approval decision.

### Transparent glass versus an opaque recess
C7's reference report explicitly retained an opaque recessed backing. That is a valid static visual presentation, but not a hole through which another room automatically renders. D1/D5 require a different, declared alpha policy. Test a known colored object behind the glass; do not use the absence of zero-alpha pixels as the glass-success criterion. Structural frame contact checks and intentionally translucent glass checks are different.

### Static door states versus animation
C2/C5 have upper door portions baked into the main doorway sprite, plus small lower projection overlays. Those overlays are not complete independently rotatable leaves. C7 has more complete parked leaves but still uses a baked passage backing. Preserve the useful static states without claiming an animation system has been implemented.

### Lateral parking and footprint
C7's two-cell doorway has leaves outside that doorway box. Its assembly reaches from -24 to 88 native x relative to the main carrier, or 112 px total visual span. Placement must reserve the neighboring wall bays even though the logical doorway footprint remains two cells. A window or nearby door must not be placed inside this reserved envelope.

## 7. QA findings and bounded corrections

**Evidence gap:** In `tools/validate_architecture_master_c5_v1.py`, `main()` validates source dimensions and that JSON constants match the expected specification, crops by constants, computes alpha metrics, and writes fields including `deviation_source_px: 0`, `drift: none`, `matches_spec: True`, and reconstruction `result: pass` as literals. These report fields are not independent measurements of every generated-art boundary. This does not prove that approved artwork is bad, but it means earlier claims of independently measured zero drift were too broad.

For future validators, distinguish four things: expected geometry, computed/observed measurements, user-reviewed visual findings, and assertions that can actually fail. Demonstrate failure using intentionally shifted or broken fixtures. Never report a manually assumed or unmeasured feature as computed evidence.

**Housekeeping:** Batch 12 QA Markdown still says all eight assets await review near the top and repeats its later APPROVED section twice. The JSON status is approved. This is a reporting inconsistency, not a request to undo approvals. Fix report generation idempotently in the bounded D0 task. Preserve historical provenance and raw validation artifacts.

**Visibility:** GitHub metadata reported the repository as public. The owner should confirm that public access to unreleased source and production art is intentional. This audit changed no repository settings.

## 8. D0 before D1

D0 should be a small preparation task, not a broad pipeline rebuild:

1. Adopt one half-open rectangle convention and explicit native/source-scale, footprint, contact-region, visual-envelope and render-origin fields. Generate scaffold, mask and diagnostic overlay from that single contract.
2. Define D1's glass/frame alpha policy and repeat joins, including shared mullions and ends so repeated alpha layers do not darken or double their posts.
3. Build reference-only small connected-room, L/T/cross, and transparent-glass test scenes. Use approved architecture unchanged.
4. Add focused bad-fixture tests: shift a join, remove a required connector pixel, or move an anchored overlay; the appropriate check must fail.
5. Correct the current report headline/duplicate approval without touching artwork, then document which prior metrics were measurements versus declared expectations.

Stop with reference-only D1 geometry/scaffold and a compact review montage. No bulk image generation, no production ingestion, no new inventory records, and no changed approval state.

After D0, D1 is the first art exercise: a connected repeat of the 32x28 back-facing glass divider, authored inside exact geometry and reviewed at native scale. No fresh full-room generation.

## 9. Production cadence and counts

Do not repeat the long wait for an entire eight-master family before any visible progress. Use small coherent subfamilies:

- D1-D4 glass boundaries: up to 4 logical assets.
- D5-D7 windows/service hatch: 3 logical assets.
- D8-D10 low partitions: up to 3 distinct logical assets, reuse where possible.
- E2-E3 elevator states: 2 logical assets.
- E4-E5 stairs: 2 logical assets, only after elevation proof.
- E1 column: 1 logical asset.

Each subgroup follows scaffold/contract -> appearance -> evidence -> staged candidates -> human visual review -> approval. Each approval can increase the inventory without waiting for all of D and E. Batch numbers are assigned from the real repository when the task begins, not preemptively reserved here.

Planning result: 28 + 15 = 43 Architecture assets, or 220 + 15 = 235 total project assets, if all proposed additions are new and approved and nothing else changes. A coverage-proven adapter can raise that; reuse can lower it. Neither masks nor optional exports should be used to make the arithmetic land on 45.

## 10. Model and conversation guidance

For this architecture audit, keep the current ChatGPT 6 Pro selection and the same conversation. For the bounded D0 geometry/QA setup, the recommendation is a fresh Codex thread on the same Hospital repository with GPT-6 Astra and High effort if available. Medium is the default recommendation for later tightly specified extraction, staging and promotion work. These are task recommendations, not guarantees of exact pixel geometry or availability.

No new Codex task has been started by this audit. The proposed scope should be reviewed before implementation.

## Sources

All repository sources are pinned to the audited commit.

- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/metadata/catalog.csv
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/metadata/manifest.json
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/docs/ARCHITECTURE.md
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/references/architecture/master_validation_v1/sources/architecture_master_plan_v1.json
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/references/architecture/rastalr_architecture_v2/architecture_v2_spec.json
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/metadata/architecture_doors_openings_batch_12_qa.md
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/tools/validate_architecture_master_c5_v1.py
- https://github.com/RastalRahl/Hospital/blob/a48cc2ce0ce5c104b679ea8b225f9c2c8787f4be/references/architecture/master_validation_C7_v1/architecture_C7_validation_report.md
- OpenAI model-label documentation checked 10 September 2026: https://help.openai.com/en/articles/20001354-GPT-5.6
