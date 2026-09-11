extends Node2D

# Demo-only foot-contact movement. Art and metadata footprints are independent.
class Figure extends Node2D:
	func _draw() -> void:
		draw_rect(Rect2(-13, -46, 26, 46), Color("182331"), false, 1)
		draw_rect(Rect2(-7, -44, 14, 12), Color("e8cba7"))
		draw_rect(Rect2(-10, -30, 20, 20), Color("d9ad59"))
		draw_rect(Rect2(-8, -10, 6, 10), Color("273746"))
		draw_rect(Rect2(2, -10, 6, 10), Color("273746"))

const DOOR_CANDIDATE := "res://repair_candidates/sliding_door_open_alpha_v1/hospital_sliding_clinical_doors_open_01_alpha_candidate.png"
const WALL_PROTOTYPE := "res://repair_candidates/back_wall_refresh_v1/hospital_wall_back_straight_01_refresh_candidate.png"
var wall_sprites: Array[Sprite2D] = []
const WALL_PROTOTYPE_V2 := "res://repair_candidates/back_wall_refresh_v2/hospital_wall_back_straight_01_refresh_candidate_v2.png"
var wall_version := 0
const FAMILY_FOLDER := "res://repair_candidates/foundation_wall_refresh_family_v1/"
var family_entries: Array[Dictionary] = []
var family_textures: Dictionary = {}
var family_enabled := false
const JUNCTION_FOLDER := "res://repair_candidates/wall_junctions_v1/"
var junction_data: Dictionary
var junction_enabled := false
var junction_sprites: Array[Sprite2D] = []
var junction_originals: Array[Sprite2D] = []
var placement_sprites: Array[Dictionary] = []
var door_main: Sprite2D
var repair_active := true
var data: Dictionary
var overlay := Node2D.new()
var world := Node2D.new()
var figure := Figure.new()
var camera := Camera2D.new()
var hud := Label.new()
var solids: Array[Dictionary] = []
var state_nodes: Array[Dictionary] = []
var anchors: Array[Vector2] = []
var debug := false
var door_open := false
var zoom_level := 2
var start := Vector2(352, 368)

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var family: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FAMILY_FOLDER + "checks.json"))
	for asset in family.assets:
		family_textures[asset.id + "__main"] = load(FAMILY_FOLDER + asset.candidate_path)
	data = JSON.parse_string(FileAccess.get_file_as_string("res://runtime_manifest.json"))
	world.y_sort_enabled = true
	add_child(world)
	add_child(overlay)
	overlay.z_index = 10
	overlay.draw.connect(draw_debug)
	for p in data.placements:
		if p.collision != null:
			var c: Array = p.collision
			solids.append({"rect": Rect2(c[0], c[1], c[2], c[3]), "state": p.state})
		if not p.has("asset"):
			continue
		var s := Sprite2D.new()
		s.texture = load("res://" + data.files[p.asset].path)
		if p.asset == "hospital_sliding_clinical_doors_open_01__main":
			door_main = s
			s.texture = load(DOOR_CANDIDATE)
		if p.asset == "hospital_wall_back_straight_01__main":
			wall_sprites.append(s)
		if family_textures.has(p.asset):
			family_entries.append({"sprite": s, "original": s.texture, "candidate": family_textures[p.asset]})
		s.centered = false
		s.position = Vector2(p.position[0], p.position[1])
		s.offset = Vector2(p.offset[0], p.offset[1])
		if p.has("sort_y"):
			s.offset.y += s.position.y - p.sort_y
			s.position.y = p.sort_y
		if p.kind == "floor":
			s.z_index = -1
		else:
			anchors.append(Vector2(p.position[0], p.position[1]))
		world.add_child(s)
		placement_sprites.append({"placement": p, "sprite": s})
		if p.state != "":
			state_nodes.append({"node": s, "state": p.state})
	build_junction_views()
	world.add_child(figure)
	figure.position = start
	add_child(camera)
	camera.position = Vector2(368, 232)
	camera.zoom = Vector2.ONE * zoom_level
	var ui := CanvasLayer.new()
	add_child(ui)
	ui.add_child(hud)
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 20)
	set_door(false)
	if "--junction-review" in OS.get_cmdline_user_args():
		await junction_review()
	elif "--junction-smoke" in OS.get_cmdline_user_args():
		set_wall_junctions(true)
		await smoke()
	elif "--family-review" in OS.get_cmdline_user_args():
		await family_review()
	elif "--wall-review" in OS.get_cmdline_user_args():
		await wall_review()
	elif "--door-review" in OS.get_cmdline_user_args():
		await door_review()
	elif "--smoke" in OS.get_cmdline_user_args():
		await smoke()

