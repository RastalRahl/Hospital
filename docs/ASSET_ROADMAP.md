# RastalR Hospital asset roadmap — revision 2

Revised 2026-09-11 at the user’s explicit request to change targets and reassess the whole pack while including every existing asset. This is the current product roadmap and supersedes the original 400-asset category budget imported at commit `2ae8aa1`. That original remains available in Git history. This revision authorizes planning changes, not asset generation or approval.

## Product definition

A coherent 32 px RPG-oblique hospital environment pack: developers can build a public arrival area, clinical departments, circulation, staff and service rooms, and a restrained abandoned version of the same hospital. Existing clinical breadth is retained; new work prioritizes the ordinary spaces and fixtures that connect it into a usable building.

**Working target: 373 logical assets — all 224 existing assets plus 149 named additions.** This is a scope-derived estimate, not a quota or a claim that 224 assets are already release-ready. There is no replacement round-number minimum or speculative stretch budget. If a proposed item fails the usefulness/distinction test, revise the backlog and target explicitly rather than manufacture a substitute.

The planned clean environment/interaction content totals **352**, and the bundled abandoned-condition set totals **21**. Both are part of this roadmap; abandoned content is produced last. All four existing glass parents stay in the 373 target and must eventually receive a separate disposition/review before release; they remain pending and parked now. Removing glass from the review layout did not delete it from product scope.

## Revised category targets

Targets below include every existing manifest record in its current category. No approved asset is deleted, merged, renumbered or reassigned by this plan.

| Category | Previous target | Current | New target | New assets | Reason |
|---|---:|---:|---:|---:|---|
| Architecture | 45 | 32 | 44 | 12 | Retain all 32 records; add 12 access, circulation, lighting and service fixtures. Fix junctions/visibility without counting technical views. |
| Reception / Waiting | 22 | 22 | 22 | 0 | Existing counters, queues, seating and lobby utilities are sufficient; finish visual repairs. |
| Patient Rooms | 32 | 29 | 32 | 3 | Add lift, bedside commode and family sleeper to complete patient support; retain every bed/state already present. |
| Examination | 20 | 22 | 22 | 0 | Retain all 22; another stool/table variant adds less value than missing support rooms. |
| ICU | 20 | 19 | 20 | 1 | Add one distinct renal-support machine; reuse ward beds and existing monitors/pumps. |
| Surgery | 24 | 19 | 22 | 3 | Add practical suction/irrigation, gowning and basin support; defer specialist perfusion and positioning apparatus. |
| Radiology | 16 | 19 | 19 | 0 | Retain all 19 imaging assets, including the specialized modalities already approved; no new scanners planned. |
| Laboratory | 20 | 20 | 22 | 2 | Add eyewash and spill kit to the existing broad instrument set. |
| Pharmacy | 14 | 18 | 18 | 0 | Retain all 18 dispensing/compounding/automation assets; no extra cabinets. |
| Emergency | 22 | 19 | 21 | 2 | Add rapid infuser and fixed decontamination shower; reuse respiratory and crash carts for airway support. |
| Exterior / Ambulance | 24 | 1 | 18 | 17 | One ambulance plus 17 arrival/approach/service fixtures; omit paid-parking machinery and duplicate vehicles. |
| Morgue | 12 | 0 | 8 | 8 | Eight purpose-built clinical morgue assets; reuse desk, sink support, instruments and storage from other categories. |
| Staff / Admin | 18 | 0 | 14 | 14 | Fourteen office/locker/break-room assets; reuse waiting chairs for meetings and shared signage boards. |
| Cafeteria / Kitchen | 14 | 0 | 14 | 14 | Fourteen service/dining/kitchen assets including meal delivery to wards; existing tray is retained in Inventory/UI. |
| Bathrooms / Utility | 14 | 0 | 18 | 18 | Increase to 18 to cover sanitation, accessibility, laundry, clean/dirty utility and compact sterile processing. |
| Signage / Decor / Safety | 25 | 0 | 22 | 22 | Twenty-two reusable sign/decor/safety deliverables; text/direction variants bundled, lobby plant reused. |
| Inventory / UI | 20 | 3 | 16 | 13 | Retain all three existing assets and add 13 distinctive pickups/UI elements; omit overlapping tiny icons. |
| Abandoned / Horror | 38 | 1 | 21 | 20 | Retain damaged bed plus 20 reusable damage/storytelling deliverables; reduce one-off damaged furniture and similar stains. |
| **Total** | **400** | **224** | **373** | **149** | Counts follow useful coverage. |

## What makes the pack complete

