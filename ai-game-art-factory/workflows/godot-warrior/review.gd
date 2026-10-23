extends Node2D
## Actual persisted RGBA sprites at exact 256px and 96px display sizes.
## Playback does not imply art approval. No engine-side mesh interpolation.
var clips: Array = []
var elapsed_ms := 0.0
var paused := false
var rendered_frames := 0
var screenshot_done := false
var font: Font

func _ready() -> void:
	font = ThemeDB.fallback_font
	if "--capture" in OS.get_cmdline_user_args():
		# Reproducible real viewport at a useful action pose, independent of boot time.
		paused = true
		elapsed_ms = 400.0
		for argument in OS.get_cmdline_user_args():
			if argument.begins_with("--capture-time-ms="):
				elapsed_ms = maxf(0.0, argument.trim_prefix("--capture-time-ms=").to_float())
	var total_frames := 0
	for direction in ["front_left", "front_right"]:
		var root: String = ProjectSettings.globalize_path("res://../../exports/warrior_v002/" + direction + "/")
		var file := FileAccess.open(root + "atlas.json", FileAccess.READ)
		if file == null:
			push_error("Missing sprite metadata: " + root)
			get_tree().quit(1)
			return
		var data = JSON.parse_string(file.get_as_text())
		var by_name: Dictionary = {}
		for entry in data.frames:
			var image := Image.load_from_file(root + entry.file)
			if image == null or image.get_width() != 256 or image.get_height() != 256:
				push_error("Invalid 256px sprite: " + root + entry.file)
				get_tree().quit(1)
				return
			by_name[entry.name] = ImageTexture.create_from_image(image)
			total_frames += 1
		for action in ["idle", "attack", "defense"]:
			var animation: Dictionary = data.animations[action]
			var textures: Array = []
			for name in animation.frames:
				textures.append(by_name[name])
			clips.append({"name": direction + " / " + action, "action": action,
				"textures": textures, "durations": animation.durations_ms,
				"duration_ms": animation.duration_ms, "loop": animation.loop})
	print("WARRIOR_SPRITES_READY clips=", clips.size(), " frames=", total_frames, " dimensions=256x256 art=pending")
	if DisplayServer.get_name() == "headless":
		print("HEADLESS_LOADING_CHECK: no rendered screenshot asserted")

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			paused = not paused
		if event.keycode == KEY_R:
			elapsed_ms = 0.0
		if event.keycode == KEY_RIGHT:
			paused = true
			elapsed_ms += 60.0

func _process(delta: float) -> void:
	if not paused:
		elapsed_ms += delta*1000.0
	rendered_frames += 1
	queue_redraw()
	if "--capture" in OS.get_cmdline_user_args() and not screenshot_done and rendered_frames > 3 and DisplayServer.get_name() != "headless":
		screenshot_done = true
		await RenderingServer.frame_post_draw
		var image: Image = get_viewport().get_texture().get_image()
		var target := ProjectSettings.globalize_path("res://../../exports/warrior_v002/godot-actual-size.png")
		var error := image.save_png(target)
		print("WARRIOR_GODOT_CAPTURE ", target, " time_ms=", elapsed_ms, " result=", error)
		get_tree().quit(error)

func _draw() -> void:
	if font == null:
		return
	draw_string(font, Vector2(20, 28), "HAMMER WARRIOR / Illustrated action review", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("253543"))
	draw_string(font, Vector2(20, 52), "256px + 96px actual sizes | SPACE pause | RIGHT advance 60ms | R restart | Art approval pending", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("4a5461"))
	for n in range(clips.size()):
		var clip: Dictionary = clips[n]
		var cycle: float = float(clip.duration_ms) + (0.0 if clip.loop else 450.0)
		var t := fmod(elapsed_ms, cycle)
		var frame_index: int = clip.textures.size()-1
		var total := 0.0
		for i in range(clip.durations.size()):
			total += float(clip.durations[i])
			if t < total:
				frame_index = i
				break
		var origin := Vector2(20+(n % 3)*414, 78+int(n/3)*350)
		draw_style_box(panel_style(n), Rect2(origin, Vector2(400, 333)))
		var color := Color("dbe1e5") if n >= 3 else Color("283947")
		draw_string(font, origin+Vector2(12, 24), str(clip.name), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, color)
		draw_string(font, origin+Vector2(12, 46), "frame %d / %d" % [frame_index+1, clip.textures.size()], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, color)
		draw_texture_rect(clip.textures[frame_index], Rect2(origin+Vector2(5, 61), Vector2(256, 256)), false)
		draw_texture_rect(clip.textures[frame_index], Rect2(origin+Vector2(285, 207), Vector2(96, 96)), false)
		draw_string(font, origin+Vector2(290, 323), "96px", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, color)

func panel_style(index: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color("293541") if index >= 3 else Color("f2f2e9")
	style.corner_radius_top_left = 6
	style.corner_radius_top_right = 6
	style.corner_radius_bottom_left = 6
	style.corner_radius_bottom_right = 6
	return style
