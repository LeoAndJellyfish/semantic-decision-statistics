# 语义决策模型在统计分析中的应用

当前研究稿：**语义决策模型在统计分析中的应用：方法论框架与研究议程**，第二版语言修订稿，2026年10月25日。

[GitHub 发布版 v2.0.0](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.0.0)提供论文 PDF 和与该版本对应的复现材料下载。

- [中文 LaTeX 新稿](semantic_decision_statistics.tex)与[论文 PDF](output/pdf/semantic_decision_statistics.pdf)。
- [研究框架与复现说明](research/semantic_clustering/README.md)。
- [构造聚类程序](scripts/semantic_clustering_study.py)：比较查询预算、二元与概率读法、判断可靠度、标准偏移及并列规则。
- [真实分类案例与复现说明](research/title_case/README.md)、[重分析程序](scripts/title_case_analysis.py)：复用标题提取错误识别实验，对齐六项预测，复算分类与概率指标，实施配对标题组重抽样。
- [语言修订与交付核验](research/manuscript_versions/20261025/verification.json)：记录信息保全、方法解释、数字复算与版面检查。

新稿以分类、聚类和变量构造为主线，采用八节论文结构。第4节纳入 Tev1 零样本与任务微调的真实分类案例；第7节保留构造聚类研究，真实语料上的聚类来源比较列入研究议程；SMS 总体估计移至附录。2026年10月5日、6日稿件分别保存在 `research/manuscript_versions/20261005/`、`research/manuscript_versions/20261006/`。

在仓库根目录使用 Python 3.12 与 NumPy 2.3.5 复算分类和聚类结果。

```sh
python scripts/title_case_analysis.py
python scripts/semantic_clustering_study.py
```

论文使用 XeLaTeX 编译。运行两遍 `xelatex -interaction=nonstopmode -halt-on-error semantic_decision_statistics.tex` 以解析交叉引用。

下列资料对应此前的测量与总体估计论文。`CHECKSUMS.sha256` 对应 v1.0.0 标签下的历史归档。

---

# 既有稿件与存档

Companion materials for **Semantic Decision Interfaces for Statistical Measurement and Population Estimation: A Methodological Framework**.

**Author:** Youyin Zhejun, Central University of Finance and Economics  
**ORCID:** https://orcid.org/0009-0009-5316-8193  
**Version:** [v1.0.0](https://github.com/LeoAndJellyfish/semantic-decision-statistics/tree/v1.0.0), 5 October 2026

## Manuscript and materials

- [Final manuscript](output/pdf/system_one_statistics_survey_english.pdf) and [LaTeX source](system_one_statistics_survey.tex).
- [Experiment specification and reproduction instructions](research/real_data/README.md).
- [Evidence records and revision history](research/README.md).
- [Versioned archive](https://github.com/LeoAndJellyfish/semantic-decision-statistics/tree/v1.0.0), with the original files and checksums.

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
