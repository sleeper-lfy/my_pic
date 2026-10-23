"""Persisted sprite-package round trip, with directional/alpha asymmetry."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from warrior_export import export_sheet, frame_names


class SpriteRoundTrip(unittest.TestCase):
    def test_source_resolution_factor_multiplies_common_scale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = Image.new('RGBA', (256, 256))
            ImageDraw.Draw(source).rectangle((20, 20, 119, 119), fill=(70, 100, 130, 255))
            source.save(root/'source.png')
            source.save(root/'correction.png')
            layout = {'uniform_scale': 0.6, 'target_foot_anchor': [128, 224],
                      'cells': {name: {'source_file': 'correction.png', 'uniform_source_scale': 0.5,
                                       'source_rect': [0, 0, 150, 150],
                                       'source_foot_anchor': [75, 130]} for name in frame_names()}}
            metadata, report = export_sheet(root/'source.png', 'front_left', root/'out', layout=layout)
            self.assertEqual(report['status'], 'technical_pass')
            self.assertAlmostEqual(metadata['frames'][0]['effective_source_pixel_scale'], 0.3)
            bbox = report['frames'][0]['bbox_alpha_nonzero']
            self.assertEqual(bbox[2]-bbox[0], 30)
            layout['cells']['idle_01']['uniform_source_scale'] = 0.6
            with self.assertRaisesRegex(ValueError, 'All frames from one source'):
                export_sheet(root/'source.png', 'front_left', root/'out', layout=layout)

    def test_padding_does_not_hide_significant_source_crop_boundary_risk(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = Image.new('RGBA', (256, 256))
            ImageDraw.Draw(source).rectangle((20, 20, 119, 119), fill=(70, 100, 130, 255))
            source.save(root/'source.png')
            layout = {'uniform_scale': 1.0, 'target_foot_anchor': [128, 224],
                      'cells': {name: {'source_rect': [20, 20, 100, 100],
                                       'source_foot_anchor': [50, 100]} for name in frame_names()}}
            metadata, report = export_sheet(root/'source.png', 'front_left', root/'out', layout=layout)
            self.assertEqual(report['status'], 'technical_failed')
            for frame in report['frames']:
                self.assertGreaterEqual(frame['safe_margin_px'], 8)
                self.assertEqual(frame['placement_clipping']['alpha_sum_lost'], 0)
                self.assertIn('source_crop_touches_significant_art', frame['errors'])
            self.assertEqual(metadata['frames'][0]['placement_from_source_crop_px'], [78, 124])

    def test_persisted_export_keeps_order_alpha_timing_and_lossless_atlas(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = Image.new('RGBA', (1024, 1024))
            draw = ImageDraw.Draw(source)
            for i in range(16):
                x, y = (i % 4)*256, (i//4)*256
                draw.polygon([(x+30, y+35), (x+190, y+70), (x+80, y+220)],
                             fill=(i*15, 250-i*12, i*9, 100+i*10))
            source.save(root/'source.png')
            metadata, report = export_sheet(root/'source.png', 'front_left', root/'out')
            self.assertEqual(report['status'], 'technical_pass')
            self.assertTrue(report['atlas_exact_reconstruction'])
            self.assertEqual(metadata['animations']['attack']['duration_ms'], 870)
            self.assertFalse(metadata['animations']['attack']['loop'])
            self.assertTrue(metadata['animations']['idle']['loop'])
            self.assertEqual([f['name'] for f in metadata['frames']][4:6], ['attack_00', 'attack_01'])
            result = root/'out/front_left'
            with Image.open(result/'atlas.png') as atlas:
                self.assertEqual(atlas.tobytes(), source.tobytes())
            with Image.open(result/'frames/defense_03.png') as frame:
                self.assertEqual(frame.getpixel((80, 90)), (225, 70, 135, 250))
                self.assertEqual(frame.getpixel((0, 0))[3], 0)
            with Image.open(result/'preview-attack.apng') as animation:
                self.assertEqual(animation.n_frames, 8)
                times = []
                for i in range(animation.n_frames):
                    animation.seek(i)
                    times.append(animation.info['duration'])
                self.assertEqual(times, [100, 140, 120, 60, 70, 100, 120, 160])
            self.assertEqual(json.loads((result/'atlas.json').read_text())['art_approval'], 'pending')


if __name__ == '__main__':
    unittest.main()
