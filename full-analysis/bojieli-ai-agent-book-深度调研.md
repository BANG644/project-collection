# bojieli/ai-agent-book — 李博杰《深入理解 AI Agent》开源全书

> GitHub: [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book)
> ⭐ 14,139 | 🍴 1,322 | 🐍 Python（书籍工具链）| Apache-2.0
> 创建: 2025-09-09 · 更新: 2026-07-21
> 作者: 李博杰（Bojie Li）· 5 种语言译本（中/台灣正體/英/泰/越）

## 一、项目亮点

- **核心公式 `Agent = LLM + 上下文 + 工具`** — 一句话统摄全书，成为中文 AI Agent 圈广泛引用的心智模型
- **全书正文 + 88 个配套实验全部开源**（70+ 可独立运行），不是「只给 PDF」的死书
- **「书籍即可执行课程」**：实验直接 clone 真实评测仓库（SWE-bench / OSWorld / GAIA / terminal-bench）动手跑
- **一年冲 14K stars + 5 种社区翻译**，是中文世界最系统、最开源的 Agent 工程教材

## 二、项目全景

一句话：**一本把 AI Agent 从原理讲到生产实战的开源教材**。围绕 `Agent = LLM + 上下文 + 工具`，用 10 章 + 引言 + 后记，配 88 个实验，覆盖从基础到多 Agent 协作的完整谱系。全书 Markdown 源码 + 编译版 PDF/EPUB 全部免费开放。

十章主题（来自 README 速览表）：

| 章 | 主题 | 核心 |
|----|------|------|
| 1 | Agent 基础知识 | 「模型即 Agent」+ Harness 工程才是竞争力 |
| 2 | 上下文工程 | KV Cache、提示工程、Agent Skills、上下文压缩 |
| 3 | 用户记忆和知识库 | 用户记忆、RAG、结构化索引、知识图谱 |
| 4 | 工具 | MCP 协议、感知/执行/协作三类工具、事件驱动异步 Agent、主动工具发现 |
| 5 | Coding Agent 与代码生成 | 代码是「能创造新工具的工具」，生产级 Coding Agent 全景 |
| 6 | Agent 的评估 | 评估环境/指标/统计显著性，GAIA/OSWorld/SWE-bench/tau2-bench/terminal-bench |
| 7 | 模型后训练 | 预训练/SFT/RL 三阶段、MiniMind 从零训、AdaptThink |
| 8 | Agent 的自我进化 | 不改权重也能成长、从工具使用者到创造者 |
| 9 | 多模态与实时交互 | 语音三范式、Computer Use、机器人 |
| 10 | 多 Agent 协作 | 协作框架、上下文共享/隔离、涌现的「Agent 社会」 |

## 三、核心架构（教学工程架构）

这不是软件项目，而是「可编译 + 可运行」的内容工程：

```
book/
├── introduction.md  chapter1.md ~ chapter10.md  afterword.md   # 正文源码
├── build_pdf.sh     # pandoc + xelatex + ElegantBook 编译 PDF
├── preamble.tex  cover.tex  crossref.lua  experiment_box.lua  # 排版/实验框渲染
├── gen_*_figs.py   # 用 Python 生成书中图表 → book/images/
├── svg_lib.py  strip_titles.py
└── 思考题参考答案.md
chapter1/ ... chapter10/   # 🔑 每章 N 个实验（README 列出数量）
```

书籍通过统一脚本生成中/台/英/泰/越 5 种 EPUB 3。实验目录（如 `chapter5/`、`chapter7/`）含可运行代码，部分直接 clone 外部基准仓库以确保读者「亲手跑评测」。

## 四、源码深度解读

### 4.1 「书籍即实验室」的实验编排（chapterN/ 目录）

每章 README 标注实验数（如第 5 章 12 个 Coding Agent 实验、第 7 章含 MiniMind 从零预训练 + VLM + AdaptThink）。第 6 章直接拉真实基准仓：

