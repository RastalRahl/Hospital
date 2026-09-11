# RastalR Modern Hospital & Emergency Services
## Original Asset-Pack Roadmap Addendum

This file restores the product-content roadmap that was omitted from the earlier Codex handoff.

It should be treated as the **canonical category-level product plan** unless the user explicitly revises it.

Important distinction:

- The original roadmap **did lock the category targets and the approximate 400-asset product scope**.
- It **did not lock a final list of 400 immutable asset IDs**.
- Therefore Codex should preserve the category targets below, inspect the current manifest, and maintain a concrete remaining-asset backlog that fulfills real hospital-building needs without filler.

---

# 1. Product target

Target: **about 400 meaningful logical assets**

Acceptable finish range:
- roughly **350–450** if the pack is genuinely complete and useful
- absolute upper bound around **500** only if additional assets are clearly valuable

Priority:
1. usefulness for building real hospital scenes;
2. modularity;
3. visual consistency;
4. meaningful variety;
5. count.

Never create filler simply to hit 400.

Count **logical assets only**.

Do **not** count separately:
- implementation components;
- exclusive orientation/state views belonging to one logical asset;
- source-scale exports;
- preview sheets;
- trivial recolors;
- animation frames;
- duplicate technical masks.

---

# 2. Locked category roadmap

| Category | Target logical assets |
|---|---:|
| Architecture | 45 |
| Reception / Waiting | 22 |
| Patient Rooms | 32 |
| Examination | 20 |
| ICU | 20 |
| Surgery | 24 |
| Radiology | 16 |
| Laboratory | 20 |
| Pharmacy | 14 |
| Emergency | 22 |
| Exterior / Ambulance | 24 |
| Morgue | 12 |
| Staff / Admin | 18 |
| Cafeteria / Kitchen | 14 |
| Bathrooms / Utility | 14 |
| Signage / Decor | 25 |
| Inventory / UI | 20 |
| Abandoned / Horror | 38 |
| **TOTAL** | **400** |

These targets are planning budgets, not quotas that justify bad assets.

A category may finish a few assets above/below target if that produces a better pack, but large deviations should be explained.

---

# 3. Intended coverage inside each category

These are **coverage budgets / subfamilies**, not immutable IDs.
Use the current manifest to avoid duplicates and turn gaps into a concrete backlog.

## Architecture — target 45

Intended coverage:
- Floors: ~5
- Solid wall system: ~8
- Doors / openings: ~12
- Glass / partitions: ~6
- Structural details / connectors: ~6
- Entrance / special architecture: ~8

Key principle:
Architecture is deterministic, grid-first, and tested in Godot.

Do not inflate count with technical views/components.

Current architecture work already includes Foundation walls/floors, Doors & Openings, and pending/staged glass. Reconcile actual current count from the manifest before planning the remaining architecture assets.

## Reception / Waiting — target 22

Coverage budget:
- Reception counters / desk modules: ~5
- Waiting seating: ~5
- Check-in / information: ~3
- Queue / barrier elements: ~2
- Lobby utilities: ~4
- Small decor / wayfinding support: ~3

Examples of useful coverage:
reception counters, accessible counter, self-check-in kiosk, visitor chair, waiting bench, brochure rack, water cooler, sanitizer, queue barrier, lobby plant.

Avoid creating multiple near-identical chairs merely for count.

## Patient Rooms — target 32

Coverage budget:
- Beds / bed states: ~4
- Bedside furniture: ~5
- Ward accessories: ~5
- Patient-support equipment: ~5
- Privacy / storage: ~5
- Room utilities: ~4
- Visitor / family furniture: ~4

Useful coverage includes:
standard hospital bed, alternate bed type/state, bedside cabinet variants, overbed table, reading light, call/power panel, IV support, patient lift/support, privacy curtain/screen, wardrobe, visitor chair, waste bin, bedside step.

## Examination — target 20

Coverage budget:
- Tables / chairs / stools: ~5
- Diagnostic devices: ~5
- Examination lighting: ~2
- Storage / hygiene: ~4
- Instruments / support: ~4

The category should furnish a complete general examination room without borrowing half its core equipment from unrelated categories.

## ICU — target 20

Coverage budget:
- Critical-care monitoring: ~4
- Respiratory / ventilation: ~4
- Infusion / IV: ~4
- Bedside support: ~4
- Emergency / specialty support: ~4

