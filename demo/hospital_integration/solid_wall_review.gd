extends "res://hospital_foundation_review.gd"
## Current review scope: solid architecture, no central glass enclosure.
const SOLID_OUT := "res://repair_candidates/solid_wall_review_v1/"

func _ready() -> void:
	await super._ready()
	for entry in placement_sprites:
		if entry.placement.kind == "glass":
			entry.sprite.visible = false
	# Rebuild from the unchanged manifest without glass contacts: no invisible
	# walls remain where the removed enclosure used to stand.
	solids.clear()
	anchors.clear()
	for p in data.placements:
		if p.kind == "glass":
			continue
		if p.collision != null:
			var c: Array = p.collision
			solids.append({"rect": Rect2(c[0], c[1], c[2], c[3]), "state": p.state})
		if p.kind != "floor" and p.has("asset"):
			anchors.append(Vector2(p.position[0], p.position[1]))
	update_hud()
	if "--solid-wall-review" in OS.get_cmdline_user_args():
		await solid_review()

func update_hud() -> void:
	super.update_hud()
	hud.text = hud.text.replace("Examination: glass bay", "Examination: open area")
	hud.text = hud.text.replace("Batch 13: pending human review", "SOLID WALL REVIEW / no glass enclosure")

func solid_review() -> void:
	DirAccess.make_dir_recursive_absolute(SOLID_OUT)
	for entry in placement_sprites:
		if entry.placement.kind == "glass":
			assert(not entry.sprite.visible)
		elif entry.placement.kind == "prop":
			assert(entry.sprite.visible)
	for point in [Vector2(368, 148), Vector2(256, 240), Vector2(480, 240), Vector2(304, 304)]:
		assert(not blocked(point), "Former glass contact must be clear")
	for route in [[Vector2(368, 120), Vector2(368, 176)], [Vector2(232, 240), Vector2(280, 240)], [Vector2(448, 240), Vector2(492, 240)]]:
		figure.position = route[0]
		move_figure(route[1] - figure.position)
		assert(figure.position.distance_to(route[1]) < 0.1, "Route %s -> %s stopped at %s" % [route[0], route[1], figure.position])
	set_door(false)
	assert(blocked(Vector2(608, 336)))
	set_door(true)
	figure.position = Vector2(608, 360)
	move_figure(Vector2(0, -64))
	assert(absf(figure.position.y - 296) < 0.1)
	assert(blocked(Vector2(368, 220)), "Examination table contact remains")
	figure.position = start
	for point in [Vector2(112, 368), Vector2(112, 312), Vector2(232, 312), Vector2(232, 216), Vector2(128, 216), Vector2(232, 216), Vector2(232, 368), Vector2(352, 368), Vector2(352, 280), Vector2(352, 368), Vector2(608, 368), Vector2(608, 248)]:
		move_figure(point - figure.position)
		assert(figure.position.distance_to(point) < 0.1)
	set_door(false)
	figure.position = start
	await capture(SOLID_OUT + "overview_godot.png")
	figure.position = Vector2(368, 176)
	await capture(SOLID_OUT + "examination_godot.png")
	key(KEY_H)
	key(KEY_H)
	for entry in placement_sprites:
		if entry.placement.kind == "glass":
			assert(not entry.sprite.visible)
	print("SOLID_WALL_REVIEW_PASS: enclosure hidden, former contacts traversable, props retained, door and hospital walkthrough pass")
	get_tree().quit()
