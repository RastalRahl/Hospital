# Asset coverage and remaining backlog

Verified 2026-09-11 against HEAD `5d1ae1f`, the current manifest and catalog. Product authority: [ASSET_ROADMAP.md](ASSET_ROADMAP.md). This is planning only: no proposed ID below exists in the manifest yet, no production batch is authorized, and no approval is changed.

## Counting and category ownership

Each non-rejected manifest parent counts once in its existing primary category. Roadmap labels map to manifest keys shown below; new category keys are proposals only. Shared use is described but never counted twice. Catalog IDs, categories and statuses agree with the manifest. All 220 approved final PNG paths exist. Pending means `needs_human_review` here (all four are glass). Signed gap is target minus current; negative means over budget. Repairs, engine geometry, implementation views, states bundled within a parent, and components add zero. Existing approved state/orientation records are retained as recorded, not retroactively merged in a documentation task.

| Roadmap category (manifest key) | Target | Current | Approved | Pending | Signed gap |
|---|---:|---:|---:|---:|---:|
| Architecture (`architecture`) | 45 | 32 | 28 | 4 | +13 |
| Reception / Waiting (`reception`) | 22 | 22 | 22 | 0 | +0 |
| Patient Rooms (`patient_rooms`) | 32 | 29 | 29 | 0 | +3 |
| Examination (`examination`) | 20 | 22 | 22 | 0 | -2 |
| ICU (`icu`) | 20 | 19 | 19 | 0 | +1 |
| Surgery (`surgery`) | 24 | 19 | 19 | 0 | +5 |
| Radiology (`radiology`) | 16 | 19 | 19 | 0 | -3 |
| Laboratory (`laboratory`) | 20 | 20 | 20 | 0 | +0 |
| Pharmacy (`pharmacy`) | 14 | 18 | 18 | 0 | -4 |
| Emergency (`emergency`) | 22 | 19 | 19 | 0 | +3 |
| Exterior / Ambulance (`exterior`) | 24 | 1 | 1 | 0 | +23 |
| Morgue (`morgue`) | 12 | 0 | 0 | 0 | +12 |
| Staff / Admin (`staff_admin`) | 18 | 0 | 0 | 0 | +18 |
| Cafeteria / Kitchen (`cafeteria_kitchen`) | 14 | 0 | 0 | 0 | +14 |
| Bathrooms / Utility (`bathrooms_utility`) | 14 | 0 | 0 | 0 | +14 |
| Signage / Decor (`signage_decor`) | 25 | 0 | 0 | 0 | +25 |
| Inventory / UI (`inventory_ui`) | 20 | 3 | 3 | 0 | +17 |
| Abandoned / Horror (`abandoned`) | 38 | 1 | 1 | 0 | +37 |
| **Total** | **400** | **224** | **220** | **4** | **+176** |

Positive category gaps total **185**; Examination (+2 current above budget), Radiology (+3) and Pharmacy (+4) account for **9** excess assets. Filling every positive gap while retaining those assets would yield **409**, not 400. No deletion or category-budget change is proposed merely to force the total.

This audit names **158 proposed additions**, giving **382 logical assets** if all prove useful and the four parked glass parents ultimately ship. Excluding those glass parents gives **378 release candidates**. Thus plan around **158 meaningful additions (approximately 160)**, not an automatic order for 176 or 185. Proposals remain subject to native-scale visual distinction and room-use checks; marginal items should be merged or dropped. The remaining budget is headroom for demonstrated needs, not unnamed production commitments. The original 400 target and 350–450 useful finish range are unchanged.

## Capabilities by category

Coverage statements below are based on manifest IDs/metadata and the existing integration findings, not a fresh visual approval of every sprite.

