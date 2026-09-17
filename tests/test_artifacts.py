import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from california_seismic.artifacts import publish_artifacts


class ArtifactPublicationTests(unittest.TestCase):
    def test_failed_replacement_removes_completion_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            staging = root / "staging"
            staging.mkdir()
            staged = staging / "dataset.parquet"
            target = root / "dataset.parquet"
            manifest = root / "manifest.json"
            staged.write_bytes(b"new")
            target.write_bytes(b"old")
            manifest.write_text('{"status": "complete"}\n', encoding="utf-8")

            with patch(
                "california_seismic.artifacts.os.replace",
                side_effect=OSError("simulated replacement failure"),
            ):
                with self.assertRaisesRegex(OSError, "simulated replacement failure"):
                    publish_artifacts(
                        [(staged, target)],
                        manifest,
                        {"status": "complete", "artifacts": {}},
                        staging,
                    )

            self.assertFalse(manifest.exists())
            self.assertEqual(target.read_bytes(), b"old")


if __name__ == "__main__":
    unittest.main()