```bash
git clone https://github.com/SWE-bench/SWE-bench.git        chapter6/SWE-bench
git clone https://github.com/xlang-ai/OSWorld.git           chapter6/OSWorld
git clone https://github.com/laude-institute/terminal-bench.git  chapter6/terminal-bench
git clone https://github.com/bojieli/minimind.git           chapter7/MiniMind-pretrain/minimind
```

**这是本书差异化的关键**：不是「读文字」，而是「读文字 + 跑真实基准」，把 Agent 评估从概念变成可比较信号。

### 4.2 排版即工程（experiment_box.lua）

`book/experiment_box.lua` 是一个 pandoc Lua 过滤器，把 Markdown 中的「实验」块渲染成 PDF/EPUB 里的统一样式实验框。内容工程与软件工程同构：用代码（Lua/Python）控制呈现，而非手工排版。

## 五、社区口碑

- **中文 AI 圈高口碑**：核心公式与章节被广泛引用，「上下文工程」「Agent Skills」等概念与当下工程实践高度同频
- **开源透明**：全文 Markdown 开放，读者可提 PR 纠错、贡献翻译（5 种语言均为社区驱动）
- **实验驱动**：1,322 forks 多是用来跑实验、做笔记，学习黏性强
- 未做大规模社媒舆情统计（「数据不可用」），但 star 增速与翻译广度是强正面信号

## 六、竞品对比（AI Agent 学习资源）

| 维度 | 本书 | Anthropic《Building Effective Agents》 | Chip Huyen《AI Engineering》 | HF Agents Course | Lilian Weng Blog |
|------|------|----------------------------------------|------------------------------|-----------------|------------------|
| 价格 | ✅ 全免费 | ✅ 免费 | ❌ 付费 | ✅ 免费 | ✅ 免费 |
| 源码开放 | ✅ 全文 MD | ❌ 仅文章 | ❌ | ⚠️ 课程 | ❌ |
| 可运行实验 | ✅ 88 个 | ❌ | ⚠️ 部分 | ✅ | ❌ |
| 生产评估聚焦 | ✅ 第 6 章真实基准 | ⚠️ 模式为主 | ✅ | ⚠️ | ✅ |
| 语言覆盖 | 中/英/泰/越/台 | 英 | 英 | 多语 | 英 |

**差异化**：在「免费 + 开源全文 + 大量可运行实验 + 生产评估导向」这个组合上几乎无直接竞品。

## 七、核心研判

**优势**
1. 罕见地把「严谨性 + 开放性 + 动手实验」三者结合
2. 第 6 章用真实基准（GAIA/SWE-bench/OSWorld）讲评估，极具实战价值
3. 核心公式 `Agent = LLM + 上下文 + 工具` 是优秀的认知脚手架
4. 社区翻译 + 全文 MD，传播飞轮强

**风险/局限**
1. 领域演进极快，内容有老化风险（作者靠持续更新对冲）
2. 中文优先，英文译本可能滞后原版
3. 88 实验的维护负担重，依赖作者与社区长期投入

**启发（可复用思路）**
- **「书籍仓库化、实验可执行化」是技术写作的新范式**——别只交付散文，交付源码 + 可跑实验室。
- **用一句话公式（Agent = LLM + 上下文 + 工具）做认知锚点**，比堆砌概念更易传播。

## 八、应用场景与启发

- **系统学习 AI Agent 工程**：从上下文工程、RAG、MCP、Coding Agent 到多 Agent 协作，单源覆盖
- **团队内训教材**：88 实验可直接改成内部 workshop
- **对同类需求的解决思路**：要写技术书/教程时，参考「全文开源 + 实验可执行 + 核心公式锚点 + 社区翻译」组合——它让一本书变成持续生长的开源项目，而非一次性出版物。

## 九、关键文件路径速查

```
book/introduction.md          # 引言（核心公式出处）
book/chapter1.md ~ chapter10.md  # 十章正文
book/build_pdf.sh             # PDF 编译（pandoc/xelatex/ElegantBook）
book/experiment_box.lua       # 实验框渲染过滤器
chapter1/ ... chapter10/      # 各章配套实验（含真实基准 clone）
README.md                     # 章节速览表 + PDF/EPUB 下载
Releases/                     # 各语言最新构建 PDF/EPUB
```