| Category | Important coverage already available | Important capabilities still missing |
|---|---|---|
| Architecture | 8 floors, 12 solid-wall records, 8 door/opening records; 4 pending glass parents. | Reliable junctions/endings and foreground visibility need repair; stairs, lifts and service/access boundaries missing. Glass parked. |
| Reception / Waiting | Modular/accessible counters, kiosk, queue system, seating, wheelchair, water cooler, plant, sanitizer and janitorial cart. | No essential new family identified; bench/rack/plant cleanup remains. |
| Patient Rooms | Multiple beds, bedside furniture, IV/oxygen, monitoring, curtains/screens, wardrobe, visitor chair and call panel. | Patient transfer lift, family sleeper and bedside commode. |
| Examination | Tables/chairs, diagnostic wall equipment, ultrasound, lighting, sink, cabinets, trays and sharps disposal. | No material general-exam gap identified from inventory; assess representative room, not additional stool variants. |
| ICU | Ventilators, monitors, pumps, suction, gas manifold, ceiling boom and isolation supplies. | Distinct bedside renal-support machine; reuse existing ward beds and monitoring. |
| Surgery | Operating table/lights, anesthesia, electrosurgery/smoke extraction, endoscopy, instruments, scrub sink and warming. | Perfusion, suction/irrigation, positioning and scrub preparation support. |
| Radiology | CT, MRI, PET/CT, gamma camera, mammography, DEXA, X-ray, C-arm, control and shielding. | No material imaging gap identified; shared waiting/storage assets cover support. |
| Laboratory | Analyzers, microscopy, PCR, centrifuges, biosafety/fume hoods, bench, samples and cold storage. | No essential new family identified; shared desk/storage can furnish ancillary areas. |
| Pharmacy | Dispensing, automation, secure/cold storage, compounding, unit-dose packaging, returns and delivery. | No essential new family identified; no more generic cabinet variants. |
| Emergency | Trauma stretchers, crash cart, defibrillator, triage, portable X-ray, immobilization, isolation and decontamination cart. | Rapid fluid delivery, fixed decontamination fixture and airway workspace. |
| Exterior / Ambulance | One ambulance. | Arrival/bay infrastructure, accessible approach, parking and exterior utilities; reuse ambulance before proposing another vehicle. |
| Morgue | No dedicated assets; reuse surgery instrument trolley, lab cold-room support and admin desk where appropriate. | Body transport/storage, autopsy and washing/preparation room. |
| Staff / Admin | No assigned assets; physician desk and visitor seating available from clinical categories. | Office workstation, records, staff lockers, meeting and break-room furnishings. |
| Cafeteria / Kitchen | No assigned assets; meal_tray_01 is already in Inventory / UI; water cooler available. | Meal service, dining furniture, cooking/prep, cold storage and dishwashing. |
| Bathrooms / Utility | No assigned assets; janitorial_cart_01, linen_hamper_01, sinks, recycling and waste bins exist elsewhere. | Accessible toilets/shower, housekeeping storage, laundry machines and utility sink. |
| Signage / Decor | No assigned assets; lobby plant, information/sign stands and brochure rack already exist in Reception. | Reusable deterministic wayfinding/safety symbols, information surfaces and limited wall decor. |
| Inventory / UI | First-aid kit, meal tray and patient-status UI. | Usable consumable/document pickups and interaction/inventory symbols. |
| Abandoned / Horror | hospital_bed_damaged_01 only. | Reusable damage/stain overlays, distinct broken equipment and environmental storytelling; develop last. |

## Priority and production gates

P0 remains foreground-wall visibility, final connected solid-wall review, authorized wall/junction and sliding-door repair promotion, then known bench/rack/plant cleanup. Reuse current scripts/contracts and Godot. Glass stays parked; no new windows. D5/new generation stays blocked until cleanup is resolved.

Next five new-content families after P0: **(1) architecture access/circulation (8); (2) ward + ICU completion (4); (3) surgery support (5); (4) emergency completion (3); (5) exterior ambulance arrival (12)**. The three small clinical completion groups intentionally fill real gaps rather than padding to a pilot quota; execute as a coherent 12-asset clinical batch where workflow permits. Exterior remainder follows as a separate 9-asset service-yard group.

