"""Reproduce the manuscript's constructed examples using exact arithmetic.

Python >= 3.9, standard library only. No model calls, empirical observations,
simulation, credentials, or external data are used. Run from any directory:
    python scripts/reproduce_examples.py
Results are written to research/worked_examples.json next to the manuscript.
"""
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import json


def encode(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    raise TypeError(type(value).__name__)


def classification_example():
    result = []
    for name, tp, fn, fp, tn in [
        ("A", 150, 50, 50, 750),
        ("B", 200, 0, 100, 700),
    ]:
        total = tp + fn + fp + tn
        prevalence = F(tp + fn, total)
        apparent = F(tp + fp, total)
        sensitivity = F(tp, tp + fn)
        specificity = F(tn, tn + fp)
        assert apparent == sensitivity * prevalence + (1 - specificity) * (1 - prevalence)
        assert F(tp + tn, total) == F(9, 10)
        result.append(dict(name=name, tp=tp, fn=fn, fp=fp, tn=tn,
                           prevalence=prevalence, apparent_prevalence=apparent,
                           bias=apparent-prevalence, accuracy=F(tp+tn, total)))
    return result


def clustering_example():
    weights = {(0, 1): F(9, 10), (1, 2): F(8, 10), (0, 2): F(1, 10)}
    # Restricted-growth strings enumerate every partition exactly once.
    partitions = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2)]
    result = []
    for labels in partitions:
        loss = sum(w if labels[i] != labels[j] else 1-w
                   for (i, j), w in weights.items())
        result.append(dict(labels=labels, disagreement=loss))
    optimum = min(result, key=lambda row: row["disagreement"])
    assert optimum["labels"] == (0, 0, 1)
    assert optimum["disagreement"] == 1
    # A posterior distribution over partitions must obey this inequality.
    lower_bound = weights[0, 1] + weights[1, 2] - 1
    assert weights[0, 2] < lower_bound
    return dict(partitions=result, necessary_lower_bound_w_ac=lower_bound)


def inference_example():
    n, N = 200, 5000
    # X,Z are independent Bernoulli(1/2); Y|X,Z ~ Bernoulli(1/5+3X/5).
    cells = []
    for x, z, y in product((0, 1), repeat=3):
        prob_y = F(1, 5) + F(3, 5)*x
        mass = F(1, 4)*(prob_y if y else 1-prob_y)
        cells.append((x, z, y, mass))
    assert sum(row[3] for row in cells) == 1
    mean_y = sum(y*p for x, z, y, p in cells)
    var_y = sum((y-mean_y)**2*p for x, z, y, p in cells)
    predictors = {
        "aligned": lambda x, z: F(1, 5)+F(3, 5)*x,
        "shifted": lambda x, z: F(7, 20)+F(3, 5)*x,
        "unrelated": lambda x, z: F(1, 5)+F(3, 5)*z,
    }
    rows = []
    for name, f in predictors.items():
        mean_f = sum(f(x, z)*p for x, z, y, p in cells)
        var_f = sum((f(x, z)-mean_f)**2*p for x, z, y, p in cells)
        cov_yf = sum((y-mean_y)*(f(x, z)-mean_f)*p for x, z, y, p in cells)
        lambda_star = cov_yf / ((1+F(n, N))*var_f)
        def variance(lam):
            return lam**2*var_f/N + (var_y+lam**2*var_f-2*lam*cov_yf)/n
        baseline = variance(F(0))
        assert baseline == F(1, 800)
        assert variance(lambda_star) <= baseline
        assert mean_y == F(1, 2)
        rows.append(dict(name=name, prediction_bias=mean_f-mean_y,
                         prediction_variance=var_f, outcome_covariance=cov_yf,
                         lambda_star=lambda_star,
                         naive_mse=(mean_f-mean_y)**2+var_f/N,
                         variance_lambda_1=variance(F(1)),
                         variance_lambda_star=variance(lambda_star),
                         relative_variance_lambda_1=variance(F(1))/baseline,
                         relative_variance_lambda_star=variance(lambda_star)/baseline))
    assert rows[0]["variance_lambda_1"] == rows[1]["variance_lambda_1"]
    assert rows[2]["lambda_star"] == 0
    return dict(n_labeled=n, N_unlabeled=N, mean_y=mean_y, var_y=var_y,
                baseline_variance=F(1, 800), predictors=rows)


def correlated_query_example():
    rho, repeats = F(4, 5), 5
    symmetrized_relative_variance = (1+rho)/2
    repeated_relative_variance = (1+(repeats-1)*rho)/repeats
    effective_queries = F(repeats)/(1+(repeats-1)*rho)
    assert symmetrized_relative_variance == F(9, 10)
    assert repeated_relative_variance == F(21, 25)
    assert effective_queries == F(25, 21)
    return dict(correlation=rho, repeats=repeats,
                symmetrized_relative_variance=symmetrized_relative_variance,
                repeated_relative_variance=repeated_relative_variance,
                effective_queries=effective_queries)


def ordinal_example():
    rows = []
    for name, probs in [('A', [F(1, 2), F(0), F(1, 2)]),
                        ('B', [F(0), F(1), F(0)])]:
        cumulative = [sum(probs[:j+1]) for j in range(2)]
        tails = [1-p for p in cumulative]
        codings = {'index': [0, 1, 2], 'unequal': [0, 1, 4]}
        means = {}
        for key, coding in codings.items():
            direct = sum(g*p for g, p in zip(coding, probs))
            tail_formula = coding[0]+sum((coding[j+1]-coding[j])*tails[j]
                                         for j in range(2))
            assert direct == tail_formula
            means[key] = direct
        assert means['index'] == 1
        rows.append(dict(name=name, probabilities=probs, cumulative=cumulative,
                         upper_tails=tails, expected_scores=means))
    assert rows[0]['expected_scores']['unequal'] == 2
    assert rows[1]['expected_scores']['unequal'] == 1
    return rows


