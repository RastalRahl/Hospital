extends Node2D

const OUT := "res://repair_candidates/perspective_cabinet_v3/"
const INK := Color("182331")
const INK_2 := Color("273746")
const FLOOR := Color("d0c9b6")
const FLOOR_ALT := Color("c7c0ad")
const WALL := Color("efe8da")
const TOP := Color("718b91")
const FIGURE := Color("d9ad59")
const FEET_Y := 330.0
const POSITIONS := [60.0, 170.0, 280.0, 390.0, 500.0, 640.0, 810.0]
var sprites: Array[Sprite2D] = []

func add_sprite(path: String, x: float) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(3, 3)
	sprite.position = Vector2(x, FEET_Y)
	sprite.centered = true
	sprite.offset.y = -float(sprite.texture.get_height()) / 2.0
	sprite.z_index = int(FEET_Y)
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

func add_adult(x: float) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = adult_image()
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(3, 3)
	sprite.position = Vector2(x, FEET_Y)
	sprite.centered = true
	sprite.offset.y = -23.0
	sprite.z_index = int(FEET_Y)
	add_child(sprite)
	sprites.append(sprite)

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_sprite(OUT + "bedside_cabinet_01_approved.png", POSITIONS[0])
	add_sprite(OUT + "bedside_cabinet_01_v1_geometry.png", POSITIONS[1])
	add_sprite(OUT + "bedside_cabinet_01_v2_art.png", POSITIONS[2])
	add_sprite(OUT + "bedside_cabinet_01_art_candidate_v3.png", POSITIONS[3])
	add_adult(POSITIONS[4])
	add_sprite("res://art/hospital_bed_standard_01__main.png", POSITIONS[5])
	add_sprite("res://art/waiting_chair_01__main.png", POSITIONS[6])
	queue_redraw()
	if "--bedside-cabinet-v3-review" in OS.get_cmdline_user_args():
		await review()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 900, 420), INK_2)
	draw_rect(Rect2(20, 80, 860, 48), WALL)
	draw_rect(Rect2(20, 128, 860, 232), FLOOR)
	draw_rect(Rect2(20, 126, 860, 2), TOP)
	for x in range(20, 881, 96):
		draw_line(Vector2(x, 128), Vector2(x, 360), FLOOR_ALT, 1)
	for y in range(128, 361, 96):
		draw_line(Vector2(20, y), Vector2(880, y), FLOOR_ALT, 1)
	var f := ThemeDB.fallback_font
	draw_string(f, Vector2(24, 28), "BEDSIDE CABINET V3 — ART PILOT", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
	draw_string(f, Vector2(24, 58), "approved       V1 geometry       V2 art          V3 art          adult          bed                 chair", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("d8cabb"))
	for x in POSITIONS:
		draw_line(Vector2(x - 5, FEET_Y), Vector2(x + 5, FEET_Y), Color("e3a94b"), 1)
		draw_line(Vector2(x, FEET_Y - 5), Vector2(x, FEET_Y + 5), Color("e3a94b"), 1)
	draw_string(f, Vector2(24, 394), "3x integer render • common bottom-center feet • production unchanged", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("b9d8d3"))

func review() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image().get_region(Rect2i(0, 0, 900, 420))
	assert(image.save_png(OUT + "bedside_cabinet_v3_godot.png") == OK)
	assert(sprites.size() == 7)
	assert(sprites[0].texture.get_size() == Vector2(35, 43))
	assert(sprites[1].texture.get_size() == Vector2(32, 36))
	assert(sprites[2].texture.get_size() == Vector2(34, 36))
	assert(sprites[3].texture.get_size() == Vector2(32, 36))
	for sprite in sprites:
		assert(sprite.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)
		assert(sprite.scale == Vector2(3, 3))
		assert(sprite.position.y == FEET_Y)
	print("BEDSIDE_CABINET_V3_REVIEW_PASS: four cabinet states rendered beside adult, bed and chair at integer scale")
	get_tree().quit()