Then complete Morgue, Staff/Admin, Cafeteria/Kitchen and Bathrooms/Utility; Signage/Decor follows across the complete layout, then Inventory/UI. Abandoned/Horror is last and derives from finished clean assets. No separate maternity/pediatrics/rehabilitation department is added. Existing pediatric beds/bassinet remain in Patient Rooms.

For each production group: inspect existing reusable alternatives at native scale before locking IDs; define footprint, anchor and independent directional needs; use one family review and early Godot proof; fix failed items only. Technical checks supplement human visual approval. All IDs below are proposed filename stems with `.png` implied. Scope **H = hospital_only**, **C = everyday_world_common**. Shared generic assets still belong to one manifest category.

## Concrete backlog

### Architecture

**P1 — next family 1. 8 proposed; projected category count 40 / target 45.**

Godot/use-case proof: Connected hospital floor with stairs/lift alcove, service hatch and controlled threshold; verify anchors, collision and visibility. Junction repairs precede this batch.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `hospital_stair_flight_01` | H | Connect hospital floors; landings/directions are implementation views. |
| `hospital_elevator_portal_01` | H | Lift entrance with its required door states bundled. |
| `hospital_elevator_cabin_01` | H | Playable lift interior distinct from the entrance. |
| `hospital_service_hatch_01` | H | Controlled counter pass-through for supplies; not a window wall. |
| `hospital_fire_door_01` | H | Fire-separated service/corridor boundary with bundled states. |
| `hospital_access_gate_01` | H | Restricted ward threshold distinct from existing clinical doors. |
| `hospital_handrail_01` | H | Accessible circulation support; unlike the existing medical equipment rail. |
| `hospital_protective_wall_bumper_01` | H | Low crash protection for trolley corridors, separate from utility rails. |

### Reception / Waiting

No new IDs proposed. Reuse the current family; complete any noted repairs without increasing inventory.

### Patient Rooms

**P2 — next family 2, combined ward/ICU completion. 3 proposed; projected category count 32 / target 32.**

Godot/use-case proof: Furnished ward room: lift fits beside bed, sleeper serves family and commode has accessible approach.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `patient_transfer_lift_01` | H | Transfer support absent from IV and oxygen stands. |
| `family_sleeper_chair_01` | H | Overnight family seating with bundled fold-out state, not another visitor chair. |
| `bedside_commode_01` | H | Bedside toileting support distinct from permanent bathroom fixtures. |

### Examination

No new IDs proposed. Reuse the current family; complete any noted repairs without increasing inventory.

### ICU

**P2 — next family 2, combined ward/ICU completion. 1 proposed; projected category count 20 / target 20.**

Godot/use-case proof: Use one existing ward bed with ICU monitoring and the new machine; retain usable access.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `icu_renal_support_machine_01` | H | Visually distinct continuous renal-support equipment, not another infusion stack. |

### Surgery

**P3 — next family 3. 5 proposed; projected category count 24 / target 24.**

Godot/use-case proof: One operating room showing each new support function with existing table/anesthesia equipment; avoid clutter.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `heart_lung_machine_01` | H | Perfusion support with reservoir/pump silhouette distinct from anesthesia. |
| `surgical_suction_irrigation_unit_01` | H | Integrated fluid management distinct from existing general suction cart. |
| `surgical_positioning_frame_01` | H | Independent support frame for operating-table positioning. |
| `scrub_gowning_station_01` | H | Gown/glove preparation storage distinct from scrub sink or supply trolley. |
| `surgical_kick_bucket_01` | H | Low mobile basin distinct from tall dual waste cart. |

### Radiology

No new IDs proposed. Reuse the current family; complete any noted repairs without increasing inventory.

### Laboratory

No new IDs proposed. Reuse the current family; complete any noted repairs without increasing inventory.

