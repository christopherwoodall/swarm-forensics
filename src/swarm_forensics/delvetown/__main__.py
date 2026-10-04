"""Run the private public-record pilot through Make targets."""

import argparse
import json
import shutil
import sys
from pathlib import Path

from .collector import collect, validate_cohort
from .records import SourceError
from .report import audit, inspect
from .transport import Reader

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "delvetown"


def destination(value):
    """Require an ignored private source directory without symlink escapes."""
    path = Path(value).absolute()
    if path.is_symlink() or RAW.is_symlink():
        raise SourceError("source path must not be a symlink")
    try:
        path.resolve().relative_to(RAW.resolve())
    except ValueError:
        raise SourceError("source output must remain under data/raw/delvetown") from None
    return path


def main(argv=None):
    """Emit content-free receipts and preserve partial-coverage diagnostics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("collect", "audit", "inspect"))
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--cohort", type=Path)
    args = parser.parse_args(argv)
    try:
        dest = destination(args.dest)
        if args.operation == "inspect":
            print(json.dumps(inspect(dest), sort_keys=True, ensure_ascii=False))
            return 0
        if args.operation == "collect":
            if args.cohort is None:
                raise SourceError("collection requires the frozen cohort file")
            cohort_path = destination(args.cohort)
            if cohort_path.stat().st_size > 200_000:
                raise SourceError("cohort metadata exceeds size limit")
            cohort = json.loads(cohort_path.read_text())["actors"]
            validate_cohort(cohort)
            if shutil.disk_usage(cohort_path.parent).free < 100_000_000:
                raise SourceError("insufficient disk space for bounded collection")
            reader = Reader([actor["did"] for actor in cohort])
            collect(cohort, dest, reader=reader)
        receipt = audit(dest)
        receipt["scope_complete"] = (receipt["accounts_complete"] == receipt["cohort_accounts"]
                                     and receipt["stop_reason"] == "finished")
        receipt["directory"] = str(dest)
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (SourceError, OSError, ValueError, KeyError):
        print("Delvetown operation failed. Preserve any partial archive and inspect its coverage.",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
