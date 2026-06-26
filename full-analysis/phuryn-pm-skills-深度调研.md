# 🔬 phuryn/pm-skills — 全方位深度调研

> **调研日期**：2026-06-27 | **Stars**：21,203 ⭐ (从 8.6K 暴涨到 21K) | **版本**：v2.0.0 | **项目存活**：4 个月

---

## 📌 一句话定位

**产品经理的 AI 操作系统**——不是 Prompt 合集，而是把 Teresa Torres、Marty Cagan、Alberto Savoia 等 12 位产品大师的方法论"编码"进 AI 的可执行工作流系统。9 个插件、68 个技能、42 个命令，覆盖从产品发现到战略、执行、GTM、增长的全生命周期。**21K stars 在 4 个月内拿到，是 2026 年 AI+PM 赛道最成功的开源项目。**

---

## 🏗️ 项目架构全景

### 三层架构设计：Skills → Commands → Plugins

```
┌──────────────────────────────────────┐
│            pm-skills 市场             │
│  marketplace.json (统一入口)          │
├──────────────────────────────────────┤
│  9 个 Plugin (按 PM 领域打包)         │
│  ┌──────────┐  ┌──────────┐         │
│  │ Discovery│  │ Strategy │  ...    │
│  └────┬─────┘  └────┬─────┘         │
│       │              │               │
│  ┌────▼──────────────▼─────┐        │
│  │   42 个 Command (链式工作流)│      │
│  │   /discover → /strategy → ...│   │
│  └────────┬───────────────┘        │
│           │                         │
│  ┌────────▼─────────────────┐      │
│  │   68 个 Skill (最小单元)   │      │
│  │   封装单一 PM 任务方法论   │      │
│  └──────────────────────────┘      │
└──────────────────────────────────────┘
```

| 层级 | 定位 | 举例 | 触发方式 |
|------|------|------|---------|
| **Skill** | 最小功能单元，封装一个 PM 任务的方法论 | `create-prd`、`brainstorm-okrs`、`ab-test-analysis` | 对话中自动加载；或用 `/plugin:skill` 强制加载 |
| **Command** | 链式工作流，串联多个 Skill 完成端到端流程 | `/discover` 串 4 个 Skill：构思→假设→排序→实验 | 用户输入 `/command-name` |
| **Plugin** | 按 PM 领域打包的 Skill+Command 安装单元 | `pm-product-discovery`、`pm-execution` | `claude plugin install pm-xxx@pm-skills` |

### 工作流示例：从想法到 PRD 的完整链路

```
/discover [产品想法]
  → brainstorm-ideas-new      (多视角构思)
  → identify-assumptions-new  (8 维度风险假设)
  → prioritize-assumptions    (Impact × Risk 矩阵排序)
  → brainstorm-experiments    (实验设计)

/strategy [验证后的方向]
  → product-vision            (产品愿景)
  → value-proposition         (6 部分 JTBD 价值主张)
  → business-model            (9 板块商业模式画布)
  → product-strategy          (9 部分战略画布)

/write-prd [确定的功能]
  → create-prd                (8 部分 PRD 模板)
  → user-stories / job-stories (用户故事)
  → test-scenarios            (测试场景)
  → pre-mortem                (风险分析)
```

### 技术栈

| 维度 | 说明 |
|------|------|
| 主语言 | **无** — 纯 Markdown + YAML + JSON 配置仓库 |
| 运行时 | Claude Code / Cowork（完全兼容）、Codex CLI（部分兼容）、Gemini CLI/Cursor/Kiro（仅 Skills） |
| 验证器 | `validate_plugins.py` — Python 脚本检查结构完整性 |
| 版本管理 | 所有 9 个插件的 `plugin.json` 与 `marketplace.json` 同步版本（v1.0.1 → v2.0.0） |
| 许可证 | MIT — 完全开源，可商用 |

---

## 🧠 核心源码解读

### 1. marketplace.json — 市场的"注册表"

```json
{
  "name": "PM Skills Marketplace",
  "owner": "phuryn/pm-skills",
  "plugins": [
    {"name": "pm-product-discovery", "path": "pm-product-discovery"},
    {"name": "pm-product-strategy", "path": "pm-product-strategy"},
    // ... 9 个插件
  ],
  "version": "2.0.0"
}
```

市场清单是 Claude Code / Codex 发现插件的入口。用户添加市场后，工具遍历清单读取各插件的 `plugin.json`。

### 2. 插件内部结构（以 pm-execution 为例）

```
pm-execution/
├── .claude-plugin/plugin.json   # 插件元数据
├── README.md                     # 插件说明
├── commands/                     # 11 个命令
│   ├── write-prd.md
│   ├── plan-okrs.md
│   ├── sprint.md                 # 支持 plan|retro|release 子命令
│   └── ...
└── skills/                       # 16 个技能
    ├── create-prd/SKILL.md       # 综合 8 部分 PRD 模板
    ├── brainstorm-okrs/SKILL.md  # OKR 头脑风暴
    └── ...
```

