"""Controlled relation-acquisition study for semantic_decision_statistics.tex.

Constructed data and simulated judgments; no external model is queried.
Requires NumPy. Run from any directory: python scripts/semantic_clustering_study.py
"""
from pathlib import Path
from itertools import combinations
import csv
import hashlib
import json
import math
import platform
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "semantic_clustering"
SEED = 20261005
REPS = 1000
BUDGETS = (12, 24, 36)


def partitions(n):
    """Each set partition appears once, as a restricted-growth string."""
    def extend(prefix, maximum):
        if len(prefix) == n:
            yield prefix
        else:
            for k in range(maximum + 2):
                yield from extend(prefix + (k,), max(maximum, k))
    return np.array(list(extend((0,), 0)), dtype=np.int8)


def posterior(signal, reliability, prior=0.25):
    pos = reliability * prior / (reliability * prior + (1-reliability) * (1-prior))
    neg = (1-reliability) * prior / ((1-reliability) * prior + reliability * (1-prior))
    return np.where(signal, pos, neg)


def summaries(values):
    return float(np.mean(values)), float(np.std(values, ddof=1)/math.sqrt(len(values)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    products = np.repeat(np.arange(3), 3)
    mechanisms = np.tile(np.arange(3), 3)
    pairs = np.array(list(combinations(range(9), 2)))
    reference = mechanisms[pairs[:, 0]] == mechanisms[pairs[:, 1]]
    product_relation = products[pairs[:, 0]] == products[pairs[:, 1]]
    assert reference.sum() == product_relation.sum() == 9
    labels = partitions(9)
    assert len(labels) == 21147
    same = labels[:, pairs[:, 0]] == labels[:, pairs[:, 1]]
    # Tie resolution uses only the product representation, never reference labels.
    geo_loss = np.count_nonzero(same != product_relation, axis=1)
    order = np.lexsort((np.arange(len(labels)), labels.max(axis=1)+1, geo_loss))
    enumeration_indices = order.copy()
    labels, same, geo_loss = labels[order], same[order], geo_loss[order]
    n_same = same.sum(axis=1)
    overlap = (same & reference).sum(axis=1)
    expected = n_same * reference.sum()/len(pairs)
    ari = (overlap-expected)/((n_same+reference.sum())/2-expected)
    pair_error = np.mean(same != reference, axis=1)
    assert np.isclose(ari[0], -1/3)  # Product and mechanism partitions cross.
    # Exact K=3 squared-error baseline on an explicitly constructed representation.
    vectors = np.concatenate((2*np.eye(3)[products], np.eye(3)[mechanisms]), axis=1)
    squared_distances = np.sum((vectors[pairs[:, 0]]-vectors[pairs[:, 1]])**2, axis=1)
    sse = np.zeros(len(labels))
    for idx, partition in enumerate(labels):
        for k in range(int(partition.max())+1):
            members = partition == k
            inside = members[pairs[:, 0]] & members[pairs[:, 1]]
            sse[idx] += squared_distances[inside].sum()/members.sum()
    k3 = labels.max(axis=1) == 2
    baseline_idx = np.flatnonzero(k3)[np.argmin(sse[k3])]
    assert np.array_equal(same[baseline_idx], product_relation)
    assert np.isclose(sse[baseline_idx], 6.0)

    edge_index = {tuple(pair): i for i, pair in enumerate(pairs)}
    triangles = np.array([[edge_index[(i,j)], edge_index[(i,k)], edge_index[(j,k)]]
                          for i,j,k in combinations(range(9),3)])
    rng = np.random.default_rng(SEED)
    reliabilities = np.where(rng.random((REPS,36)) < .5, .95, .80)
    errors = rng.random((REPS,36)) >= reliabilities
    signals = np.logical_xor(reference, errors)
    wrong_signals = np.logical_xor(product_relation, errors)
    permutations = np.argsort(rng.random((REPS,36)), axis=1)
    scores = {
        "perfect": np.broadcast_to(reference, (REPS,36)).astype(float),
        "heterogeneous": posterior(signals, reliabilities),
        "overconfident": posterior(signals, np.full((REPS,36), .99)),
        "wrong_criterion": posterior(wrong_signals, reliabilities),
    }
    records = []
    summary = []
    same_float = same.astype(np.float64)
    for condition, p in scores.items():
        for budget in BUDGETS:
            mask = np.zeros((REPS,36), dtype=bool)
            np.put_along_axis(mask, permutations[:,:budget], True, axis=1)
            hard = p > .5
            soft_idx, hard_idx, alt_soft_idx, alt_hard_idx = [], [], [], []
            soft_optima, hard_optima, feasible = [], [], []
            for start in range(0, REPS, 100):
                sl = slice(start, min(start+100,REPS))
                # Partition-invariant constants sum(p) are omitted.
                soft_loss = same_float @ ((1-2*p[sl])*mask[sl]).T
                hard_loss = same_float @ ((1-2*hard[sl].astype(float))*mask[sl]).T
                for column in range(soft_loss.shape[1]):
                    a, b = soft_loss[:,column], hard_loss[:,column]
                    soft_ties = np.flatnonzero(np.isclose(a,a.min(),rtol=0,atol=1e-9))
                    hard_ties = np.flatnonzero(np.isclose(b,b.min(),rtol=0,atol=1e-9))
                    soft_idx.append(int(soft_ties[0]))
                    hard_idx.append(int(hard_ties[0]))
                    alt_order = np.lexsort((enumeration_indices[soft_ties], labels[soft_ties].max(axis=1)+1))
                    alt_soft_idx.append(int(soft_ties[alt_order[0]]))
                    alt_hard_order = np.lexsort((enumeration_indices[hard_ties], labels[hard_ties].max(axis=1)+1))
                    alt_hard_idx.append(int(hard_ties[alt_hard_order[0]]))
                    soft_optima.append(len(soft_ties)); hard_optima.append(len(hard_ties))
                    # Minimum total binary disagreement equals zero iff feasible.
                    positive_edges = (hard[sl][column] & mask[sl][column]).sum()
                    feasible.append(bool(np.isclose(b.min()+positive_edges, 0)))
            soft_idx, hard_idx = np.array(soft_idx), np.array(hard_idx)
            observed = mask[:,triangles].all(axis=2)
            conflict = (hard[:,triangles].sum(axis=2) == 2) & observed
            error_by_rep = ((hard != reference)*mask).sum(axis=1)/budget
            brier_by_rep = ((p-reference)**2*mask).sum(axis=1)/budget
            diff = ari[soft_idx]-ari[hard_idx]
            row = {"condition": condition, "budget": budget, "replications": REPS}
            for name, values in {
                "judgment_error": error_by_rep,
                "brier": brier_by_rep,
                "hard_ari": ari[hard_idx], "soft_ari": ari[soft_idx],
                "soft_ari_alternative_tie": ari[alt_soft_idx],
                "hard_ari_alternative_tie": ari[alt_hard_idx],
                "ari_difference_alternative_tie": ari[alt_soft_idx]-ari[alt_hard_idx],
                "soft_pair_error_alternative_tie": pair_error[alt_soft_idx],
                "hard_pair_error_alternative_tie": pair_error[alt_hard_idx],
                "soft_multiple_optima": np.asarray(soft_optima)>1,
                "hard_multiple_optima": np.asarray(hard_optima)>1,
                "ari_difference": diff,
                "hard_pair_error": pair_error[hard_idx],
                "soft_pair_error": pair_error[soft_idx],
                "hard_query_error": ((same[hard_idx] != reference)*mask).sum(axis=1)/budget,
                "soft_query_error": ((same[soft_idx] != reference)*mask).sum(axis=1)/budget,
                "hard_exact_recovery": np.isclose(ari[hard_idx],1),
                "soft_exact_recovery": np.isclose(ari[soft_idx],1),
                "strict_feasible": np.array(feasible, dtype=float),
            }.items():
                row[name], row[name+"_mcse"] = summaries(np.asarray(values,dtype=float))
            row["triangle_conflict"] = float(conflict.sum()/observed.sum())
            row["observed_triangles"] = int(observed.sum())
            row["conflicting_triangles"] = int(conflict.sum())
            # Feasible cases are kept separate from all-repetition comparisons.
            row["strict_feasible_ari"] = float(ari[hard_idx][feasible].mean()) if any(feasible) else None
            summary.append(row)
            for rep in range(REPS):
                records.append({"condition":condition,"budget":budget,"rep":rep,
                                "hard_ari":float(ari[hard_idx[rep]]),
                                "soft_ari":float(ari[soft_idx[rep]]),
                                "hard_partition":"".join(map(str,labels[hard_idx[rep]])),
                                "soft_partition":"".join(map(str,labels[soft_idx[rep]])),
                                "hard_pair_error":float(pair_error[hard_idx[rep]]),
                                "soft_pair_error":float(pair_error[soft_idx[rep]]),
                                "soft_ari_alternative_tie":float(ari[alt_soft_idx[rep]]),
                                "hard_ari_alternative_tie":float(ari[alt_hard_idx[rep]]),
                                "soft_pair_error_alternative_tie":float(pair_error[alt_soft_idx[rep]]),
                                "hard_pair_error_alternative_tie":float(pair_error[alt_hard_idx[rep]]),
                                "soft_optima":int(soft_optima[rep]),
                                "hard_optima":int(hard_optima[rep]),
                                "strict_feasible":int(feasible[rep])})
            print(condition, budget, "ARI hard/soft", round(row["hard_ari"],4),
                  round(row["soft_ari"],4), "feasible", round(row["strict_feasible"],3), flush=True)

    # Complete, noiseless information must recover the exact reference partition.
    perfect_full = next(r for r in summary if r["condition"]=="perfect" and r["budget"]==36)
    assert perfect_full["hard_exact_recovery"] == perfect_full["soft_exact_recovery"] == 1
    for budget in BUDGETS:
        h = next(r for r in summary if r["condition"]=="heterogeneous" and r["budget"]==budget)
        o = next(r for r in summary if r["condition"]=="overconfident" and r["budget"]==budget)
        assert h["judgment_error"] == o["judgment_error"]
        assert h["hard_ari"] == o["hard_ari"]
    with (OUT/"summary.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    with (OUT/"replications.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    result={"study_type":"constructed records with simulated judgments; no model calls",
            "seed":SEED,"records":9,"pairs":36,"partitions":len(labels),
            "replications":REPS,"budgets":BUDGETS,"reliabilities":[.95,.80],
            "pair_prior":.25,"overconfident_reported_reliability":.99,
            "baseline":{"ari":float(ari[baseline_idx]),"sse":float(sse[baseline_idx]),
                        "representation":"[2*onehot(product), onehot(mechanism)]","K":3},
            "tie_break":"smallest product-relation disagreement, then K, then enumeration index",
            "alternative_tie_break":"smallest K, then original enumeration index; post-result sensitivity check",
            "python":platform.python_version(),"numpy":np.__version__,
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "summary":summary}
    (OUT/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    product_names = ["智能门锁","烟雾报警器","室内温控器"]
    mechanism_names = ["供电模块失效","断电后配置丢失","传感测量失真"]
    endings = [
        ["更换合格电池后仍无法通电，供电模块无输出。", "断电后已保存的密码丢失，需重新配置。", "无人触碰时持续报告开门。"],
        ["更换合格电池后仍无法通电，供电模块无输出。", "断电后已保存的报警阈值丢失，需重新配置。", "室内无烟时持续报告烟雾。"],
        ["更换合格电池后仍无法通电，供电模块无输出。", "断电后已保存的时段设置丢失，需重新配置。", "温度恒定时持续报告升温。"],
    ]
    with (OUT/"records.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["id","product","mechanism","text"])
        writer.writeheader()
        for i,(product,mechanism) in enumerate(zip(products, mechanisms)):
            writer.writerow({"id":i,"product":product_names[product],"mechanism":mechanism_names[mechanism],
                             "text":product_names[product]+"："+endings[product][mechanism]})


if __name__ == "__main__":
    main()
