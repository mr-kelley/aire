import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from aire.config import load_config, version_satisfies  # noqa: E402


class TestVersionSatisfies(unittest.TestCase):
    def test_equal(self):
        self.assertTrue(version_satisfies("0.1.0", "0.1.0"))

    def test_newer(self):
        self.assertTrue(version_satisfies("0.2.0", "0.1.0"))
        self.assertTrue(version_satisfies("1.0.0", "0.9.9"))

    def test_older(self):
        self.assertFalse(version_satisfies("0.1.0", "0.2.0"))
        self.assertFalse(version_satisfies("0.9.9", "1.0.0"))

    def test_uneven_lengths(self):
        self.assertTrue(version_satisfies("0.1.0", "0.1"))
        self.assertTrue(version_satisfies("0.1", "0.1.0"))


class TestLoadConfig(unittest.TestCase):
    def test_absent(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = load_config(Path(d))
            self.assertFalse(cfg.present)
            self.assertIsNone(cfg.profile)
            self.assertIsNone(cfg.parse_error)

    def test_valid(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".aire").mkdir()
            (Path(d) / ".aire" / "config.toml").write_text(
                'aire_version_min = "0.1.0"\nprofile = "B"\nlocal_model_floor = 8192\n'
            )
            cfg = load_config(Path(d))
            self.assertTrue(cfg.present)
            self.assertEqual(cfg.aire_version_min, "0.1.0")
            self.assertEqual(cfg.profile, "B")
            self.assertEqual(cfg.local_model_floor, 8192)
            self.assertIsNone(cfg.parse_error)

    def test_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".aire").mkdir()
            (Path(d) / ".aire" / "config.toml").write_text("[[[ not valid toml = =")
            cfg = load_config(Path(d))
            self.assertTrue(cfg.present)
            self.assertIsNotNone(cfg.parse_error)


if __name__ == "__main__":
    unittest.main()
