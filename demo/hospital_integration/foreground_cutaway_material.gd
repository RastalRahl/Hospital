extends "res://hospital_wall_material.gd"
## Presentation cut only. Ground topology remains the full connected strip.
const CUT_HEIGHT := 12

func wall_height(x: int, y: int, cutaway: bool) -> int:
	var height := super.wall_height(x, y, cutaway)
	if height > 0 and y >= 408:
		return CUT_HEIGHT
	return height

func row_image(ground_y: int) -> Image:
	var img := Image.create(720, 45, false, Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	for x in range(24, 712):
		var height := wall_height(x, ground_y, true)
		if height == 0:
			continue
		for z in range(height):
			img.set_pixel(x, FULL - z, face_material(x, ground_y, z, IVORY))
		img.set_pixel(x, FULL - height, cap_material(x, ground_y, TOP))
	return img
