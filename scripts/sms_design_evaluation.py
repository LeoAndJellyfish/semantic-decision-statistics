"""Fixed-model SMS predictions and finite-population sampling-design evaluation."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.metadata
import json
import platform
import statistics
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'real_data'
MODEL = ROOT / 'tmp' / 'models' / 'sms-nli'
REPO = 'cross-encoder/nli-MiniLM2-L6-H768'
REV = 'b95119ce93d3e065de6214e38cd4a97b0f2f2c6d'
ARTIFACT = 'onnx/model_quint8_avx2.onnx'
DATA_URL = 'https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'
HYPOTHESES = [
    'This message is legitimate personal or transactional communication.',
    'This message is unsolicited promotional or fraudulent spam.',
]
SEED, REPS, BUDGETS = 20261005, 10000, (200, 400)
PILOT_PER_STRATUM, MIN_MAIN, SHRINK = 20, 10, 0.2
COEFFICIENT_BOUNDS = (-1.0, 1.0)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def download(url, path):
    if not path.exists():
        print('Downloading', path.name, flush=True)
        with urllib.request.urlopen(url, timeout=90) as src, path.open('wb') as dst:
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
    return digest(path)


def records():
    with zipfile.ZipFile(OUT / 'sms_spam_collection.zip') as z:
        raw = z.read('SMSSpamCollection').decode('utf-8')
    # Split on newline, preserving any other characters inside a message.
    rows = [line.rstrip('\r').split('\t', 1) for line in raw.split('\n') if line.rstrip('\r')]
    assert all(len(row) == 2 and row[0] in ('spam', 'ham') for row in rows)
    return rows


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    MODEL.mkdir(parents=True, exist_ok=True)
    meta = {'dataset_url': DATA_URL, 'model_repo': REPO, 'revision': REV,
            'artifact': ARTIFACT, 'hypotheses': HYPOTHESES, 'hashes': {}}
    meta['hashes']['sms_spam_collection.zip'] = download(DATA_URL, OUT / 'sms_spam_collection.zip')
    with zipfile.ZipFile(OUT / 'sms_spam_collection.zip') as z:
        (OUT / 'original_readme.txt').write_bytes(z.read('readme'))
    for name in ('config.json', 'tokenizer.json', 'README.md', ARTIFACT):
        url = f'https://huggingface.co/{REPO}/resolve/{REV}/{name}'
        meta['hashes'][name] = download(url, MODEL / Path(name).name)
    rows = records()
    meta.update(rows=len(rows), spam_rows=sum(r[0] == 'spam' for r in rows),
                duplicate_text_rows=len(rows) - len({r[1] for r in rows}))
    save_json('provenance.json', meta)
    print(json.dumps({k: v for k, v in meta.items() if k != 'hashes'}), flush=True)


def predict():
    import onnxruntime as ort
    from tokenizers import Tokenizer
    meta = json.loads((OUT / 'provenance.json').read_text(encoding='utf-8'))
    for name, expected in meta['hashes'].items():
        path = OUT / name if name.endswith('.zip') else MODEL / Path(name).name
        assert digest(path) == expected, (name, 'artifact hash changed')
    rows = records()
    tok = Tokenizer.from_file(str(MODEL / 'tokenizer.json'))
    lengths = [len(tok.encode(text, h).ids) for _, text in rows for h in HYPOTHESES]
    tok.enable_truncation(max_length=512, strategy='only_first')
    tok.enable_padding(pad_id=1, pad_token='<pad>')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(MODEL / Path(ARTIFACT).name), options,
                                   providers=['CPUExecutionProvider'])
    print('Model inputs', [x.name for x in session.get_inputs()], flush=True)
    scores, start = [], time.time()
    for lo in range(0, len(rows), 24):
        pairs = [(text, h) for _, text in rows[lo:lo + 24] for h in HYPOTHESES]
        enc = tok.encode_batch(pairs)
        candidates = {'input_ids': np.asarray([e.ids for e in enc], dtype=np.int64),
                      'attention_mask': np.asarray([e.attention_mask for e in enc], dtype=np.int64),
                      'token_type_ids': np.asarray([e.type_ids for e in enc], dtype=np.int64)}
        logits = session.run(None, {x.name: candidates[x.name] for x in session.get_inputs()})[0]
        # config.json fixes index 1 as entailment; normalize across candidate descriptions.
        assert json.loads((MODEL / 'config.json').read_text())['label2id']['entailment'] == 1
        ent = np.asarray(logits, dtype=np.float64).reshape(-1, 2, 3)[:, :, 1]
        ent -= ent.max(axis=1, keepdims=True)
        prob = np.exp(ent)
        scores.extend((prob[:, 1] / prob.sum(axis=1)).tolist())
        if lo % 480 == 0:
            print(f'Predicted {min(lo + 24, len(rows))}/{len(rows)} in {time.time()-start:.1f}s', flush=True)
    f = np.asarray(scores)
    assert len(f) == len(rows) and np.isfinite(f).all() and ((f >= 0) & (f <= 1)).all()
    order = np.lexsort((np.arange(len(f)), f))
    strata = np.empty(len(f), dtype=int)
    for h, ids in enumerate(np.array_split(order, 4)):
        strata[ids] = h
    with (OUT / 'predictions.csv').open('w', encoding='utf-8', newline='') as out:
        w = csv.writer(out)
        w.writerow(['row_id', 'text_sha256', 'y_spam', 'score', 'stratum'])
        for i, ((label, text), score, h) in enumerate(zip(rows, f, strata)):
            w.writerow([i, hashlib.sha256(text.encode()).hexdigest(), int(label == 'spam'), format(score, '.17g'), h])
    meta['prediction'] = {'max_tokens': 512, 'batch_records': 24, 'truncated_pairs': sum(n > 512 for n in lengths),
                          'max_untruncated_pair_tokens': max(lengths), 'runtime_seconds': time.time() - start,
                          'provider': 'CPUExecutionProvider', 'threads': 4,
                          'python': platform.python_version(),
                          'versions': {p: importlib.metadata.version(p) for p in ['numpy', 'onnxruntime', 'tokenizers']},
                          'predictions_sha256': digest(OUT / 'predictions.csv')}
    save_json('provenance.json', meta)
    print(meta['prediction'], flush=True)


def allocate(remaining_sizes, variances, main_budget):
    k = np.full(4, MIN_MAIN, dtype=int)
    # For unit costs, the largest marginal variance reduction solves the discrete convex problem.
    a = remaining_sizes.astype(float) ** 2 * variances
    for _ in range(main_budget - int(k.sum())):
        gain = np.where(k < remaining_sizes, a / (k * (k + 1)), -1)
        k[np.argmax(gain)] += 1
    assert k.sum() == main_budget and (k >= MIN_MAIN).all() and (k <= remaining_sizes).all()
    return k


def pilot_coefficient(y, f, pilots, groups, fmean, score_variance):
    """Design-weighted pilot covariance; the score moments are known for all rows."""
    if score_variance == 0:
        return 0.0
    M = len(f)
    cross_moment = sum(len(g) / M * np.mean(y[p] * (f[p] - fmean))
                       for p, g in zip(pilots, groups))
    covariance = M / (M - 1) * cross_moment
    return float(np.clip(covariance / score_variance, *COEFFICIENT_BOUNDS))


def evaluate():
    rows = list(csv.DictReader((OUT / 'predictions.csv').open(encoding='utf-8')))
    y = np.array([int(r['y_spam']) for r in rows], dtype=float)
    f = np.array([float(r['score']) for r in rows])
    h = np.array([int(r['stratum']) for r in rows])
    assert len(y) == len(records())
    meta = json.loads((OUT / 'provenance.json').read_text())
    assert digest(OUT / 'predictions.csv') == meta['prediction']['predictions_sha256']
    M, target, fmean = len(y), float(y.mean()), float(f.mean())
    e = y - f
    score_variance = float(f.var(ddof=1))
    label_variance = float(y.var(ddof=1))
    covariance = float(np.cov(y, f, ddof=1)[0, 1])
    oracle = covariance / score_variance if score_variance > 0 else 0.0
    constrained_oracle = float(np.clip(oracle, 0, 1))
    groups = [np.flatnonzero(h == g) for g in range(4)]
    rem_sizes = np.array([len(g) - PILOT_PER_STRATUM for g in groups])
    rng = np.random.default_rng(SEED)
    z = statistics.NormalDist().inv_cdf(0.975)
    summary, allocations, coefficient_diagnostics, paired = [], {}, {}, {}
    with gzip.open(OUT / 'replications.csv.gz', 'wt', encoding='utf-8', newline='') as out:
        w = csv.writer(out)
        w.writerow(['budget', 'rep', 'method', 'estimate', 'variance', 'covered', 'width',
                    'coefficient', 'true_conditional_variance'])
        for budget in BUDGETS:
            result = {key: [] for key in ['srs_labels', 'srs_residual', 'pilot_residual', 'pilot_tuned']}
            ks, tuned_coefficients = [], []
            for rep in range(REPS):
                s = rng.choice(M, budget, replace=False)
                estimates = [float(y[s].mean()), float(fmean + e[s].mean())]
                variances = [float((1 - budget / M) * a[s].var(ddof=1) / budget) for a in (y, e)]
                exact_variances = [(1 - budget / M) * a.var(ddof=1) / budget for a in (y, e)]
                pilot, pilots, remaining, s2 = [], [], [], []
                for g in groups:
                    p = rng.choice(g, PILOT_PER_STRATUM, replace=False)
                    pilot.extend(p)
                    pilots.append(p)
                    remaining.append(np.setdiff1d(g, p, assume_unique=True))
                    s2.append(e[p].var(ddof=1))
                s2 = np.array(s2)
                shrunk = (1 - SHRINK) * s2 + SHRINK * s2.mean()
                k = allocate(rem_sizes, shrunk, budget - 4 * PILOT_PER_STRATUM)
                ks.append(k)
                coefficient = pilot_coefficient(y, f, pilots, groups, fmean, score_variance)
                tuned_coefficients.append(coefficient)
                est, var = fmean + e[pilot].sum() / M, 0.0
                est_tuned = coefficient * fmean + (y[pilot] - coefficient * f[pilot]).sum() / M
                var_tuned, exact_fixed, exact_tuned = 0.0, 0.0, 0.0
                for g in range(4):
                    smain = rng.choice(remaining[g], k[g], replace=False)
                    er = e[smain]
                    weight = rem_sizes[g] / M
                    est += weight * er.mean()
                    var += weight**2 * (1 - k[g] / rem_sizes[g]) * er.var(ddof=1) / k[g]
                    er_tuned = y[smain] - coefficient * f[smain]
                    factor = weight**2 * (1 - k[g] / rem_sizes[g]) / k[g]
                    est_tuned += weight * er_tuned.mean()
                    var_tuned += factor * er_tuned.var(ddof=1)
                    # Full labels below are evaluation diagnostics, never design inputs.
                    exact_fixed += factor * e[remaining[g]].var(ddof=1)
                    exact_tuned += factor * (y[remaining[g]] - coefficient * f[remaining[g]]).var(ddof=1)
                estimates.append(float(est))
                variances.append(float(var))
                estimates.append(float(est_tuned))
                variances.append(float(var_tuned))
                exact_variances.extend([float(exact_fixed), float(exact_tuned)])
                for method, est, var, coef, exact in zip(result, estimates, variances,
                                                        [0.0, 1.0, 1.0, coefficient], exact_variances):
                    half = z * np.sqrt(var)
                    covered = bool(est - half <= target <= est + half)
                    result[method].append((est, var, covered, 2 * half, exact))
                    w.writerow([budget, rep, method, est, var, int(covered), 2 * half, coef, exact])
            for method, vals in result.items():
                arr = np.asarray(vals)
                err = arr[:, 0] - target
                mse = err**2
                coverage = float(arr[:, 2].mean())
                summary.append({'budget': budget, 'labels': budget, 'method': method,
                                'bias': float(err.mean()), 'bias_mcse': float(err.std(ddof=1) / np.sqrt(REPS)),
                                'mse': float(mse.mean()), 'mse_mcse': float(mse.std(ddof=1) / np.sqrt(REPS)),
                                'coverage': coverage, 'coverage_mcse': float(np.sqrt(coverage * (1 - coverage) / REPS)),
                                'width': float(arr[:, 3].mean()),
                                'width_mcse': float(arr[:, 3].std(ddof=1) / np.sqrt(REPS)),
                                'empirical_variance': float(arr[:, 0].var(ddof=1)),
                                'mean_estimated_variance': float(arr[:, 1].mean()),
                                'mean_true_conditional_variance': float(arr[:, 4].mean()),
                                'true_conditional_variance_mcse': float(arr[:, 4].std(ddof=1) / np.sqrt(REPS))})
            coef = np.asarray(tuned_coefficients)
            coefficient_diagnostics[str(budget)] = {
                'mean': float(coef.mean()), 'sd': float(coef.std(ddof=1)),
                'quantiles_05_50_95': np.quantile(coef, [0.05, 0.5, 0.95]).tolist(),
                'fraction_lower_bound': float(np.mean(coef == COEFFICIENT_BOUNDS[0])),
                'fraction_upper_bound': float(np.mean(coef == COEFFICIENT_BOUNDS[1])),
                'fraction_positive': float(np.mean(coef > 0))}
            fixed_err = np.asarray(result['pilot_residual'])[:, 0] - target
            tuned_err = np.asarray(result['pilot_tuned'])[:, 0] - target
            squared_error_difference = tuned_err**2 - fixed_err**2
            paired[str(budget)] = {'comparison': 'pilot_tuned minus pilot_residual',
                                   'mse_difference': float(squared_error_difference.mean()),
                                   'mse_difference_mcse': float(squared_error_difference.std(ddof=1) / np.sqrt(REPS))}
            allocations[str(budget)] = {'mean_main': np.mean(ks, axis=0).tolist(),
                                         'min_main': np.min(ks, axis=0).tolist(),
                                         'max_main': np.max(ks, axis=0).tolist()}
            print('Evaluated budget', budget, flush=True)
    baseline = {'labels': 0, 'method': 'uncorrected_prediction', 'estimate': fmean,
                'bias': fmean - target, 'mse': (fmean - target)**2, 'coverage': None, 'width': None}
    full = {'target': target, 'N': M, 'positive_labels': int(y.sum()), 'seed': SEED,
            'replications_per_budget': REPS, 'budgets': BUDGETS, 'pilot_per_stratum': PILOT_PER_STRATUM,
            'min_main_per_stratum': MIN_MAIN, 'variance_shrinkage': SHRINK, 'z': z,
            'score_mean': fmean, 'uncorrected': baseline, 'summary': summary, 'allocations': allocations,
            'weight_rule': {'bounds': COEFFICIENT_BOUNDS,
                            'covariance': 'M/(M-1) * sum_h W_h * mean_pilot_h(y_i*(f_i-fbar_U))',
                            'denominator': 'known full-corpus S_f^2',
                            'allocation': 'shared original unit-weight pilot residual allocation',
                            'paired_samples': 'same pilot and main-stage labels as pilot_residual'},
            'coefficient_diagnostics': coefficient_diagnostics, 'paired_mse_comparison': paired,
            'score_label_diagnostics': {'label_variance': label_variance, 'score_variance': score_variance,
                                        'covariance': covariance, 'correlation': float(np.corrcoef(y, f)[0, 1]),
                                        'unit_residual_variance': float(e.var(ddof=1))},
            'oracle_srs_reference': {
                'unconstrained_coefficient': oracle, 'coefficient_constrained_0_1': constrained_oracle,
                'unconstrained_variance_ratio_to_labels': float((y - oracle*f).var(ddof=1) / label_variance),
                'variance_ratio_constrained_0_1': float((y - constrained_oracle*f).var(ddof=1) / label_variance),
                'variances': {str(n): float((1 - n/M) * (y - oracle*f).var(ddof=1) / n) for n in BUDGETS}},
            'strata': [{'h': j, 'N': len(g), 'score_min': float(f[g].min()), 'score_max': float(f[g].max()),
                        'reference_prevalence': float(y[g].mean()), 'residual_sd': float(e[g].std(ddof=1))} for j, g in enumerate(groups)],
            'theoretical_srs': {str(n): {'labels': (1 - n/M) * float(y.var(ddof=1)) / n,
                                         'residual': (1 - n/M) * float(e.var(ddof=1)) / n} for n in BUDGETS},
            'prediction_sha256': digest(OUT / 'predictions.csv'), 'script_sha256': digest(Path(__file__))}
    save_json('results.json', full)
    with (OUT / 'summary.csv').open('w', encoding='utf-8', newline='') as out:
        w = csv.DictWriter(out, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    print(json.dumps(full, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare', 'predict', 'evaluate'])
    args = parser.parse_args()
    globals()[args.stage]()