### Pharmacy

No new IDs proposed. Reuse the current family; complete any noted repairs without increasing inventory.

### Emergency

**P4 — next family 4. 3 proposed; projected category count 22 / target 22.**

Godot/use-case proof: Trauma bay plus decontamination threshold using existing triage/resuscitation furniture.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `emergency_rapid_infuser_01` | H | Rapid fluid-delivery apparatus distinct from IV pole and warming trolley. |
| `emergency_decontamination_shower_01` | H | Fixed emergency wash-down station; complements existing decontamination cart. |
| `emergency_airway_workstation_01` | H | Airway preparation surface with dedicated support, distinct from generic crash cart; merge if silhouette cannot justify it. |

### Exterior / Ambulance

**P5 — next family 5 (first 12 rows); remainder P6. 21 proposed; projected category count 22 / target 24.**

Godot/use-case proof: Ambulance arrival and accessible entrance with the existing vehicle; canopy respects character visibility. First 12 rows form arrival pilot; remaining 9 form service-yard follow-up.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `ambulance_bay_canopy_01` | H | Covered ambulance arrival; structural legs/roof are components. |
| `ambulance_bay_wheel_guide_01` | H | Vehicle docking alignment at unloading position. |
| `ambulance_bay_marking_01` | H | Standalone deterministic no-parking/loading marking set; no text variations counted. |
| `ambulance_shore_power_pedestal_01` | H | Parked emergency-vehicle support distinct from general utility cabinet. |
| `entrance_bollard_01` | C | Protect pedestrian entrance from vehicles. |
| `accessible_curb_ramp_01` | C | Step-free arrival transition; directions bundled. |
| `curb_segment_01` | C | Separate drive and walkway; corners/endings bundled. |
| `exterior_entry_steps_01` | C | Short entrance level change, distinct from interior full stair flight. |
| `entrance_weather_mat_01` | C | Clearly marked indoor/outdoor threshold. |
| `exterior_bench_01` | C | Weatherproof waiting seat distinct from upholstered indoor benches. |
| `exterior_path_light_01` | C | Pedestrian arrival lighting; lit state bundled. |
| `hospital_entrance_sign_monument_01` | H | Freestanding entrance sign support; lettering belongs to signage. |
| `parking_payment_station_01` | C | Visitor parking payment interaction. |
| `parking_barrier_arm_01` | C | Controlled parking access; open/closed views bundled. |
| `parking_space_marking_01` | C | Reusable parking bay layout, not individual stripe assets. |
| `pedestrian_crossing_marking_01` | C | Safe route from parking to entrance. |
| `exterior_waste_container_01` | C | Weatherproof large outdoor waste unit unlike indoor bins. |
| `service_yard_generator_01` | C | Backup utility infrastructure with distinctive generator housing. |
| `exterior_electrical_cabinet_01` | C | Building service access separate from generator. |
| `ambulance_wash_hose_station_01` | H | Vehicle cleaning support in service yard. |
| `exterior_drain_channel_01` | C | Drainage along bay/approach; repeat/end views bundled. |

### Morgue

**P6 — missing support spaces. 11 proposed; projected category count 11 / target 12.**

Godot/use-case proof: Clinical morgue suite: transport route into storage, autopsy work zone and wash/prep access; no graphic remains needed.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `mortuary_body_trolley_01` | H | Covered body transfer; do not duplicate trauma stretcher. |
| `mortuary_refrigeration_bank_01` | H | Body storage chambers with door/tray views bundled. |
| `mortuary_loading_lift_01` | H | Transfer to storage shelves distinct from bedside lift. |
| `autopsy_table_01` | H | Drained clinical work surface distinct from operating table. |
| `autopsy_extraction_unit_01` | H | Dedicated table-side ventilation support. |
| `mortuary_wash_station_01` | H | Large body-preparation washing station, not ordinary hand basin. |
| `mortuary_body_scale_01` | H | Trolley-compatible weighing platform distinct from patient scale. |
| `mortuary_specimen_station_01` | H | Autopsy collection workspace distinct from laboratory analyzer. |
| `mortuary_preparation_cabinet_01` | H | Purpose-built preparation supply storage; reject if generic cabinet suffices. |
| `mortuary_body_bag_01` | H | Standalone closed transport bag distinct from trolley cover component. |
| `mortuary_transfer_board_01` | H | Body transfer surface distinct from existing radiology rack. |