Focus on equipment that visibly distinguishes an ICU from a normal patient room.

## Surgery — target 24

Coverage budget:
- OR core furniture / table / lights: ~5
- Anesthesia / airway: ~4
- Sterile instrument / storage: ~4
- Electrosurgery / smoke management: ~3
- Imaging / endoscopy: ~3
- Specialized OR support: ~5

The goal is a convincingly furnishable operating room, not a catalog of tiny surgical instruments.

## Radiology — target 16

Coverage budget:
- Core imaging modalities: ~6
- Patient positioning / support: ~3
- Workstation / control: ~2
- Contrast / modality accessories: ~3
- Storage / room support: ~2

Prioritize visually distinct imaging equipment and practical room support.

## Laboratory — target 20

Coverage budget:
- Analyzers / core instruments: ~6
- Benches / workstations: ~3
- Sample handling: ~4
- Cold / cryogenic storage: ~3
- Safety / waste / support: ~4

The set should support both a general clinical lab and some specialty-lab flavor.

## Pharmacy — target 14

Coverage budget:
- Dispensing / shelving / storage: ~4
- Automated dispensing: ~2
- Secure / cold storage: ~2
- Compounding / preparation: ~3
- Counter / workstation / support: ~3

Avoid duplicating generic cabinets already well covered elsewhere unless the pharmacy version is meaningfully distinct.

## Emergency — target 22

Coverage budget:
- Trauma / resuscitation: ~5
- Triage / treatment: ~4
- Transport: ~3
- Respiratory / infusion: ~3
- Decontamination / isolation: ~2
- Department support / supplies: ~5

The category should support a recognizable emergency/trauma room and triage area.

## Exterior / Ambulance — target 24

Coverage budget:
- Ambulances / emergency vehicle variants: ~4
- Emergency vehicle support: ~2
- Ambulance-bay infrastructure: ~5
- Hospital entrance exterior: ~4
- Parking / road / curb pieces: ~4
- Exterior utilities / signs / support: ~5

Examples:
ambulance, alternate ambulance state/orientation only when genuinely useful, bollards, bay markings, canopy, curb/ramp, exterior bench, entrance sign support, emergency entrance fixtures, exterior waste/utilities.

Do not turn this into a generic city pack.

## Morgue — target 12

Coverage budget:
- Body transport / storage: ~4
- Autopsy room: ~3
- Prep / washing: ~2
- Admin / storage / support: ~3

Examples:
body trolley, mortuary stretcher, body storage/refrigeration, autopsy table, instrument support, wash/prep station, storage.

Keep treatment clinical and usable rather than sensational.

## Staff / Admin — target 18

Coverage budget:
- Desks / computer workstations: ~5
- Office seating / storage: ~4
- Staff lockers / break-room: ~4
- Meeting / admin: ~3
- Boards / clocks / miscellaneous: ~2

This category should furnish nurse/admin offices and staff-only spaces.

Reuse Everyday World Common assets where appropriate instead of making hospital-branded duplicates.

## Cafeteria / Kitchen — target 14

Coverage budget:
- Service counters: ~3
- Dining tables / seating: ~4
- Cooking / prep: ~3
- Refrigeration / storage: ~2
- Washing / waste: ~2

This is hospital cafeteria support, not a full restaurant pack.

## Bathrooms / Utility — target 14

Coverage budget:
- Toilets: ~2
- Sinks / vanities: ~2
- Shower / accessibility: ~3
- Janitorial / cleaning: ~3
- Laundry / utility: ~2
- Small fixtures / consumables: ~2

Must support accessible hospital restroom and janitorial/utility rooms.

## Signage / Decor — target 25

Coverage budget:
- Department identification signs: ~5
- Directional / wayfinding: ~5
- Safety / regulatory pictograms: ~4
- Wall decor: ~4
- Clocks / boards / information: ~3
- Plants / ambient decor: ~4

Important:
Readable sign text/pictograms should be deterministic and separated from generated artwork when needed.

No fake AI text.

## Inventory / UI — target 20

Coverage budget:
- Medical-consumable pickups/items: ~5
- Medicines / containers: ~4
- Documents / cards / paperwork: ~3
- Equipment / inventory icons: ~4
- Status / interaction UI: ~4

These should be actual useful deliverables, not metadata disguised as asset count.

Keep their visual language compatible with the pack and game use.

