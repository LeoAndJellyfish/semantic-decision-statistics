# 语义决策模型在统计分析中的应用

游尹哲郡 · 中央财经大学 · 2026 年 11 月 10 日修订稿（16 页） · [v2.1.0](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.1.0)

[阅读论文 PDF](output/pdf/semantic_decision_statistics.pdf) · [下载 PDF](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/download/v2.1.0/semantic_decision_statistics.pdf) · [LaTeX 源文件](semantic_decision_statistics.tex) · [下载全部复现材料（ZIP）](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/download/v2.1.0/semantic_decision_statistics_materials_v2.1.0.zip)

## 数据与结果

| 案例 | 数据 | 归档结果 |
| --- | --- | --- |
| [论文标题提取错误识别](research/title_case/) | [测试集逐条预测 CSV](research/title_case/predictions.csv) · [上游数据与训练配置](https://github.com/LeoAndJellyfish/paper-title-error-classification/tree/1b0ce28d265454680b5b383bbb7ff0929dca688b) | [指标 CSV](research/title_case/summary.csv) · [完整结果 JSON](research/title_case/results.json) |
| [构造聚类实验](research/semantic_clustering/) | [九条构造记录 CSV](research/semantic_clustering/records.csv) | [汇总 CSV](research/semantic_clustering/summary.csv) · [完整结果 JSON](research/semantic_clustering/results.json) |
| [SMS 总体比例估计](research/real_data/) | [归档标签与模型分数 CSV](research/real_data/predictions.csv) · [原始语料 ZIP](research/real_data/sms_spam_collection.zip) | [汇总 CSV](research/real_data/summary.csv) · [完整结果 JSON](research/real_data/results.json) |

## 复算

解压复现材料，在根目录使用 Python 3.12 运行以下命令。

```sh
python -m pip install numpy==2.3.5
python scripts/title_case_analysis.py
python scripts/semantic_clustering_study.py
python scripts/sms_design_evaluation.py evaluate
```

标题与 SMS 案例使用随附的固定预测，聚类实验由脚本生成模拟判断。结果写入各自的案例目录。聚类和 SMS 脚本也会生成逐次模拟记录。下载文件可用 [SHA-256 清单](CHECKSUMS.sha256)核对。

如需重新生成论文，使用 `xelatex -interaction=nonstopmode -halt-on-error semantic_decision_statistics.tex` 编译至交叉引用稳定。早期稿件、完整逐次模拟记录和审校材料可从 [v2.0.0 归档](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.0.0)获取。

## 协作工具

在项目中，我使用了 `collaborative-research` 梳理研究路线和核查证据，并使用 `academic-less-ai-tone` 审校中文稿件。 [研究协作技能](https://github.com/LeoAndJellyfish/collaborative-dev-research-skills) · [中文学术写作技能](https://github.com/LeoAndJellyfish/academic-less-ai-tone)
