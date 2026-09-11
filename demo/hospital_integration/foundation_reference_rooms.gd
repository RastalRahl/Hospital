extends "res://connected_reference_rooms.gd"
## Material-only adaptation of the human-approved Foundation V2 language.
const FINISH_OUT := "res://repair_candidates/foundation_connected_finish_v1/"
const FAMILY := "res://repair_candidates/foundation_wall_refresh_family_v1/"
var back_finish: Image
var left_finish: Image
var right_finish: Image
var finish_enabled := true

func face_material(x: int, y: int, z: int, color: Color) -> Color:
	if not finish_enabled:
		return color
	# 44 visible face rows use source rows 8..51, without resizing its art.
	var result := back_finish.get_pixel(posmod(x, 32), 51 - z)
	if z >= 7:
		if wall_height(x - 2, y, true) == 0 and x > 52:
			result = left_finish.get_pixel(12, 16)
		if wall_height(x + 2, y, true) == 0 and x < 332:
			result = right_finish.get_pixel(6, 16)
	if z == 0 or wall_height(x + 1, y, true) == 0:
		result = back_finish.get_pixel(16, 51)
	elif wall_height(x - 1, y, true) == 0:
		result = back_finish.get_pixel(16, 8)
	return result

func cap_material(x: int, y: int, color: Color) -> Color:
	if not finish_enabled:
		return color
	# Profile follows the union's exposed upper/left boundaries. No tile-edge
	# outlines: a T/cross continues through its shared interior.
	var distance := 8
	for offset in range(1, 9):
		if wall_height(x - offset, y, true) == 0 or wall_height(x, y - offset, true) == 0:
			distance = offset - 1
			break
	var row := distance if distance < 7 else 4
	if wall_height(x + 1, y, true) == 0 or wall_height(x, y + 1, true) == 0:
		row = 7
	return back_finish.get_pixel(16, row)

func refresh() -> void:
	textures.clear()
	finish_enabled = false
	textures.append(ImageTexture.create_from_image(build_image(true)))
	finish_enabled = true
	textures.append(ImageTexture.create_from_image(build_image(true)))
	queue_redraw()

func _ready() -> void:
	back_finish = (load(FAMILY + "hospital_wall_back_straight_01_refresh_candidate.png") as Texture2D).get_image()
	left_finish = (load(FAMILY + "hospital_wall_side_left_01_refresh_candidate.png") as Texture2D).get_image()
	right_finish = (load(FAMILY + "hospital_wall_side_right_01_refresh_candidate.png") as Texture2D).get_image()
	await super._ready()
	if "--foundation-room-review" in OS.get_cmdline_user_args():
		await finish_review()

func projected_wall(x: int, y: int) -> bool:
	for ground_y in range(y, y + FULL + 1):
		if wall_height(x, ground_y, true) == FULL:
			return true
	return false

func finish_review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(FINISH_OUT))
	assert(build_image(false).save_png(FINISH_OUT + "empty_native.png") == OK)
	# Geometry/collision are inherited unchanged; repeat the practical route.
	feet = Vector2i(124, 156)
	for target in [Vector2i(124, 252), Vector2i(284, 252), Vector2i(284, 156), Vector2i(284, 252), Vector2i(156, 252), Vector2i(156, 316)]:
		walk_to(target)
	assert(blocked(Vector2i(208, 156)))
	assert(blocked(Vector2i(100, 128)))
	for pose in [["rooms", Vector2i(284, 156)], ["corridor", Vector2i(208, 252)], ["behind_wall", Vector2i(250, 164)], ["doorway", Vector2i(284, 180)], ["exit", Vector2i(156, 316)]]:
		feet = pose[1]
		refresh()
		var plain := textures[0].get_image()
		var finished := textures[1].get_image()
		var changed := 0
		for y in range(finished.get_height()):
			for x in range(finished.get_width()):
				if not plain.get_pixel(x, y).is_equal_approx(finished.get_pixel(x, y)):
					assert(projected_wall(x, y), "Material escaped wall at %s" % Vector2i(x, y))
					changed += 1
		assert(changed > 1000)
		# Source band values on an unobstructed horizontal run, plus its
		# neighboring repeat boundary: no separator is introduced at x=64.
		for x in [63, 64, 65]:
			assert(finished.get_pixel(x, 65).is_equal_approx(back_finish.get_pixel(posmod(x, 32), 33)))
			assert(finished.get_pixel(x, 80).is_equal_approx(back_finish.get_pixel(posmod(x, 32), 48)))
		if pose[0] == "behind_wall":
			assert(not finished.get_pixel(250, 144).is_equal_approx(FIGURE))
		elif pose[0] in ["doorway", "exit", "corridor"]:
			assert(finished.get_pixel(feet.x, feet.y - 20).is_equal_approx(FIGURE))
		assert(finished.save_png(FINISH_OUT + pose[0] + "_native.png") == OK)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(FINISH_OUT + pose[0] + "_godot.png") == OK)
	print("FOUNDATION_CONNECTED_FINISH_PASS: source bands, wall-only pixel changes, unchanged walkthrough and occlusion")
	get_tree().quit()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(48, 48), "RASTALR / FOUNDATION FINISH ON FIXED GEOMETRY", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, IVORY)
	draw_string(font, Vector2(48, 82), "Human-approved material language / reference adaptation | Same full-height walls, furniture and figure", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, IVORY)
	for i in range(textures.size()):
		var origin := Vector2(40 + i * 800, 142)
		draw_string(font, origin - Vector2(0, 16), ["A / PLAIN CONSTRUCTION", "B / FOUNDATION CAP, PLASTER + BASE"][i], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
		draw_texture_rect(textures[i], Rect2(origin, Vector2(canvas_dimensions()) * 2), false)
		if show_grid:
			for x in range(32, 353, 32):
				draw_line(origin + Vector2(x, 76) * 2, origin + Vector2(x, 320) * 2, Color(0.3, 0.9, 0.8, 0.35))
	draw_string(font, Vector2(48, 896), "Existing Foundation V2 pixels supply the finish. Grid, heights, openings and collision are unchanged.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
	draw_string(font, Vector2(48, 930), "WASD move / F furniture / G grid / R reset | Reference only; production approval and camera decision pending.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
