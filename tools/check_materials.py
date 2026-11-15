"""Verify bundled file hashes and compare rerun results with paper references."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ("title_case", "semantic_clustering", "sms")
RUN_METADATA = {"python", "numpy", "script_sha256"}


def compare(expected, actual, location):
    if isinstance(expected, dict):
        assert isinstance(actual, dict), location
        keys = set(expected) - RUN_METADATA
        assert keys == set(actual) - RUN_METADATA, f"{location}: keys differ"
        for key in sorted(keys):
            compare(expected[key], actual[key], f"{location}/{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(expected) == len(actual), location
        for i, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, f"{location}/{i}")
    elif isinstance(expected, bool) or expected is None:
        assert expected is actual, f"{location}: {expected!r} != {actual!r}"
    elif isinstance(expected, (int, float)):
        assert isinstance(actual, (int, float)) and not isinstance(actual, bool), location
        assert math.isclose(expected, actual, rel_tol=1e-10, abs_tol=1e-12), f"{location}: {expected!r} != {actual!r}"
    else:
        assert expected == actual, f"{location}: {expected!r} != {actual!r}"


def compare_csv(expected_path, actual_path):
    with expected_path.open(encoding="utf-8-sig", newline="") as f:
        expected = list(csv.DictReader(f))
    with actual_path.open(encoding="utf-8-sig", newline="") as f:
        actual = list(csv.DictReader(f))
    assert len(expected) == len(actual), str(actual_path)
    for i, (left, right) in enumerate(zip(expected, actual), 1):
        assert left.keys() == right.keys(), str(actual_path)
        for key, value in left.items():
            other = right[key]
            if value == other:
                continue
            try:
                a, b = float(value), float(other)
            except (TypeError, ValueError):
                raise AssertionError(f"{actual_path.name}:{i}/{key}: {value!r} != {other!r}") from None
            assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12), f"{actual_path.name}:{i}/{key}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", action="store_true", help="Also compare all three rerun cases with reference results")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "reproduction/outputs")
    args = parser.parse_args()
    verified = []
    for line in (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"File checksum differs: {relative}"
        verified.append(relative)
    assert verified and len(verified) == len(set(verified)), "Missing or duplicate checksum entries"
    compared = []
    if args.results:
        for case in CASES:
            reference = ROOT / "reproduction/reference" / case
            generated = args.results_dir / case
            compare(json.loads((reference / "results.json").read_text(encoding="utf-8")),
                    json.loads((generated / "results.json").read_text(encoding="utf-8")), case)
            compare_csv(reference / "summary.csv", generated / "summary.csv")
            compared.append(case)
        compare_csv(ROOT / "reproduction/data/semantic_clustering/records.csv",
                    args.results_dir / "semantic_clustering/records.csv")
    print(json.dumps({"verified_files": len(verified), "compared_cases": compared}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
