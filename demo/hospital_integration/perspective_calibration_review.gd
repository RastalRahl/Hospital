extends Node2D

const OUT := "res://repair_candidates/perspective_calibration_v1/"
const INK := Color("182331")
const INK_2 := Color("273746")
const FLOOR := Color("d0c9b6")
const FLOOR_ALT := Color("c7c0ad")
const WALL := Color("efe8da")
const TOP := Color("718b91")
const FIGURE := Color("d9ad59")
const ROW_Y := [224.0, 420.0]
const X := [98.0, 240.0, 330.0, 410.0, 520.0, 638.0]
var sprites: Array[Sprite2D] = []
var show_guides := true

func add_sprite(path: String, position: Vector2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(2, 2)
	sprite.position = position
	sprite.centered = true
	sprite.offset.y = -float(sprite.texture.get_height()) / 2.0
	sprite.z_index = int(position.y)
	add_child(sprite)
	sprites.append(sprite)
	return sprite

func adult_image() -> ImageTexture:
	var person := Image.create(26, 46, false, Image.FORMAT_RGBA8)
	person.fill(Color.TRANSPARENT)
	person.fill_rect(Rect2i(7, 0, 12, 12), INK)
	person.fill_rect(Rect2i(8, 1, 10, 10), Color("e8cba7"))
	person.fill_rect(Rect2i(0, 12, 26, 23), INK)
	person.fill_rect(Rect2i(1, 13, 24, 21), FIGURE)
	person.fill_rect(Rect2i(4, 35, 7, 11), INK)
	person.fill_rect(Rect2i(15, 35, 7, 11), INK)
	return ImageTexture.create_from_image(person)

func add_adult(position: Vector2) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = adult_image()
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(2, 2)
	sprite.position = position
	sprite.centered = true
	sprite.offset.y = -23.0
	sprite.z_index = int(position.y)
	add_child(sprite)
	sprites.append(sprite)

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# Approved row.
	add_sprite(OUT + "reception_counter_straight_01_approved.png", Vector2(X[0], ROW_Y[0]))
	add_sprite(OUT + "bedside_cabinet_01_approved.png", Vector2(X[1], ROW_Y[0]))
	add_sprite(OUT + "medical_cart_base_01_approved.png", Vector2(X[2], ROW_Y[0]))
	add_adult(Vector2(X[3], ROW_Y[0]))
	add_sprite("res://art/hospital_bed_standard_01__main.png", Vector2(X[4], ROW_Y[0]))
	add_sprite("res://art/waiting_chair_01__main.png", Vector2(X[5], ROW_Y[0]))
	# Candidate row, with unchanged scale anchors.
	add_sprite(OUT + "reception_counter_straight_01_perspective_candidate.png", Vector2(X[0], ROW_Y[1]))
	add_sprite(OUT + "bedside_cabinet_01_perspective_candidate.png", Vector2(X[1], ROW_Y[1]))
	add_sprite(OUT + "medical_cart_base_01_perspective_candidate.png", Vector2(X[2], ROW_Y[1]))
	add_adult(Vector2(X[3], ROW_Y[1]))
	add_sprite("res://art/hospital_bed_standard_01__main.png", Vector2(X[4], ROW_Y[1]))
	add_sprite("res://art/waiting_chair_01__main.png", Vector2(X[5], ROW_Y[1]))
	queue_redraw()
	if "--perspective-calibration-review" in OS.get_cmdline_user_args():
		await review()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 720, 480), INK_2)
	for top in [68.0, 264.0]:
		draw_rect(Rect2(20, top, 680, 44), WALL)
		draw_rect(Rect2(20, top + 44, 680, 128), FLOOR)
		draw_rect(Rect2(20, top + 42, 680, 2), TOP)
		if show_guides:
			for x in range(20, 701, 64):
				draw_line(Vector2(x, top + 44), Vector2(x, top + 172), FLOOR_ALT, 1)
			for y in range(int(top + 44), int(top + 173), 64):
				draw_line(Vector2(20, y), Vector2(700, y), FLOOR_ALT, 1)
	var f := ThemeDB.fallback_font
	draw_string(f, Vector2(24, 28), "PERSPECTIVE CALIBRATION V1", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
	draw_string(f, Vector2(24, 56), "APPROVED — broad right faces / inconsistent yaw", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("d8cabb"))
	draw_string(f, Vector2(24, 252), "CANDIDATE — rectangular grid / depth straight upward", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("b9d8d3"))
	for i in range(X.size()):
		if show_guides:
			for row_y in ROW_Y:
				draw_line(Vector2(X[i] - 5, row_y), Vector2(X[i] + 5, row_y), Color("e3a94b"), 1)
				draw_line(Vector2(X[i], row_y - 5), Vector2(X[i], row_y + 5), Color("e3a94b"), 1)

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_G:
		show_guides = not show_guides
		queue_redraw()

func review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var review_crop := image.get_region(Rect2i(0, 0, 720, 480))
	assert(review_crop.save_png(OUT + "perspective_calibration_godot.png") == OK)
	for sprite in sprites:
		assert(sprite.texture != null)
		assert(sprite.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)
		assert(sprite.scale == Vector2(2, 2))
	# Candidate dimensions are deliberately smaller than or equal to approved
	# canvases and all six row anchors remain identical.
	assert(sprites[6].texture.get_width() == 72 and sprites[6].texture.get_height() == 38)
	assert(sprites[7].texture.get_width() == 32 and sprites[7].texture.get_height() == 36)
	assert(sprites[8].texture.get_width() == 36 and sprites[8].texture.get_height() == 42)
	for i in range(6):
		assert(sprites[i].position.x == sprites[i + 6].position.x)
		assert(sprites[i].position.y + 196.0 == sprites[i + 6].position.y)
	print("PERSPECTIVE_CALIBRATION_REVIEW_PASS: 3 candidates rendered with adult, bed and chair anchors; integer scale; matching feet")
	get_tree().quit()
