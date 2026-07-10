# iOfficeAI/OfficeCLI — 为 AI Agent 而生的 Office 套件 CLI

> **调研日期**: 2026-07-11 | **Stars**: 14,303⭐ (当日 +1,210) | **Forks**: 965
> **语言**: C# (.NET 10, 自包含 AOT 单文件) | **许可**: Apache License 2.0
> **创建**: 2026-03-15 | **最近推送**: 2026-07-10 | **仓库**: https://github.com/iOfficeAI/OfficeCLI
> **官网**: https://officecli.ai

---

## 项目亮点（差异化）

- **内置高保真渲染引擎 = 给 AI "眼睛"**：自研 HTML 渲染引擎把 `.docx/.xlsx/.pptx` 渲染成 HTML/PNG，让 Agent 能"看见"自己生成的版面并修正溢出/重叠，而无需安装 Office。这是它相对 python-docx 等库最本质的差异化。
- **三层渐进式架构（L1→L2→L3）**：读视图 → DOM 元素操作 → 原始 XML 兜底，Agent 由浅入深，最小化 token 消耗。
- **350+ Excel 函数落地即算**：写入 `=SUM(A1:A2)` 后取回已是计算值，无需绕道 Office 重算；原生 OOXML 透视表一条命令生成。
- **单二进制零安装**：.NET 运行时已嵌入二进制，无运行时、无 Office、跨平台（mac/win/linux arm64/x64）。
- **原生 MCP Server + 自动安装**：一条 `officecli mcp claude` 把全部文档能力暴露为 JSON-RPC 工具；安装时自动探测并写入各 Agent 的 skill 文件。

## 项目全景

OfficeCLI 定位是"全球首个、最好的面向 AI Agent 的 Office 套件"，用一行命令把 Word/Excel/PowerPoint 的创建、读取、修改、校验能力交给任意 AI 编程 Agent。它要解决的核心痛点是：**传统 Office 自动化要么依赖笨重的 Office/LibreOffice 安装（无法 headless/CI），要么依赖 python-docx/openpyxl 这类库——Agent 能改 DOM 但"看不见"渲染结果，常常生成版面溢出的文档而不自知**。

项目由 iOfficeAI 维护（同团队还有 AionUi 桌面端、Morph 动画），2026-03 创建，2026-07 仍在高频迭代（当日 Trending +1,210）。社区活跃度中等偏高，Discord 有专门频道，Wiki 文档极详尽（每个命令/元素/属性都有页面）。

## 核心架构

```
officecli (单二进制, .NET 自包含)
├── Program.cs                  # 入口
├── CommandBuilder.*            # 命令构造器模式 (Add/Set/Get/Query/Batch/Raw/Help/View/Dump/Merge/Watch...)
├── Core/                       # 各格式 OOXML 解析/序列化内核
├── Handlers/                   # 命令处理分发
├── Help/                       # 内建 help 系统 (agent 不必猜测属性名)
├── McpServer.cs                # 内置 MCP Server (JSON-RPC, 单 command 参数透传)
├── McpInstaller.cs             # 探测并注册到 Claude/Cursor/VSCode/LMStudio
├── ResidentClient.cs           # 常驻模式客户端 (命名管道)
└── ResidentServer.cs           # 常驻模式服务端 (60s 空闲自动 flush)
```

**三层架构（start simple, go deep only when needed）**：

| 层 | 用途 | 代表命令 |
|----|------|----------|
| **L1 Read** | 内容语义视图 | `view` (text/annotated/outline/stats/issues/html/svg/screenshot) |
| **L2 DOM** | 结构化元素操作 | `get` `query` `set` `add` `remove` `move` `swap` |
| **L3 Raw XML** | XPath 直通，万能兜底 | `raw` `raw-set` `add-part` `validate` |

路径寻址采用 1-based 索引的本地名（如 `/slide[1]/shape[2]`），Agent 无需理解 XML 命名空间即可导航文档。

## 源码深度解读

**1. CommandBuilder 模式（命令即对象）**
所有动词被拆成 `CommandBuilder.Add.cs` / `CommandBuilder.Set.cs` / `CommandBuilder.GetQuery.cs` / `CommandBuilder.Batch.cs` / `CommandBuilder.Raw.cs` 等独立文件，每个文件负责一类操作的参数解析与执行。这种"一个动词一个类"的切分让 `help` 系统能针对单个元素类型精确吐出属性名与取值格式（如 `officecli pptx set shape.fill`），避免 Agent 盲猜——这是 README 反复强调的"self-healing"能力的实现基础。

**2. Resident 常驻模式（命名管道 + 自适应 flush）**
`ResidentClient.cs` / `ResidentServer.cs` 通过命名管道把文档常驻内存，多步操作零文件 I/O。`ResidentServer` 带"自适应 2–10s 空闲 flush"（按实测保存成本缩放），`OFFICECLI_RESIDENT_FLUSH=each` 可强制每次变更落盘。设计权衡很清晰：officecli 自身的 `get/query/view` 永远看到最新编辑，所以工作流内从不需要 save；只有"非 officecli 程序（python-docx、Word、渲染器）要读文件"前才需 `save`/`close`。这种"延迟 flush"对 Agent 长链任务显著降延迟。