func set_door(open: bool) -> void:
	door_open = open
	for entry in state_nodes:
		entry.node.visible = entry.state == ("open" if open else "closed")
	update_hud()
	overlay.queue_redraw()

func update_hud() -> void:
	hud.text = "RASTALR / HOSPITAL INTEGRATION   |   Batch 13: pending human review\nWASD / arrows: move   E: door (%s)   G: grid + contacts   R: reset   1 / 2 / 3: zoom\nReception / waiting: west     Examination: glass bay     Patient room: east     Corridor: south" % ("OPEN" if door_open else "CLOSED")
	hud.text += "\nDoor: UNAPPROVED alpha repair candidate" if repair_active else "\nDoor comparison: approved opaque original"
	hud.text += " | V walls: " + ("REFERENCE-ONLY family" if family_enabled else ["approved original", "REFERENCE-ONLY v1", "REFERENCE-ONLY v2"][wall_version])
	hud.text += " | J junctions: " + ("REFERENCE-ONLY" if junction_enabled else "original")

func blocked(point: Vector2) -> bool:
	var feet := Rect2(point - Vector2(9, 8), Vector2(18, 8))
	for s in solids:
		if s.state == "closed" and door_open:
			continue
		if feet.intersects(s.rect):
			return true
	if junction_enabled:
		for c in junction_data.collision_additions:
			if feet.intersects(Rect2(c[0], c[1], c[2], c[3])):
				return true
	return false

func move_figure(delta: Vector2) -> void:
	# Substep to avoid tunnelling even when a frame stalls.
	var steps := maxi(1, ceili(delta.length() / 3.0))
	for i in range(steps):
		var step := delta / steps
		var next := figure.position + Vector2(step.x, 0)
		if not blocked(next):
			figure.position.x = next.x
		next = figure.position + Vector2(0, step.y)
		if not blocked(next):
			figure.position.y = next.y

func _physics_process(delta: float) -> void:
	var direction := Vector2(float(Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT)) - float(Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT)), float(Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN)) - float(Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP)))
	move_figure(direction.normalized() * 100.0 * delta)
	camera.position = Vector2(368, 232) if zoom_level < 3 else figure.position.snapped(Vector2.ONE)
	if debug:
		overlay.queue_redraw()

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.physical_keycode:
		KEY_J:
			set_wall_junctions(not junction_enabled)
		KEY_V:
			set_wall_family(not family_enabled)
		KEY_G:
			debug = not debug
			overlay.queue_redraw()
		KEY_R:
			figure.position = start
		KEY_E:
			# Do not close a solid through the reference figure.
			if not door_open or not Rect2(571, 320, 74, 24).has_point(figure.position):
				set_door(not door_open)
		KEY_1, KEY_2, KEY_3:
			zoom_level = event.physical_keycode - KEY_0
			camera.zoom = Vector2.ONE * zoom_level