### Staff / Admin

**P6 — missing support spaces. 15 proposed; projected category count 15 / target 18.**

Godot/use-case proof: Nurse/admin office, locker area and small meeting/break room using shared clinical desk where sufficient.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `office_workstation_01` | C | Full office desktop setup distinct from compact physician desk; computer is a component. |
| `office_task_chair_01` | C | Adjustable office seating unlike visitor chair/clinical stool. |
| `filing_cabinet_01` | C | Records drawers, not clinical supply storage. |
| `document_bookcase_01` | C | Open document/binder storage distinct from medication shelving. |
| `staff_locker_bank_01` | C | Personal staff belongings; individual doors are views/components. |
| `locker_room_bench_01` | C | Narrow changing bench distinct from waiting seating. |
| `staff_coat_rack_01` | C | Personal clothing storage distinct from radiation-apron rack. |
| `meeting_table_01` | C | Shared team/admin workspace distinct from bedside surfaces. |
| `meeting_chair_01` | C | Stackable meeting seating; require distinct silhouette from waiting chair. |
| `staff_break_sofa_01` | C | Shared rest seating unlike bedside sleeper. |
| `staff_break_table_01` | C | Small low break-room surface distinct from meeting/dining tables. |
| `office_printer_copier_01` | C | Full document output distinct from pharmacy label printer. |
| `document_shredder_01` | C | Confidential-paper disposal interaction. |
| `staff_time_clock_01` | C | Staff attendance/check-in terminal distinct from patient kiosk. |
| `hospital_records_cart_01` | H | Transport paper case files, not generic medical supply cart. |

### Cafeteria / Kitchen

**P6 — missing support spaces. 13 proposed; projected category count 13 / target 14.**

Godot/use-case proof: Compact serving line, accessible dining aisle and back-of-house prep/wash area; reuse existing meal tray.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `cafeteria_hot_service_counter_01` | C | Hot meal serving line. |
| `cafeteria_cold_display_counter_01` | C | Chilled food display distinct from enclosed refrigerator. |
| `cafeteria_cashier_station_01` | C | Meal payment station distinct from reception desk. |
| `cafeteria_dining_table_01` | C | Dining surface with wheelchair-accessible edge. |
| `cafeteria_dining_chair_01` | C | Washable dining chair; avoid repeating waiting-chair silhouette. |
| `cafeteria_tray_return_01` | C | Separate used-tray return point. |
| `commercial_range_01` | C | Cooking equipment absent from clinical rooms. |
| `kitchen_prep_table_01` | C | Food-safe preparation surface distinct from surgical instrument table. |
| `kitchen_extraction_hood_01` | C | Cooking ventilation; not laboratory fume hood. |
| `commercial_refrigerator_01` | C | Food storage visibly distinct from medication fridge. |
| `kitchen_pantry_rack_01` | C | Bulk food container shelving; use containers to distinguish from clinical racks. |
| `commercial_dishwasher_01` | C | Dishwashing equipment distinct from autoclave. |
| `kitchen_pot_wash_sink_01` | C | Deep multi-basin wash station distinct from clinical hand sink. |

### Bathrooms / Utility

**P6 — missing support spaces. 12 proposed; projected category count 12 / target 14.**