| Scene/use case | Required coverage and reuse | Release proof |
|---|---|---|
| Public arrival and waiting | Existing ambulance, reception/queue/check-in/seating plus canopy, accessible approach and directory. | Walkable arrival-to-reception route; vehicle unloading and canopy do not hide the player. |
| Connected inpatient floor | Existing walls/floors/doors/bedrooms and curtains; new lights, stairs/lift, handrails and access controls. | L/T/cross connections, returns, endpoints, door passage and foreground visibility work in furnished rooms. Connector views do not inflate counts. |
| Ward and ICU | Reuse current beds and monitoring; add transfer/overnight/toileting support and renal-support machine. | Furnished ward and distinct ICU bay with readable equipment and movement space. |
| Examination and emergency | Retain current examination/triage/trauma coverage; add two emergency functions. | Complete general exam and trauma scenes without unexplained missing core fixtures. |
| Surgery and instrument processing | Existing OR equipment and laboratory autoclave; new fluid/gowning support, washer and clean packing station. | OR plus separate compact instrument-processing vignette; reused assets documented once. |
| Imaging, laboratory and pharmacy | Retain every specialized modality/analyzer/dispensing asset; add two lab safety items. | Representative rooms verify camera, scale, sorting and native readability; no exhaustive new equipment catalog. |
| Staff/admin and nurse station | Existing reception counters/physician desk/chairs plus office, records, lockers and break furnishings. | Nurse/admin office, changing area and small break/meeting space can be assembled from shared assets. |
| Sanitary and building support | New accessible WC/shower, laundry and clean/dirty utility fixtures; reuse janitorial cart, bins, hampers and cabinets. | Distinct restroom, clean supply, soiled utility and laundry layouts; no generic cart duplication. |
| Food and mortuary services | Compact cafeteria/kitchen, meal delivery and clinical morgue set with shared support furnishings. | Serving/prep/delivery vignette and trolley/storage/preparation route. |
| Wayfinding and interaction | Shared deterministic sign systems, boards/safety fixtures and limited pickup/UI set. | Native-scale readable navigation and a small interaction example; translations/states are bundled. |
| Abandoned hospital | Existing damaged bed plus reusable overlays and a limited set of broken obstacles. | A clean room can become recognizably abandoned while retaining the same visual language. |

These are visual/game-asset use cases, not architectural or clinical compliance claims. Keep the Godot integration demo as the primary practical test; add small reusable review layouts when a missing room needs one, not a separate bespoke validator per prop.

## Production sequence

0. **Close cleanup:** foreground-wall visibility, final connected-wall review and authorized wall/door repair promotion; fix the known bench/rack/plant issues. No D5 or new generation before this is resolved. Glass remains parked until its separate review is scheduled.
1. **Building essentials:** architecture (12), bathrooms/utility (18), signage/decor/safety (22), staff/admin (14). These are the first four content families; split larger families into coherent 12–20-asset pilots where useful.
2. **Clinical completion:** one 11-asset family across Patient Rooms (3), ICU (1), Surgery (3), Laboratory (2), Emergency (2). This is the fifth family, not five padded batches.
3. **Support services:** exterior/arrival (17), cafeteria/kitchen (14), morgue (8).
4. **Interaction and complete clean-pack review:** Inventory/UI (13), all clean room examples, and resolution of the four existing glass approvals without adding glass/windows.
5. **Alternate condition:** 20 new abandoned assets plus the existing damaged bed.
6. **Release assembly:** package and verify every retained/approved logical parent and its required views, with examples and documentation.

## Scope choices and boundaries

- Shift effort from the previous backlog’s optional specialist machines, paid parking, extra meeting chair, similar tiny pickups and numerous damage variations toward general lights, sanitary fixtures, clean linen, sterile processing, safety fixtures and meal delivery. See the explicit proposal changes in [ASSET_COVERAGE_STATUS.md](ASSET_COVERAGE_STATUS.md). Only unproduced proposals are removed.
- No new general hospital departments are required for this release. Existing pediatric beds and bassinet remain useful within Patient Rooms; full maternity, pediatric, rehabilitation, dentistry or psychiatric departments are future scope decisions.
- No characters/animations, surgical simulation, full city/road network, full restaurant pack or comprehensive hospital engineering simulation is included. The debug figure is a scale/testing aid.
- No new windows or glass family expansion. Retain and later review the four existing pending glass assets; do not promote them because they appear in this roadmap.
- Stair/lift pieces provide environment art, anchors, states and an example assembly; this does not promise a complete elevator controller or multistory game framework.

## Counting, ownership and delivery

Use [the manifest](../metadata/manifest.json) as the inventory authority and [ASSET_COVERAGE_STATUS.md](ASSET_COVERAGE_STATUS.md) for live counts, every retained ID, new IDs, scopes and room proofs. Count each logical parent once in its existing primary category. Reuse shared props freely across rooms without creating a second asset. Existing approved state records are retained as-is; new animation frames, directions, components, masks, export scales, text localizations and trivial recolors add no count.

Every new proposal must justify a distinct silhouette or interaction/use at native scale. Prefer revision/reuse when an existing sprite does the job. Generic fixtures use `everyday_world_common`; clinical equipment uses `hospital_only`. Sign text/pictograms are deterministic and separately authored where needed. All production continues to follow AGENTS.md, transparent pixel-art rules and the explicit approval path.

Release requires approved production files, declared footprints/anchors and view selection, usable architecture examples, representative furnished room scenes, catalog/contact sheets, import instructions, license/credits and a complete versioned release archive. Test the packaged files, exclude downloaded references and internal experiments, and resolve all pending intended inclusions. Counts alone never constitute release approval.

## Basis for reassessment

The existing manifest is the primary evidence for what is already covered. Hospital support-space references reinforce the need to cover more than clinical equipment: [NHS HBN 00-03](https://www.england.nhs.uk/publication/designing-generic-clinical-and-clinical-support-spaces-hbn-00-03/) describes clinical and support spaces, and [HBN 00-04](https://www.england.nhs.uk/publication/designing-stairways-lifts-and-corridors-in-healthcare-buildings-hbn-00-04/) covers circulation, stairs and lifts. [HBN 00-09, sections 3.69–3.79](https://www.england.nhs.uk/wp-content/uploads/2021/05/HBN_00-09_infection_control.pdf) distinguishes dirty utility, clean supply and linen storage.

The proposed pixel-art families and counts are our product-design judgment informed by that coverage, not counts prescribed by those sources. The local itch.io references remain construction/camera references; their pixels are not included in the pack.