func draw_debug() -> void:
	if not debug:
		return
	for x in range(32, 705, 32):
		overlay.draw_line(Vector2(x,96), Vector2(x,416), Color(0.2,0.5,0.7,0.4))
	for y in range(96, 417, 32):
		overlay.draw_line(Vector2(32,y), Vector2(704,y), Color(0.2,0.5,0.7,0.4))
	for a in anchors:
		overlay.draw_line(a-Vector2(3,0),a+Vector2(3,0),Color.CYAN)
		overlay.draw_line(a-Vector2(0,3),a+Vector2(0,3),Color.CYAN)
	for s in solids:
		if s.state != "closed" or not door_open:
			overlay.draw_rect(s.rect,Color(1,0.4,0.2,0.8),false,1)
	if junction_enabled:
		for c in junction_data.collision_additions:
			overlay.draw_rect(Rect2(c[0],c[1],c[2],c[3]),Color.MAGENTA,false,1)
	overlay.draw_rect(Rect2(figure.position-Vector2(9,8),Vector2(18,8)),Color.YELLOW,false,1)

func capture(path: String) -> void:
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	assert(error == OK, "Screenshot save failed")

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = code
	event.pressed = true
	_unhandled_key_input(event)

func smoke() -> void:
	DirAccess.make_dir_recursive_absolute("res://.qa")
	DirAccess.make_dir_recursive_absolute("res://captures")
	key(KEY_3)
	assert(zoom_level == 3 and camera.zoom == Vector2(3,3))
	key(KEY_2)
	key(KEY_G)
	assert(debug)
	await capture("res://.qa/debug.png")
	key(KEY_G)
	figure.position = Vector2(80,400)
	key(KEY_R)
	assert(figure.position == start)
	assert(blocked(Vector2(608,336)), "Closed door must collide")
	set_door(true)
	assert(not blocked(Vector2(608,336)), "Open passage must clear")
	figure.position = Vector2(608,360)
	move_figure(Vector2(0,-64))
	assert(absf(figure.position.y - 296) < 0.1, "Open door crossing")
	set_door(false)
	figure.position = Vector2(608,360)
	move_figure(Vector2(0,-64))
	assert(figure.position.y >= 344, "Closed door blocks crossing")
	assert(blocked(Vector2(368,220)), "Bed/table floor contact")
	assert(not blocked(Vector2(352,320)), "Glass entrance is traversable")
	assert(blocked(Vector2(304,304)), "Glass trim collision")
	figure.position = Vector2(352,288)
	move_figure(Vector2(0,64))
	assert(absf(figure.position.y - 352) < 0.1, "Walk through glass entrance")
	# Explicit walkthrough of this layout, using the same movement/collision code.
	set_door(true)
	figure.position = start
	for point in [Vector2(112,368), Vector2(112,312), Vector2(232,312), Vector2(232,216), Vector2(128,216), Vector2(232,216), Vector2(232,368), Vector2(352,368), Vector2(352,280), Vector2(352,368), Vector2(608,368), Vector2(608,248)]:
		move_figure(point - figure.position)
		assert(figure.position.distance_to(point) < 0.1, "Walkthrough target %s reached %s" % [point,figure.position])
	set_door(false)
	# Same figure on each side of back pane, no opacity or material overrides.
	figure.position = Vector2(368,140)
	assert(not blocked(figure.position), "Behind-glass pose must be reachable floor")
	await capture("res://.qa/repair_glass_behind.png")
	# Verify actual viewport transmission against the supplied pane alpha.
	var pane_texture: Texture2D = load("res://art/hospital_glass_partition_back_01__repeat.png")
	var pane := pane_texture.get_image().get_pixel(11,8)
	var expected := Color("d9ad59").lerp(Color(pane.r,pane.g,pane.b,1),pane.a)
	var behind := get_viewport().get_texture().get_image()
	var observed := behind.get_pixelv(Vector2i(get_global_transform_with_canvas() * Vector2(363,128)))
	assert(Vector3(observed.r-expected.r,observed.g-expected.g,observed.b-expected.b).length() < 0.01, "Native glass alpha transmission")
	figure.position = Vector2(368,176)
	assert(not blocked(figure.position), "Front-glass pose must be reachable floor")
	await capture("res://.qa/repair_glass_front.png")
	var front := get_viewport().get_texture().get_image()
	assert(front.get_pixelv(Vector2i(get_global_transform_with_canvas() * Vector2(363,136))).to_rgba32() == Color("e8cba7").to_rgba32(), "Figure must render in front of pane")
	set_door(true)
	figure.position = Vector2(608,324)
	await capture("res://.qa/repair_door_open.png")
	set_door(false)
	figure.position = start
	await capture("res://.qa/repair_overview.png")
	print("HOSPITAL_SMOKE_PASS: closed/open collision, crossing, furniture contact, glass entrance, glass pixel sorting, reception/waiting/exam/bedside walkthrough and screenshots")
	get_tree().quit()