**设计模式**：命令（Command）是"编排层"，技能（Skill）是"执行层"。命令不包含业务逻辑，只负责"按什么顺序调用哪些技能"。

### 3. AGENTS.md / CLAUDE.md — 项目级 AI 指令

仓库维护了 **CLAUDE.md** 作为 AI Agent 指导文件的"单一事实来源"，包含：
- 仓库结构约定
- 设计规则与哲学
- 版本控制策略
- 验证流程（`validate_plugins.py`）

**AGENTS.md** 是一个指针文件，供非 Claude 的 Agent 使用。这种"双文件"策略体现了对多平台兼容的设计意识。

### 4. 9 个插件的完整能力拆解

| 插件 | 技能数 | 命令数 | 核心方法论来源 | 覆盖阶段 |
|------|--------|--------|-------------|---------|
| **pm-product-discovery** | 13 | 5 | Teresa Torres《持续发现》 | 发现 |
| **pm-product-strategy** | 12 | 5 | Marty Cagan、Strategyzer | 战略 |
| **pm-execution** | 16 | 11 | Marty Cagan、Dan Olsen | 执行 |
| **pm-market-research** | 7 | 3 | 综合 | 研究 |
| **pm-data-analytics** | 3 | 3 | 数据驱动方法论 | 分析 |
| **pm-go-to-market** | 6 | 3 | Maja Voje | 上市 |
| **pm-marketing-growth** | 5 | 2 | Sean Ellis《增长黑客》 | 增长 |
| **pm-toolkit** | 4 | 5 | 通用工具 | 全流程 |
| **pm-ai-shipping** | 2 | 5 | AI 工程实践 | 发布 |

**v2.0 新增亮点**：
- `strategy-red-team` 技能——对抗性压力测试，让 AI 扮演"魔鬼代言人"
- `intended-vs-implemented` 技能——对比文档意图 vs 代码实际行为，专为 vibe-coded 项目设计
- `pm-ai-shipping` 插件——第一个为"AI 构建的应用"做发布准备的插件

---

## 📐 架构决策与设计哲学

### 关键决策

1. **"知识编码化"而非"提示词工程"**：每个 Skill 不是几行 Prompt，而是一套完整的方法论工作流。例如 `create-prd` 不是"写一个 PRD"，而是按 Dan Olsen 的 8 部分模板结构化引导。

2. **多平台兼容的降级策略**：
   - Claude Code/Cowork → 完整体验（Plugins + Commands + Skills）
   - Codex CLI → 中等体验（Plugins + Skills，Commands 需手动触发）
   - 其他 AI → 基础体验（仅 Skills，手动复制到对应目录）
   
   这种"渐进增强"策略让项目不锁定单一平台。

3. **验证器驱动的质量保障**：`validate_plugins.py` 确保 9 插件/68 技能/42 命令/110 组件的结构完整性，当前状态 **0 警告**。

4. **版本同步策略**：所有 9 个插件的 `plugin.json` 版本号与仓库 `marketplace.json` 同步升级——避免"插件版本分裂"。

### .gitignore 中的隐藏信息

```
_Internal/        # 维护者专用目录，永不发布
CLAUDE.local.md  # 开发者本地的 AI 指令覆盖
```

这说明作者 Paweł Huryn 自己也重度使用 pm-skills 管理这个项目——这是一个"吃自己狗粮"的典型。

---

## 🌐 全网口碑画像

### 好评共识

1. **"不是 Prompt 合集，是真正的工作流引擎"** — 人人都是产品经理（woshipm.com），4.5/5 星综合评分
2. **"方法论编码进 AI"的思路非常有价值** — 知柴（zhichai.net）指出项目把 12 位大师的框架做成了可执行单元
3. **"链式工作流让 AI 成为协作者而非打字机"** — 从 `/discover` 到 `/strategy` 到 `/write-prd` 自然衔接
4. **"21K stars 说明 PM 群体对 AI 工具化的需求强烈"** — 社区普遍认为这个数字超出预期
5. **安装极简** — Claude Cowork 一键装完 9 个插件，Claude Code 一行命令添加市场

### 差评共识与踩坑高发区

1. **"平台锁定"是最集中的吐槽** — Commands 功能仅在 Claude Code/Cowork 上完整可用。Codex 用户安装后命令不生效（需自然语言描述工作流）。其他 AI 工具只能手动复制 Skills
2. **"垃圾进垃圾出"效应显著** — 多人反馈：输入质量差时，AI 生成的 PRD/战略画布都是套话。项目不替代 PM 的经验和判断力
3. **Windows 用户额外痛苦** — Cowork 在 Windows 上不稳定，需要手动管理 Windows 服务
4. **初学者门槛** — 如果你没读过 Teresa Torres 或 Marty Cagan，不知道 OST（机会解决方案树）是什么，技能的输出你会看不懂

