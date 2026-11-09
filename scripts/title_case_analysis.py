"""Reanalyse frozen title-classification predictions; no model inference or training."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/title_case"
MODELS = ("nb", "word2vec", "bert", "systemone", "tev1-nf4-zero-shot", "tev1_finetuned")
PROBABILITY_MODELS = ("systemone", "tev1-nf4-zero-shot", "tev1_finetuned")
COMMIT = "1b0ce28d265454680b5b383bbb7ff0929dca688b"
REPOSITORY = "https://github.com/LeoAndJellyfish/paper-title-error-classification"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(title):
    return " ".join(unicodedata.normalize("NFKC", title).casefold().split())


def import_case(source):
    """Align six published outputs and verify their archived dataset and metrics."""
    records = [json.loads(line) for line in (source / "materials/dataset/test.jsonl").read_text(encoding="utf-8").splitlines()]
    ids = [row["sample_id"] for row in records]
    if len(ids) != 1000 or len(set(ids)) != 1000:
        raise ValueError("Expected the fixed 1,000-record test set")
    files = ["materials/dataset/test.jsonl", "materials/dataset/manifest.json",
             "materials/dataset/processed-dataset.zip", "materials/results/metrics.json",
             "materials/results/matched-nf4-control.json", "configs/baseline.json",
             "configs/tev1_finetune.json", "configs/systemone.json"]
    predictions = {}
    for name in MODELS:
        rel = f"materials/results/predictions/{name}.csv"
        files.append(rel)
        with (source / rel).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != 1000 or {row["sample_id"] for row in rows} != set(ids):
            raise ValueError(f"Prediction alignment failed: {name}")
        predictions[name] = {row["sample_id"]: row for row in rows}
    merged = []
    title_groups = {}
    for record in records:
        if identity(record["title_raw"]) != record["title_identity"]:
            raise ValueError("Title identity mismatch")
        group = title_groups.setdefault(record["title_identity"], len(title_groups) + 1)
        row = {"title_identity": group, "label": record["label"], "empty_title": int(record["empty_title"])}
        for name in MODELS:
            item = predictions[name][record["sample_id"]]
            if int(item["true_label"]) != record["label"]:
                raise ValueError("Reference labels differ between models")
            if record["empty_title"] and (item["prediction_origin"] != "empty_title_rule" or int(item["predicted_label"]) != 1):
                raise ValueError("Empty-title rule mismatch")
            for key in ("predicted_label", "score", "score_type"):
                row[f"{name}_{key}"] = item[key]
        merged.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(merged[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(merged)

    dataset = read_json(source / "materials/dataset/manifest.json")
    sets = {"test": {row["title_identity"] for row in records}}
    partitions = {}
    with zipfile.ZipFile(source / "materials/dataset/processed-dataset.zip") as archive:
        for name in ("train", "validation", "test"):
            content = archive.read(name + ".jsonl")
            if hashlib.sha256(content).hexdigest() != dataset["artifacts_sha256"][name + ".jsonl"]:
                raise ValueError("Dataset archive hash mismatch")
            rows = [json.loads(line) for line in content.splitlines()]
            sets[name] = {row["title_identity"] for row in rows}
            partitions[name] = {"n": len(rows), "unique_titles": len(sets[name]),
                                "labels": dict(Counter(row["label"] for row in rows))}
            if len(rows) != dataset["partitions"][name]["total"]:
                raise ValueError("Partition count mismatch")
    overlaps = {f"{a}_{b}": len(sets[a] & sets[b]) for a, b in (("train", "validation"), ("train", "test"), ("validation", "test"))}
    if any(overlaps.values()):
        raise ValueError("Normalized titles overlap between partitions")

    expected = read_json(source / "materials/results/metrics.json")
    expected["tev1-nf4-zero-shot"] = {"metrics": read_json(source / "materials/results/matched-nf4-control.json")}
    run_root = source / "materials/results/runs"
    q4_run = "systemone-tev1-20261004-full-v1"
    nf4_run = "tev1-qlora-20261004-full-v1"
    for run in (q4_run, nf4_run):
        files.extend(f"materials/results/runs/{run}/{name}.json" for name in ("config", "model", "manifest", "diagnostics"))
    files.extend(f"materials/results/runs/{nf4_run}/{name}.json" for name in ("selection", "explanation"))
    write_json(OUT / "provenance.json", {
        "source_repository": REPOSITORY, "source_commit": COMMIT, "source_date": "2026-10-06",
        "source_sha256": {rel: digest(source / rel) for rel in files},
        "dataset_manifest": dataset, "independent_archive_audit": {"partitions": partitions, "identity_overlaps": overlaps},
        "baseline_config": read_json(source / "configs/baseline.json"),
        "decision_config": read_json(source / "configs/systemone.json"),
        "finetune_config": read_json(source / "configs/tev1_finetune.json"),
        "q4_model": read_json(run_root / q4_run / "model.json"),
        "q4_diagnostics": read_json(run_root / q4_run / "diagnostics.json"),
        "nf4_model": read_json(run_root / nf4_run / "model.json"),
        "nf4_selection": read_json(run_root / nf4_run / "selection.json"),
        "nf4_run_timing": {key: read_json(run_root / nf4_run / "manifest.json")[key]
                           for key in ("started_at", "completed_at", "elapsed_seconds", "elapsed_scope")},
        "expected_test_metrics": {name: expected[name]["metrics"]["test"] for name in MODELS},
        "expected_probability_metrics": {name: expected[name]["metrics"]["probability"]["nonempty"] for name in PROBABILITY_MODELS},
        "merged_predictions_sha256": digest(OUT / "predictions.csv"),
        "merged_predictions_format": "The title_identity column contains group numbers assigned in order of first appearance.",
        "new_analysis": "metrics recomputation, conditional paired cluster bootstrap and error-cost comparison; no inference or training",
    })


def metrics(cm):
    tn, fp, fn, tp = np.moveaxis(np.asarray(cm, dtype=float), -1, 0)
    return {"accuracy": (tn + tp) / (tn + fp + fn + tp),
            "macro_f1": (2 * tn / (2 * tn + fp + fn) + 2 * tp / (2 * tp + fp + fn)) / 2,
            "invalid_precision": tp / (tp + fp), "invalid_recall": tp / (tp + fn)}


def probability_metrics(y, p):
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("Invalid probability")
    bins = []
    ece = 0.0
    bin_index = np.minimum((p * 10).astype(int), 9)
    for k in range(10):
        mask = bin_index == k
        n = int(mask.sum())
        mean = float(p[mask].mean()) if n else None
        observed = float(y[mask].mean()) if n else None
        if n:
            ece += n / len(y) * abs(mean - observed)
        bins.append({"lower": k / 10, "upper": (k + 1) / 10, "n": n,
                     "mean_probability": mean, "observed_frequency": observed})
    clipped = np.clip(p, 1e-15, 1 - 1e-15)
    return {"n": len(y), "brier_score": float(np.mean((p - y) ** 2)),
            "log_loss": float(-np.mean(y * np.log(clipped) + (1 - y) * np.log1p(-clipped))),
            "ece": ece, "bins": bins}


def analyse(repetitions, seed):
    with (OUT / "predictions.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    provenance = read_json(OUT / "provenance.json")
    if digest(OUT / "predictions.csv") != provenance["merged_predictions_sha256"]:
        raise ValueError("Frozen predictions changed")
    y = np.asarray([int(row["label"]) for row in rows])
    empty = np.asarray([bool(int(row["empty_title"])) for row in rows])
    pred = np.asarray([[int(row[f"{name}_predicted_label"]) for name in MODELS] for row in rows])
    summaries, probabilities = {}, {}
    for j, name in enumerate(MODELS):
        summaries[name] = {}
        for scope, mask in (("all", np.ones(len(rows), dtype=bool)), ("nonempty", ~empty)):
            cm = np.bincount(y[mask] * 2 + pred[mask, j], minlength=4)
            computed = {key: float(value) for key, value in metrics(cm).items()}
            reference = provenance["expected_test_metrics"][name][scope]
            if cm.reshape(2, 2).tolist() != reference["confusion_matrix"]:
                raise ValueError("Archived confusion matrix mismatch")
            if any(abs(computed[key] - reference[key]) > 1e-12 for key in ("accuracy", "macro_f1")):
                raise ValueError("Archived metric mismatch")
            summaries[name][scope] = {"n": int(mask.sum()), "confusion_matrix": cm.reshape(2, 2).tolist(), **computed}
        if name in PROBABILITY_MODELS:
            p = np.asarray([float(row[f"{name}_score"]) for row in rows if not int(row["empty_title"])])
            if np.any((p > 0.5).astype(int) != pred[~empty, j]):
                raise ValueError("Decision/probability mismatch")
            probabilities[name] = probability_metrics(y[~empty], p)
            reference = provenance["expected_probability_metrics"][name]
            if any(abs(probabilities[name][key] - reference[key]) > 1e-12 for key in ("brier_score", "log_loss", "ece")):
                raise ValueError("Archived probability metric mismatch")

    # Resample title groups within each reference class; all methods share each draw.
    groups = {}
    for i, row in enumerate(rows):
        if not empty[i]:
            groups.setdefault((int(y[i]), row["title_identity"]), []).append(i)
    tensors = {}
    for label in (0, 1):
        values = []
        for (group_label, _), indices in groups.items():
            if group_label == label:
                values.append([np.bincount(y[indices] * 2 + pred[indices, j], minlength=4) for j in range(len(MODELS))])
        tensors[label] = np.asarray(values).reshape(len(values), -1)
    rng = np.random.default_rng(seed)
    bootstrap_cm = np.zeros((repetitions, len(MODELS), 4), dtype=np.int64)
    for label, tensor in tensors.items():
        count = len(tensor)
        for start in range(0, repetitions, 1000):
            n = min(1000, repetitions - start)
            weights = rng.multinomial(count, np.full(count, 1 / count), size=n)
            bootstrap_cm[start:start + n] += (weights @ tensor).reshape(n, len(MODELS), 4)
    bootstrap_cm[:, :, 3] += int(empty.sum())  # The common 24-row rule is held fixed.
    boot = metrics(bootstrap_cm)
    comparisons = {}
    new = MODELS.index("tev1_finetuned")
    for old_name in ("tev1-nf4-zero-shot", "bert"):
        old = MODELS.index(old_name)
        old_correct, new_correct = pred[:, old] == y, pred[:, new] == y
        differences = {}
        for key in ("accuracy", "macro_f1"):
            delta = boot[key][:, new] - boot[key][:, old]
            differences[key] = {"difference": summaries["tev1_finetuned"]["all"][key] - summaries[old_name]["all"][key],
                                "percentile_95_interval": np.quantile(delta, [0.025, 0.975]).tolist()}
        comparisons[old_name] = {"new_model": "tev1_finetuned", "differences": differences,
                                "corrected": int((~old_correct & new_correct).sum()),
                                "introduced_errors": int((old_correct & ~new_correct).sum()),
                                "both_correct": int((old_correct & new_correct).sum()),
                                "both_wrong": int((~old_correct & ~new_correct).sum())}
    results = {"study_date": "2026-10-06", "python": platform.python_version(), "numpy": np.__version__,
               "source_commit": COMMIT, "models": summaries, "probability": probabilities,
               "bootstrap": {"repetitions": repetitions, "seed": seed, "unit": "normalized nonempty title group",
                             "stratification": "reference class", "groups_by_class": {str(k): len(v) for k, v in tensors.items()},
                             "fixed_empty_rule_rows": int(empty.sum()), "interval": "paired percentile 95%",
                             "scope": "fixed trained models and archived test-source composition; training variability excluded"},
               "comparisons": comparisons,
               "error_cost": {"nf4_to_finetuned_fn_change": -208, "nf4_to_finetuned_fp_change": 61,
                              "fn_to_fp_cost_ratio_boundary": 61 / 208},
               "checks": {"six_prediction_files_aligned": True, "archived_metrics_recomputed": True,
                          "probability_metrics_recomputed": True, "decision_threshold_checked": True}}
    write_json(OUT / "results.json", results)
    with (OUT / "summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("model", "scope", "n", "accuracy", "macro_f1", "invalid_precision", "invalid_recall", "tn", "fp", "fn", "tp"), lineterminator="\n")
        writer.writeheader()
        for name, scopes in summaries.items():
            for scope, values in scopes.items():
                cm = np.asarray(values["confusion_matrix"]).reshape(-1)
                writer.writerow({"model": name, "scope": scope, **{k: v for k, v in values.items() if k != "confusion_matrix"},
                                 **dict(zip(("tn", "fp", "fn", "tp"), map(int, cm)))})
    print(json.dumps({"comparisons": comparisons, "probability": {name: {k: v for k, v in values.items() if k != "bins"} for name, values in probabilities.items()},
                      "bootstrap": results["bootstrap"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-from", type=Path, help="Optional local checkout of the pinned source repository")
    parser.add_argument("--repetitions", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()
    if args.import_from:
        import_case(args.import_from)
    analyse(args.repetitions, args.seed)