## Abandoned / Horror — target 38

Coverage budget:
- Damage overlays: ~8
- Grime / blood / leaks / stains: ~7
- Broken furniture / equipment states: ~6
- Abandoned-room props: ~5
- Environmental-storytelling elements: ~6
- Hazard / lighting / decal support: ~6

Key rule:
This is the **same hospital world in an abandoned/damaged state**, not a separate unrelated horror art style.

Prefer reusable overlays when possible:
- cracks;
- peeling paint;
- grime;
- stains;
- broken glass;
- damage;
- caution/hazard treatment.

Only count an overlay as a logical asset when it is a genuinely useful standalone deliverable.

---

# 4. Categories that were NOT part of the locked 400 roadmap

Do not spontaneously create separate major categories for:
- Maternity
- Pediatrics
- Rehabilitation

Those were previously explored as possible directions but were **not part of the locked 400-category roadmap**.

Assets useful to those settings may still appear where they naturally belong, but creating full new departments requires explicit user approval and a roadmap revision.

---

# 5. How Codex should turn this roadmap into the remaining backlog

Codex should not assume "400 - current manifest count" is enough.

Create and maintain a coverage matrix with:

- roadmap category;
- target count;
- current logical manifest count;
- approved count;
- pending count;
- missing-to-target count;
- important covered capabilities;
- important missing capabilities;
- proposed remaining asset IDs/names;
- priority;
- Godot demo/use-case that proves usefulness.

Use the current `metadata/manifest.json` / catalog as the source of truth for current counts.

Do not use stale handoff counts if the repository has advanced.

For every proposed new asset:
1. confirm it is not already represented by an existing logical asset;
2. explain its practical hospital-building use;
3. determine whether it belongs in Hospital Only or Everyday World Common;
4. avoid near-duplicate variants;
5. prefer assets that make a complete room/department possible.

---

# 6. Recommended completion order

After the current cleanup/production-approval phase:

1. Finish remaining Architecture capabilities needed by real room building.
2. Complete underfilled **core hospital departments** before polishing edge categories.
3. Build missing support spaces:
   - Exterior / Ambulance
   - Morgue
   - Staff / Admin
   - Cafeteria / Kitchen
   - Bathrooms / Utility
4. Complete Signage / Decor.
5. Complete Inventory / UI.
6. Build Abandoned / Horror last, using the finished clean hospital as its base.

If current manifest auditing shows that a supposedly "completed" clinical category is materially below its roadmap coverage, fill the meaningful gap rather than blindly moving on.

---

# 7. Faster production rule

The D1-D4 glass workflow was too expensive to repeat.

For ordinary props:
- plan coherent batches of about 8–20;
- generate/create the family;
- one visual review;
- one extraction/QA pass;
- stage;
- test representative assets in Godot;
- fix failed items only;
- approve.

For established architecture:
- prototype one representative unit;
- test in Godot;
- approve visual language;
- propagate across family;
- one family QA/integration pass;
- stage/approve.

Use targeted tests while iterating.
Run full suite once at completed batch/task boundaries.

Godot integration should happen **early**, not after hours of isolated validation.

---

# 8. Persistent documentation

Codex should place this roadmap into the repository as a concise canonical planning file, recommended path:

`docs/ASSET_ROADMAP.md`

Then update `docs/CODEX_PROJECT_STATE.md` to reference it.

Codex should maintain a second generated/current file if useful, for example:

`docs/ASSET_COVERAGE_STATUS.md`

That file should be computed/reconciled from the manifest and show current counts and the concrete remaining backlog.

Do not overwrite this original roadmap merely because current counts differ.
Roadmap changes require explicit user approval.


## Repository reconciliation note — 2026-09-11

Imported from the user-supplied roadmap addendum; replacement-character punctuation normalized to en dashes. Category targets above are unchanged. The ZIP’s companion update prompt is not a separate task instruction. The user explicitly adopted this document’s category-level targets. Concrete IDs remain proposals, maintained in [ASSET_COVERAGE_STATUS.md](ASSET_COVERAGE_STATUS.md) against the current [manifest](../metadata/manifest.json).

The latest user direction parks glass and removes it from the solid-wall review. The glass budget does not authorize resuming it or adding windows. Complete current cleanup before new production. Existing orientation/state records remain in the audited manifest total; future technical views, frames and components add no logical count.
