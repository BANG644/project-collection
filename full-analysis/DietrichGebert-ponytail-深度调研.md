# 🔬 DietrichGebert/ponytail — 全方位深度调研

## 📌 一句话定位

**让 AI 编码代理从「写得多=写得好」转变为「写得少=写得好」的行为改造插件**——通过注入 YAGNI 决策阶梯，强制代理在写代码前按七步检查必要性，减少 54% 代码量和 22% Token 消耗，且保持 100% 安全评分。

## ⭐ 项目亮点

- **七步决策阶梯（The Ladder）**：YAGNI → 已有代码复用 → 标准库 → 原生平台 → 已装依赖 → 一行解决 → 最小实现。**不是提示词里随手一提的技巧，而是刻进规则文件里每轮对话自动执行的硬约束。** 这是它和 Cursor 里随手写一句"be concise"的提示词最根本的区别。
- **跨平台统一行为**：同一条规则通过 `SKILL.md`、`.cursor/rules/`、`AGENTS.md`、`mcp/plugin` 等 16 种格式分发到 Claude Code / Codex / Cursor / Windsurf / Gemini CLI / Pi / OpenCode / Devin / Hermes / Copilot 等平台，**行为高度一致**。
- **可量化的基准测试**：不是"感觉代码变少了"——它有完整的基准测试套件（`benchmarks/`），在 Claude Code on FastAPI + React 项目上跑 12 个真实功能任务，复测 n=4，给出 LOC / Token / 成本 / 时间的精确对比数据。
- **安全底线不妥协**：基准测试中安全评分保持 100%，规则明确写死「不在信任边界、数据丢失防护、安全、可访问性上偷懒」——这是 YAGNI 的"不纳入范围"边界的教科书级实践。
- **四级强度可调节**：`lite`（建议但不强制）/ `full`（默认强制）/ `ultra`（YAGNI 极端主义） / `off`——相同的规则骨架，不同执行力度，适合不同阶段的项目。

## 🏗️ 项目架构全景

### 目录结构

```
ponytail/
├── skills/ponytail/SKILL.md          # 🌟 OpenClaw skill 标准格式（权威源）
├── .cursor/rules/ponytail.mdc        # Cursor 规则文件
├── .windsurf/rules/ponytail.md       # Windsurf 规则
├── .clinerules/ponytail.md           # Cline 规则
├── .kiro/steering/ponytail.md        # Kiro 规则
├── .github/copilot-instructions.md   # Copilot 规则
├── AGENTS.md                         # 通用规则（Claude Code 等读取）
├── .opencode/command/ponytail.md     # OpenCode 命令
├── .opencode/plugins/ponytail.mjs    # OpenCode 插件
├── .claude-plugin/plugin.json        # Claude Code 插件元数据
├── .codex-plugin/plugin.json         # Codex 插件元数据
├── .devin-plugin/plugin.json         # Devin 插件元数据
├── ponytail-mcp/                     # MCP 服务器（最轻量的端）
│   └── index.js                      #    实现 compress + retrieve
├── hooks/                            # 生命周期钩子
│   ├── ponytail-runtime.js           # 运行时钩子
│   ├── ponytail-config.js            # 配置管理
│   └── ponytail-statusline.sh        # 状态栏指示
├── commands/                         # TOML 命令定义
├── benchmarks/                       # 完整基准测试框架
│   ├── behavior.js                   # 行为测试
│   ├── correctness.test.js           # 正确性验证
│   └── promptfooconfig.yaml          # PromptFoo 配置
└── package.json                      # npm 包（插件市场分发）
```

### 核心设计哲学

**规则=产品，不是代码=产品。** 整个仓库的"产品"不是可执行代码，而是那几份 SKILL.md / AGENTS.md / rules 文件。所有代码（hooks、mcp、commands）都是为规则服务的辅助层。这是 AI Agent skill 类项目最典型的架构模式——和传统的 npm/pip 包截然不同。

### 技术栈

- **核心规则**：Markdown + YAML frontmatter（纯文本）
- **插件分发**：Node.js（package.json + mjs 插件）
- **Hook 系统**：JavaScript + Shell
- **基准测试**：PromptFoo（`promptfooconfig.yaml`）+ 自定义 JS 测试
- **MCP 端**：Node.js（`ponytail-mcp/index.js`）

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 效果 |
|------|------|
| **快速 MVP 原型** | Agent 生成的功能代码天然就是用 `input type="date"` 而非 flatpickr + wrapper 的极简版本 |
| **遗留项目瘦身** | `/ponytail-audit` 扫描全库，`ponytail:` 注释标记每一处精简路径 |
| **团队编码规范落地** | 规则注入到 CI 或 Agent 配置中，替代人工 code review 的"过度设计"检测 |
| **Token 成本敏感场景** | 在大规模 LLM 调用中直接降低 22% Token 消耗 |

### 可借鉴的解决方案模式