Godot/use-case proof: Accessible restroom/shower and utility/laundry room; reuse reception janitorial cart and ward hamper.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `accessible_toilet_01` | C | Accessible floor-standing WC with usable approach. |
| `wall_hung_toilet_01` | C | Compact restroom fixture, distinct installation from accessible WC. |
| `accessible_washbasin_01` | C | Knee-clearance basin unlike cabinet-mounted examination sink. |
| `restroom_mirror_01` | C | Independent wall fixture above basin. |
| `accessible_shower_seat_01` | C | Fold-down shower seating; states bundled. |
| `shower_fixture_01` | C | Shower head/control set, one logical fixture. |
| `accessibility_grab_bar_01` | C | Sanitary transfer support; unlike corridor handrail, orientations bundled. |
| `janitorial_mop_sink_01` | C | Low utility basin distinct from handwashing sink. |
| `cleaning_tool_rack_01` | C | Wall storage for mops/brushes; no duplicate janitorial cart. |
| `utility_washing_machine_01` | C | Laundry washing function. |
| `utility_tumble_dryer_01` | C | Separate drying appliance, not washing-machine state. |
| `toilet_paper_dispenser_01` | C | Restroom consumable fixture unlike existing exam paper-roll holder. |

### Signage / Decor

**P7 — after support spaces. 19 proposed; projected category count 19 / target 25.**

Godot/use-case proof: Deterministic reusable symbols/sign supports applied across rooms; text/localizations are views, not new IDs. Verify legibility at native scale.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `hospital_department_sign_system_01` | H | Single coordinated department-label system; five texts do not become five logical assets. |
| `direction_arrow_symbol_01` | C | Navigation arrow; all directions bundled. |
| `overhead_wayfinding_board_01` | C | Suspended multi-destination support distinct from freestanding information stand. |
| `wall_wayfinding_board_01` | C | Wall-mounted destination support; count only if distinct placement/use from overhead board. |
| `floor_route_marker_01` | C | Floor navigation indicator with bundled directions/colors. |
| `exit_pictogram_01` | C | Deterministic exit symbol without protected marks. |
| `accessible_facility_pictogram_01` | C | Accessible-facility identification. |
| `restroom_pictogram_01` | C | Restroom identification family, not per-gender inflated counts. |
| `no_entry_pictogram_01` | C | Restricted-access instruction. |
| `hand_hygiene_pictogram_01` | H | Handwashing station instruction, abstract deterministic drawing. |
| `radiation_warning_pictogram_01` | H | Imaging-room hazard identification. |
| `wet_floor_sign_01` | C | Portable warning prop unlike queue barrier. |
| `wall_clock_01` | C | Time reference for wards/offices; do not duplicate under Staff. |
| `staff_noticeboard_01` | C | Pin-board announcements, one asset shared with Admin. |
| `patient_information_whiteboard_01` | H | Bedside care-information surface; text content is separate. |
| `framed_wall_art_01` | C | One restrained decorative composition, no recolor count. |
| `wall_planter_01` | C | Wall-mounted greenery distinct from existing floor lobby plant. |
| `visitor_directory_board_01` | H | Building-level map/directory distinct from directional list; map layout is a component. |
| `room_occupancy_indicator_01` | H | Door-side available/occupied indicator; states bundled. |

### Inventory / UI

**P8 — after signage. 17 proposed; projected category count 20 / target 20.**

