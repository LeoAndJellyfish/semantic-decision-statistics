# SMS corpus sampling-design evaluation

This specification was written before model prediction and sampling simulation on 5 October 2026. It defines a single illustrative analysis; no model or prompt search is planned.

- **Population and target:** every labeled row of the original UCI SMS Spam Collection archive, retaining duplicate messages as separate corpus rows. Estimate the proportion whose supplied label is `spam`. The supplied labels are fixed reference outcomes for sampling calculations; no new human annotation is collected.
- **Source:** Almeida and Hidalgo (2011), UCI Machine Learning Repository, DOI [10.24432/C5CC84](https://doi.org/10.24432/C5CC84), CC BY 4.0 according to the repository. Preserve the archive and original readme. Report the parsed row count if it differs from the repository headline count.
- **Interface:** two candidate descriptions: `This message is legitimate personal or transactional communication.` and `This message is unsolicited promotional or fraudulent spam.` A message is the premise; each description is an NLI hypothesis. Softmax the two entailment logits in that order; retain the second value as the auxiliary score. The score is not assumed calibrated to the archived spam labels.
- **Fixed model:** `cross-encoder/nli-MiniLM2-L6-H768`, revision `b95119ce93d3e065de6214e38cd4a97b0f2f2c6d`, artifact `onnx/model_quint8_avx2.onnx`. This is an open NLI model with a quantized ONNX readout. Its model card reports SNLI/MultiNLI training. No target-corpus fitting, prompt selection, or recalibration is performed.
- **Preprocessing:** retain message text; tokenize the premise/hypothesis pair, truncate the premise if needed to a maximum of 512 tokens, and pad within batches. Labels never enter model inputs. Record truncations and all artifact checksums.
- **Design:** form four equal-size rank strata using score, breaking score ties by original row index. For budgets 200 and 400 labels, compare the SRS label mean, the uncorrected full-corpus score mean, the SRS residual estimator with fixed coefficient one, and pilot-guided stratified residual estimation. The two SRS estimators share each draw. The pilot has 20 random labels per stratum (80 total), included in the budget and estimator. Unit label cost is one; actual human review time is unmeasured.
- **Allocation:** shrink each pilot residual variance by 20% toward their pooled average; allocate the remaining labels to minimize the plug-in conditional variance, imposing at least ten main-stage labels per remaining stratum. Integer allocation uses successive largest variance reductions. The main sample is drawn randomly without replacement from records outside the pilot. Use the existing two-stage estimator and its conditional variance formula.
- **Evaluation:** 10,000 independent repetitions per budget, NumPy PCG64 seed 20261005. Report signed bias, MSE, nominal 95% normal-interval coverage, mean interval width, and label count. Include finite-population corrections. Uncorrected full-corpus predictions form a fixed point estimator with zero verification labels; a design-based interval is undefined, recorded as not applicable. No interval clipping. Report Monte Carlo uncertainty and avoid selecting designs according to favorable results.

Run `scripts/sms_design_evaluation.py prepare`, `predict`, and `evaluate` from the workspace root. `evaluate` needs NumPy; model prediction additionally needs ONNX Runtime and Tokenizers. The script records package versions and prediction checksums. `predictions.csv` retains row IDs, source hashes, reference labels, scores, and strata. `results.json`, `summary.csv`, and `replications.csv.gz` retain the actual simulation outputs. The downloaded model remains a local cache; source URLs and hashes support retrieval.

This case evaluates finite-corpus sampling designs. It does not estimate a contemporary SMS traffic population or measure human review costs, label disagreement, or Jev performance. The published collection's labeling process and its relation to unsolicited receipt remain separate measurement questions.

## Reproduction environment and results

Executed with Python 3.12.14, NumPy 2.5.3, ONNX Runtime 1.30.0 and Tokenizers 0.23.2. For simulation from saved predictions, install NumPy and run:

```powershell
python scripts/sms_design_evaluation.py evaluate
```

To regenerate predictions, install the three versions above, then run the `prepare` and `predict` stages before `evaluate`. The recorded ONNX CPU run used four inference threads, batches of 24 messages and a 512-token pair limit; no pair required truncation. The original download contains 5,574 rows, 747 spam labels and 403 repeated-text occurrences. All rows were retained.

At 200 and 400 labels, SRS residual correction increased MSE relative to the SRS label estimator by 18.6% and 18.0%. The pilot design increased MSE relative to SRS correction by 53.2% and 15.8%. The original results are retained exactly in the extension below; its additional coefficient rule was specified before the new simulation. The uncorrected corpus mean had a small fixed error (0.004163) and lower squared error than the sampled estimators at these budgets; its design-based interval is undefined. See the complete unrounded metrics and Monte Carlo standard errors in `results.json`.

Saved replication summaries were independently recomputed. Exact hypergeometric evaluation of the SRS normal interval gives coverage 0.950575 at 200 labels and 0.938430 at 400, consistent with simulated 0.9510 and 0.9369. The normal intervals have finite-sample coverage error. The measurement identity and the four constructed numerical tables remain in the manuscript. The eight constructed examples were separately re-executed using exact arithmetic.

## Targeted weight extension: rule fixed before the additional simulation

This extension follows inspection of the original unit-weight results and the observed weak negative score-label association; it is not a preregistered experiment. The corpus, predictions, budgets, number of repetitions and original three verified designs remain fixed. One additional design is evaluated, without a search over alternative tuning rules.

The pilot-tuned difference estimator shares the 80-label stratified pilot, allocation computed from unit-weight pilot residuals, and main-stage samples with the existing pilot-stratified estimator. For known full-corpus score mean fbar and sample variance S_f^2, estimate S_yf by M/(M-1) times the sum over strata of W_h times the pilot mean of y_i(f_i-fbar). This covariance estimator is design-unbiased under the stratified pilot. The coefficient is that covariance estimate divided by S_f^2, clipped to [-1,1]; a zero score variance gives coefficient zero. The bounds are fixed before running this extension and permit a negative auxiliary association. No full-corpus labels enter coefficient estimation or allocation.

Hold the coefficient fixed through the main stage. Substitute lambda_P f_i for f_i in the existing two-stage estimator and use y_i-lambda_P f_i throughout its pilot contribution and conditional variance estimate. Reuse the main-stage samples and allocation so that the paired comparison isolates coefficient adjustment. Pilot allocation is deliberately kept at its original unit-weight rule; no claim of joint allocation/weight optimality is made. The conditional estimator is unbiased for every realized pilot, so averaging its conditional variance accounts for pilot and coefficient randomness; the normal interval remains an approximation.

Full-label correlation, unconstrained and [0,1]-constrained SRS oracle coefficients, and their exact SRS variances are diagnostic references only. The two-stage design is evaluated with its own conditional variance, not the SRS oracle formula. Saved replication rows will include coefficients and true conditional variances for verification; full-label diagnostics do not enter an implementable estimator. The original random-number sequence is retained by using no extra sampling calls.

## Weight-extension results

The score-label correlation is -0.0544966266. The finite-corpus SRS oracle coefficient is -0.1463191191, giving variance 0.9970301177 times the SRS label-mean variance (a 0.297% reduction). Under the interval [0,1], the SRS oracle coefficient is zero. These are full-label, fixed-coefficient SRS references. The operational pilot estimator is evaluated with the two-stage conditional variance and uses no unverified outcomes for tuning.

| Total labels | Estimator | Bias (percentage points) | MSE x 10^4 | Coverage (%) | Mean width (percentage points) |
|---:|---|---:|---:|---:|---:|
| 200 | SRS labels | 0.032 | 5.568 | 95.10 | 9.256 |
| 200 | SRS correction, coefficient 1 | 0.016 | 6.604 | 94.44 | 10.061 |
| 200 | Pilot correction, coefficient 1 | 0.007 | 10.117 | 93.96 | 12.419 |
| 200 | Pilot-tuned difference | 0.010 | 9.642 | 93.84 | 12.102 |
| 400 | SRS labels | -0.024 | 2.637 | 93.69 | 6.420 |
| 400 | SRS correction, coefficient 1 | -0.017 | 3.113 | 94.67 | 6.971 |
| 400 | Pilot correction, coefficient 1 | -0.024 | 3.603 | 94.67 | 7.476 |
| 400 | Pilot-tuned difference | -0.023 | 3.413 | 94.73 | 7.287 |

Tuning reduced MSE by 4.7% and 5.3% relative to the original pilot design. Its MSE remained 73.2% and 29.4% higher than the SRS label mean. The paired MSE reductions are 0.4752 and 0.1901 in the displayed units, with Monte Carlo standard errors 0.0464 and 0.0165. The coefficient's standard deviation was approximately 0.25 at both budgets, despite its mean being close to the SRS oracle. Both pilot designs spend 80 labels before the main stage; the labels remain in the estimate, with 120 or 320 fresh labels supporting the remaining-frame correction. The uncorrected full-corpus score mean remains a fixed zero-verification estimate with smaller realized squared error and no design-based confidence interval.

`results.json` records each coefficient distribution, exact SRS references, paired MSE differences, and mean true conditional variances. `replications.csv.gz` now contains 80,000 rows: four verified methods, two budgets, and 10,000 repetitions. Every original summary statistic was reproduced exactly; the saved predictions were unchanged. Replications were independently reaggregated, and estimated variances were compared with full-label conditional design variances. An eight-record enumeration covering 16 pilot samples and nine main-stage samples per pilot checked conditional unbiasedness, conditional variance and the expectation of its sample-variance estimator to floating-point precision, including coefficients at both bounds. The normal intervals retain finite-sample coverage error.

## Availability and attribution

The companion archive includes the article source/PDF, analysis scripts, fixed predictions, original UCI archive/readme, simulation outputs and existing evidence logs. Model weights and downloaded research-paper PDFs are excluded. The pinned model can be retrieved by the `prepare` stage. The original UCI authors and DOI above must remain cited, and the model card identifies its authors and Apache 2.0 license. The versioned materials are available at [v1.0.0](https://github.com/LeoAndJellyfish/semantic-decision-interfaces/releases/tag/v1.0.0). The author confirmed completion of the final scientific, reference, code and numerical-result review on 5 October 2026.
