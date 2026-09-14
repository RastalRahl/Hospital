# Perspective unification and repair plan

Established 2026-09-14 from the current 224-record manifest, native PNG inspection, category contact sheets, the 26 x 46 px adult scale reference, the canonical RastalR camera reference and the user-supplied itch.io architecture references. This plan changes no artwork, metadata or approval state.

## Decision and scope

The pack uses a **rectangular-grid RPG oblique camera**. Ground and construction edges remain horizontal and vertical, depth recedes straight upward, and objects do not use diamond-isometric diagonals or perspective convergence. A front-facing box normally shows its top and front face; a large default right face makes the object read as turned away from the room grid. Directional views must be authored separately when gameplay needs them.

The audit assigns every existing logical asset exactly once:

- **144 assets require perspective redraw or substantial camera correction**, organized into nine repair batches below.
- **80 assets retain their present perspective language**. Retention is a perspective judgment only; it does not approve scale, clipping, wall art, glass or other release concerns.
- The repair program adds **zero** logical assets. Existing IDs, provenance and approval history stay intact.

The main recurring defect is a lower three-quarter presentation with broad right faces and skewed top planes. It is strongest in counters, cabinets, carts, workstations and large clinical machines. The correction should preserve each asset's function and recognizable details while rebuilding its mass on the canonical room grid.

## Calibration gate

Before batch R1, make one small Godot calibration scene using the existing integration demo and debug adult. Use `hospital_bed_standard_01`, `waiting_chair_01`, `nurse_call_panel_01` and `mri_scanner_01` as perspective anchors. Redraw only these three representative repair prototypes first:

1. `reception_counter_straight_01` — modular room-grid furniture;
2. `bedside_cabinet_01` — small freestanding cabinet and adult-relative scale;
3. `medical_cart_base_01` — mobile clinical equipment.

Human acceptance of those three fixes the camera/face proportions for the remaining batches. Do not reinterpret the entire pack from each individual source sprite. Use the downloaded packs only for room-construction logic; author original RastalR pixels.

Calibration V1 is preserved as a reference-only geometry study in [`perspective_calibration_v1`](../demo/hospital_integration/repair_candidates/perspective_calibration_v1/findings.md). The user rejected its art treatment as too crude. A richer, scale-corrected bedside-cabinet V2 is now ready for human review in [`perspective_cabinet_v2`](../demo/hospital_integration/repair_candidates/perspective_cabinet_v2/findings.md). If accepted, apply V2's detail density, materials and cluster language to new counter/cart art while retaining V1's camera constraints. Production art and approvals remain unchanged.

## Repair batches

Each batch is a coherent revision family. During iteration, use native-scale contact sheets and a furnished Godot room; run targeted manifest/alpha/integration checks. Run the full suite once when the batch is complete. Recheck logical footprint, anchor and adult-relative scale while the sprite is open, but do not change metadata merely to excuse an oversized drawing.

### R1 — Public arrival and reception (17)

Highest player exposure and the clearest modular-furniture calibration family.

- `ambulance_01`
- `brochure_rack_01`
- `hand_sanitizer_stand_01`
- `janitorial_cart_01`
- `lobby_plant_01`
- `queue_barrier_corner_01`
- `queue_ticket_dispenser_01`
- `reception_counter_accessible_01`
- `reception_counter_corner_01`
- `reception_counter_small_01`
- `reception_counter_straight_01`
- `reception_information_stand_01`
- `recycling_bin_01`
- `self_checkin_kiosk_01`
- `waiting_chair_contrast_01`
- `water_cooler_01`
- `wheelchair_standard_01`

Acceptance focus: counters join cleanly on the 32 px grid; kiosks/racks remain human-scaled; mobile items face the room grid; the ambulance reads in the same oblique world without fake convergence.

### R2 — Patient-room support (13)