**「规则即跨平台适配层」的架构模式值得所有 Agent skill 项目学习。** Ponytail 不写数据库、不写 API 服务、不暴露 RESTful 接口——它就是一个规则文本的转换工厂。每条规则有三个版本：
1. **SKILL.md**（OpenClaw 标准，权威源）→ 构建脚本自动派生出
2. **AGENTS.md**（通用文本格式，所有读文件的 Agent 通用）
3. **.cursor/rules/.windsurf/rules/.clinerules/**（平台专有格式）

这种"一个权威源 → 派生出 N 个平台格式"的模式，是对 Agent skill 碎片化（Claude Code / Codex / OpenCode / Gemini CLI 各说各话）的务实回应。

### 同类需求的可参考思路

**如果你需要一个「让 AI 在特定行为维度上做出改变」的 skill，ponytail 的架构是最好的参考模板。** 它的设计回答了几个关键问题：
- 行为规则用纯文本（Markdown）写，不用 YAML 或 JSON——因为 AI 读纯文本更鲁棒
- 规则要有「层级」：核心理念（The Ladder）→ 具体行为规则（Rules）→ 强度调节（lite/full/ultra）
- 要有「不适用边界」——明确写出什么时候**不要**偷懒（安全、数据丢失、信任边界），防止 AI 误用
- 要有「可度量性」——没有基准测试的规则只是"想法"

## 🧠 核心源码解读

### 1. 七步决策阶梯（SKILL.md / rules 权威源）

这是整个项目的灵魂，以 Markdown 规则形式嵌入每个平台的配置：

```markdown
## The ladder

Stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need = skip (YAGNI)
2. **Already in this codebase?** A helper, util, type, or pattern → reuse
3. **Stdlib does it?** Use it.
4. **Native platform feature covers it?** `<input type="date">` over picker
5. **Already-installed dependency solves it?** Use it. Never add a new one.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.
```

**设计决策精妙之处**：阶梯的顺序就是"浪费程度"的排序。第 1 层（YAGNI）== 最大的浪费（根本不该写的功能），第 6-7 层 == 最小的浪费（写了但很短）。Agent 从最浪费的开始检查，一旦发现不需要就立刻停下——这意味着**大多数任务在第 1-3 步就被解决，根本走不到写代码的步骤**。这是 `-54% LOC` 的核心来源。

### 2. 强度调节的 `ponytail:` 注释系统

规则要求 Agent 对每一个特意精简的决策加上注释：

```markdown
Mark deliberate simplifications with a `ponytail:` comment.
If the shortcut has a known ceiling, the comment names the ceiling
and the upgrade path:
# ponytail: global lock, per-account locks if throughput matters
```

这个设计让「删减」变得显式、可审计。普通开发者看到 `# ponytail: X, add when Y` 能立刻知道"这里是故意缩水的，不是因为不知道更好的写法"。它把 AI 的隐式权衡变成了显式文档。

### 3. Hook 系统（`ponytail-runtime.js`）

插件模式下的运行时钩子，在 Agent 的每个响应周期注入行为：

```javascript
// hooks/ponytail-runtime.js (精简骨架)
// 钩子在每个 agent 响应周期执行，维持 ponytail 行为
// 检查当前 ponytail 级别 (lite/full/ultra/off)
// 在每次 code-gen 前预处理 prompt 上下文
// 在响应后检查代码是否遵循了阶梯规则
// 如果发现偏离（先写代码后想必要性），注入纠正
```

**设计点**：钩子系统保证了「每轮对话都激活，不会渐变回默认行为」——这是利用 LLM 做行为改造时最常遇到的问题：第一轮效果很好，第三轮倒退回老习惯。Ponytail 用在每个请求周期前中后都运行的钩子来对抗这种「行为漂移」。

## 📐 架构决策与设计哲学

- **为什么不用一个大型插件而拆成 N 份规则？** 因为不同平台对 skill/plugin 的支持程度不同。Claude Code 有完整的 `/plugin` 命令，Cursor 只读 `.cursor/rules/`，Devin CLI 读 `plugin.json`。每种格式都是一个"最小公约数"——但它们读的是同一份核心规则。
- **规则即契约**：Ponytail 不做「自己生成代码」的事，它只修改 Agent 生成代码的**决策过程**。这让它和 MCP 工具有本质区别。
- **安全边界作为产品特性**：README 把「不会在安全上偷懒」作为核心卖点——这说明作者深刻理解：YAGNI 最容易被误解为"什么都不要做"，而现实是需要**选择性地不做**。

## 🌐 全网口碑画像

### 好评共识

- **代码量减少效果显著**：中文社区评测显示"原本 100 行代码的事变成 1 行，确实做到了"——CSDN 教程、AI工具集等均有实测数据支撑。
- **跨平台覆盖完整**：被评价为"目前见过的支持平台最全的 Agent skill"，从 Claude Code 到 Vim（通过 AGENTS.md）都有覆盖。
- **安装零摩擦**：`/plugin marketplace add` + `/plugin install` 两步操作即可，中文社区教程普遍称赞"不需要改配置"。

### 差评共识 & 踩坑高发区

- **过度削减问题**：部分场景下 ultra 模式会删掉必需的边界检查——GitHub Issues 中有用户反馈"ultra 模式把我的 error handling 也干掉了"。这是 YAGNI 类项目最难平衡的线。
- **学习和适应成本**：新用户需要理解"The Ladder"的行为，否则会觉得 AI 在偷懒。有用户反馈"第一次用 pontytail 时我以为 AI 崩了，因为什么都不写"。
- **规则扩散维护难**：16 个平台的规则文件需要同步更新。`check-rule-copies.js` 脚本用于检测不一致，但本质上这是「一个权威源 → N 份副本」带来的维护债。

### 争议焦点

- **YAGNI vs 可预见性**：资深开发者群体分化——一方认为 "Ponytail 是业界急需的 AI 过工程矫正器"，另一方认为 "过度 YAGNI 会让代码库往『最简但最难改』的方向退化"。这本质上是软件工程中「预先设计 vs 敏捷演进」的老辩论在 AI 时代的重现。

## ⚔️ 竞品对比

| 维度 | Ponytail | Caveman | 普通"be concise"提示 |
|------|---------|---------|-------------------|
| **定位** | 三阶决策阶梯（YAGNI → 标准库 → 最小实现）+ 安全边界 | 纯风格控制（简洁输出）| 一次性提示词，无结构化 |
| **决策机制** | 7 步阶梯 + 强度分级 | 无明确决策流程 | 无 |
| **可量化数据** | ✅ `-54% LOC, -22% Token, -20% 成本, -27% 时间` | LOC -20%, Token +7% | 无 |
| **安全评分** | 100%（基准测试验证） | — | 不可知 |
| **跨平台** | 16+ | 有限 | 仅当前平台 |
| **审查命令** | `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt` | 无 | 无 |
| **强度调节** | lite / full / ultra / off | 无分级 | 无 |

*Caveman 数据来源：ponytail 仓库自带的 benchmarks/ 对比结果。*

## 🎯 核心研判

### 项目优势（不可替代的价值）

**Ponytail 是目前唯一一个将「YAGNI」变成 AI Agent 可执行、可度量、可审计的工程化方案的 skill。** 它的价值不在于让 AI 写更少的代码，而在于让 AI **先想再写**——以及在想和写之间架了一个决策过滤器。对于 Token 计费的云 LLM 场景，-22% Token 直接等价于-22% 成本。

### 项目风险

- **行为漂移问题**：虽然有 hooks 维持，但 LLM 在不同模型（Sonnet vs Haiku vs Opus）上对规则的遵守程度不同。规则在人读和 AI 读之间始终存在语义鸿沟。
- **YAGNI 的黑暗面**：在 fast-paced 组件的项目中，过度 YAGNI 可能导致未来重构成本远高于现在多写的几行。`ultra` 模式尤其需要注意。
- **规则文件碎片化**：16 个平台、N 份规则文件，同步维护是持续性痛点。虽然 `check-rule-copies.js` 能检测不一致，但修复本身是手工操作。

### 适用场景 & 不适用场景

**适合**：快速 MVP / Token 成本敏感 / 团队成员有过度设计倾向 / 遗留代码瘦身

**不适合**：高可靠性系统（金融交易、医疗设备）、需要显式 future-proofing 的基础设施代码、大团队协作（YAGNI 决策缺乏统一 review 出口）

### 趋势判断

**上升期。** 随着 AI coding agent 在开发者中的渗透率增加，"AI 生成过多代码"会从一个小烦恼变成主要痛点的规模级问题。Ponytail 服务的正是一个越来越大的市场。但竞争也在加剧——Cursor 和 Claude Code 都在原生引入类似的规则系统，Ponytail 需要持续维护平台兼容性来维持先发优势。

## 📂 关键文件路径速查

| 文件 | 位置 | 说明 |
|------|------|------|
| 核心规则（权威源） | `skills/ponytail/SKILL.md` | OpenClaw 标准格式，所有规则的母版 |
| 通用 Agent 规则 | `AGENTS.md` | 所有读文件的 Agent 通用 |
| Cursor 规则 | `.cursor/rules/ponytail.mdc` | Cursor 平台专用 |
| Claude Code 插件元数据 | `.claude-plugin/plugin.json` | Claude Code 插件市场注册 |
| MCP 服务器实现 | `ponytail-mcp/index.js` | 最轻量的端 |
| 基准测试套件 | `benchmarks/` | 所有量化指标的数据来源 |
| 运行时钩子 | `hooks/ponytail-runtime.js` | 维持行为不漂移 |
| 规则一致性检查 | `scripts/check-rule-copies.js` | 检测跨平台规则不同步 |
| 卸载脚本 | `scripts/uninstall.js` | 彻底清除所有平台残留 |
