# DeltaTeX 中文快速指南

DeltaTeX 是一个面向数学 LaTeX 的语义风险差异检查器。普通 diff 告诉你
字符发生了变化；DeltaTeX 尝试进一步说明这是求和边界、不等号、逆或转置
运算，还是上下标发生了变化。

## 安装与运行

```bash
git clone https://github.com/derricksun711-bit/deltatex.git
cd deltatex
python -m pip install .
python -m deltatex examples/paper_v1.tex examples/paper_v2.tex \
  --html report.html --json report.json
```

DeltaTeX 使用可审计的轻量规则，不是定理证明器，也不是完整 LaTeX
解析器。复杂自定义宏、多文件论文和无标签公式插入可能影响结果。

完整功能、示例、限制和开发说明见 [英文 README](./README.md)，实际输出见
[HTML 演示报告](./docs/demo-report.html)。
