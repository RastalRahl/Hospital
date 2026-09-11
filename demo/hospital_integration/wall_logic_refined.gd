extends "res://wall_logic_test.gd"
## Reuses V1 footprint connectivity; original cutaway rendering and practical room.
const REVIEW := "res://repair_candidates/wall_logic_reference_v3/"
const FLOOR := Color("d0c9b6")
const TOP := Color("718b91")
const FIGURE := Color("d9ad59")
var feet := Vector2i(284, 160)
var furnished := true
var actor_images: Array[Image] = []
var actor_feet := [Vector2i(244, 136), Vector2i(309, 130)]
var person: Image
var movement_remainder := 0.0

func wall_height(x: int, y: int, cutaway: bool) -> int:
	var h := super.wall_height(x, y, cutaway)
	# A room-level cut plane, not an isolated low strip at the very front.
	if cutaway and h > 0 and y >= 180:
		return LOW
	return h

func blocked(at: Vector2i) -> bool:
	if at.x < 61 or at.x > 322 or at.y < 92 or at.y > 252:
		return true
	for y in range(at.y - 7, at.y + 1):
		for x in range(at.x - 9, at.x + 9):
			if wall_height(x, y, true) > 0:
				return true
	if furnished:
		for contact in [Rect2i(228, 115, 32, 21), Rect2i(296, 117, 26, 13)]:
			if contact.intersects(Rect2i(at - Vector2i(9, 7), Vector2i(18, 8))):
				return true
	return false

func draw_actors(img: Image, y: int) -> void:
	if not furnished:
		return
	for i in range(actor_images.size()):
		if actor_feet[i].y == y:
			var art := actor_images[i]
			img.blend_rect(art, Rect2i(Vector2i.ZERO, art.get_size()), actor_feet[i] - Vector2i(art.get_width() / 2, art.get_height()))
	if feet.y == y:
		img.blend_rect(person, Rect2i(0, 0, 26, 46), feet - Vector2i(13, 46))

func canvas_dimensions() -> Vector2i:
	return SIZE

func floor_rectangle() -> Rect2i:
	return Rect2i(44, 76, 296, 180)

func ground_y_end() -> int:
	return 257

func build_image(cutaway: bool) -> Image:
	var dimensions := canvas_dimensions()
	var img := Image.create(dimensions.x, dimensions.y, false, Image.FORMAT_RGBA8)
	img.fill(Color("273746"))
	img.fill_rect(floor_rectangle(), FLOOR)
	for y in range(76, ground_y_end()):
		if cutaway:
			draw_actors(img, y)
		for x in range(44, 340):
			var h := wall_height(x, y, cutaway)
			if h == 0:
				continue
			var left_edge := wall_height(x - 1, y, cutaway) < h
			var right_edge := wall_height(x + 1, y, cutaway) < h
			# RPG cutaway convention: a south-going low boundary reaches the
			# full wall's top border through its cut face. It must not begin as
			# a tab midway down the plaster. Only the final full-height row owns
			# this reveal; subsequent low rows extend it with normal depth sorting.
			var south_h := wall_height(x, y + 1, cutaway)
			var south_return := cutaway and h == FULL and south_h == LOW
			# A two-pixel recess at openings, shaded independently by facing.
			var jamb_left := wall_height(x - 2, y, cutaway) == 0 and x > 52
			var jamb_right := wall_height(x + 2, y, cutaway) == 0 and x < 332
			for z in range(h - 1, -1, -1):
				var color := IVORY
				if z < 8:
					color = TOP
				if jamb_left:
					color = Color("bbc7c2")
				if jamb_right:
					color = Color("8ca2a3")
				if z == 0 or right_edge:
					color = INK
				elif left_edge:
					color = Color("526975")
				if south_return:
					color = TOP
					if wall_height(x - 1, y + 1, cutaway) == 0:
						color = Color("b6c7c5")
					elif wall_height(x + 1, y + 1, cutaway) == 0:
						color = INK
				img.set_pixel(x, y - z, color)
			var top := TOP
			if left_edge or wall_height(x, y - 1, cutaway) < h:
				top = Color("b6c7c5")
			elif right_edge or wall_height(x, y + 1, cutaway) < h:
				top = INK
			if south_return:
				top = TOP
				if wall_height(x - 1, y + 1, cutaway) == 0:
					top = Color("b6c7c5")
				elif wall_height(x + 1, y + 1, cutaway) == 0:
					top = INK
			img.set_pixel(x, y - h, top)
	return img

