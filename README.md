# Semantic Decision Interfaces for Statistical Measurement and Population Estimation

Companion materials for **Semantic Decision Interfaces for Statistical Measurement and Population Estimation: A Methodological Framework**.

**Author:** Youyin Zhejun, Central University of Finance and Economics  
**ORCID:** https://orcid.org/0009-0009-5316-8193  
**Version:** [v1.0.0](https://github.com/LeoAndJellyfish/semantic-decision-interfaces/releases/tag/v1.0.0), 5 October 2026

## Manuscript and materials

- [Final manuscript](output/pdf/system_one_statistics_survey_english.pdf) and [LaTeX source](system_one_statistics_survey.tex).
- [Experiment specification and reproduction instructions](research/real_data/README.md).
- [Evidence records and revision history](research/README.md).
- [Versioned archive](https://github.com/LeoAndJellyfish/semantic-decision-interfaces/releases/tag/v1.0.0), with a downloadable companion ZIP and checksums.

The archive contains the original UCI SMS data, fixed model predictions, simulation outputs, analysis code and evidence records. Model weights, runtime environments and downloaded research-paper PDFs are retrieved separately from their documented sources.

## Reproduce the analysis

From the repository root, with Python 3.12 and NumPy 2.5.3:

```sh
python scripts/sms_design_evaluation.py evaluate
```

This stage uses the saved predictions and source archive. It writes `results.json`, `summary.csv`, and `replications.csv.gz` under `research/real_data/`. The experiment compares four verified estimators at 200 and 400 labels, with 10,000 repetitions per budget; the fixed uncorrected prediction mean is recorded separately. Both two-stage designs include their 80 pilot labels in the total budget.

To regenerate predictions, install ONNX Runtime 1.30.0 and Tokenizers 0.23.2 alongside NumPy, then run:

```sh
python scripts/sms_design_evaluation.py prepare
python scripts/sms_design_evaluation.py predict
python scripts/sms_design_evaluation.py evaluate
```

The model revision, input descriptions and artifact hashes are fixed in the experiment instructions. The original run used the ONNX CPU provider.

The constructed examples use the Python standard library:

```sh
python scripts/reproduce_examples.py
```

File integrity can be checked against `CHECKSUMS.sha256`. Gzip container timestamps may differ after rerunning the simulation; the underlying numerical records and summaries are the comparison targets.

## Sources and author review

The SMS Spam Collection is by Almeida and Hidalgo (2011), [DOI: 10.24432/C5CC84](https://doi.org/10.24432/C5CC84); UCI identifies CC BY 4.0 for the dataset. Its original archive and readme are included. The pinned model card identifies Apache 2.0; model weights are retrieved from the original repository. Source records retain original URLs for literature files excluded from this archive.

The author confirmed completion of the final scientific, reference, code and numerical-result review on 5 October 2026. The manuscript discloses AI assistance and author responsibility. The analysis conditions on archived labels and includes no newly collected human verification data.
