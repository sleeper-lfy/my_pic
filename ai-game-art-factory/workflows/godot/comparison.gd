extends Node2D
# Actual exported PNGs loaded directly. This scene does not certify visual quality.
var clips: Array = []
var elapsed_ms := 0.0
var rendered_frames := 0
var screenshot_done := false
var font: Font

func _ready() -> void:
	font = ThemeDB.fallback_font
	for route in ["B", "C"]:
		for weapon in ["hammer_a", "hammer_b"]:
			var name: String = route + "_" + weapon
			var root: String = ProjectSettings.globalize_path("res://../../exports/parts_experiment/" + name + "/")
			var file := FileAccess.open(root + "animation.json", FileAccess.READ)
			if file == null:
				push_error("Missing exported metadata: " + name)
				get_tree().quit(1)
				return
			var data = JSON.parse_string(file.get_as_text())
			var textures: Array = []
			var total_ms := 0
			for frame in data.frames:
				var im := Image.load_from_file(root + frame.file)
				if im == null or im.get_width() != 256 or im.get_height() != 256:
					push_error("Bad exported image: " + name + "/" + frame.file)
					get_tree().quit(1)
					return
				textures.append(ImageTexture.create_from_image(im))
				total_ms += int(frame.duration_ms)
			clips.append({"name": name, "data": data, "textures": textures, "total_ms": total_ms})
	print("ART_FACTORY_SCENE_READY clips=", clips.size(), " frames=52 dimensions=256x256; art=UNAPPROVED")
	if DisplayServer.get_name() == "headless":
		print("HEADLESS_FUNCTIONAL_CHECK_ONLY: dummy renderer; no Godot screenshot claimed")

func _process(delta: float) -> void:
	elapsed_ms += delta * 1000.0
	rendered_frames += 1
	queue_redraw()
	if "--capture" in OS.get_cmdline_user_args() and not screenshot_done and rendered_frames > 3 and DisplayServer.get_name() != "headless":
		screenshot_done = true
		await RenderingServer.frame_post_draw
		var image: Image = get_viewport().get_texture().get_image()
		var target := ProjectSettings.globalize_path("res://../../previews/parts_experiment/godot-actual-size.png")
		var error := image.save_png(target)
		print("GODOT_CAPTURE ", target, " result=", error)
		get_tree().quit(error)

func _draw() -> void:
	if font == null:
		return
	draw_string(font, Vector2(24,30), "UNAPPROVED ART EXPERIMENT | B: authored 2D / C: projected 3D", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("283943"))
	draw_string(font, Vector2(24,56), "Same painted parts; 4 attack keys / 13 samples. Neither route has passed art acceptance.", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("48535a"))
	for n in range(clips.size()):
		var clip = clips[n]
		var t := fmod(elapsed_ms, float(clip.total_ms) + 200.0)
		var index: int = clip.textures.size() - 1
		var accumulated := 0
		for i in range(clip.data.frames.size()):
			accumulated += int(clip.data.frames[i].duration_ms)
			if t < accumulated:
				index = i
				break
		var col := n % 2
		var row := int(n / 2)
		var origin := Vector2(24 + col * 500, 82 + row * 310)
		draw_string(font, origin + Vector2(0,18), clip.name + " | 96px and 256px", HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("283943"))
		draw_texture_rect(clip.textures[index],Rect2(origin+Vector2(0,150),Vector2(96,96)),false)
		draw_texture_rect(clip.textures[index],Rect2(origin+Vector2(145,30),Vector2(256,256)),false)
