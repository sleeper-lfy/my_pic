import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from factory import fingerprint, cache_valid, digest


class CacheTests(unittest.TestCase):
    def test_weapon_change_invalidates_only_dependent_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);body=root/'body';a=root/'hammer_a';b=root/'hammer_b'
            for p in [body,a,b]:p.write_text(p.name)
            old_a=fingerprint([body,a]);old_b=fingerprint([body,b])
            a.write_text('revised hammer design')
            self.assertNotEqual(old_a,fingerprint([body,a]))
            self.assertEqual(old_b,fingerprint([body,b]))
            body.write_text('new torso')
            self.assertNotEqual(old_b,fingerprint([body,b]))

    def test_missing_or_corrupted_output_is_not_a_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'frame.png';p.write_bytes(b'original')
            entry={'input_hash':'key','outputs':{'frame.png':digest(p)}}
            self.assertTrue(cache_valid(entry,'key',root))
            p.write_bytes(b'corrupt');self.assertFalse(cache_valid(entry,'key',root))
            p.unlink();self.assertFalse(cache_valid(entry,'key',root))
            self.assertFalse(cache_valid({},'key',root))

if __name__=='__main__':unittest.main()
