# 语义决策接口方法论框架：修订与核验材料

更新日期：2026-10-05。文献检索截止日期维持为 2026-10-04。投稿期刊待定，Statistics Surveys 保留为候选。

英文题目为 **Semantic Decision Interfaces for Statistical Measurement and Population Estimation: A Methodological Framework**。原位修订的源稿为 [system_one_statistics_survey.tex](../system_one_statistics_survey.tex)，定稿为 [英文 PDF](../output/pdf/system_one_statistics_survey_english.pdf)，共 33 页、50 项参考文献。

本次有限总体权重与先导调权修订、前次记录和作者复核清单见 [revision_notes.md](revision_notes.md)。

## 核验材料

| 文件 | 内容 |
|---|---|
| [search_log.csv](search_log.csv) | 46 条检索、来源访问或复核记录；种子文献另行标明 |
| [evidence_matrix.csv](evidence_matrix.csv) | 63 条证据记录，覆盖全部参考文献及构造算例 |
| [bibliography_audit.csv](bibliography_audit.csv) | 由当前 TeX 提取的 50 项参考文献及来源链接 |
| [preprint_audit.csv](preprint_audit.csv) | 10 篇预印本的固定版本、提交时间、题名、作者及核查位置 |
| [numeric_claim_audit.csv](numeric_claim_audit.csv) | 14 项外部数字或实验设计声明、八组构造算例及新增 SMS 案例 |
| [study_provenance.csv](study_provenance.csv) | 九篇近期研究的作者关联、机构或联系信息及资助披露 |
| [dataset_overlap.csv](dataset_overlap.csv) | 数据集、数据划分或协议层面的重用情况；逐条样本交集未计算 |
| [source_manifest.csv](source_manifest.csv) | 本地来源副本、来源地址和 SHA-256 摘要 |
| [real_data/README.md](real_data/README.md) | SMS 案例设计、原始语料、固定预测及调权结果；200/400 标签预算各 10,000 次模拟，四种核验方法，共 80,000 条模拟记录 |
| [worked_examples.json](worked_examples.json) | 八组构造算例的精确分数及小数结果 |
| [pdf_review.json](pdf_review.json) | 页面检查与文本提取兼容性记录 |
| [verification.json](verification.json) | 引用、交叉引用、复算、编译及成品一致性检查 |

来源核对由 OpenAI Codex 辅助完成。作者已于 2026-10-05 确认完成科学内容、引用、代码及数值结果的最终复核。预印本作者未披露的关系和资助标为未披露；本稿作者已确认无所询供应商关系、研究经费及免费 API 额度。

## 复算与结构检查

运行：

`python scripts/reproduce_examples.py`

该脚本使用 Python 标准库及精确有理数，覆盖分类比例、关系分区、残差校正、查询相关性、序数得分、记录链接、分层分配及自适应先导设计。输入均为构造分布或矩阵。

当前修订的引用、结构、编译及成品一致性检查已记录于 `verification.json`，页面检查见 `pdf_review.json`。工作区的旧版 `scripts/audit_manuscript.py` 保留早期默认路径，未收入本次复现包。作者科学复核已完成。

## 编译与审阅

当前英文稿已通过本机 MiKTeX XeLaTeX 编译。最终日志无 LaTeX 警告、未解析引用或溢出提示；页面核验情况见 `pdf_review.json`。

PDF 默认文本提取中的部分词间连写与提取距离阈值有关。源文件、放大渲染、不同解析器及词间阈值已分别对照。内置编译器仍返回 `Unable to find standard directories for platform`；当前 LaTeX 编辑器保留。先前中文 PDF 继续保存在原路径。

## 投稿准备

当前采用单文件 `article` 结构和作者—年份引文。正式模板随最终期刊选择调整。如选择 Statistics Surveys，可依据 [IMS 官方作者包](https://www.e-publications.org/ims/support/imsco-instructions.html)及其[模板仓库](https://github.com/vtex-soft/texsupport.ims_cosponsored-ss)完成迁移。

作者已确认完成最终复核。通讯作者邮箱随投稿信息填写。稿件、代码、固定预测、模拟结果及校验信息见 [v1.0.0 归档](https://github.com/LeoAndJellyfish/semantic-decision-statistics/tree/v1.0.0)。当前稿尚未提交期刊、arXiv 或其他平台。

