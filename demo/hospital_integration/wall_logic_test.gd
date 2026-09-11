extends Node2D
## Original geometry study. No third-party pixels or production overrides.
## Footprints: 32px cells, centered strip [12,20); ground -> screen (x,y-height).
const TILE := 32
const FULL := 44
const LOW := 12
const SIZE := Vector2i(384, 288)
const OUT := "res://repair_candidates/wall_logic_reference_v1/"
const INK := Color("182331")
const CAP := Color("a6b9ba")
const IVORY := Color("e6e3d3")
var textures: Array[ImageTexture] = []
var show_grid := false

func wall_height(x: int, y: int, cutaway: bool) -> int:
	# Ten by six cells. All intersections are unions of these strips.
	var outer_vertical := (x >= 44 and x < 52) or (x >= 332 and x < 340)
	var horizontal := (y >= 76 and y < 84) or (y >= 172 and y < 180)
	var front := y >= 236 and y < 244
	var divider := x >= 204 and x < 212
	if x < 44 or x >= 340 or y < 76 or y >= 244:
		return 0
	# Two clear 32px doorways, including a separate exposed wall end.
	if y >= 172 and y < 180 and ((x >= 108 and x < 140) or (x >= 268 and x < 300)):
		return 0
	# Entrance in the front strip; end faces use the same renderer.
	if front and x >= 140 and x < 172:
		return 0
	if outer_vertical or horizontal or front or divider:
		# The low front replaces the final row of each connected side too.
		return LOW if cutaway and front else FULL
	return 0

func build_image(cutaway: bool) -> Image:
	var img := Image.create(SIZE.x, SIZE.y, false, Image.FORMAT_RGBA8)
	img.fill(Color("273746"))
	img.fill_rect(Rect2i(44, 76, 296, 168), Color("bac5bf"))
	# Draw ground rows back-to-front. Each occupied ground pixel is a column;
	# shared columns are emitted once, so corners cannot acquire double borders.
	for y in range(76, 244):
		for x in range(44, 340):
			var h := wall_height(x, y, cutaway)
			if h == 0:
				continue
			var edge := wall_height(x - 1, y, cutaway) < h or wall_height(x + 1, y, cutaway) < h
			for z in range(h - 1, -1, -1):
				var color := IVORY
				if z < 8:
					color = Color("718b91")
				if z == 0:
					color = INK
				if edge:
					color = Color("526975")
				img.set_pixel(x, y - z, color)
			var top := CAP
			if wall_height(x - 1, y, cutaway) < h or wall_height(x, y - 1, cutaway) < h:
				top = Color("d5ded7")
			elif wall_height(x + 1, y, cutaway) < h or wall_height(x, y + 1, cutaway) < h:
				top = INK
			img.set_pixel(x, y - h, top)
	return img

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for cutaway in [false, true]:
		textures.append(ImageTexture.create_from_image(build_image(cutaway)))
	queue_redraw()
	if "--wall-logic-review" in OS.get_cmdline_user_args():
		# Connectivity/opening assertions exercise actual ground geometry.
		assert(wall_height(208, 80, false) == FULL) # T
		assert(wall_height(208, 176, false) == FULL) # cross
		assert(wall_height(48, 80, false) == FULL) # L
		assert(wall_height(120, 176, false) == 0) # doorway
		assert(wall_height(48, 239, true) == LOW)
		assert(wall_height(48, 235, true) == FULL)
		var pixels := textures[0].get_image()
		# Inspect rendered intersections: no outline or face may split the cap.
		for point in [Vector2i(48, 36), Vector2i(208, 36), Vector2i(208, 132)]:
			assert(pixels.get_pixelv(point).is_equal_approx(CAP))
		assert(pixels.get_pixel(120, 160).is_equal_approx(Color("bac5bf")))
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
		for i in range(2):
			assert(textures[i].get_image().save_png(OUT + ["continuous.png", "cutaway.png"][i]) == OK)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(OUT + "godot_review.png") == OK)
		print("WALL_LOGIC_REVIEW_PASS")
		get_tree().quit()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_G:
		show_grid = not show_grid
		queue_redraw()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(48, 48), "RASTALR / CONNECTED WALL CONSTRUCTION STUDY", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, IVORY)
	draw_string(font, Vector2(48, 82), "Original geometry | 32px grid / 8px strip / 44px wall | Reference only | G: ground grid", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, IVORY)
	for i in range(textures.size()):
		var origin := Vector2(40 + i * 800, 142)
		draw_string(font, origin - Vector2(0, 16), ["A / CONTINUOUS HEIGHT", "B / SAME NETWORK, 12px FRONT CUTAWAY"][i], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
		draw_texture_rect(textures[i], Rect2(origin, Vector2(SIZE) * 2), false)
		if show_grid:
			for x in range(32, 353, TILE):
				draw_line(origin + Vector2(x, 76) * 2, origin + Vector2(x, 244) * 2, Color(0.3, 0.9, 0.8, 0.35))
			for y in range(64, 257, TILE):
				draw_line(origin + Vector2(32, y) * 2, origin + Vector2(352, y) * 2, Color(0.3, 0.9, 0.8, 0.35))
	draw_string(font, Vector2(48, 768), "Both: outer L corners, central T + cross, two internal doorways and a front entrance.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
	draw_string(font, Vector2(48, 802), "B deliberately exposes the height step: inspect the tall terminal faces before accepting this cutaway policy.", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, IVORY)
