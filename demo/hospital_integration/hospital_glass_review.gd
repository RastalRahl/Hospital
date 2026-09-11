extends "res://hospital_foundation_review.gd"
## Reference-only material/frame redraw within the existing glass support mask.
const GLASS_OUT := "res://repair_candidates/glass_enclosure_refresh_v1/"
const GLAZE := Color8(173, 207, 214, 56)
const RAIL := Color("526f7c")
const GLINT := Color("acccd5")
var glass_entries: Array[Dictionary] = []
var glass_enabled := false
var frame_before := 0
var frame_after := 0

func make_glass(source: Image, asset: String, first: bool) -> Image:
	var result := Image.create(source.get_width(), source.get_height(), false, Image.FORMAT_RGBA8)
	result.fill(Color.TRANSPARENT)
	var side := "side_" in asset
	var corner := "corner" in asset
	var last := asset.ends_with("__main")
	for y in range(source.get_height()):
		for x in range(source.get_width()):
			var original := source.get_pixel(x, y)
			if original.a == 0:
				continue
			var rail := false
			var highlight := false
			if side:
				rail = x == 0 or x == source.get_width() - 1 or (last and y >= source.get_height() - 2) or (corner and y < 2)
				highlight = x == 0 or (corner and y == 1)
				# The inner side rail starts below the back pane's lower rail;
				# otherwise it pokes upward into that pane at the corner.
				var inner_x := source.get_width() - 1 if "side_left" in asset else 0
				if corner and y >= 2 and y < 28 and x == inner_x:
					rail = false
			else:
				rail = y < 2 or y >= source.get_height() - 2
				# Back enclosure endpoints are owned by the existing corner
				# views; only exposed front-run ends need vertical end rails.
				if "front_cutaway" in asset:
					rail = rail or (first and x < 2) or (last and x >= source.get_width() - 2)
				highlight = y == 1
			result.set_pixel(x, y, (GLINT if highlight else RAIL) if rail else GLAZE)
			assert((result.get_pixel(x, y).a > 0) == (original.a > 0))
			if original.a == 1.0:
				frame_before += 1
			if rail:
				frame_after += 1
	return result

func _ready() -> void:
	await super._ready()
	var review := "--hospital-glass-review" in OS.get_cmdline_user_args()
	if review:
		DirAccess.make_dir_recursive_absolute(GLASS_OUT)
	var previous_end: Dictionary = {}
	var mapping: Array[Dictionary] = []
	for entry in placement_sprites:
		var p: Dictionary = entry.placement
		if p.kind != "glass":
			continue
		var sprite: Sprite2D = entry.sprite
		var original: Texture2D = sprite.texture
		var group := "back" if "_back_" in p.asset else "front"
		var start_x := int(p.position[0] + p.offset[0])
		var first: bool = not previous_end.has(group) or previous_end[group] != start_x
		if not "side_" in p.asset:
			previous_end[group] = start_x + original.get_width()
		var candidate := make_glass(original.get_image(), p.asset, first)
		var filename := "%s_at_%d_%d.png" % [p.asset, int(p.position[0]), int(p.position[1])]
		glass_entries.append({"sprite": sprite, "original": original, "candidate": ImageTexture.create_from_image(candidate), "position": sprite.position, "offset": sprite.offset})
		mapping.append({"source": data.files[p.asset].path, "candidate": filename, "placement": p, "source_sha256": FileAccess.get_sha256("res://" + data.files[p.asset].path)})
		if review:
			assert(candidate.save_png(GLASS_OUT + filename) == OK)
	set_glass(true)
	if review:
		var file := FileAccess.open(GLASS_OUT + "mapping.json", FileAccess.WRITE)
		file.store_string(JSON.stringify({"reference_only": true, "glaze_alpha": 56, "opaque_samples_before": frame_before, "opaque_samples_after": frame_after, "placements": mapping}, "  "))
		file.close()
		await glass_review()

func set_glass(enabled: bool) -> void:
	glass_enabled = enabled
	for entry in glass_entries:
		entry.sprite.texture = entry.candidate if enabled else entry.original
		assert(entry.sprite.position == entry.position and entry.sprite.offset == entry.offset)
	update_hud()

func update_hud() -> void:
	super.update_hud()
	hud.text += " | O glass: " + ("light-frame reference" if glass_enabled else "original comparison")

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_O:
		set_glass(not glass_enabled)
		return
	super._unhandled_key_input(event)

func glass_probe_pixel() -> Color:
	return GLAZE if glass_enabled else super.glass_probe_pixel()

func glass_review() -> void:
	assert(glass_entries.size() == 22)
	assert(frame_after < frame_before / 2)
	set_door(false)
	figure.position = start
	set_glass(false)
	await capture(GLASS_OUT + "original_godot.png")
	set_glass(true)
	await capture(GLASS_OUT + "candidate_godot.png")
	for pose in [["behind", Vector2(368, 140)], ["inside", Vector2(368, 176)], ["front", Vector2(352, 320)]]:
		figure.position = pose[1]
		assert(not blocked(figure.position))
		await capture(GLASS_OUT + pose[0] + "_godot.png")
	# Expose corners without changing any architectural placement or transform.
	for entry in placement_sprites:
		if entry.placement.kind == "prop":
			entry.sprite.visible = false
	figure.visible = false
	await capture(GLASS_OUT + "unobstructed_godot.png")
	for entry in placement_sprites:
		if entry.placement.kind == "prop":
			entry.sprite.visible = true
	figure.visible = true
	key(KEY_O)
	assert(not glass_enabled)
	key(KEY_O)
	assert(glass_enabled)
	figure.position = start
	print("HOSPITAL_GLASS_REVIEW_PASS: 22 fixed placements, same support masks, reduced frames, O restore and three poses")
	# The inherited smoke probes this candidate's actual pane RGBA and checks
	# native source-over transmission, sorting, doors and the complete route.
	await smoke()
