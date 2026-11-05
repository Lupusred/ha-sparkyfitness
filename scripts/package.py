"""Create a deterministic installation ZIP without caches, keys or test files."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "custom_components" / "sparkyfitness"
ALLOWED = {".py", ".json", ".yaml", ".png", ".md", ".upstream"}


def package(destination=ROOT / "dist" / "sparkyfitness.zip"):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if path.is_file() and path.suffix in ALLOWED and "__pycache__" not in path.parts:
                info = ZipInfo(
                    str(Path("sparkyfitness") / path.relative_to(SOURCE)), (2026, 1, 1, 0, 0, 0)
                )
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
    return destination


if __name__ == "__main__":
    print(package())