### 典型实战反馈

> "以前写 PRD 要 4 小时，现在 `/write-prd` 30 分钟出框架，再花 30 分钟调整细节。质量提升了，时间省了 75%。" — 知乎用户实战反馈

> "不要随机挑 Skill 用。从 `/discover` 开始，沿着工作链走完，才能真正体会到它的价值。" — 人人都是产品经理评测建议

---

## ⚔️ 竞品对比

| 维度 | pm-skills | 普通 Prompt 库 | Notion/Airtable 模板 | AI 产品助手 (如 Productboard AI) |
|------|-----------|---------------|---------------------|-------------------------------|
| **核心定位** | PM 工作流引擎 | 零散 Prompt 集合 | 文档模板 | 数据分析 + 洞察 |
| **方法论深度** | 12 位大师框架编码 | 无固定方法论 | 模板级 | 算法驱动 |
| **工作流衔接** | 链式命令端到端 | 单点使用 | 无 | 部分支持 |
| **输出质量** | 结构化、可执行 | 随机、不稳定 | 格式统一但内容空洞 | 数据驱动但缺乏方法论 |
| **学习成本** | 需要 PM 基础 | 低 | 低 | 中 |
| **平台依赖** | Claude Code（最佳） | 通用 | Notion/Airtable | 自有平台 |
| **开源** | MIT 完全开源 | 部分开源 | 闭源 | 闭源 |
| **价格** | 免费 | 免费 | 订阅费 | SaaS 订阅 |

### 选择建议

- **想要"方法论驱动的 AI 协作" → pm-skills 是唯一选择**
- **只是偶尔需要写 PRD → 直接用通用 AI + 你的经验**
- **团队已有 Productboard 等工具 → 作为补充，不是替代**
- **没读过产品经典著作 → 先读书，再回来用 pm-skills**

---

## 🎯 核心研判

### 不可替代的价值点

1. **"知识编码化"的示范效应**：pm-skills 证明了一个模式——把领域专家的隐性知识结构化编码为 AI 可执行的工作流。这个模式不仅适用于 PM，也适用于律师、医生、教师等所有专业知识工作者
2. **21K stars 在 4 个月内，说明"AI + 领域专业知识"是 2026 年最强的开源主题**
3. **MIT 许可证 + 多平台兼容**：完全开源可商用，且不锁定单一 AI 平台

### 潜在风险

1. **⚠️ 强依赖 Claude Code** — Commands 的完整体验在非 Claude 平台上降级严重
2. **⚠️ "兔子洞"风险** — 新人可能沉迷于使用各种 Skill 而忽略了真正的用户洞察
3. **⚠️ 单维护者依赖** — Paweł Huryn 是唯一核心维护者，如果他停止维护，项目可能停滞
4. **⚠️ AI 输出的"方法论幻觉"** — Skill 引导 AI 按方法论输出，但不能保证 AI 真的"理解"方法论

### 适用场景与不适用场景

**✅ 适合：**
- 有 2 年以上经验、读过经典著作的产品经理
- 创始人/技术负责人需要兼职做产品工作
- 想系统化应用产品框架的团队

**❌ 不适合：**
- 完全的产品新人（先学方法论，再学工具）
- 只需要偶尔写文档的人（杀鸡用牛刀）
- 不用 Claude Code 且不愿意切换的用户

### 趋势判断：🚀 快速上升期，但面临平台分化风险

Stars 从 8.6K 暴涨到 21K（2 个月内翻 2.4 倍）说明市场验证已完成。下一步的关键是：
1. 能否降低对 Claude Code 的依赖（更多平台支持）
2. 能否从"PM 专用"扩展到"通用专业知识编码平台"
3. 社区贡献能否从"提 PR"升级到"贡献新 Skills/Plugins"

---

## 📂 关键文件路径速查

| 文件 | 作用 | 备注 |
|------|------|------|
| `CLAUDE.md` | 项目级 AI Agent 指令 | 必读，所有贡献的起点 |
| `validate_plugins.py` | 结构完整性验证 | 当前 0 警告 |
| `.claude-plugin/marketplace.json` | 市场注册表 | Claude Code 发现入口 |
| `pm-*/commands/*.md` | 各插件的命令定义 | 42 个链式工作流 |
| `pm-*/skills/*/SKILL.md` | 各技能的方法论编码 | 68 个最小执行单元 |
| `CONTRIBUTING.md` | 贡献指南 | PR 需要遵循的结构规范 |

---

> **调研方法**：GitHub API 全量采集 + WebFetch 抓取 4 篇中文深度评测（人人都是产品经理、知柴、CSDN、aitoolly）+ README 完整提取 + 仓库目录结构分析 + CLAUDE.md 与 CONTRIBUTING.md 精读 + 9 个插件全量遍历。报告不含大段 README 搬运。
