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
  - `scripts/check_tex.py`：Agent 每次修改后运行的规则检查脚本（Python 3，仅用标准库）。输出末尾列出每篇论文必须具备的几项及其是否通过，Agent 需要把这份清单贴在回复里：先写清论文的故事，全文围绕它展开，每条结论都有图表作为证据；Agent 按循环工作：修改、运行所有检查、审稿（可用时并行启动多个审稿子 agent）、修复问题，并在论文中记录每一轮，直到某一轮既没有错误也没有新的审稿意见为止；选 3-5 篇与本文最相近的论文作为风格参考，逐页看过，写作风格以它们为准，图表展示什么由 agent 自己决定，不照搬；查明并遵守会议的模板、附录要求和三项页数限制：正文（long paper）多少页、参考文献是否有页数上限、全文总页数是否有上限（查不到时默认正文 8 页，参考文献不计入）；最相关工作的图表在能说明我们方法的特点或审稿人会期待时复现；与最新 SOTA 比较；至少 3 张图且每张都经过 `figure_qa.py` 检查，其中方法部分必须有一张架构图，由 agent 用 `generate_image` 工具生成（工具不可用或生成失败时会询问用户）；必须用 pdflatex 编译（与 Overleaf 和 arXiv 一致，缺少时不许改用其他工具，要与用户沟通直到装好），编译出的 PDF 每一页都用 `page_qa.py` 看过；论文需要的实验由 agent 自己跑完，或记录为运行中、受阻（并已询问用户）；结果前先说明指标。它还会标出每一句讨论我们的方法输在哪里的句子（论文要主动推销自己的故事，用一切支持它的结果作证据），以及口语化的表达（缩写、口语词、感叹句、反问句）和超短句，保证语句正式、具有学术专业性
  - `scripts/figure_qa.py`：画完每张图后检查（图例是否遮挡数据、内容是否重叠或超出范围、文字和标记是否过大过小、坐标范围和页边是否留白过多、子图标题是否直接写结论），并生成预览图供查看
  - `scripts/page_qa.py`：每次编译后强制 agent 逐页查看 PDF。它渲染每一页，框出留白（栏内空白、栏提前结束、图比栏窄、段落间被拉开的空白）、超出页边的内容和过短的段落末行，并以图片查看器能保留的最高分辨率输出彩色图片：正文每页切成四块（约 200 dpi），其余页切成两半（约 150 dpi），被切开的图表另外完整输出（最高 300 dpi）。每张图片印有一个校验码，agent 只有真正看过图片才能拿到；重新编译后只需查看有变化的页。当前 PDF 的校验码确认之前，`check_tex.py` 不会通过。加上 `--reference` 时，它为风格参考论文生成概览拼图，用来学习它的写法和结构
  - `agents/openai.yaml`：Agent 元信息

常见使用场景：

- 撰写或重写 Abstract / Introduction / Method / Experiments / Conclusion
- 改善段落衔接与章节逻辑
- 做 claim-evidence 对齐检查
- 提交前从 reviewer 视角进行自审

## 图表：有信息量、好看、有说服力

图不必证明故事中的某条结论，因为一篇论文有很多图，结论却只有几条。只要展示有信息量的内容，例如结果、对比、方法如何工作、模型学到了什么，就值得放。最重要的是画得好看、有说服力：全文统一的风格，印刷尺寸下清晰的文字，整齐的排版，直接的对比加放大的细节，诚实的坐标轴。agent 先用一句话写下每张图展示什么，再选最清楚的形式，反复重画直到好看且有说服力，不照搬别的论文的图。每张图表在图表计划中占一行（`label: 展示的内容 -> 形式`），作为某条结论证据的图表标上它的编号（如 `[C1]`），保证每条结论都有证据。正文中同一种形式最多用于两张图。方法部分必须有一张架构图，展示输入、每个模块、数据流和输出：agent 用 `generate_image` 生成，逐字核对图中每个标签，工具不可用或多次生成失败时向用户询问。Caption 先说明展示的是什么，再分别说明各子图，最后用不超过两句话给出结论，总长不超过 50 词（teaser 或 pipeline 图不超过 80 词）。详见 `research-paper-writing/references/figures.md` 和 `research-paper-writing/references/table-types.md`。画完后用 `scripts/figure_qa.py` 检查每张图，最后一次修改后没检查过的图会被检查脚本拒绝。

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
