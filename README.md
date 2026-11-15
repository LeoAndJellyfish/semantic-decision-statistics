# 语义决策模型在统计分析中的应用

游尹哲郡 · 中央财经大学 · 2026 年 11 月 16 日修订稿

语义决策模型提供的类别、成对关系与等级概率，如何进入分类、聚类和测量？本研究结合论文题名提取案例、构造聚类实验与 SMS 抽样案例，讨论判断质量、概率校准、响应性能和总成本。Jev 的快速结构化响应与校准决策定位依据官方文档；分类案例使用 Tev1，聚类关系分数由程序按设定生成。

**[阅读论文](paper/semantic_decision_statistics.pdf) · [下载论文 PDF](https://raw.githubusercontent.com/LeoAndJellyfish/semantic-decision-statistics/main/paper/semantic_decision_statistics.pdf) · [下载论文与复现材料 ZIP](https://github.com/LeoAndJellyfish/semantic-decision-statistics/archive/refs/heads/main.zip)**

## 阅读与使用

| 需要的内容 | 入口 |
| --- | --- |
| 完整论文与可编辑源码 | [论文 PDF](paper/semantic_decision_statistics.pdf) · [LaTeX 源码](paper/source/semantic_decision_statistics.tex) · [编译说明](paper/README.md) |
| 直接查看实验结果 | [题名识别](reproduction/reference/title_case/summary.csv) · [投诉聚类](reproduction/reference/semantic_clustering/summary.csv) · [SMS 比例估计](reproduction/reference/sms/summary.csv) |
| 复算论文中的指标和模拟 | [数据、环境与运行说明](reproduction/README.md) |
| 追溯原始实验和模型配置 | [题名实验固定版本](https://github.com/LeoAndJellyfish/paper-title-error-classification/tree/1b0ce28d265454680b5b383bbb7ff0929dca688b) · [SMS 数据与模型来源](reproduction/data/sms/provenance.json) |

## 三个案例

| 案例 | 材料与复现内容 | 数据 |
| --- | --- | --- |
| 论文题名提取错误识别 | 对齐六种方法的固定预测，复算分类指标、概率指标、配对自助区间与错误代价 | [1,000 条测试记录的标签与预测](reproduction/data/title_case/predictions.csv) |
| 按故障机制聚类 | 九条构造投诉、36 对关系；四种判断条件、三个查询预算，各重复 1,000 次 | [投诉原型](reproduction/data/semantic_clustering/records.csv) |
| 垃圾短信比例估计 | 5,574 条归档短信及固定辅助分数；在两档核验预算下比较抽样估计 | [原始语料](reproduction/data/sms/sms_spam_collection.zip) · [标签与分数](reproduction/data/sms/predictions.csv) |

## 开始复现

下载上方 ZIP 并解压，在仓库根目录运行以下命令。基础复现使用 Python 3.12 与 NumPy 2.3.5，可在 CPU 上复算。

```sh
python -m pip install -r reproduction/requirements.txt
python tools/check_materials.py
python reproduction/scripts/title_case_analysis.py
python reproduction/scripts/semantic_clustering_study.py
python reproduction/scripts/sms_design_evaluation.py evaluate
python tools/check_materials.py --results
```

重跑结果写入 `reproduction/outputs/`。`reproduction/data/` 保存固定输入，`reproduction/reference/` 保存论文采用的未舍入结果，两者分别供输入读取和结果对照。[各案例说明与可选的模型分数重算](reproduction/README.md)

## 目录

```text
paper/                       论文 PDF、LaTeX 源码及编译说明
reproduction/
  scripts/                   三个案例的分析程序
  data/                      固定输入、来源记录与原始语料
  reference/                 论文采用的汇总表和完整结果
  outputs/                   本次运行生成的结果
  requirements.txt           基础复现依赖
  requirements-inference.txt SMS 模型分数重算依赖
  README.md                  运行命令、字段和方法说明
tools/check_materials.py      文件校验与复现结果对照
CHECKSUMS.sha256              随附文件的 SHA-256 校验值
```

`outputs/` 和模型缓存于运行时生成。[历史版本](https://github.com/LeoAndJellyfish/semantic-decision-statistics/releases)保留在 GitHub Releases，各版本材料以其随附说明和校验值为准。

## 引用与致谢

游尹哲郡. (2026). 语义决策模型在统计分析中的应用：方法论框架与研究议程. 中央财经大学，2026 年 11 月 16 日修订稿。

SMS Spam Collection 的来源与许可见[UCI 数据集页面](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)和[原始说明](reproduction/data/sms/original_readme.txt)。题名案例的原始数据分区、模型设置和固定预测来自上方链接的独立实验仓库。

在项目中，我使用了 [collaborative-research](https://github.com/LeoAndJellyfish/collaborative-dev-research-skills) 梳理研究路线和核查证据，并使用 [academic-less-ai-tone](https://github.com/LeoAndJellyfish/academic-less-ai-tone) 审校中文稿件。
