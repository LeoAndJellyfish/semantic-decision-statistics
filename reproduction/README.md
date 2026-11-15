# 数据与复现

[返回仓库首页](../README.md) · [完整论文](../paper/semantic_decision_statistics.pdf) · [下载全部材料](https://github.com/LeoAndJellyfish/semantic-decision-statistics/archive/refs/heads/main.zip)

三个案例可独立运行。基础复现读取随附的固定预测或生成构造关系，复算论文中的统计量、模拟结果与抽样比较。模型训练与固定预测的生成过程另有对应入口。

## 环境和运行位置

基础复现环境为 Python 3.12 与 NumPy 2.3.5。以下命令从仓库根目录执行；依赖安装完成后，三个统计程序均可离线运行。

```sh
python -m pip install -r reproduction/requirements.txt
python tools/check_materials.py
```

`data/` 保存固定输入和来源记录，`reference/` 保存论文采用的结果。脚本默认将新结果写入 `outputs/` 下的对应案例目录，也可通过 `--output-dir` 指定位置。参考文件保留原始运行环境和脚本摘要，新结果记录本次运行的信息。

## 论文题名提取错误识别

**[固定预测](data/title_case/predictions.csv) · [来源和版本](data/title_case/provenance.json) · [参考分类表](reference/title_case/summary.csv) · [完整参考结果](reference/title_case/results.json)**

测试集有 1,000 条记录。`label=1` 表示提取错误，`empty_title` 标记空标题；24 条空标题按统一规则判为错误。`title_identity` 是归一化题名组编号，供分组重抽样使用。其余字段保存六种方法的标签、分数与分数类型。归档字段名 `systemone` 对应 Tev1 的 Q4_K_M 部署，`tev1-nf4-zero-shot` 与 `tev1_finetuned` 分别对应 NF4 零样本和启用 QLoRA 任务适配器的方案。

```sh
python reproduction/scripts/title_case_analysis.py
```

程序核对固定预测与原实验混淆矩阵，复算分类及概率指标，并按 963 个归一化非空题名组执行 10,000 次配对分层自助重抽样，种子为 `20261006`。结果中的 `scope=all` 对应 1,000 条记录，`nonempty` 对应 976 条非空记录。新结果为 `outputs/title_case/summary.csv` 和 `results.json`。

原题名、训练与验证分区、六种方法的配置、训练和预测流程见[论文题名提取实验的固定提交](https://github.com/LeoAndJellyfish/paper-title-error-classification/tree/1b0ce28d265454680b5b383bbb7ff0929dca688b)。已下载该仓库固定版本时，可使用 `--import-from <本地仓库路径>` 重新对齐输入；该操作更新本案例的输入与来源记录。

## 按故障机制聚类

**[九条构造投诉](data/semantic_clustering/records.csv) · [参考汇总表](reference/semantic_clustering/summary.csv) · [完整参考结果](reference/semantic_clustering/results.json)**

投诉原型包含三种产品与三种故障机制。程序按四种判断条件生成成对分数，分别查询 12、24、36 对记录，每个条件重复 1,000 次，共 12,000 次模拟；固定种子为 `20261005`。参考划分按故障机制定义，求解枚举九条记录的全部 21,147 个划分。

```sh
python reproduction/scripts/semantic_clustering_study.py
```

输出包括 `summary.csv`、`results.json`、逐次模拟的 `replications.csv` 及重新生成的 `records.csv`，保存在 `outputs/semantic_clustering/`。`condition=perfect` 表示所查记录对均判断正确；`budget` 为查询对数，`hard_exact_recovery` 为主并列规则下二元方案完整恢复参考划分的比例。关系分数由程序生成，具体条件与两种并列规则见论文第 7 节和完整结果。

## SMS 垃圾短信比例估计

**[原始语料](data/sms/sms_spam_collection.zip) · [固定预测](data/sms/predictions.csv) · [来源与模型版本](data/sms/provenance.json) · [参考汇总表](reference/sms/summary.csv) · [完整参考结果](reference/sms/results.json)**

[UCI SMS Spam Collection](https://doi.org/10.24432/C5CC84) 归档数据有 5,574 条记录，其中 747 条标为垃圾短信；相同文本出现的记录按原始行保留。`row_id` 对应原始行号，`text_sha256` 为文本摘要，`y_spam` 为参考标签，`score` 为固定模型分数，`stratum` 为抽样层。数据集采用 CC BY 4.0，参见[UCI 数据集页面](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)和[原始说明](data/sms/original_readme.txt)。

```sh
python reproduction/scripts/sms_design_evaluation.py evaluate
```

程序在 200 和 400 条人工核验预算下分别重复抽样 10,000 次，种子为 `20261005`。结果写入 `outputs/sms/summary.csv` 与 `results.json`，逐次记录保存为 `replications.csv.gz`。运行时校验固定预测的 SHA-256，并根据归档行数检查分析总体。

### 从原始短信重新计算模型分数

固定模型为 `cross-encoder/nli-MiniLM2-L6-H768`，版本号为 `b95119ce93d3e065de6214e38cd4a97b0f2f2c6d`，使用 `onnx/model_quint8_avx2.onnx`。原运行依赖记录在 `data/sms/provenance.json`，对应安装清单为 `requirements-inference.txt`。可在独立环境中执行：

```sh
python -m pip install -r reproduction/requirements-inference.txt
python reproduction/scripts/sms_design_evaluation.py prepare
python reproduction/scripts/sms_design_evaluation.py predict
python reproduction/scripts/sms_design_evaluation.py evaluate --data-dir reproduction/outputs/sms-rescoring --output-dir reproduction/outputs/sms-rescoring-evaluation
```

`prepare` 从 UCI 和固定的 Hugging Face 模型版本下载文件，模型缓存位于 `reproduction/cache/models/sms-nli/`。新计算的输入和分数写入 `outputs/sms-rescoring/`，相应抽样结果写入 `outputs/sms-rescoring-evaluation/`。基础复现使用随附的固定分数；原始分数生成采用的描述、候选顺序、量化文件、运行库和推理设置可在来源记录及脚本中核对。

## 校验结果

三个案例运行完毕后，在仓库根目录执行：

```sh
python tools/check_materials.py --results
```

该命令核验随附文件的 SHA-256，并将三个案例新生成的汇总表和完整结果与 `reference/` 对照。数值比较采用相对容差 `1e-10` 和绝对容差 `1e-12`；Python、NumPy 版本与脚本摘要按本次运行记录。自定义输出总目录时，可通过 `--results-dir` 提供其中含有三个案例子目录的位置。
