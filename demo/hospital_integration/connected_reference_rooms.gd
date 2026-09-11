extends "res://wall_logic_refined.gd"
## Two furnished rooms and a connecting corridor; one full-height convention.
const CONNECTED_OUT := "res://repair_candidates/connected_reference_rooms_v1/"
const CONTACTS := [Rect2i(84, 115, 32, 21), Rect2i(139, 115, 26, 13), Rect2i(228, 115, 32, 21), Rect2i(297, 115, 26, 13)]

func wall_height(x: int, y: int, _cutaway: bool) -> int:
	# Original upper-room L/T/cross footprint plus a deeper corridor.
	if y < 204:
		return super.wall_height(x, y, false)
	if x < 44 or x >= 340 or y >= 308:
		return 0
	if y >= 300 and x >= 140 and x < 172:
		return 0
	return FULL if x < 52 or x >= 332 or y >= 300 else 0

func canvas_dimensions() -> Vector2i:
	return Vector2i(384, 352)

func floor_rectangle() -> Rect2i:
	return Rect2i(44, 76, 296, 244)

func ground_y_end() -> int:
	return 321

func blocked(at: Vector2i) -> bool:
	if at.x < 61 or at.x > 322 or at.y < 92 or at.y > 316:
		return true
	for y in range(at.y - 7, at.y + 1):
		for x in range(at.x - 9, at.x + 9):
			if wall_height(x, y, true) > 0:
				return true
	if furnished:
		for contact in CONTACTS:
			if contact.intersects(Rect2i(at - Vector2i(9, 7), Vector2i(18, 8))):
				return true
	return false

func _ready() -> void:
	await super._ready()
	actor_images.append(actor_images[0])
	actor_images.append(actor_images[1])
	actor_feet = [Vector2i(100, 136), Vector2i(152, 128), Vector2i(244, 136), Vector2i(310, 128)]
	feet = Vector2i(124, 156)
	refresh()
	if "--connected-room-review" in OS.get_cmdline_user_args():
		await connected_review()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_R:
		feet = Vector2i(124, 156)
		refresh()
	else:
		super._unhandled_key_input(event)

func walk_to(target: Vector2i) -> void:
	assert(feet.x == target.x or feet.y == target.y)
	while feet != target:
		var step := Vector2i(signi(target.x - feet.x), signi(target.y - feet.y))
		assert(not blocked(feet + step), "Walkthrough blocked at %s" % (feet + step))
		feet += step

func connected_review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(CONNECTED_OUT))
	for y in range(76, 308):
		for x in range(44, 340):
			assert(wall_height(x, y, true) in [0, FULL])
	var empty := build_image(false)
	for center in [Vector2i(48, 36), Vector2i(208, 36), Vector2i(208, 132), Vector2i(336, 36)]:
		for dy in range(-2, 3):
			for dx in range(-2, 3):
				assert(empty.get_pixelv(center + Vector2i(dx, dy)).is_equal_approx(TOP))
	assert(empty.save_png(CONNECTED_OUT + "empty_native.png") == OK)
	assert(blocked(Vector2i(208, 156)))
	assert(blocked(Vector2i(250, 176)))
	assert(blocked(Vector2i(100, 128)))
	assert(blocked(Vector2i(244, 128)))
	# Actual per-pixel route: room A -> corridor -> room B -> front exit.
	feet = Vector2i(124, 156)
	for target in [Vector2i(124, 252), Vector2i(284, 252), Vector2i(284, 156), Vector2i(284, 252), Vector2i(156, 252), Vector2i(156, 316)]:
		walk_to(target)
	for pose in [["room_a", Vector2i(124, 156)], ["room_b", Vector2i(284, 156)], ["corridor_crossing", Vector2i(208, 252)], ["behind_wall", Vector2i(250, 164)], ["doorway", Vector2i(284, 180)], ["exit", Vector2i(156, 316)]]:
		feet = pose[1]
		assert(not blocked(feet))
		refresh()
		var pixels := textures[1].get_image()
		if pose[0] == "behind_wall":
			assert(not pixels.get_pixel(250, 144).is_equal_approx(FIGURE))
		elif pose[0] in ["doorway", "exit", "corridor_crossing"]:
			assert(pixels.get_pixel(feet.x, feet.y - 20).is_equal_approx(FIGURE))
		assert(pixels.save_png(CONNECTED_OUT + pose[0] + "_native.png") == OK)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(CONNECTED_OUT + pose[0] + "_godot.png") == OK)
	print("CONNECTED_REFERENCE_ROOMS_PASS: full-height L/T/cross, both rooms traversed, corridor opening, exit, collision and occlusion")
	get_tree().quit()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(48, 48), "RASTALR / CONNECTED ROOMS, ONE WALL CONVENTION", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, IVORY)
	draw_string(font, Vector2(48, 82), "SmallBurg-derived convention | 32px grid / 8px strip / 44px on every wall | WASD / F / G / R", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, IVORY)
	for i in range(textures.size()):
		var origin := Vector2(40 + i * 800, 142)
		draw_string(font, origin - Vector2(0, 16), ["A / L CORNERS, NORTH T, CENTRAL CROSS", "B / TWO ROOMS + CONNECTING CORRIDOR"][i], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
		draw_texture_rect(textures[i], Rect2(origin, Vector2(canvas_dimensions()) * 2), false)
		if show_grid:
			for x in range(32, 353, 32):
				draw_line(origin + Vector2(x, 76) * 2, origin + Vector2(x, 320) * 2, Color(0.3, 0.9, 0.8, 0.35))
			for y in range(64, 321, 32):
				draw_line(origin + Vector2(32, y) * 2, origin + Vector2(352, y) * 2, Color(0.3, 0.9, 0.8, 0.35))
	draw_string(font, Vector2(48, 896), "Two 32px room doorways, a wide corridor connection and a front exit. No mixed-height junction patches.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
	draw_string(font, Vector2(48, 930), "Reference only. Full front walls can hide the figure; ground contact still governs movement.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
