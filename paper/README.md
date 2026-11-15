# 论文与源码

[阅读完整论文](semantic_decision_statistics.pdf) · [LaTeX 源文件](source/semantic_decision_statistics.tex) · [返回仓库首页](../README.md)

论文题目为《语义决策模型在统计分析中的应用：方法论框架与研究议程》，作者为游尹哲郡（中央财经大学），当前稿件日期为 2026 年 11 月 16 日。

`source/semantic_decision_statistics.tex` 是完整的单文件源码，公式、表格与参考文献均在其中。编译使用 XeLaTeX，依赖 `ctex`、Fandol 中文字体及源码导言区列出的宏包，可使用 TeX Live 或 MiKTeX。

从仓库根目录进入源码目录，运行两次 XeLaTeX：

```sh
cd paper/source
xelatex -interaction=nonstopmode -halt-on-error -output-directory=.. semantic_decision_statistics.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=.. semantic_decision_statistics.tex
```

生成文件为 `paper/semantic_decision_statistics.pdf`。统计程序与输入数据集中在 [reproduction](../reproduction/README.md)；论文附录 C 中的文件路径均相对于仓库根目录。
