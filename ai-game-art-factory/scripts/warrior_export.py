"""Pack a reviewed 4 x 4 illustrated sheet into transparent game sprites.

This only crops, uniformly resizes and packages existing pixels. It never removes
backgrounds, invents missing art, or uses in-between frame morphing. Row-major
order is idle (4), attack (8), defense (4). Technical validity is not art approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
SIZE = 256
GIF_BACKGROUND = '#26313e'
DURATIONS = {
    'idle': [250, 250, 250, 250],
    'attack': [100, 140, 120, 60, 70, 100, 120, 160],
    'defense': [120, 180, 220, 180],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8')) if path else None


def frame_names():
    return [f'{action}_{i:02d}' for action, times in DURATIONS.items() for i in range(len(times))]


def alpha_sum(image):
    return sum(value*count for value, count in enumerate(image.getchannel('A').histogram()))


def significant_count(image, threshold=16):
    return sum(image.getchannel('A').histogram()[threshold:])


def source_edge_check(crop):
    """Detect source crop contact; padding cannot repair this source-level risk."""
    alpha = crop.getchannel('A')
    w, h = crop.size
    edges = [alpha.crop((0, 0, w, 1)), alpha.crop((0, h-1, w, h))]
    if h > 2:
        edges.extend([alpha.crop((0, 1, 1, h-1)), alpha.crop((w-1, 1, w, h-1))])
    hist = [sum(edge.histogram()[i] for edge in edges) for i in range(256)]
    return {'edge_nonzero_alpha_pixels': sum(hist[1:]),
            'edge_significant_alpha_ge16_pixels': sum(hist[16:]),
            'edge_max_alpha': max((i for i, count in enumerate(hist) if count), default=0),
            'interpretation': 'A significant occupied crop edge can mean source clipping or contamination by another cell. Output padding does not fix it.'}


def check_image(image: Image.Image, name: str, margin=8):
    alpha = image.getchannel('A')
    bbox = alpha.getbbox()
    errors = []
    if bbox is None:
        errors.append('empty_frame')
    elif min(bbox[0], bbox[1], SIZE-bbox[2], SIZE-bbox[3]) < margin:
        errors.append('less_than_8px_safe_margin')
    if alpha.getextrema()[0] != 0:
        errors.append('no_fully_transparent_pixels')
    histogram = alpha.histogram()
    significant_bbox = alpha.point(lambda value: 255 if value >= 16 else 0).getbbox()
    return {'name': name, 'dimensions': list(image.size), 'mode': image.mode,
            'bbox_alpha_nonzero': list(bbox) if bbox else None,
            'safe_margin_px': min(bbox[0], bbox[1], SIZE-bbox[2], SIZE-bbox[3]) if bbox else None,
            'bbox_alpha_ge16': list(significant_bbox) if significant_bbox else None,
            'significant_safe_margin_px': min(significant_bbox[0], significant_bbox[1], SIZE-significant_bbox[2], SIZE-significant_bbox[3]) if significant_bbox else None,
            'alpha_min_max': list(alpha.getextrema()),
            'visible_pixels': sum(histogram[1:]),
            'fully_opaque_pixels': histogram[255], 'errors': errors}


def compose_contact(frames, directory: Path, direction: str):
    # Rectangles below are review backgrounds only; exported sprites stay RGBA.
    width, height = 1200, 880
    canvas = Image.new('RGB', (width, height), '#e6e5df')
    draw = ImageDraw.Draw(canvas)
    try:
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    except OSError:
        title_font = font = ImageFont.load_default()
    draw.text((18, 12), f'{direction} | Actual 96px / 128px sprites | Art approval pending', fill='#243040', font=title_font)
    for i, (name, frame) in enumerate(frames.items()):
        x, y = 18+(i % 4)*296, 52+(i // 4)*202
        draw.text((x, y), name, fill='#243040', font=font)
        draw.rectangle((x, y+25, x+119, y+170), fill='#eef0eb')
        draw.rectangle((x+124, y+25, x+277, y+170), fill='#26313e')
        small = frame.resize((96, 96), Image.Resampling.LANCZOS)
        medium = frame.resize((128, 128), Image.Resampling.LANCZOS)
        canvas.paste(small, (x+12, y+64), small)
        canvas.paste(medium, (x+137, y+32), medium)
    canvas.save(directory/'contact-review.png')


def write_gif(images, durations, path):
    """One shared palette per clip, solid review background, explicit 10ms timing."""
    flattened = []
    for image in images:
        if image.mode == 'RGBA':
            canvas = Image.new('RGBA', image.size, GIF_BACKGROUND)
            canvas.alpha_composite(image)
            flattened.append(canvas.convert('RGB'))
        else:
            flattened.append(image.convert('RGB'))
    samples = []
    for image in flattened:
        sample = image.copy()
        sample.thumbnail((256, 256), Image.Resampling.LANCZOS)
        samples.append(sample)
    sw = max(image.width for image in samples)
    palette_source = Image.new('RGB', (sw, sum(image.height for image in samples)), GIF_BACKGROUND)
    y = 0
    for sample in samples:
        palette_source.paste(sample, (0, y))
        y += sample.height
    palette = palette_source.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    quantized = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in flattened]
    times = [max(10, round(duration/10)*10) for duration in durations]
    quantized[0].save(path, format='GIF', save_all=True, append_images=quantized[1:],
                      duration=times, loop=0, disposal=2, optimize=False)
    with Image.open(path) as decoded:
        decoded_times = []
        for frame in ImageSequence.Iterator(decoded):
            frame.load()
            decoded_times.append(frame.info.get('duration', 0))
    if sum(decoded_times) != sum(times):
        raise RuntimeError('GIF decoded duration differs from encoded timeline: '+str(path))
    return {'file': Path(path).name, 'background': GIF_BACKGROUND, 'alpha': False,
            'palette': 'one shared 256-color median-cut palette; no dithering',
            'timing_quantization_ms': 10, 'requested_durations_ms': durations,
            'quantized_durations_ms': times, 'decoded_durations_ms': decoded_times,
            'decoded_frames': len(decoded_times), 'duration_ms': sum(decoded_times),
            'dimensions': list(images[0].size), 'bytes': Path(path).stat().st_size,
            'sha256': sha256(Path(path))}


def export_comparison(output):
    output = Path(output).resolve()
    clips = []
    for direction in ['front_left', 'front_right']:
        directory = output/direction
        data = json.loads((directory/'atlas.json').read_text())
        by_name = {item['name']: item for item in data['frames']}
        for action in DURATIONS:
            clip = data['animations'][action]
            images = []
            for name in clip['frames']:
                with Image.open(directory/by_name[name]['file']) as image:
                    image.load()
                    images.append(image.convert('RGBA'))
            clips.append({'direction': direction, 'action': action, 'images': images,
                          'durations': clip['durations_ms'], 'duration': clip['duration_ms'],
                          'loop': clip['loop']})
    period = 2000
    boundaries = {0, period}
    quantized_events = []
    for clip in clips:
        clip['events'] = []
        starts = range(0, period, clip['duration']) if clip['loop'] else [0]
        for start in starts:
            value = start
            for frame_index, duration in enumerate(clip['durations']):
                if value < period:
                    presentation = round(value/20)*20
                    if presentation < period:
                        boundaries.add(presentation)
                        clip['events'].append((presentation, frame_index))
                        quantized_events.append({'clip': clip['direction']+'/'+clip['action'],
                            'frame': frame_index, 'original_start_ms': value,
                            'presentation_start_ms': presentation, 'error_ms': presentation-value})
                value += duration
    boundaries = sorted(boundaries)
    try:
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except OSError:
        title_font = font = ImageFont.load_default()
    images, durations = [], []
    sample_indices = []
    for start, end in zip(boundaries, boundaries[1:]):
        canvas = Image.new('RGB', (864, 692), GIF_BACKGROUND)
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 10), 'HAMMER WARRIOR | 2 directions / 3 actions', fill='#edf0e7', font=title_font)
        draw.text((16, 36), '256px sprite canvases | Key-frame review | Art approval pending', fill='#c1cbd3', font=font)
        indices = []
        for n, clip in enumerate(clips):
            frame_index = 0
            for event_time, index in clip['events']:
                if event_time <= start:
                    frame_index = index
            indices.append(frame_index)
            x, y = 12+(n % 3)*284, 70+(n//3)*306
            draw.rounded_rectangle((x, y, x+272, y+294), radius=5, fill='#344251')
            draw.text((x+8, y+8), f"{clip['direction']} / {clip['action']}", fill='#edf0e7', font=font)
            image = clip['images'][frame_index]
            canvas.paste(image, (x+8, y+33), image)
        if images and canvas.tobytes() == images[-1].tobytes():
            durations[-1] += end-start
        else:
            images.append(canvas)
            durations.append(end-start)
            sample_indices.append({'start_ms': start, 'clip_frame_indices': indices})
    report = write_gif(images, durations, output/'actions-comparison.gif')
    # A matching still showing raised/guard poses; the GIF contains the full cycles.
    sample = max((i for i, item in enumerate(sample_indices) if item['start_ms'] <= 400), default=0)
    images[sample].save(output/'actions-comparison.png')
    report.update({'status': 'decoded_pass', 'art_approval': 'pending',
                   'policy': 'One 2000ms review cycle; idle loops; attack and defense play once then hold their final frame. Frame-change events are snapped to a20ms presentation grid; collisions merge.',
                   'event_grid_ms': 20,
                   'max_event_time_error_ms': max(abs(event['error_ms']) for event in quantized_events),
                   'minimum_decoded_duration_ms': min(report['decoded_durations_ms']),
                   'quantized_events': quantized_events,
                   'clips': [f"{clip['direction']}/{clip['action']}" for clip in clips],
                   'sample_indices': sample_indices})
    if report['minimum_decoded_duration_ms'] < 20 or report['max_event_time_error_ms'] > 10 or report['duration_ms'] != 2000:
        raise RuntimeError('Comparison GIF presentation timing failed')
    (output/'comparison-gif.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def export_sheet(sheet: Path, direction: str, output: Path, durations=None, offsets=None, layout=None, layout_base_dir=None):
    sheet = Path(sheet).resolve()
    output = Path(output).resolve()/direction
    durations = durations or DURATIONS
    offsets = offsets or {}
    layout_base_dir = Path(layout_base_dir).resolve() if layout_base_dir else sheet.parent
    if layout:
        if set(layout.get('cells', {})) != set(frame_names()):
            raise ValueError('Reviewed layout must define all 16 named cells exactly')
        scale = layout.get('uniform_scale')
        target_anchor = layout.get('target_foot_anchor', [128, 224])
        if not isinstance(scale, (int, float)) or not 0 < scale <= 4:
            raise ValueError('Reviewed layout requires a positive common uniform_scale <=4')
        if len(target_anchor) != 2 or any(not isinstance(v, (int, float)) for v in target_anchor):
            raise ValueError('target_foot_anchor must be [x,y]')
    else:
        target_anchor = [128, 224]
    if set(durations) != set(DURATIONS):
        raise ValueError('Durations must contain exactly idle, attack, defense')
    for action, expected in DURATIONS.items():
        if len(durations[action]) != len(expected) or any(not isinstance(n, int) or n <= 0 for n in durations[action]):
            raise ValueError('Invalid positive integer duration list for '+action)
    unknown_offsets = set(offsets)-set(frame_names())
    if unknown_offsets:
        raise ValueError('Unknown frame offsets: '+str(sorted(unknown_offsets)))
    with Image.open(sheet) as original:
        original.load()
        if not layout and original.width != original.height:
            raise ValueError('A square 4 x 4 sheet is required')
        if 'A' not in original.getbands() and 'transparency' not in original.info:
            raise ValueError('Source has no alpha; remove its background with the art tool before export')
        source = original.convert('RGBA')
    if source.getchannel('A').getextrema()[0] == 255:
        raise ValueError('Source is fully opaque; a real transparent source is required')
    source_cache = {sheet: source}
    source_hashes = {sheet: sha256(sheet)}
    source_scales = {sheet: layout['uniform_scale'] if layout else SIZE/(source.width/4)}
    cell = source.width/4
    # Resize the entire sheet once. This preserves one common scale even for
    # generated sources such as 1254px, whose cells have fractional boundaries.
    scaled_source = None if layout else (source if source.size == (1024, 1024) else source.resize((1024, 1024), Image.Resampling.LANCZOS))
    output.mkdir(parents=True, exist_ok=True)
    (output/'frames').mkdir(exist_ok=True)
    frames = {}
    atlas = Image.new('RGBA', (SIZE*4, SIZE*4))
    metadata = {'schema': 'warrior-sprite-export/1', 'direction': direction,
                'source': {'file': str(sheet), 'sha256': sha256(sheet), 'size': list(source.size), 'cell_size': cell},
                'uniform_cell_scale': layout['uniform_scale'] if layout else SIZE/cell, 'frame_size': [SIZE, SIZE],
                'background_removed': False, 'inbetween_generation': False,
                'art_approval': 'pending', 'atlas': 'atlas.png', 'frames': [], 'animations': {},
                'anchor_convention': 'top-left pixel origin; source foot anchors are explicitly reviewed image landmarks, not measured skeletal sockets',
                'target_anchor': target_anchor,
                'layout': layout,
                'source_scale_policy': 'Effective pixel scale = layout uniform_scale times per-source uniform_source_scale (resolution normalization, default1). Every frame from the same source file must share that effective scale.',
                'operations': ('explicit reviewed crop; shared-scale BICUBIC affine resample; integer placement from reviewed foot anchor; lossless packing' if layout else 'one whole-sheet LANCZOS rescale to1024; 256px grid crop; optional explicit integer translation; lossless packing')}
    quality = []
    index = 0
    for action in DURATIONS:
        names = []
        for local_frame, duration in enumerate(durations[action]):
            name = f'{action}_{local_frame:02d}'
            x, y = (index % 4)*cell, (index//4)*cell
            source_rect = [x, y, cell, cell]
            source_rect_rounded = [round(x), round(y), round(x+cell)-round(x), round(y+cell)-round(y)]
            source_anchor = None
            anchor_error = None
            base_placement = [0, 0]
            frame_source_path = sheet
            frame_source = source
            frame_scale = SIZE/cell
            source_normalization_scale = 1.0
            if layout:
                entry = layout['cells'][name]
                frame_scale = layout['uniform_scale']
                if 'source_file' in entry:
                    frame_source_path = (layout_base_dir/entry['source_file']).resolve()
                    source_normalization_scale = entry.get('uniform_source_scale', 1.0)
                    if not isinstance(source_normalization_scale, (int, float)) or not 0 < source_normalization_scale <= 4:
                        raise ValueError('Invalid source-specific uniform scale for '+name)
                    frame_scale = layout['uniform_scale']*source_normalization_scale
                    if frame_source_path not in source_cache:
                        with Image.open(frame_source_path) as extra:
                            extra.load()
                            if 'A' not in extra.getbands() and 'transparency' not in extra.info:
                                raise ValueError('Override source has no alpha: '+str(frame_source_path))
                            source_cache[frame_source_path] = extra.convert('RGBA')
                        if source_cache[frame_source_path].getchannel('A').getextrema()[0] == 255:
                            raise ValueError('Override source is fully opaque: '+str(frame_source_path))
                        source_hashes[frame_source_path] = sha256(frame_source_path)
                    frame_source = source_cache[frame_source_path]
                elif 'uniform_source_scale' in entry:
                    raise ValueError('Per-frame rescaling is forbidden; uniform_source_scale requires source_file: '+name)
                if frame_source_path in source_scales and source_scales[frame_source_path] != frame_scale:
                    raise ValueError('All frames from one source must share exactly one scale: '+str(frame_source_path))
                source_scales[frame_source_path] = frame_scale
                source_rect = entry.get('source_rect')
                source_anchor = entry.get('source_foot_anchor')
                if not isinstance(source_rect, list) or len(source_rect) != 4 or any(not isinstance(v, int) for v in source_rect):
                    raise ValueError('source_rect must have four integers for '+name)
                sx, sy, sw, sh = source_rect
                if min(sx, sy) < 0 or min(sw, sh) <= 0 or sx+sw > frame_source.width or sy+sh > frame_source.height:
                    raise ValueError('Source rect outside source image: '+name)
                if not isinstance(source_anchor, list) or len(source_anchor) != 2 or any(not isinstance(v, (int, float)) for v in source_anchor):
                    raise ValueError('source_foot_anchor must be local [x,y] for '+name)
                crop = frame_source.crop((sx, sy, sx+sw, sy+sh))
                source_rect_rounded = source_rect
                scale = frame_scale
                # An identical affine scale for every crop, even when crop widths
                # differ by one pixel. No per-frame bounding-box normalization.
                scaled = crop.transform((math.ceil(sw*scale), math.ceil(sh*scale)),
                    Image.Transform.AFFINE, (1/scale, 0, 0, 0, 1/scale, 0), Image.Resampling.BICUBIC)
                base_placement = [round(target_anchor[i]-source_anchor[i]*scale) for i in range(2)]
                anchor_error = [base_placement[i]+source_anchor[i]*scale-target_anchor[i] for i in range(2)]
                frame = Image.new('RGBA', (SIZE, SIZE))
                frame.paste(scaled, tuple(base_placement))
                placement_loss = {'alpha_sum_lost': alpha_sum(scaled)-alpha_sum(frame),
                                  'significant_alpha_ge16_pixels_lost': significant_count(scaled)-significant_count(frame)}
            else:
                sx, sy, sw, sh = source_rect_rounded
                crop = source.crop((sx, sy, sx+sw, sy+sh))
                cell_x, cell_y = (index % 4)*SIZE, (index//4)*SIZE
                frame = scaled_source.crop((cell_x, cell_y, cell_x+SIZE, cell_y+SIZE))
                placement_loss = {'alpha_sum_lost': 0, 'significant_alpha_ge16_pixels_lost': 0}
            source_crop_check = source_edge_check(crop)
            raw_alpha_sum = alpha_sum(frame)
            offset = offsets.get(name, [0, 0])
            if len(offset) != 2 or any(not isinstance(v, int) for v in offset):
                raise ValueError('Offsets must be [integer dx, integer dy]: '+name)
            if offset != [0, 0]:
                shifted = Image.new('RGBA', (SIZE, SIZE))
                shifted.paste(frame, tuple(offset))
                frame = shifted
                if alpha_sum(frame) != raw_alpha_sum:
                    raise ValueError('Offset would clip visible pixels: '+name)
            frames[name] = frame
            file = output/'frames'/f'{name}.png'
            frame.save(file)
            rect = [(index % 4)*SIZE, (index//4)*SIZE, SIZE, SIZE]
            atlas.paste(frame, (rect[0], rect[1]))
            item = {'name': name, 'action': action, 'index': index, 'local_frame': local_frame,
                    'file': f'frames/{name}.png', 'rect': rect, 'duration_ms': duration,
                    'source_rect': source_rect,
                    'source_file': str(frame_source_path),
                    'source_sha256': source_hashes[frame_source_path],
                    'uniform_source_scale': frame_scale,
                    'source_resolution_normalization': source_normalization_scale,
                    'effective_source_pixel_scale': frame_scale,
                    'source_rect_rounded': source_rect_rounded,
                    'source_foot_anchor_local': source_anchor,
                    'target_foot_anchor': target_anchor if layout else None,
                    'anchor_rounding_error_px': anchor_error,
                    'placement_from_source_crop_px': base_placement,
                    'translation_px': offset,
                    'sha256': sha256(file)}
            metadata['frames'].append(item)
            frame_quality = check_image(frame, name)
            frame_quality['source_crop_boundary'] = source_crop_check
            frame_quality['placement_clipping'] = placement_loss
            if source_crop_check['edge_significant_alpha_ge16_pixels']:
                frame_quality['errors'].append('source_crop_touches_significant_art')
            if placement_loss['alpha_sum_lost']:
                frame_quality['errors'].append('output_placement_clipped_alpha')
            quality.append(frame_quality)
            names.append(name)
            index += 1
        metadata['animations'][action] = {'frames': names, 'duration_ms': sum(durations[action]),
                                          'durations_ms': durations[action], 'loop': action == 'idle'}
        images = [frames[name] for name in names]
        # Preview repeats every clip for review. Game metadata keeps attack and guard one-shot.
        images[0].save(output/f'preview-{action}.webp', save_all=True, append_images=images[1:],
                       duration=durations[action], loop=0, lossless=True, exact=True, method=6)
        images[0].save(output/f'preview-{action}.apng', format='PNG', save_all=True,
                       append_images=images[1:], duration=durations[action], loop=0,
                       disposal=0, blend=0)
        metadata['animations'][action]['gif'] = write_gif(images, durations[action], output/f'preview-{action}.gif')
    metadata['sources'] = [{'file': str(path), 'sha256': source_hashes[path],
                            'dimensions': list(source_cache[path].size),
                            'uniform_scale': source_scales[path]}
                           for path in source_cache]
    atlas.save(output/'atlas.png')
    metadata['atlas_sha256'] = sha256(output/'atlas.png')
    (output/'atlas.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    compose_contact(frames, output, direction)
    # Decode persisted exports and verify that atlas cells reconstruct exact PNG RGBA.
    decoded = []
    with Image.open(output/'atlas.png') as packed:
        packed.load()
        for item in metadata['frames']:
            x, y, w, h = item['rect']
            with Image.open(output/item['file']) as image:
                image.load()
                if image.tobytes() != packed.crop((x, y, x+w, y+h)).tobytes():
                    raise RuntimeError('Atlas reconstruction mismatch: '+item['name'])
    for path in sorted(output.glob('preview-*.*')):
        with Image.open(path) as image:
            count = 0
            decoded_durations = []
            for frame in ImageSequence.Iterator(image):
                frame.load()
                count += 1
                decoded_durations.append(frame.info.get('duration', 0))
            decoded.append({'file': path.name, 'decoded_frames': count, 'bytes': path.stat().st_size,
                            'durations_ms': decoded_durations, 'duration_ms': sum(decoded_durations)})
    errors = [{'frame': item['name'], 'error': err} for item in quality for err in item['errors']]
    report = {'status': 'technical_pass' if not errors else 'technical_failed',
              'art_approval': 'pending', 'source_sha256': metadata['source']['sha256'],
              'frames': quality, 'atlas_exact_reconstruction': True, 'decoded_animations': decoded,
              'errors': errors,
              'not_automatically_verified': ['hand anatomy', 'identity/clothing continuity',
                  'weapon grip', 'actual foot contact', 'agreement with guide poses', 'commercial art quality']}
    (output/'technical-qa.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return metadata, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path)
    parser.add_argument('--direction', choices=['front_left', 'front_right'])
    parser.add_argument('--comparison', action='store_true', help='Build one six-panel GIF from both persisted direction exports')
    parser.add_argument('--output', type=Path, default=ROOT/'exports/warrior_v002')
    parser.add_argument('--durations-json', type=Path, help='JSON object mapping idle/attack/defense to millisecond lists')
    parser.add_argument('--offsets-json', type=Path, help='Explicit frame-name -> [dx,dy] in output pixels; rejected if clipping')
    parser.add_argument('--layout-json', type=Path, help='Reviewed source rectangles + local foot anchors, one uniform scale, common target foot anchor')
    args = parser.parse_args()
    if args.comparison:
        report = export_comparison(args.output)
        print(json.dumps({key: report[key] for key in ['file', 'status', 'decoded_frames', 'duration_ms', 'bytes']}))
        return 0
    if not args.sheet or not args.direction:
        parser.error('--sheet and --direction are required unless --comparison is used')
    metadata, report = export_sheet(args.sheet, args.direction, args.output,
                                    load_json(args.durations_json), load_json(args.offsets_json), load_json(args.layout_json),
                                    args.layout_json.parent if args.layout_json else None)
    print(json.dumps({'status': report['status'], 'direction': args.direction,
                      'frames': len(metadata['frames']), 'errors': report['errors'],
                      'output': str(args.output/args.direction)}, ensure_ascii=False))
    return 0 if report['status'] == 'technical_pass' else 2


if __name__ == '__main__':
    raise SystemExit(main())
