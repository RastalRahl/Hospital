extends "res://wall_logic_refined.gd"
## Single-convention study based on SmallBurg examples/cosy_house.png.
## All walls are FULL, including front. No mixed-height reveal is activated.
const ROOM_OUT := "res://repair_candidates/single_reference_room_v1/"

func wall_height(x: int, y: int, _cutaway: bool) -> int:
	if x < 44 or x >= 308 or y < 76 or y >= 244:
		return 0
	if y >= 236 and x >= 172 and x < 204:
		return 0
	return FULL if x < 52 or x >= 300 or y < 84 or y >= 236 else 0

func blocked(at: Vector2i) -> bool:
	if at.x < 61 or at.x > 290 or at.y < 92 or at.y > 272:
		return true
	for y in range(at.y - 7, at.y + 1):
		for x in range(at.x - 9, at.x + 9):
			if wall_height(x, y, true) > 0:
				return true
	if furnished:
		for contact in [Rect2i(96, 115, 32, 21), Rect2i(163, 115, 26, 13)]:
			if contact.intersects(Rect2i(at - Vector2i(9, 7), Vector2i(18, 8))):
				return true
	return false

func build_image(with_actors: bool) -> Image:
	var img := super.build_image(with_actors)
	# Frame the smaller study floor; no wall/actor pixels occupy this margin.
	img.fill_rect(Rect2i(308, 76, 32, 180), Color("273746"))
	return img

func _ready() -> void:
	await super._ready()
	actor_feet = [Vector2i(112, 136), Vector2i(176, 128)]
	feet = Vector2i(220, 164)
	refresh()
	if "--single-room-review" in OS.get_cmdline_user_args():
		await room_review()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_R:
		feet = Vector2i(220, 164)
		refresh()
	else:
		super._unhandled_key_input(event)

func room_review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(ROOM_OUT))
	for y in range(76, 244):
		for x in range(44, 308):
			assert(wall_height(x, y, true) in [0, FULL])
	var empty := build_image(false)
	for point in [Vector2i(48, 36), Vector2i(304, 36), Vector2i(48, 196), Vector2i(304, 196)]:
		assert(empty.get_pixelv(point).is_equal_approx(TOP))
	assert(empty.save_png(ROOM_OUT + "empty_native.png") == OK)
	assert(blocked(Vector2i(112, 240)))
	assert(blocked(Vector2i(112, 128)))
	for y in range(164, 253):
		assert(not blocked(Vector2i(188, y)))
	for pose in [["room", Vector2i(220, 164)], ["behind_front", Vector2i(240, 228)], ["doorway", Vector2i(188, 244)]]:
		feet = pose[1]
		assert(not blocked(feet))
		refresh()
		var pixels := textures[1].get_image()
		if pose[0] == "behind_front":
			assert(not pixels.get_pixel(240, 208).is_equal_approx(FIGURE))
		else:
			assert(pixels.get_pixel(feet.x, feet.y - 20).is_equal_approx(FIGURE))
		assert(pixels.save_png(ROOM_OUT + pose[0] + "_native.png") == OK)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(ROOM_OUT + pose[0] + "_godot.png") == OK)
	print("SINGLE_REFERENCE_ROOM_PASS: one height, four corners, doorway traversal, furniture/wall contacts, front occlusion")
	get_tree().quit()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(48, 48), "RASTALR / ONE COMPLETE WALL CONVENTION", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, IVORY)
	draw_string(font, Vector2(48, 82), "SmallBurg cosy_house construction study | 32px grid / 8px strip / 44px height on EVERY wall", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, IVORY)
	for i in range(textures.size()):
		var origin := Vector2(40 + i * 800, 142)
		draw_string(font, origin - Vector2(0, 16), ["A / EMPTY ROOM", "B / SAME ROOM, FURNITURE + 26x46 FIGURE"][i], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
		draw_texture_rect(textures[i], Rect2(origin, Vector2(SIZE) * 2), false)
		if show_grid:
			for x in range(32, 321, 32):
				draw_line(origin + Vector2(x, 76) * 2, origin + Vector2(x, 256) * 2, Color(0.3, 0.9, 0.8, 0.35))
	draw_string(font, Vector2(48, 768), "Continuous top border, full horizontal faces, narrow side boundaries. Front wall intentionally stays full.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
	draw_string(font, Vector2(48, 802), "Reference study only | WASD move / F furniture / G grid / R reset | Full front can hide the figure.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