# One bounded candidate comparison, using the existing room and Y-sort order.
func door_review() -> void:
	DirAccess.make_dir_recursive_absolute("res://.qa")
	DirAccess.make_dir_recursive_absolute("res://captures/door_alpha_repair")
	set_door(false)
	figure.position = Vector2(608,360)
	move_figure(Vector2(0,-64))
	assert(figure.position.y >= 344, "Closed door blocks approach")
	await capture("res://captures/door_alpha_repair/closed_approach.png")
	set_door(true)
	figure.position = Vector2(608,324)
	assert(not blocked(figure.position))
	repair_active = false
	door_main.texture = load("res://art/hospital_sliding_clinical_doors_open_01__main.png")
	update_hud()
	await capture("res://captures/door_alpha_repair/before_opaque.png")
	repair_active = true
	door_main.texture = load(DOOR_CANDIDATE)
	update_hud()
	await capture("res://captures/door_alpha_repair/after_transparent.png")
	var result := get_viewport().get_texture().get_image()
	var transform := get_global_transform_with_canvas()
	assert(result.get_pixelv(Vector2i(transform * Vector2(608,306))).to_rgba32() == Color("d9ad59").to_rgba32(), "Figure body visible through aperture")
	# Header still occludes a head pixel; no figure Z override.
	assert(result.get_pixelv(Vector2i(transform * Vector2(608,286))).to_rgba32() != Color("e8cba7").to_rgba32(), "Header remains in front of rear figure")
	# Compare against the actual room with ONLY the doorway main carrier hidden.
	door_main.visible = false
	await capture("res://.qa/door_room_control.png")
	var control := get_viewport().get_texture().get_image()
	var aperture := Rect2i(Vector2i(transform * Vector2(583,298)),Vector2i(104,68))
	assert(result.get_region(aperture).get_data() == control.get_region(aperture).get_data(), "Entire aperture reveals actual existing room")
	door_main.visible = true
	move_figure(Vector2(0,12))
	assert(absf(figure.position.y-336)<0.1, "Crossing open threshold")
	await capture("res://captures/door_alpha_repair/crossing.png")
	move_figure(Vector2(0,24))
	assert(absf(figure.position.y-360)<0.1, "Reach foreground")
	await capture("res://captures/door_alpha_repair/in_front.png")
	# Exercise a real parked-leaf overlap at its ground anchor.
	figure.position = Vector2(568,320)
	await capture("res://.qa/door_leaf_behind.png")
	var rear := get_viewport().get_texture().get_image()
	assert(rear.get_pixelv(Vector2i(transform * Vector2(568,305))).to_rgba32() != Color("d9ad59").to_rgba32(), "Parked leaf occludes rear figure")
	figure.position = Vector2(568,348)
	await capture("res://.qa/door_leaf_front.png")
	var fore := get_viewport().get_texture().get_image()
	assert(fore.get_pixelv(Vector2i(transform * Vector2(568,320))).to_rgba32() == Color("d9ad59").to_rgba32(), "Foreground figure sorts ahead of leaf")
	print("DOOR_ALPHA_REVIEW_PASS: closed approach, open crossing, aperture room equivalence, header and leaf occlusion")
	get_tree().quit()

# Reference-only RGB override. Does not modify placement or runtime manifest.
func set_wall_prototype(version: int) -> void:
	wall_version = version
	var paths := ["res://art/hospital_wall_back_straight_01__main.png", WALL_PROTOTYPE, WALL_PROTOTYPE_V2]
	var texture: Texture2D = load(paths[version])
	for sprite in wall_sprites:
		sprite.texture = texture
	update_hud()

