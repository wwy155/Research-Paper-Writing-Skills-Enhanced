# Skills: Research Paper Writing

> 重要归属说明
> 本仓库中的大部分写作经验与方法论来自彭思达老师公开的学习笔记：
> https://pengsida.notion.site/c1a22465a0fa4b15a12985223916048e
> 彭老师原始仓库：
> https://github.com/pengsida/learning_research
> 衷心感谢彭思达老师把这些宝贵经验公开分享出来。
> 我主要做了资料整理、结构化适配，以及 Skills 封装。

## 仓库介绍

当前仓库提供 1 个技能包：

- `research-paper-writing/`
  - `SKILL.md`：核心流程、使用规则，以及每次修改都要遵守的写作与排版规则
  - `references/`：按章节拆分的写作指南与模板
  - `scripts/check_tex.py`：Agent 每次修改后运行的规则检查脚本（Python 3，仅用标准库）。输出末尾列出每篇论文必须具备的几项及其是否通过，Agent 需要把这份清单贴在回复里：查明并遵守会议的模板、页数限制和附录要求；复现最相关工作的图表；与最新 SOTA 比较；至少 3 张图且每张都经过 `figure_qa.py` 检查；结果前先说明指标
  - `scripts/paperstyle.py`：图表美化方案（matplotlib 设置、固定的方法配色、LaTeX 表格宏）
  - `scripts/figure_forms.py`：常见结论对应的画法（权衡、规模扩展、鲁棒性、分类别增益、误差分布、超参数敏感性），用 `paperstyle` 绘制
  - `scripts/figure_qa.py`：画完每张图后检查（图例是否遮挡数据、内容是否重叠或超出范围、文字和标记是否过大过小、坐标范围和页边是否留白过多、子图标题是否直接写结论），并生成预览图供查看
  - `agents/openai.yaml`：Agent 元信息

常见使用场景：

- 撰写或重写 Abstract / Introduction / Method / Experiments / Conclusion
- 改善段落衔接与章节逻辑
- 做 claim-evidence 对齐检查
- 提交前从 reviewer 视角进行自审

## 先想结论，再选图形

画图之前，agent 先用一句话写下这张图要表达的结论，再选最能体现它的图形。例如“又好又省”用散点图（成本取对数轴），“提升来自哪里”用排序的增益条形图。结论与图形的对照表、改写示例和应避免的图形见 `research-paper-writing/references/figure-table-styles.md`。每张图和每个表在图表规划（figure plan）里记一行 `label: 结论 -> 图形`；正文中同一种图形最多用两次。图注先写展示的是什么，有子图时写 (a)、(b) 各是什么，最后用不超过两句话写结论，全文不超过 50 词（teaser 或 pipeline 图不超过 80 词）。表格按 `research-paper-writing/references/table-types.md` 选择类型：SOTA 对比、插件式对比、消融、效率等。画完图后由 `scripts/figure_qa.py` 逐张检查，检查脚本会拒绝自上次修改后未经检查的图。`scripts/figure_forms.py` 可直接画出每种图形（下图为示意数据）：

![六种常见结论对应的图形](docs/figure-forms.png)

## 图表美化方案

Skill 规定了四套方案：`clean`（默认）、`soft`、`vivid` 和 `mono`（适合黑白打印）。同一篇论文的所有图表只用一套方案；你没选时，agent 会用 ask 工具问你。详见 `research-paper-writing/references/figure-table-styles.md`。

![四套图表美化方案预览](docs/figure-table-styles.png)

## 安装方式

以下命令默认在仓库根目录执行。

这些命令是复制安装，更新本仓库后已安装的副本不会跟着变。更新后请删除已安装的目录再复制一次，或者一开始就用 `ln -s "$PWD/research-paper-writing" <skills 目录>/` 代替 `cp -R`。

### 1) Codex

将技能复制到 `$CODEX_HOME/skills/`：

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R research-paper-writing "$CODEX_HOME/skills/"
```

使用示例：

```text
Use $research-paper-writing to improve my paper's Introduction.
```

### 2) CC（Claude Code）

可选择全局安装或项目级安装。

全局安装：

```bash
mkdir -p "$HOME/.claude/skills"
cp -R research-paper-writing "$HOME/.claude/skills/"
```

项目级安装：

```bash
mkdir -p .claude/skills
cp -R research-paper-writing .claude/skills/
```

使用时建议在提示词中显式指定，例如：`Please use the research-paper-writing skill`。

### 3) Gemini

可将该技能复制到 Gemini 的技能目录：

```bash
mkdir -p "$HOME/.gemini/skills"
cp -R research-paper-writing "$HOME/.gemini/skills/"
```

随后在 Gemini 中直接给出具体任务（例如：重写 Abstract 并做 claim-evidence 检查）。

## 致谢

再次说明：仓库核心知识来源于彭思达老师公开笔记；我主要负责整理与 Skills 化适配。
彭老师原始仓库：https://github.com/pengsida/learning_research

## 许可证

本项目采用 MIT License，详见 [LICENSE](./LICENSE)。