- `bedside_cabinet_01`
- `bedside_cabinet_drawers_01`
- `bedside_reading_light_01`
- `bedside_step_01`
- `linen_hamper_01`
- `overbed_table_01`
- `oxygen_concentrator_01`
- `patient_monitor_bedside_compact_01`
- `patient_room_wardrobe_01`
- `patient_room_waste_bin_01`
- `patient_storage_cabinet_01`
- `privacy_curtain_corner_01`
- `privacy_screen_mobile_01`

Acceptance focus: match the retained bed family, keep bedside clearances useful, and declare or redraw the reading-light direction instead of leaving an ambiguous side view.

### R3 — Examination rooms (14)

- `blood_pressure_monitor_01`
- `exam_room_sink_unit_01`
- `exam_room_supply_cabinet_01`
- `exam_room_wall_cabinet_01`
- `examination_chair_adjustable_01`
- `examination_table_01`
- `glove_dispenser_01`
- `instrument_trolley_01`
- `medical_cart_base_01`
- `physician_desk_small_01`
- `portable_ultrasound_01`
- `sharps_bin_01`
- `small_medical_tray_01`
- `thermometer_dock_01`

Acceptance focus: cabinets and sink align with room walls; tables/chairs share the bed camera; wall-mounted assets use a clear authored wall orientation.

### R4 — ICU and respiratory equipment (16)

- `emergency_respiratory_cart_01`
- `high_flow_oxygen_unit_01`
- `humidifier_respiratory_unit_01`
- `icu_bedside_supply_unit_01`
- `icu_bedside_terminal_01`
- `icu_ceiling_equipment_boom_01`
- `icu_equipment_tower_01`
- `icu_isolation_supply_cart_01`
- `icu_monitor_advanced_01`
- `icu_overbed_medical_rail_01`
- `icu_storage_cabinet_01`
- `icu_ventilator_advanced_01`
- `infusion_pump_stack_01`
- `suction_unit_mobile_01`
- `syringe_pump_single_01`
- `ventilator_standard_01`

Acceptance focus: preserve distinct silhouettes without turning every unit to the same diagonal; screen faces and carts should be readable in a grid-aligned bay.

### R5 — Emergency and trauma (16)

- `crash_cart_equipped_01`
- `emergency_blanket_warmer_01`
- `emergency_decontamination_cart_01`
- `emergency_defibrillator_01`
- `emergency_isolation_transport_stretcher_01`
- `emergency_supply_cart_01`
- `emergency_treatment_chair_01`
- `folding_stretcher_storage_rack_01`
- `portable_xray_unit_01`
- `trauma_equipment_cart_01`
- `trauma_immobilization_rack_01`
- `trauma_overbed_table_01`
- `trauma_stretcher_01`
- `trauma_stretcher_raised_01`
- `triage_vital_signs_station_01`
- `triage_workstation_01`

Acceptance focus: stretchers share the retained hospital-bed projection; treatment stations remain navigable; equipment state variants keep identical camera and footprint logic.

### R6 — Surgery (17)

- `anesthesia_machine_01`
- `electrosurgical_smoke_evacuator_01`
- `electrosurgical_unit_01`
- `endoscopy_imaging_tower_01`
- `mayo_stand_01`
- `operating_table_01`
- `operating_table_raised_01`
- `patient_warming_unit_01`
- `sterile_equipment_stand_01`
- `sterile_supply_cart_01`
- `surgical_instrument_table_01`
- `surgical_instrument_trolley_01`
- `surgical_linen_hamper_01`
- `surgical_scrub_sink_01`
- `surgical_video_recording_unit_01`
- `surgical_waste_cart_dual_01`
- `warming_infusion_trolley_01`

Acceptance focus: operating-table states remain registered; carts/tables align with the operating room; tall equipment does not gain an exaggerated side face.

### R7 — Radiology (15)

