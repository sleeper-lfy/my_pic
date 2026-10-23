"""Technical image checks; these do not confer artistic approval."""
from pathlib import Path
import math
from PIL import Image


def check_frames(paths, durations, size=(256, 256), anchors=None, padding=8):
    errors, warnings, bounds = [], [], []
    if not paths:
        errors.append('zero_frames')
    if len(paths) != len(durations):
        errors.append('timing_count_mismatch')
    if any(not isinstance(t, (int, float)) or not math.isfinite(t) or t <= 0 for t in durations):
        errors.append('invalid_duration')
    for index, path in enumerate(paths):
        try:
            with Image.open(path) as image:
                if image.size != size:
                    errors.append(f'{index}:wrong_size')
                if image.mode != 'RGBA':
                    errors.append(f'{index}:missing_rgba')
                    continue
                alpha = image.getchannel('A')
                bbox = alpha.getbbox()
                bounds.append(bbox)
                if not bbox:
                    errors.append(f'{index}:blank')
                    continue
                if alpha.getextrema()[0] == 255:
                    errors.append(f'{index}:opaque_background')
                if bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= size[0] or bbox[3] >= size[1]:
                    errors.append(f'{index}:edge_clipping_risk')
                if min(bbox[0], bbox[1], size[0]-bbox[2], size[1]-bbox[3]) < padding:
                    warnings.append(f'{index}:padding_below_{padding}px')
        except (OSError, ValueError) as exc:
            errors.append(f'{index}:unreadable:{type(exc).__name__}')
    if anchors is not None:
        if len(anchors) != len(paths) or any(len(a) != 2 or not all(math.isfinite(v) for v in a) for a in anchors):
            errors.append('invalid_anchors')
        elif anchors and max(math.dist(a, anchors[0]) for a in anchors) > 1:
            errors.append('foot_anchor_drift_over_1px')
    return {'status': 'failed' if errors else 'passed', 'frames_checked': len(paths),
            'errors': errors, 'warnings': warnings, 'bounds': bounds,
            'scope': 'file format, alpha, bounds, timing, optional supplied anchors; no visual approval'}
