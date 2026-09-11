# Connected rooms using one wall convention

User authorized extending the single-reference room into two connected rooms with L/T/cross contacts, furniture and a figure walkthrough. This scene preserves the same SmallBurg-inspired visible convention: 44px walls everywhere, narrow connected caps, full horizontal faces and a full front. No mixed-height reveal is active and no third-party pixels are used.

## Layout and inspection

Two upper rooms each contain the existing approved hospital bed and bedside cabinet at native size. Each has a 32px doorway into the corridor. The north divider creates a T; the internal horizontal wall and its southern divider extension form a cross. The divider ends before a 96px ground-depth corridor connection, so both rooms remain reachable. The outer enclosure supplies L corners; the front has a 32px exit.

The first iteration's corridor was too shallow visually: the full front face concealed most of the passage. The completed version adds two ground rows of depth without changing wall heights. Codex inspected the furnished Godot view and corridor-crossing image. The caps connect consistently at the T and cross, and the deeper corridor shows the figure and travel space clearly. The cross's short southern arm has an exposed full-height end face; this is an explicit wall terminal within the single-height model, not a mixed-height connector patch. Terminal finish remains plain geometry.

`corridor_crossing_godot.png` is the main review. Room A/B, rear-wall, doorway and exit poses are captured separately. Full walls still occlude the figure near their front faces as expected. This candidate demonstrates this layout, not arbitrary autotiling or finished Foundation art. User visual acceptance is still required before applying finishes and integrating the hospital. Production policy, artwork and approvals remain unchanged: **224 / 220 approved / 4 pending**.

## Implementation and practical checks

`connected_reference_rooms.gd` reuses the existing renderer, actor drawing and movement. The original upper-room footprint is reused; only the corridor and front boundary extend. Three overridable bounds in the shared renderer allow the deeper canvas without duplicating its drawing logic. Their defaults reproduce the previous scenes.

Open `../../connected_reference_rooms.tscn` and press F6. WASD moves; F toggles furniture/figure; G shows the grid; R resets in room A. The 26x46 figure uses an 18x8 foot contact and four declared furniture contacts.

```powershell
& C:/Godot/Godot_v4.7.1-stable_win64_console.exe --path demo/hospital_integration --log-file .qa/connected_room_run.log res://connected_reference_rooms.tscn --quit-after 240 -- --connected-room-review
```

Expect `CONNECTED_REFERENCE_ROOMS_PASS`. Checks cover 5x5 cap regions at L/T/cross contacts, every occupied ground pixel's single height, solid-wall and bed collision, a one-pixel-step walkthrough from room A through the corridor to room B and the front exit, and rear/doorway/corridor/exit figure visibility. The earlier single-room scene was also rerun after generalizing the renderer and produced byte-identical tracked images with `SINGLE_REFERENCE_ROOM_PASS`.

Verification: Godot connected-room and single-room checks passed; focused integration tests **10 passed in 0.36s**; full suite once after completion **379 passed in 58.89s**. Existing preservation baseline confirms **3,533 files unchanged**, including production, downloaded references and five user-owned demo files. Git inspection confirms earlier candidate evidence unchanged. `git diff --check` passed.