- `contrast_media_warmer_01`
- `ct_mri_coil_storage_rack_01`
- `ct_scanner_01`
- `dexa_bone_density_scanner_01`
- `fluoroscopy_c_arm_01`
- `mri_ferromagnetic_screening_station_01`
- `mri_safe_equipment_cart_01`
- `nuclear_medicine_gamma_camera_01`
- `pet_ct_scanner_01`
- `radiography_table_system_01`
- `radiology_lead_apron_rack_01`
- `radiology_patient_step_platform_01`
- `radiology_patient_transfer_board_rack_01`
- `radiology_positioning_aids_cart_01`
- `radiology_workstation_01`

Acceptance focus: scanners retain modality-specific silhouettes while their beds, bores, racks and consoles occupy the same projection. Large scanners must be judged in rooms, not compressed to fit a contact-sheet cell.

### R8 — Laboratory (18)

- `automated_chemistry_analyzer_01`
- `hematology_analyzer_01`
- `laboratory_analyzer_01`
- `laboratory_autoclave_01`
- `laboratory_biosafety_cabinet_01`
- `laboratory_biosample_cart_01`
- `laboratory_centrifuge_01`
- `laboratory_fume_hood_01`
- `laboratory_handwash_sink_01`
- `laboratory_incubator_01`
- `laboratory_micropipette_station_01`
- `laboratory_refrigerator_01`
- `laboratory_vortex_mixer_01`
- `laboratory_workbench_01`
- `pcr_thermal_cycler_01`
- `refrigerated_centrifuge_01`
- `specimen_storage_cabinet_01`
- `ultra_low_freezer_01`

Acceptance focus: make benches, cabinets and equipment read as one laboratory system; keep front controls legible without using a low product-render angle.

### R9 — Pharmacy (18)

- `automated_medication_dispensing_cabinet_01`
- `controlled_substance_safe_01`
- `iv_medication_storage_rack_01`
- `locked_medication_cart_01`
- `medication_delivery_cart_01`
- `medication_pickup_counter_01`
- `medication_sorting_tray_station_01`
- `pharmacy_clean_bench_01`
- `pharmacy_compounding_workstation_01`
- `pharmacy_dispensing_counter_01`
- `pharmacy_label_printer_station_01`
- `pharmacy_medication_shelving_01`
- `pharmacy_refrigerator_01`
- `pharmacy_returns_bin_station_01`
- `prescription_will_call_rack_01`
- `tablet_counting_station_01`
- `unit_dose_packaging_machine_01`
- `unit_dose_storage_cabinet_01`

Acceptance focus: all counters, benches, cabinets and shelving form usable straight room runs; machines sit on those surfaces without a conflicting camera.

## Perspective-retain register (80)

These assets already use an acceptable camera construction or are effectively flat/front-facing. They remain subject to ordinary visual and scale review.

### Architecture (32)

- Floors: `hospital_floor_alt_01`, `hospital_floor_alt_02`, `hospital_floor_alt_03`, `hospital_floor_alt_04`, `hospital_floor_plain_01`, `hospital_floor_plain_02`, `hospital_floor_plain_03`, `hospital_floor_plain_04`.
- Solid walls: `hospital_wall_back_straight_01`, `hospital_wall_back_straight_02`, `hospital_wall_back_straight_03`, `hospital_wall_back_straight_04`, `hospital_wall_side_left_01`, `hospital_wall_side_left_02`, `hospital_wall_side_right_01`, `hospital_wall_side_right_02`, `hospital_front_wall_cutaway_01`, `hospital_front_wall_cutaway_02`, `hospital_front_wall_cutaway_03`, `hospital_front_wall_cutaway_04`.
- Doors/openings: `hospital_door_glazed_closed_01`, `hospital_door_single_closed_01`, `hospital_door_single_half_open_01`, `hospital_double_doors_closed_01`, `hospital_double_doors_half_open_01`, `hospital_equipment_opening_wide_01`, `hospital_sliding_clinical_doors_closed_01`, `hospital_sliding_clinical_doors_open_01`.
- Pending glass: `hospital_glass_partition_back_01`, `hospital_glass_partition_side_left_01`, `hospital_glass_partition_side_right_01`, `hospital_glass_partition_front_cutaway_01`.