Godot/use-case proof: Small Godot pickup/inventory overlay exercise showing selection and readable native icons; world props do not imply extra icon counts.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `inventory_bandage_roll_01` | H | Bandage pickup, distinct from complete first-aid kit. |
| `inventory_gauze_pack_01` | H | Flat dressing packet distinct from bandage roll. |
| `inventory_syringe_01` | H | Single-use supply icon with distinct silhouette. |
| `inventory_exam_gloves_01` | H | Glove supply pickup, not wall-dispenser duplicate. |
| `inventory_surgical_mask_01` | H | Wearable supply pickup. |
| `inventory_medicine_vial_01` | H | Injectable container icon. |
| `inventory_tablet_blister_01` | H | Tablet strip icon distinct from vial. |
| `inventory_iv_fluid_bag_01` | H | Consumable fluid bag distinct from world IV stand. |
| `inventory_ointment_tube_01` | H | Topical medicine container. |
| `inventory_patient_chart_01` | H | Patient document item with abstract content. |
| `inventory_access_card_01` | C | Restricted-door access item. |
| `inventory_prescription_01` | H | Medication document distinct from chart; no generated readable text. |
| `inventory_stethoscope_01` | H | Portable diagnostic equipment icon. |
| `inventory_penlight_01` | H | Small inspection tool distinct from room examination lamp. |
| `ui_interaction_prompt_01` | C | Reusable interact indicator with key glyph variants bundled. |
| `ui_inventory_slot_01` | C | Inventory selection frame with normal/selected states bundled. |
| `ui_objective_marker_01` | C | Navigation/objective marker distinct from patient-status panel. |

### Abandoned / Horror

**P9 — last, built against finished clean pack. 30 proposed; projected category count 31 / target 38.**

Godot/use-case proof: Reuse clean hospital layout to demonstrate overlay compatibility, distinct broken silhouettes and readable hazards. No gore required; states must add function or clear geometry.

| Proposed ID | Scope | Practical use / distinction |
|---|---|---|
| `wall_crack_overlay_01` | C | Reusable structural crack pattern; directions/size exports bundled. |
| `plaster_loss_overlay_01` | C | Exposed underlying wall material distinct from crack line. |
| `peeling_paint_overlay_01` | C | Curling surface finish damage distinct from missing plaster. |
| `floor_tile_break_overlay_01` | C | Localized missing/broken flooring. |
| `ceiling_water_damage_overlay_01` | C | Overhead water-damage marks compatible with wall tops. |
| `rust_runoff_overlay_01` | C | Metal corrosion streaks distinct from dirt. |
| `soot_overlay_01` | C | Localized fire residue distinct from general grime. |
| `impact_damage_overlay_01` | C | Concentrated impact crater distinct from long cracks. |
| `floor_grime_overlay_01` | C | Reusable traffic dirt, no recolor variants counted. |
| `wall_damp_overlay_01` | C | Vertical moisture ingress. |
| `water_puddle_overlay_01` | C | Standing water with small contact treatment. |
| `dried_blood_stain_overlay_01` | H | Restrained non-graphic environmental stain, one pattern family. |
| `chemical_spill_overlay_01` | H | Distinct contained laboratory spill cue, not a puddle recolor. |
| `mold_patch_overlay_01` | C | Clustered growth distinct from damp stain. |
| `leaking_pipe_01` | C | Damaged utility with leak origin; liquid frames are components. |
| `wheelchair_broken_01` | H | Deformed/missing-wheel silhouette; no grime-only duplicate. |
| `patient_monitor_broken_01` | H | Broken housing/screen geometry, not merely powered-off monitor. |
| `medicine_cabinet_broken_01` | H | Damaged opened storage with displaced contents. |
| `ceiling_light_fallen_01` | C | Detached hanging fixture with visibly altered geometry. |
| `sink_broken_01` | C | Broken basin/plumbing exposing a distinct obstacle. |
| `abandoned_supply_crate_01` | H | Sealed forgotten clinical supplies, not generic supply cart. |
| `discarded_medical_records_01` | H | Loose floor paperwork cluster distinct from inventory chart. |
| `covered_equipment_01` | H | Dust-sheet storage silhouette distinct from working machine. |
| `discarded_linen_pile_01` | H | Floor pile distinct from ward hamper or bed-state view. |
| `overturned_locker_01` | C | Toppled obstruction; new geometry, not a rotated rendered sprite. |
| `door_barricade_01` | C | Reusable physical blocked-door obstacle. |
| `broken_glass_debris_01` | C | Standalone floor debris unrelated to resuming glass partitions. |
| `hazard_tape_barrier_01` | C | Cordons an unsafe area; one logical barrier set. |
| `exposed_cable_bundle_01` | C | Electrical hazard/obstruction distinct from stain overlay. |
| `abandoned_warning_beacon_01` | C | Portable emergency warning light; frames/states bundled. |

