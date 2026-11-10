# SMS 总体比例估计

[原始语料](sms_spam_collection.zip)来自 Almeida 和 Hidalgo（2011）的 SMS Spam Collection，共 5,574 行，其中 747 行标为垃圾短信。数据集采用 CC BY 4.0。来源与作者说明见 [UCI 数据集](https://doi.org/10.24432/C5CC84)和[原始说明文件](original_readme.txt)。

[固定预测](predictions.csv)保存行号 `row_id`、短信文本摘要 `text_sha256`、参考标签 `y_spam`、模型分数 `score` 及抽样层 `stratum`。语料与预测的校验值、固定模型版本和输入描述见[来源记录](provenance.json)。

在仓库根目录运行 `python scripts/sms_design_evaluation.py evaluate`。程序从随附语料和固定预测复算 200、400 两档核验预算下的抽样结果，各重复 10,000 次。输出为[汇总指标](summary.csv)、[完整结果](results.json)及逐次记录 `replications.csv.gz`。如需从短信文本重新生成模型分数，见[归档中的模型与运行说明](https://github.com/LeoAndJellyfish/semantic-decision-statistics/blob/v2.0.0/research/real_data/README.md#reproduction-environment-and-results)。