**3. MCP Server 的极简契约**
`McpServer.cs` 把全部命令收敛为一个 `command` 字符串参数，原样透传给 CLI（`{"command":"help docx paragraph"}`），而非结构化 `{"format","type"}` 对象。好处是 MCP 工具 schema 极简、与 CLI 行为完全一致，无需维护两套参数映射。

## 社区口碑

- **正向**：README 展示的全 AI 生成文档（学术论文/年报/销售看板/融资 deck）质量高，渲染引擎闭环（render→look→fix）是 Agent 文档自动化的关键缺口填补者；Apache 2.0 + 单二进制让团队易落地到 CI/Docker。
- **争议点**：自称"world's first"偏营销；作为 2026-03 才创建的新项目，生态与稳定性仍需时间验证；构建仍需 .NET 10 SDK（尽管运行时不依赖）。
- **时机**：2026-07-10 当日 GitHub Trending +1,210，处于上升期，与"AI Agent 操作 Office"赛道热度吻合。

## 竞品对比

| | OfficeCLI | MS Office | LibreOffice | python-docx/openpyxl |
|---|---|---|---|---|
| 开源免费 | ✅ Apache 2.0 | ✗ | ✅ | ✅ |
| AI-native CLI + JSON | ✅ | ✗ | ✗ | ✗ |
| 零安装单二进制 | ✅ | ✗ | ✗ | ✗ (需 Python) |
| 路径寻址元素 | ✅ | ✗ | ✗ | ✗ |
| 内置渲染引擎 | ✅ | ✗ | ✗ | ✗ |
| Headless HTML/PNG | ✅ | ✗ | 部分 | ✗ |
| 模板 merge `{{key}}` | ✅ | ✗ | ✗ | ✗ |
| dump→batch 往返 | ✅ | ✗ | ✗ | ✗ |
| 三格式一体 | ✅ | ✅ | ✅ | 分库 |

**补充研判**：相对 `python-pptx`/`docxcompose` 等库，OfficeCLI 赢在"Agent 友好"（确定性 JSON、路径寻址、渲染闭环、MCP），而非功能广度；对纯人类 Python 脚本场景，python-docx 仍更轻。赛道内暂无同形态直接竞品（其他"AI Office"多为 SaaS 或桌面应用，非 CLI+SDK+MCP 三位一体）。

## 核心研判

**优势**
- 渲染引擎是真正的护城河：把"Agent 看不见版面"这个行业顽疾在二进制内解决，CI/Docker 无头环境也能闭环。
- 三层架构 + 路径寻址 + 内建 help，把 token 成本与 Agent 出错率同时压低，工程取舍成熟。
- MCP + 自动安装降低接入门槛，契合"Agent 直接操作办公文档"的明确需求增长。

**局限 / 风险**
- 项目极新（<4 个月），API 与二进制仍在快速变化，生产长尾风险待观察。
- 重度功能（350+ 函数、透视表、mermaid→形状、3D .glb）实现复杂度高，边界 bug 概率不低。
- 与用户已有的 docx/office 类技能生态可能重叠，需明确"CLI 引擎"vs"技能编排"的分工。

**定位**：AI Agent 办公文档自动化的底层引擎首选评估对象；适合"Agent 批量生成/校验报告、PPT、Excel"的 CI 与桌面场景。

## 关键文件速查

| 路径 | 功能 |
|------|------|
| `src/officecli/Program.cs` | CLI 入口 |
| `src/officecli/CommandBuilder.*.cs` | 各动词命令构造器（Add/Set/Get/Query/Batch/Raw/View/Dump/Merge/Watch） |
| `src/officecli/Core/` | OOXML 解析/序列化内核 |
| `src/officecli/McpServer.cs` | 内置 MCP Server（单 `command` 参数透传） |
| `src/officecli/McpInstaller.cs` | 自动探测并注册到各 Agent |
| `src/officecli/ResidentClient.cs` / `ResidentServer.cs` | 常驻模式（命名管道 + 自适应 flush） |
| `SKILL.md` (根, 403 行) | Agent 技能主文件（L1/L2/L3 策略、MCP 设计、specialized skills 路由） |
| `skills/officecli-pptx` `skills/officecli-docx` `skills/officecli-xlsx` `skills/officecli-financial-model` `skills/officecli-academic-paper` `skills/morph-ppt` 等 | 11 个专用技能（融资 deck/学术论文/财务模型/数据看板/Morph 动画） |
| `schemas/` `sdk/` `plugins/` | JSON schema、Python/Node SDK、可扩展插件（导出 .pdf/.doc/.hwpx） |
