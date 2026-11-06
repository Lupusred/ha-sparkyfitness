"""Release package, official artwork and service metadata checks."""

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import yaml

from custom_components.sparkyfitness.services import SCHEMAS
from scripts.package import package

ROOT = Path(__file__).resolve().parents[1]


def test_package_contains_only_installation_files(tmp_path):
    first = package(tmp_path / "first.zip").read_bytes()
    second = package(tmp_path / "second.zip").read_bytes()
    assert first == second
    with ZipFile(tmp_path / "first.zip") as archive:
        names = archive.namelist()
        assert "sparkyfitness/manifest.json" in names
        assert "sparkyfitness/services.yaml" in names
        assert "sparkyfitness/brand/LICENSE.upstream" in names
        assert not any("__pycache__" in n or n.endswith(".pyc") or "/tests/" in n for n in names)
        assert archive.testzip() is None


def test_official_artwork_integrity():
    expected = {
        "icon.png": "47bfa43deb5d452913c51378450c4275b81dec43b6e693a02a3e3f6e3290aa2d",
        "icon@2x.png": "f67223da57dfa7da25e3ebe394430f934f19f51cf8ca59e8440b809029fe701b",
    }
    for name, digest in expected.items():
        assert (
            hashlib.sha256(
                (ROOT / "custom_components/sparkyfitness/brand" / name).read_bytes()
            ).hexdigest()
            == digest
        )


def test_service_metadata_matches_schema_and_translations():
    component = ROOT / "custom_components/sparkyfitness"
    metadata = yaml.safe_load((component / "services.yaml").read_text())
    assert set(metadata) == set(SCHEMAS)
    for lang in ("en", "de"):
        translated = json.loads((component / "translations" / f"{lang}.json").read_text())
        assert set(translated["services"]) == set(SCHEMAS)
        for name, schema in SCHEMAS.items():
            fields = {str(k) for k in schema.schema}
            assert (
                fields
                == set(metadata[name]["fields"])
                == set(translated["services"][name]["fields"])
            )
