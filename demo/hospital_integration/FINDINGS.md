# Hospital layout inspection

Single bounded pass from `a55120924814ee72efb0f8a85086d216ec56e94e`. Reviewed at native 2x gameplay zoom in Godot **4.7.1.stable.official.a13da4feb**, Compatibility renderer / NVIDIA RTX 3050 Laptop.

The floor shrank from **24x11 to 21x10 tiles** (20.5% less area). Counter, kiosk and brochure rack now serve one waiting group; cooler and plant occupy perimeter positions. All six examination props, including the supply cabinet, are inside the glass bay. Bedside cabinet, IV stand and visitor chair surround the bed; the corridor and door approach stay clear. All 20 prop types retain their original native bytes and sizes.

## Remaining issues, in priority order

1. **Asset representation — noticeable:** `hospital_sliding_clinical_doors_open_01` retains its opaque recessed backing. The figure's body is hidden while standing behind the open doorway even though collision is cleared; parked leaves remain additive. The original layout capture exposes this limitation. The separate, unapproved alpha candidate now resolves it in the demo only; production artwork remains unchanged.
2. **Asset artwork — noticeable:** `hospital_wall_back_straight_01`, `hospital_wall_side_left_01`, `hospital_wall_side_right_01` and `hospital_front_wall_cutaway_01` have repeated dark divisions/segmented caps. `hospital_floor_plain_01` shows fine texture and tonal repetition. No seam-concealing overlays were added.
3. **Asset artwork/proportions — noticeable:** `waiting_bench_2seat_01` remains compact beside `waiting_chair_01` and `visitor_chair_patient_room_01` (native widths 52 / 40 / 48px). Its two-seat silhouette has a finer pixel density. `brochure_rack_01` and `lobby_plant_01` retain visible stray pixels/fine texture. These exact IDs need art review; none was resized or cleaned.
4. **Layout — acceptable limitation:** authored north-facing door and shallow cutaways constrain the patient-room frontage. The solid divider remains visibly butt-joined. The examination entrance is a 64px gap between straight glass runs, with no invented junction or door orientation. Current routes pass, but this sample does not establish support for other layouts.
5. **Runtime implementation — acceptable limitation:** contacts remain demo-only base rectangles and side partitions sort per cell. The tested paths and front/behind glass poses pass; this is not exhaustive per-pixel occlusion coverage. Local certificate/shader-cache warnings remain non-blocking; the launcher provides a writable log path.

## Captures and verification

- `overview_before.png`: byte-identical original overview. `overview.png`: improved clean overview. `captures/layout_glass_behind.png`, `captures/layout_glass_front.png`, `captures/layout_door_open.png`: actual Godot viewport captures, not composites.
- Scripted engine movement reaches reception, waiting, examination and bedside. Closed door blocks; open door passes; the glass entrance and furniture contacts behave correctly. Existing reset, integer zoom and overlay assertions pass.
- Behind-pane viewport sample equals source-alpha blending: **(175,178,151)** from alpha **150/255** over the figure's yellow. The same glass renders behind the foreground figure with its unmodified skin color **(232,203,167)**. Opaque corner contacts remain 48px north / 32px south, without stacked glass.
- Three existing focused tests were updated for the layout; no increase in test count. Full suite run once at completion: **370 passed in 58.59s**. Fresh import and GPU smoke from an isolated extraction of the cache-free ZIP also passed.

Inventory remains **224 total / 220 approved / 4 needs_human_review**. All source PNGs, manifest/catalog and historical evidence remain unchanged. Batch 13 is intentionally pending; no production replacement, approval or D5 work occurred.


## Open-door alpha candidate � current pass

From `ca7833878ab312f163054011aab2845d24728d39`, with no layout changes. Native C7 clear-passage geometry maps to `[4,14,60,52)`, but direct pixel inspection identifies inner jambs at x4..6/x59 and threshold rows48..51. The narrower half-open mask **[7,14,59,48)** removes only recessed backing: **1,768 changed alpha pixels; zero RGB changes; zero changes outside the mask**. Canvas64x52, anchor, header, jambs, threshold and both byte-identical parked leaves are retained. The full rationale and boundary samples are in the candidate's `repair.json`.

Godot4.7.1 GPU review passes closed-door approach, open passage/crossing/foreground, header occlusion and parked-leaf rear/front ordering. The entire104x68 screen-pixel aperture equals a control render with only the main doorway hidden, proving it reveals the existing room and figure. No fake backdrop, shader, color removal or Z override is used. The preserved threshold and header can still legitimately cover feet/head at their ground-relative positions. This is an unapproved repair candidate, not a production replacement.

`captures/door_alpha_repair/door_and_glass_review.png` is a compact before/after plus pending-glass comparison made from unscaled Godot capture crops. Existing glass capture bytes are preserved. Final verification: **4 focused tests passed; full suite run once, 371 passed in 86.18s**. Fresh cache-free ZIP import and GPU door review also passed. No GDScript/import failures; the host certificate-store warning is unrelated to this offline demo.
