import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from quality import check_frames


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'frame.png'
        image=Image.new('RGBA',(256,256)); ImageDraw.Draw(image).rectangle((40,40,200,232),fill='white'); image.save(self.path)

    def test_valid_rgba(self):
        self.assertEqual(check_frames([self.path],[100])['status'],'passed')

    def test_blank_and_missing_file_rejected(self):
        Image.new('RGBA',(256,256)).save(self.path)
        self.assertIn('0:blank',check_frames([self.path],[100])['errors'])
        self.path.unlink()
        self.assertEqual(check_frames([self.path],[100])['status'],'failed')

    def test_missing_alpha_rejected(self):
        Image.new('RGB',(256,256)).save(self.path)
        self.assertIn('0:missing_rgba',check_frames([self.path],[100])['errors'])

    def test_clipping_timing_and_anchor_drift(self):
        image=Image.new('RGBA',(256,256)); ImageDraw.Draw(image).rectangle((0,40,200,232),fill='white'); image.save(self.path)
        q=check_frames([self.path,self.path],[0,float('nan')],anchors=[[128,232],[132,232]])
        self.assertIn('0:edge_clipping_risk',q['errors'])
        self.assertIn('invalid_duration',q['errors'])
        self.assertIn('foot_anchor_drift_over_1px',q['errors'])

    def test_zero_frames_and_count_mismatch(self):
        self.assertIn('zero_frames',check_frames([],[])['errors'])
        self.assertIn('timing_count_mismatch',check_frames([self.path],[])['errors'])

if __name__=='__main__': unittest.main()
