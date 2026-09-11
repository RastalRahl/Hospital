extends "res://foundation_reference_rooms.gd"
## Reuse the reviewed finish; actual hospital footprints are supplied by its scene.
var strips: Array[Rect2i] = []

func wall_height(x: int, y: int, _cutaway: bool) -> int:
	for strip in strips:
		if strip.has_point(Vector2i(x, y)):
			return FULL
	return 0

func row_image(ground_y: int) -> Image:
	var img := Image.create(720, 45, false, Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	for x in range(24, 712):
		if wall_height(x, ground_y, false) == 0:
			continue
		for z in range(FULL):
			img.set_pixel(x, FULL - z, face_material(x, ground_y, z, IVORY))
		img.set_pixel(x, 0, cap_material(x, ground_y, TOP))
	return img
