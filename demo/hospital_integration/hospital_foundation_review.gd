extends "res://main.gd"
## Actual hospital integration, reference-only. Startup project remains main.tscn.
const HOSPITAL_FINISH_OUT := "res://repair_candidates/hospital_foundation_integration_v1/"
const ADDED_CONTACTS := [Rect2i(24, 88, 8, 8), Rect2i(704, 88, 8, 8), Rect2i(504, 88, 8, 8), Rect2i(504, 320, 8, 16)]
var candidate_rows: Array[Sprite2D] = []
var hospital_finish_enabled := false

func _ready() -> void:
	await super._ready()
	var material = load("res://hospital_wall_material.gd").new()
	material.back_finish = (load(FAMILY_FOLDER + "hospital_wall_back_straight_01_refresh_candidate.png") as Texture2D).get_image()
	material.left_finish = (load(FAMILY_FOLDER + "hospital_wall_side_left_01_refresh_candidate.png") as Texture2D).get_image()
	material.right_finish = (load(FAMILY_FOLDER + "hospital_wall_side_right_01_refresh_candidate.png") as Texture2D).get_image()
	for p in data.placements:
		if p.kind == "wall":
			var c: Array = p.collision
			material.strips.append(Rect2i(c[0], c[1], c[2], c[3]))
	for rect in ADDED_CONTACTS:
		material.strips.append(rect)
	for y in range(88, 416):
		var row: Image = material.row_image(y)
		if row.is_invisible():
			continue
		var sprite := Sprite2D.new()
		sprite.texture = ImageTexture.create_from_image(row)
		sprite.centered = false
		# One ground row per sprite keeps existing native Y-sort with props,
		# glass, doors and the moving figure; no foreground overlay is used.
		sprite.position = Vector2(0, y + 1)
		sprite.offset = Vector2(0, -45)
		world.add_child(sprite)
		candidate_rows.append(sprite)
	material.free()
	set_hospital_finish(true)
	if "--hospital-foundation-review" in OS.get_cmdline_user_args():
		await integration_review()

func set_hospital_finish(enabled: bool) -> void:
	set_wall_junctions(false)
	set_wall_family(false)
	hospital_finish_enabled = enabled
	for entry in placement_sprites:
		if entry.placement.kind == "wall":
			entry.sprite.visible = not enabled
	for sprite in candidate_rows:
		sprite.visible = enabled
	update_hud()
	overlay.queue_redraw()

func update_hud() -> void:
	super.update_hud()
	if hospital_finish_enabled:
		hud.text = hud.text.get_slice(" | V walls:", 0)
	hud.text += "\nH actual hospital walls: " + ("FOUNDATION REFERENCE / full front / 4 added contacts" if hospital_finish_enabled else "ORIGINAL comparison")

func blocked(point: Vector2) -> bool:
	if super.blocked(point):
		return true
	if hospital_finish_enabled:
		var contact := Rect2(point - Vector2(9, 8), Vector2(18, 8))
		for rect in ADDED_CONTACTS:
			if contact.intersects(Rect2(rect)):
				return true
	return false

func draw_debug() -> void:
	super.draw_debug()
	if debug and hospital_finish_enabled:
		for rect in ADDED_CONTACTS:
			overlay.draw_rect(Rect2(rect), Color.MAGENTA, false, 1)

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_H:
			set_hospital_finish(not hospital_finish_enabled)
			return
		if hospital_finish_enabled and event.physical_keycode in [KEY_V, KEY_J, KEY_K]:
			return
	# V/J compare historical modes only after H restores original walls.
	super._unhandled_key_input(event)

func integration_review() -> void:
	DirAccess.make_dir_recursive_absolute(HOSPITAL_FINISH_OUT)
	assert(candidate_rows.size() == 328)
	set_door(false)
	figure.position = start
	set_hospital_finish(false)
	await capture(HOSPITAL_FINISH_OUT + "original_godot.png")
	set_hospital_finish(true)
	await capture(HOSPITAL_FINISH_OUT + "candidate_godot.png")
	for pose in [["front_near", Vector2(112, 400)], ["front_clear", Vector2(112, 368)], ["divider", Vector2(528, 352)], ["door_open", Vector2(608, 336)]]:
		set_door(pose[0] == "door_open")
		figure.position = pose[1]
		assert(not blocked(figure.position))
		await capture(HOSPITAL_FINISH_OUT + pose[0] + "_godot.png")
		var pixels := get_viewport().get_texture().get_image()
		if pose[0] in ["front_near", "front_clear"]:
			var point := Vector2i(get_global_transform_with_canvas() * (figure.position + Vector2(0, -20)))
			var visible := pixels.get_pixelv(point).to_rgba32() == Color("d9ad59").to_rgba32()
			assert(visible == (pose[0] == "front_clear"))
	for rect in ADDED_CONTACTS:
		assert(blocked(Vector2(rect.position + Vector2i(4, 7))))
	key(KEY_H)
	assert(not hospital_finish_enabled)
	key(KEY_H)
	assert(hospital_finish_enabled)
	figure.position = start
	set_door(false)
	print("HOSPITAL_FOUNDATION_REVIEW_PASS: original/candidate, four connections, full-front visibility and H restore")
	# Existing practical smoke covers the actual reception/exam/patient-room
	# route, door collisions and glass transmission pixels, then quits.
	await smoke()