Architecture retains its perspective contract, but the 12 solid walls still require the already planned junction/visibility/art repair and formal promotion. The four glass parents remain pending and parked. The open sliding door keeps its separate alpha-repair candidate. None of those are perspective redraws.

### Reception / waiting (6)

- `queue_barrier_straight_01`
- `reception_medical_sign_stand_01`
- `waiting_bench_2seat_01`
- `waiting_bench_3seat_01`
- `waiting_chair_01`
- `waiting_chair_single_01`

The two benches retain their perspective but still need the known proportion/scale correction.

### Patient rooms (16)

- `hospital_bassinet_01`
- `hospital_bed_bariatric_01`
- `hospital_bed_head_raised_01`
- `hospital_bed_pediatric_01`
- `hospital_bed_rails_lowered_01`
- `hospital_bed_standard_01`
- `hospital_bed_unmade_01`
- `iv_stand_dual_01`
- `nurse_call_panel_01`
- `oxygen_cylinder_mobile_01`
- `patient_monitor_wall_01`
- `privacy_curtain_folded_01`
- `privacy_curtain_straight_01`
- `visitor_chair_patient_room_01`
- `wall_medical_rail_01`
- `wall_oxygen_panel_01`

### Examination (8)

- `doctor_stool_01`
- `examination_lamp_01`
- `medical_stool_01`
- `otoscope_ophthalmoscope_unit_01`
- `paper_roll_holder_01`
- `patient_chair_exam_room_01`
- `patient_scale_01`
- `wall_diagnostic_set_01`

### ICU (3)

- `iv_stand_single_01`
- `mobile_oxygen_air_manifold_01`
- `patient_monitor_floor_01`

### Emergency (3)

- `emergency_iv_pole_loaded_01`
- `emergency_wall_resuscitation_panel_01`
- `stretcher_wall_dock_01`

### Surgery (2)

- `surgical_light_ceiling_01`
- `surgical_stool_01`

### Radiology (4)

- `mammography_unit_01`
- `mobile_radiation_shield_01`
- `mri_scanner_01`
- `radiology_contrast_injector_01`

### Laboratory (2)

- `cryogenic_storage_dewar_01`
- `laboratory_microscope_01`

### Inventory/UI and abandoned (4)

- `hospital_bed_damaged_01`
- `meal_tray_01`
- `medical_inventory_first_aid_kit_01`
- `ui_patient_status_01`

## Cross-batch release checks

The current technical QA reports 46 `touching_canvas_edge` warnings. That signal is not a perspective verdict, but every affected file must be rechecked when its family is handled. The following 17 assets also draw substantially beyond their declared logical-footprint width and need an explicit scale/overhang judgment in Godot; overhang alone is not failure because metadata footprints describe placement rather than canvas bounds:

`bedside_reading_light_01`, `examination_lamp_01`, `examination_table_01`, `fluoroscopy_c_arm_01`, `hematology_analyzer_01`, `icu_bedside_supply_unit_01`, `laboratory_autoclave_01`, `laboratory_biosample_cart_01`, `laboratory_micropipette_station_01`, `meal_tray_01`, `medical_inventory_first_aid_kit_01`, `mri_ferromagnetic_screening_station_01`, `paper_roll_holder_01`, `pharmacy_returns_bin_station_01`, `radiology_patient_step_platform_01`, `radiology_workstation_01`, `wheelchair_standard_01`.

An asset leaves its repair batch only when it passes native-scale visual review, the adult/room test, palette and alpha checks, footprint/anchor verification, and the existing manifest/catalog contracts. Preserve old approved artwork and provenance through the normal revision path. Human visual acceptance remains required before approval metadata changes.

## Production order

Finish the current architecture cleanup first. Then complete the calibration gate and R1–R9 in order. Do not begin the roadmap's 149 new assets until this perspective program and the retained-asset scale exceptions are resolved. The canonical target remains 373 because revisions do not add logical assets.