func wall_review() -> void:
	var folder := "res://repair_candidates/back_wall_refresh_v2/"
	assert(wall_sprites.size() == 25, "21 perimeter and 4 internal wall copies")
	var placement_before: Array = []
	for sprite in wall_sprites:
		placement_before.append([sprite.position,sprite.offset,sprite.scale,sprite.rotation,sprite.z_index])
	set_door(true)
	for version in range(3):
		set_wall_prototype(version)
		var label: String = ["approved", "v1", "v2"][version]
		await capture(folder + "godot_" + label + ".png")
		var crop := Rect2i(Vector2i(get_global_transform_with_canvas() * Vector2(256,44)),Vector2i(512,104))
		assert(get_viewport().get_texture().get_image().get_region(crop).save_png(folder + "godot_8cell_" + label + ".png") == OK)
		for i in wall_sprites.size():
			var sprite := wall_sprites[i]
			assert(placement_before[i] == [sprite.position,sprite.offset,sprite.scale,sprite.rotation,sprite.z_index], "Wall placement remains unchanged")
	print("WALL_PROTOTYPE_REVIEW_PASS: approved/v1/v2; same camera/zoom; 21 perimeter + 4 internal copies; transforms and draw anchors unchanged")
	get_tree().quit()

# All twelve candidates are loaded; only existing matching placements are overridden.
func set_wall_family(enabled: bool) -> void:
	if junction_enabled:
		set_wall_junctions(false)
	family_enabled = enabled
	wall_version = 0
	for entry in family_entries:
		entry.sprite.texture = entry.candidate if enabled else entry.original
	update_hud()

func family_review() -> void:
	assert(family_textures.size() == 12)
	var before: Array = []
	for entry in family_entries:
		var s: Sprite2D = entry.sprite
		before.append([s.position, s.offset, s.scale, s.rotation, s.z_index])
	set_door(true)
	for enabled in [false, true]:
		set_wall_family(enabled)
		var label := "refreshed" if enabled else "approved"
		await capture(FAMILY_FOLDER + "godot_" + label + ".png")
		var regions := {
			"back": Rect2i(608,168,512,104),
			"left": Rect2i(120,272,40,640),
			"right": Rect2i(1504,272,40,640),
			"front": Rect2i(480,872,512,40),
			"doorway": Rect2i(1080,640,424,120),
			"northwest_corner": Rect2i(100,150,200,210),
			"northeast_corner": Rect2i(1380,150,184,210)
		}
		for region in regions:
			assert(get_viewport().get_texture().get_image().get_region(regions[region]).save_png(FAMILY_FOLDER + "godot_" + region + "_" + label + ".png") == OK)
		for i in family_entries.size():
			var s: Sprite2D = family_entries[i].sprite
			assert(before[i] == [s.position,s.offset,s.scale,s.rotation,s.z_index])
	print("WALL_FAMILY_REVIEW_PASS: 12 candidates loaded; ", family_entries.size(), " unchanged placements; identical camera/zoom")
	get_tree().quit()

# Explicit native replacement views, not a generic connector or auto-tiling system.
func build_junction_views() -> void:
	junction_data = JSON.parse_string(FileAccess.get_file_as_string(JUNCTION_FOLDER + "junctions.json"))
	for p in junction_data.placements:
		for selected in p.replaces:
			var matches := 0
			for entry in placement_sprites:
				if entry.placement.asset == selected.asset and entry.placement.position == selected.position:
					junction_originals.append(entry.sprite)
					matches += 1
			assert(matches == 1, "Junction selector must resolve exactly once")
		var view: Dictionary = junction_data.assets[p.view]
		var s := Sprite2D.new()
		s.texture = load(JUNCTION_FOLDER + view.path)
		assert(s.texture != null)
		s.centered = false
		s.position = Vector2(p.position[0], p.sort_y)
		s.offset = Vector2(-view.image_anchor[0], p.position[1] - p.sort_y - view.image_anchor[1])
		s.visible = false
		world.add_child(s)
		junction_sprites.append(s)