func refresh() -> void:
	textures.clear()
	textures.append(ImageTexture.create_from_image(build_image(false)))
	textures.append(ImageTexture.create_from_image(build_image(true)))
	queue_redraw()

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for name in ["hospital_bed_standard_01", "bedside_cabinet_01"]:
		actor_images.append((load("res://art/" + name + "__main.png") as Texture2D).get_image())
	person = Image.create(26, 46, false, Image.FORMAT_RGBA8)
	person.fill(Color.TRANSPARENT)
	person.fill_rect(Rect2i(7, 0, 12, 12), INK)
	person.fill_rect(Rect2i(8, 1, 10, 10), Color("e8cba7"))
	person.fill_rect(Rect2i(0, 12, 26, 23), INK)
	person.fill_rect(Rect2i(1, 13, 24, 21), FIGURE)
	person.fill_rect(Rect2i(4, 35, 7, 11), INK)
	person.fill_rect(Rect2i(15, 35, 7, 11), INK)
	refresh()
	if "--wall-refined-review" in OS.get_cmdline_user_args():
		await review()

func _process(delta: float) -> void:
	if "--wall-refined-review" in OS.get_cmdline_user_args():
		return
	var step := Vector2i(int(Input.is_physical_key_pressed(KEY_D)) - int(Input.is_physical_key_pressed(KEY_A)), int(Input.is_physical_key_pressed(KEY_S)) - int(Input.is_physical_key_pressed(KEY_W)))
	if step != Vector2i.ZERO:
		movement_remainder += delta * 64.0 / Vector2(step).length()
		for pixel in range(int(movement_remainder)):
			for axis in [Vector2i(step.x, 0), Vector2i(0, step.y)]:
				if not blocked(feet + axis):
					feet += axis
		movement_remainder -= floor(movement_remainder)
		refresh()
	else:
		movement_remainder = 0.0

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_F:
			furnished = not furnished
		elif event.keycode == KEY_R:
			feet = Vector2i(284, 160)
		elif event.keycode == KEY_G:
			show_grid = not show_grid
		refresh()

func review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(REVIEW))
	furnished = false
	var empty := build_image(true)
	assert(empty.get_pixel(208, 36).is_equal_approx(TOP))
	assert(empty.get_pixel(208, 132).is_equal_approx(TOP))
	assert(empty.get_pixel(208, 224).is_equal_approx(TOP))
	# Lower branches connect to the upper cap, not the middle of its face.
	for x in [48, 208, 336]:
		for y in range(132, 225):
			assert(empty.get_pixel(x, y).is_equal_approx(TOP))
	# Plaster beside the narrow reveal remains intact.
	assert(empty.get_pixel(216, 150).is_equal_approx(IVORY))
	assert(empty.save_png(REVIEW + "empty_native.png") == OK)
	furnished = true
	assert(blocked(Vector2i(250, 176)))
	assert(blocked(Vector2i(244, 128))) # bed contact
	for y in range(156, 217):
		assert(not blocked(Vector2i(284, y))) # complete doorway traversal
	for x in [48, 208, 336]:
		for y in range(180, 244):
			assert(wall_height(x, y, true) == LOW) # no tall front terminals
	for pose in [["behind_wall", Vector2i(250, 164)], ["doorway", Vector2i(284, 180)], ["front", Vector2i(284, 212)]]:
		feet = pose[1]
		assert(not blocked(feet))
		refresh()
		var pixels := textures[1].get_image()
		if pose[0] == "behind_wall":
			assert(not pixels.get_pixel(250, 144).is_equal_approx(FIGURE))
		else:
			assert(pixels.get_pixel(feet.x, feet.y - 20).is_equal_approx(FIGURE))
		assert(pixels.save_png(REVIEW + pose[0] + "_native.png") == OK)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(REVIEW + pose[0] + "_godot.png") == OK)
	print("WALL_REFINED_REVIEW_PASS: doorway traversal, bed/wall contacts, front heights, figure occlusion")
	get_tree().quit()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(48, 48), "RASTALR / ROOM-LEVEL CUTAWAY REVIEW", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, IVORY)
	draw_string(font, Vector2(48, 82), "Reference only | WASD move / F furniture / G grid / R reset | Figure 26 x 46px", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, IVORY)
	for i in range(textures.size()):
		var origin := Vector2(40 + i * 800, 142)
		draw_string(font, origin - Vector2(0, 16), ["A / FULL-HEIGHT CONSTRUCTION", "B / LOWER FRONT ROOMS + PRACTICAL SCALE"][i], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
		draw_texture_rect(textures[i], Rect2(origin, Vector2(SIZE) * 2), false)
		if show_grid:
			for x in range(32, 353, 32):
				draw_line(origin + Vector2(x, 76) * 2, origin + Vector2(x, 244) * 2, Color(0.3, 0.9, 0.8, 0.35))
			for y in range(64, 257, 32):
				draw_line(origin + Vector2(32, y) * 2, origin + Vector2(352, y) * 2, Color(0.3, 0.9, 0.8, 0.35))
	draw_string(font, Vector2(48, 768), "Lower side returns connect to the upper wall border through a continuous narrow cutaway edge.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
	draw_string(font, Vector2(48, 802), "Wall ends have shaded jambs; floor and cap use distinct values. Original approved furniture, native size.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
