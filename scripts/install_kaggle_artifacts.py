"""Extract the Kaggle export ZIP into artifacts/kaggle/ and verify every deep checkpoint loads.

Usage: python scripts/install_kaggle_artifacts.py [artifacts/incoming/northgate_submission_artifacts.zip]

* Refuses any archive member that is a test split, or that would escape artifacts/kaggle/.
* Loads each *_best.pt with northgate.models.deep (strict state-dict, feature order checked
  against the v1 pipeline, preprocessing statistics required) and prints the result.
* Never trains anything. artifacts/ is git-ignored.
"""
from __future__ import annotations
import json, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import northgate  # noqa: F401  (sets OMP_NUM_THREADS before torch loads)
from northgate import features as F
from northgate.models import deep

DEST = ROOT / "artifacts" / "kaggle"


def main(zip_path: Path) -> int:
    if not zip_path.exists():
        print(f"Not found: {zip_path}"); return 1
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        bad = [n for n in names if n.endswith("test.csv") or ".." in Path(n).parts or Path(n).is_absolute()]
        if bad:
            print("Refusing archive; disallowed members:", bad); return 1
        z.extractall(DEST)
    print(f"Extracted {len(names)} files to {DEST.relative_to(ROOT)}")
    status = {}
    for p in sorted((DEST / "models" / "deep").glob("*.pt")):
        try:
            m = deep.load(p, expected_features=F.FEATURES)
            status[p.name] = f"OK  {m.name}: seq {m.seq}, hidden {m.hidden}, {len(m.features)} features, {len(m.tickers)} tickers"
        except Exception as e:
            status[p.name] = f"FAIL {type(e).__name__}: {e}"
    for k, v in status.items():
        print(f"  {k:<22} {v}")
    (DEST / "LOAD_CHECK.json").write_text(json.dumps(status, indent=2))
    return 0 if status and all(v.startswith("OK") for v in status.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifacts/incoming/northgate_submission_artifacts.zip"))