def linkage_example():
    match_likelihood, nonmatch_likelihood = F(4, 5), F(1, 50)
    likelihood_ratio = match_likelihood/nonmatch_likelihood
    rows = []
    for prior in [F(1, 1000), F(1, 10)]:
        posterior = prior*likelihood_ratio/(1-prior+prior*likelihood_ratio)
        thresholds = {}
        for cost_ratio in [F(1), F(5)]:
            threshold = cost_ratio*(1-prior)/prior
            posterior_threshold = cost_ratio/(1+cost_ratio)
            assert (likelihood_ratio >= threshold) == (posterior >= posterior_threshold)
            thresholds[str(cost_ratio)] = dict(likelihood_ratio=threshold,
                posterior=posterior_threshold, link=likelihood_ratio >= threshold)
        rows.append(dict(prior=prior, posterior=posterior, thresholds=thresholds))
    assert likelihood_ratio == 40
    assert rows[0]['posterior'] == F(40, 1039)
    assert rows[1]['posterior'] == F(40, 49)
    return dict(match_likelihood=match_likelihood,
                nonmatch_likelihood=nonmatch_likelihood,
                likelihood_ratio=likelihood_ratio, populations=rows)


def allocation_example():
    sizes, weights = [8000, 2000], [F(4, 5), F(1, 5)]
    std, costs, sqrt_costs, budget = [F(1, 10), F(2, 5)], [1, 4], [1, 2], 240
    denominator = sum(w*s*c for w, s, c in zip(weights, std, sqrt_costs))
    optimum = [F(budget)*w*s/c/denominator
               for w, s, c in zip(weights, std, sqrt_costs)]
    assert optimum == [80, 40]
    def variance(n):
        return sum(w*w*(1-F(nh, mh))*s*s/nh
                   for w, mh, s, nh in zip(weights, sizes, std, n))
    proposed, proportional = [80, 40], [120, 30]
    assert sum(c*n for c, n in zip(costs, proposed)) == budget
    assert sum(c*n for c, n in zip(costs, proportional)) == budget
    # Enumerate every feasible integer allocation with at least two per stratum.
    feasible = [(variance([n1, n2]), n1, n2)
                for n1 in range(2, budget+1)
                for n2 in range(2, budget//4+1) if n1+4*n2 <= budget]
    best = min(feasible)
    assert best[1:] == tuple(proposed)
    assert variance(proposed) == F(59, 250000)
    assert variance(proportional) == F(197, 750000)
    assert variance(proposed)/variance(proportional) == F(177, 197)
    return dict(population_sizes=sizes, weights=weights, residual_sd=std,
                unit_costs=costs, budget=budget, optimal_allocation=proposed,
                proportional_allocation=proportional,
                optimal_variance=variance(proposed),
                proportional_variance=variance(proportional),
                variance_ratio=variance(proposed)/variance(proportional),
                integer_allocations_enumerated=len(feasible))


def adaptive_pilot_example():
    # Eight fixed records, two strata, f=0. Pilot samples two records per stratum.
    outcomes = [[F(0), F(0), F(1), F(1)], [F(0), F(1), F(2), F(3)]]
    mean = sum(sum(h) for h in outcomes)/8
    pilots = list(combinations(range(4), 2))
    conditional_checks, main_outcomes = [], 0
    for pilot in product(pilots, repeat=2):
        pilot_values = [[outcomes[h][i] for i in pilot[h]] for h in range(2)]
        pilot_variances = [(a-b)**2/2 for a, b in pilot_values]
        # Outcome-dependent choice of which remaining stratum to census.
        allocation = [2, 1] if pilot_variances[0] >= pilot_variances[1] else [1, 2]
        remaining = [[i for i in range(4) if i not in pilot[h]] for h in range(2)]
        main_choices = [list(combinations(remaining[h], allocation[h])) for h in range(2)]
        estimates = []
        for selected in product(*main_choices):
            estimate = sum(sum(x) for x in pilot_values)/8
            estimate += sum(F(2, 8)*sum(outcomes[h][i] for i in selected[h])/allocation[h]
                            for h in range(2))
            estimates.append(estimate)
        conditional_mean = sum(estimates)/len(estimates)
        conditional_variance = sum((x-mean)**2 for x in estimates)/len(estimates)
        theoretical_variance = F(0)
        for h in range(2):
            a, b = [outcomes[h][i] for i in remaining[h]]
            remaining_variance = (a-b)**2/2
            theoretical_variance += F(2, 8)**2*(1-F(allocation[h], 2))*remaining_variance/allocation[h]
        assert conditional_mean == mean
        assert conditional_variance == theoretical_variance
        main_outcomes += len(estimates)
        conditional_checks.append(conditional_variance)
    return dict(population_mean=mean, pilot_configurations=len(conditional_checks),
                main_sample_outcomes=main_outcomes,
                all_conditional_means_equal_target=True,
                all_conditional_variances_match_formula=True,
                average_conditional_variance=sum(conditional_checks)/len(conditional_checks))


if __name__ == "__main__":
    results = {"provenance": "Constructed examples; exact enumeration, no model benchmark",
               "classification": classification_example(),
               "clustering": clustering_example(),
               "inference": inference_example(),
               "correlated_queries": correlated_query_example(),
               "ordinal": ordinal_example(),
               "linkage": linkage_example(),
               "allocation": allocation_example(),
               "adaptive_pilot": adaptive_pilot_example()}
    target = Path(__file__).resolve().parents[1]/"research"/"worked_examples.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, default=encode, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(results, default=encode, indent=2))