## Budget reconciliation and decisions

- **Architecture (45):** eight proposed additions put it at 40. Its original sub-budgets sum to 45 but the current mix already has 8 floors/12 wall records versus the approximate 5/8 allocation. Do not fill the balance with more finishes, connectors or glass views. Junctions and visibility are required capabilities even when they add no IDs. Forty-five is useful headroom; it is not yet evidence that five more logical products are needed.

- **Examination (20), Radiology (16), Pharmacy (14):** actual 22/19/18 make these budgets low relative to the existing approved breadth. Radiology includes distinct PET/CT, gamma camera and DEXA modalities; pharmacy includes distinct automation/packaging/returns operations. Retain useful coverage and stop expansion. Examination has some overlapping stool/diagnostic coverage worth checking during final curation; do not infer that every overrun is equally valuable. Targets remain unchanged unless the user revises them.

- **Signage/Decor (25):** proposed 19 reflects reusable department text/direction sets counted once and reuse of the existing lobby plant/sign stands. Twenty-five now looks high if met through per-label or recolor counting. Keep six slots uncommitted.

- **Abandoned/Horror (38):** one existing plus 30 proposed gives 31. Reusable overlays provide more scene variety than one damaged copy of every clean prop. Thirty-eight looks high as a minimum quota; keep seven slots open until scene tests expose worthwhile gaps.

- **Exterior (24):** one existing plus 21 proposed gives 22. Only one ambulance is presently justified; new technical directions/states are not extra vehicles. Keep two slots open instead of filling the approximate four-vehicle sub-budget.

- **Staff/Admin, Cafeteria/Kitchen, Bathrooms/Utility and Morgue:** proposed totals 15/13/12/11 intentionally reuse the physician desk, meal tray, janitorial cart, linen hamper and instrument trolley already owned elsewhere. Zero assigned assets does not mean zero reusable capability. The targets remain reasonable budgets, with shared coverage reducing new work.

The proposal leaves 27 slots unfilled in below-target categories and retains the 9 existing excess assets: 400 - 27 + 9 = 382. Do not silently rewrite roadmap targets to these projections. No category is conclusively too small in functional scope solely because its count is exceeded; final room tests decide usefulness.

## Release work outside logical asset counts

After content/repair approval, ship production PNGs and required implementation views, stable placement/anchor metadata, architecture assembly examples, representative furnished Godot rooms, catalog/contact sheets, import/use instructions, license/credits and a complete release archive. Exclude local third-party reference packs, rejected candidates and internal review clutter. Validate the actual release contents. These deliverables and repairs do not inflate asset counts.

## Maintenance and checks

At each completed batch, recompute the table from manifest primary categories, cross-check catalog IDs/statuses, remove fulfilled proposals, and re-evaluate shared capability before naming more IDs. Update this file and CODEX_PROJECT_STATE.md; edit category targets in ASSET_ROADMAP.md only on explicit user instruction.

Documentation checks: target sum, manifest/catalog reconciliation, all approved final paths, unique non-colliding proposed IDs, category/projection arithmetic, local links, and preservation of all pre-existing non-task files. No art-generation, ingest or approval command is part of this task.

Completed checks: **379 tests passed in 108.37s**; focused historical-audit allowance test passed. The only non-document edits register the two explicitly requested planning-document paths in the historical addition allowlist and test that exact allowance; no asset processing or approval behavior changed. Source category targets match exactly; 158 proposed IDs are unique and absent from the manifest; all non-task baseline files remain unchanged. No Godot rerun was needed for this documentation-only product change.
