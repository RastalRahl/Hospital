extends "res://solid_wall_review.gd"
## Current reference review: low outer foreground wall, original ground contacts.
const VISIBILITY_OUT := "res://repair_candidates/foreground_visibility_v1/"
var full_textures: Array[Texture2D] = []
var low_textures: Array[Texture2D] = []
var cutaway_enabled := false

func _ready() -> void:
	await super._ready()
	var material = load("res://foreground_cutaway_material.gd").new()
	material.back_finish = (load(FAMILY_FOLDER + "hospital_wall_back_straight_01_refresh_candidate.png") as Texture2D).get_image()
	material.left_finish = (load(FAMILY_FOLDER + "hospital_wall_side_left_01_refresh_candidate.png") as Texture2D).get_image()
	material.right_finish = (load(FAMILY_FOLDER + "hospital_wall_side_right_01_refresh_candidate.png") as Texture2D).get_image()
	for p in data.placements:
		if p.kind == "wall":
			var c: Array = p.collision
			material.strips.append(Rect2i(c[0], c[1], c[2], c[3]))
	for rect in ADDED_CONTACTS:
		material.strips.append(rect)
	for sprite in candidate_rows:
		full_textures.append(sprite.texture)
		var y := int(sprite.position.y) - 1
		low_textures.append(ImageTexture.create_from_image(material.row_image(y)) if y >= 408 else sprite.texture)
	material.free()
	set_cutaway(true)
	if "--foreground-visibility-review" in OS.get_cmdline_user_args():
		await visibility_review()

func set_cutaway(enabled: bool) -> void:
	cutaway_enabled = enabled
	for i in range(candidate_rows.size()):
		candidate_rows[i].texture = low_textures[i] if enabled else full_textures[i]
	update_hud()

func update_hud() -> void:
	super.update_hud()
	hud.text = hud.text.replace("FOUNDATION REFERENCE / full front / 4 added contacts", "FOUNDATION REFERENCE / 4 added contacts")
	hud.text += " | C front: " + ("LOW CUTAWAY" if cutaway_enabled else "FULL HEIGHT")

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_C:
		set_cutaway(not cutaway_enabled)
		return
	super._unhandled_key_input(event)

func screen_color(at: Vector2) -> Color:
	return get_viewport().get_texture().get_image().get_pixelv(Vector2i(get_global_transform_with_canvas() * at))

func visibility_review() -> void:
	DirAccess.make_dir_recursive_absolute(VISIBILITY_OUT)
	figure.position = Vector2(112, 400)
	set_cutaway(false)
	await capture(VISIBILITY_OUT + "before_godot.png")
	assert(screen_color(figure.position + Vector2(0, -20)).to_rgba32() != Color("d9ad59").to_rgba32())
	set_cutaway(true)
	await capture(VISIBILITY_OUT + "after_godot.png")
	assert(screen_color(figure.position + Vector2(0, -20)).to_rgba32() == Color("d9ad59").to_rgba32())
	for x in [42, 112, 352, 528, 694]:
		figure.position = Vector2(x, 408)
		assert(not blocked(figure.position))
		move_figure(Vector2(0, 12))
		assert(figure.position.y == 408, "Cutaway cannot change collision")
		await capture(VISIBILITY_OUT + "edge_%d_godot.png" % x)
		assert(screen_color(figure.position + Vector2(0, -20)).to_rgba32() == Color("d9ad59").to_rgba32())
		assert(screen_color(figure.position + Vector2(0, -40)).to_rgba32() == Color("e8cba7").to_rgba32())
	# All unaffected wall rows are the original texture objects, not copies.
	for i in range(candidate_rows.size()):
		if candidate_rows[i].position.y <= 408:
			assert(full_textures[i] == low_textures[i])
		else:
			var row := low_textures[i].get_image()
			for y in range(row.get_height()):
				for x in range(24, 712):
					assert(row.get_pixel(x, y).a == (0.0 if y < 32 else 1.0))
	# Original full-height connections/collision and door walkthrough remain.
	for rect in ADDED_CONTACTS:
		assert(blocked(Vector2(rect.position + Vector2i(4, 7))))
	set_door(false)
	assert(blocked(Vector2(608, 336)))
	set_door(true)
	figure.position = Vector2(608, 360)
	move_figure(Vector2(0, -64))
	assert(absf(figure.position.y - 296) < 0.1)
	figure.position = start
	for point in [Vector2(112, 368), Vector2(112, 312), Vector2(232, 312), Vector2(232, 216), Vector2(128, 216), Vector2(232, 216), Vector2(232, 368), Vector2(352, 368), Vector2(352, 280), Vector2(352, 368), Vector2(608, 368), Vector2(608, 248)]:
		move_figure(point - figure.position)
		assert(figure.position.distance_to(point) < 0.1)
	set_door(false)
	key(KEY_C)
	assert(not cutaway_enabled)
	key(KEY_C)
	assert(cutaway_enabled)
	key(KEY_H)
	key(KEY_H)
	assert(hospital_finish_enabled and cutaway_enabled)
	for entry in placement_sprites:
		if entry.placement.kind == "glass":
			assert(not entry.sprite.visible)
	figure.position = start
	await capture(VISIBILITY_OUT + "overview_godot.png")
	print("FOREGROUND_VISIBILITY_PASS: torso/head visible at five front positions; opaque cutaway, unchanged contacts, door and walkthrough")
	get_tree().quit()
