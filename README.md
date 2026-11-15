# 语义决策模型在统计分析中的应用

游尹哲郡 · 中央财经大学 · 2026 年 11 月修订稿 · 16 页

**[下载论文 PDF](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/download/v2.1.0/semantic_decision_statistics.pdf)　·　[下载复现材料 ZIP](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/download/v2.1.0/semantic_decision_statistics_materials_v2.1.0.zip)**

一条题名对应一个分类标签，两条投诉之间则可以记录一条同组关系。论文讨论按自然语言标准取得的标签、关系和等级怎样进入分类、聚类和测量。标题识别使用 1,000 条归档测试记录，投诉聚类使用九条构造记录和模拟判断。

## 数据与结果

| 案例 | 数据 | 结果 |
| --- | --- | --- |
| 论文标题提取错误识别 | [1,000 条测试记录的标签与预测](research/title_case/predictions.csv) | [六种方法的分类指标](research/title_case/summary.csv) |
| 按故障机制聚类 | [九条构造投诉](research/semantic_clustering/records.csv) | [不同查询次数下的聚类结果](research/semantic_clustering/summary.csv) |
| 垃圾短信比例估计（附录） | [5,574 条短信的标签与分数](research/real_data/predictions.csv) | [抽样估计结果](research/real_data/summary.csv) |

## 复算

解压复现材料，在含有 `scripts` 和 `research` 的目录中运行相应案例。三个案例均可在 CPU 上复算。[数据说明与运行命令](research/README.md)

[在线阅读论文](output/pdf/semantic_decision_statistics.pdf) · [LaTeX 源文件](semantic_decision_statistics.tex) · [v2.1.0 发布记录](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases/tag/v2.1.0)

在项目中，我使用了 [collaborative-research](https://github.com/LeoAndJellyfish/collaborative-dev-research-skills) 梳理研究路线和核查证据，并使用 [academic-less-ai-tone](https://github.com/LeoAndJellyfish/academic-less-ai-tone) 审校中文稿件。
