# Architecture Doors & Openings — Production Batch 12 QA

Status: **PASS — technical QA complete; all eight logical assets await human visual review.**

## Logical inventory

- Logical assets: 8
- Technical implementation components: 5
- Components counted as logical assets: no
- Normalization: `architecture_grid_preserving` for every main module and component

| Logical asset | Main native size | Components | QA |
| --- | --- | --- | --- |
| `hospital_door_single_closed_01` | `[32, 52]` | none | pass |
| `hospital_door_single_half_open_01` | `[32, 52]` | leaf_projection [32, 11] @ [0, 51] | pass |
| `hospital_door_glazed_closed_01` | `[32, 52]` | none | pass |
| `hospital_double_doors_closed_01` | `[64, 52]` | none | pass |
| `hospital_double_doors_half_open_01` | `[64, 52]` | left_leaf_projection [32, 11] @ [0, 51], right_leaf_projection [32, 11] @ [32, 51] | pass |
| `hospital_sliding_clinical_doors_closed_01` | `[64, 52]` | none | pass |
| `hospital_sliding_clinical_doors_open_01` | `[64, 52]` | left_parked_leaf [28, 38] @ [-24, 14], right_parked_leaf [28, 38] @ [60, 14] | pass |
| `hospital_equipment_opening_wide_01` | `[96, 52]` | none | pass |

## Reconstruction

All eight actual normalized candidates reconstructed cleanly in both five-cell original-layout and eight-cell relocated-layout tests, using only approved Batch 11 back walls, floors, and front cutaways. The mixed corridor also passed grid, cap/base/teal, floor, threshold, overlay-order, alpha-gap, overlap, and cumulative-drift checks.

## Review artifacts

- `review_contact_sheet`: `previews/contact_sheets/production_batch_12_architecture_doors_openings_review.png`
- `chatgpt_qa_montage`: `previews/architecture/production_batch_12_architecture_doors_openings_qa_montage.png`
- `original_reconstructions`: `previews/architecture/production_batch_12_architecture_doors_openings_reconstructed_original.png`
- `extended_reconstructions`: `previews/architecture/production_batch_12_architecture_doors_openings_reconstructed_extended.png`
- `mixed_corridor`: `previews/architecture/production_batch_12_architecture_doors_openings_mixed_corridor.png`
- `review_bundle`: `release/production_batch_12_architecture_doors_openings_review_bundle.zip`
