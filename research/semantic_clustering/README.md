# 构造聚类实验

[构造记录](records.csv)来自三类产品与三类故障机制的交叉组合，每个组合一条投诉原型。脚本生成关系判断，并按故障机制评价划分。每种判断条件和查询预算重复 1,000 次，共 12,000 次。

在仓库根目录运行 `python scripts/semantic_clustering_study.py`，生成构造记录、[汇总指标](summary.csv)、[完整结果](results.json)及逐次模拟记录 `replications.csv`。实验设定与核验细节见[归档说明](https://github.com/LeoAndJellyfish/semantic-decision-statistics/blob/v2.0.0/research/semantic_clustering/README.md)。