func set_wall_junctions(enabled: bool) -> void:
	# Clearing the flag first avoids recursion when enabling the refreshed family.
	junction_enabled = false
	if enabled:
		set_wall_family(true)
	junction_enabled = enabled
	for s in junction_originals:
		s.visible = not enabled
	for s in junction_sprites:
		s.visible = enabled
	update_hud()
	overlay.queue_redraw()

func junction_review() -> void:
	assert(junction_sprites.size() == 6 and junction_originals.size() == 7)
	var before: Array = []
	for entry in placement_sprites:
		var s: Sprite2D = entry.sprite
		before.append([s.position, s.offset, s.scale, s.rotation, s.z_index])
	var solids_before := solids.duplicate(true)
	set_wall_family(true)
	set_door(true)
	for enabled in [false, true]:
		set_wall_junctions(enabled)
		var label := "after" if enabled else "before"
		await capture(JUNCTION_FOLDER + "godot_" + label + ".png")
		# Keep the furnished overview, then expose the same contacts without props
		# for the close crops; no furniture or camera placement is changed.
		for entry in placement_sprites:
			if entry.placement.kind == "prop":
				entry.sprite.visible = false
		figure.visible = false
		await capture(JUNCTION_FOLDER + "godot_unobstructed_" + label + ".png")
		var result := get_viewport().get_texture().get_image()
		var regions := {
			"northwest": Rect2(4,36,100,100),
			"northeast": Rect2(652,36,80,100),
			"divider_north": Rect2(468,36,80,112),
			"divider_east": Rect2(468,252,116,100),
			"southwest": Rect2(4,368,100,60),
			"southeast": Rect2(652,368,80,60)
		}
		for name in regions:
			var region: Rect2 = regions[name]
			var box := Rect2i(Vector2i(get_global_transform_with_canvas() * region.position), Vector2i(region.size * 2))
			assert(result.get_region(box).save_png(JUNCTION_FOLDER + name + "_" + label + ".png") == OK)
		for entry in placement_sprites:
			if entry.placement.kind == "prop":
				entry.sprite.visible = true
		figure.visible = true
		for i in placement_sprites.size():
			var s: Sprite2D = placement_sprites[i].sprite
			assert(before[i] == [s.position, s.offset, s.scale, s.rotation, s.z_index])
		assert(solids == solids_before, "Existing contacts unchanged")
	# Check the three new 8px-wide contacts at points whose foot rectangles did
	# not touch either former wall: catches diagonal-only topology connections.
	for point in [Vector2(16,96), Vector2(720,96), Vector2(496,328)]:
		set_wall_junctions(false)
		assert(not blocked(point), "Control exposes missing corner contact")
		set_wall_junctions(true)
		assert(blocked(point), "Junction contact closes gap")
	# Actual Y-sort probe beside the internal return, with no z-index override.
	figure.position = Vector2(501,330)
	await capture(JUNCTION_FOLDER + "divider_figure_behind.png")
	var transform := get_global_transform_with_canvas()
	var behind := get_viewport().get_texture().get_image()
	assert(behind.get_pixelv(Vector2i(transform * Vector2(501,310))).to_rgba32() != Color("d9ad59").to_rgba32())
	figure.position = Vector2(501,348)
	await capture(JUNCTION_FOLDER + "divider_figure_front.png")
	var front := get_viewport().get_texture().get_image()
	assert(front.get_pixelv(Vector2i(transform * Vector2(501,328))).to_rgba32() == Color("d9ad59").to_rgba32())
	figure.position = start
	set_wall_junctions(false)
	assert(junction_originals.all(func(s): return s.visible))
	assert(junction_sprites.all(func(s): return not s.visible))
	print("WALL_JUNCTION_REVIEW_PASS: six junctions, seven exclusive replacements, unchanged original transforms/contacts, three added contacts, figure Y-sort and toggle restore")
	get_tree().quit()
