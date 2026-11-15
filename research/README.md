# 数据说明与复现

[下载论文 v2.1.0 对应的复现材料](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/download/v2.1.0/semantic_decision_statistics_materials_v2.1.0.zip)，解压后打开含有 `scripts` 和 `research` 的目录。以下命令均从该目录运行，每个案例可独立复算。使用 Python 3.12 和 NumPy 2.3.5，安装依赖后可离线运行。

```sh
python -m pip install numpy==2.3.5
```

## 论文标题提取错误识别

[逐条预测](title_case/predictions.csv)含 1,000 条测试记录。每行给出参考标签 `label`（1 为提取错误）、空标题标记 `empty_title`、归一化标题组编号 `title_identity`，以及六种方法的预测、分数和分数类型。24 条空标题按统一规则判为错误。`title_identity` 供分组重抽样使用。原题名、训练和验证分区、模型配置可从[论文题名提取实验的固定版本](https://github.com/LeoAndJellyfish/paper-title-error-classification/tree/1b0ce28d265454680b5b383bbb7ff0929dca688b)获取。

```sh
python scripts/title_case_analysis.py
```

脚本读取随附预测，计算分类与概率指标，执行 10,000 次配对分层自助重抽样。查看[分类指标](title_case/summary.csv)时，`scope=all` 对应论文的 1,000 条记录，`nonempty` 对应其中 976 条非空标题。[完整结果](title_case/results.json) · [数据来源与校验值](title_case/provenance.json)

## 按故障机制聚类

[九条构造投诉](semantic_clustering/records.csv)列出产品、故障机制及投诉文本。脚本按四种设定生成成对判断，每种设定分别查询 12、24、36 对投诉，每档重复 1,000 次，共 12,000 次模拟。参考划分按故障机制定义。

```sh
python scripts/semantic_clustering_study.py
```

[结果表](semantic_clustering/summary.csv)中的 `condition=perfect` 表示所查记录对均判断正确。`budget` 是查询对数，`hard_exact_recovery` 是主规则下使用二元判断完整恢复九条记录参考划分的比例。脚本另生成逐次记录 `replications.csv`。[完整结果](semantic_clustering/results.json)

## 垃圾短信比例估计

[UCI SMS Spam Collection](https://doi.org/10.24432/C5CC84) 的[原始语料](real_data/sms_spam_collection.zip)共 5,574 条，其中 747 条标为垃圾短信。[固定预测](real_data/predictions.csv)以 `row_id` 对应原始行号，另含文本的 SHA-256 摘要、参考标签 `y_spam`、模型分数 `score` 和抽样层 `stratum`。数据集采用 CC BY 4.0。[原始说明](real_data/original_readme.txt) · [来源与模型版本](real_data/provenance.json)

```sh
python scripts/sms_design_evaluation.py evaluate
```

程序在 200 和 400 条人工核验预算下分别重复抽样 10,000 次。结果写入案例目录，逐次记录为 `replications.csv.gz`。[估计结果](real_data/summary.csv) · [完整结果](real_data/results.json) · [从原始短信生成模型分数](https://github.com/LeoAndJellyfish/semantic-decision-statistics/blob/v2.0.0/research/real_data/README.md#reproduction-environment-and-results)

## 论文与版本

三个脚本均在对应案例目录内生成 `summary.csv` 和 `results.json`。校验下载文件时，使用所在版本根目录的 `CHECKSUMS.sha256`。如需编译[论文源文件](../semantic_decision_statistics.tex)，在根目录运行 `xelatex -interaction=nonstopmode -halt-on-error semantic_decision_statistics.tex` 至交叉引用稳定。[论文与复现包 v2.1.0](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.1.0) · [早期稿件与逐次模拟记录 v2.0.0](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.0.0)
