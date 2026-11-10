# 论文标题提取错误识别

[逐条预测](predictions.csv)覆盖 1,000 条测试记录，含 24 条按统一规则处理的空标题。参考标签 `label` 中，1 表示错误提取。`empty_title` 标记空标题。`title_identity` 是归一化标题组编号，用于配对重抽样。六种方法分别保存预测标签、分数和分数类型。

原题名、文献 ID、训练与验证分区、模型配置和逐条预测原档见[上游固定提交](https://github.com/LeoAndJellyfish/paper-title-error-classification/tree/1b0ce28d265454680b5b383bbb7ff0929dca688b)。复算所用输入及校验值见[来源记录](provenance.json)。

在仓库根目录运行 `python scripts/title_case_analysis.py`，从固定预测复算分类与概率指标，并执行 10,000 次配对标题组自助重抽样。归档输出为[指标汇总](summary.csv)和[完整结果](results.json)。
