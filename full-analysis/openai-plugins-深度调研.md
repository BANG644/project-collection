# 🔬 openai/plugins — 全方位深度调研

> **调研日期**：2026-06-27 | **Stars**：3,597 ⭐ (快速增长中) | **项目存活**：3 个月

---

## 📌 一句话定位

**OpenAI 官方维护的 Codex 插件精选合集**——它不是"一个插件"，而是 Codex 生态的"应用商店精选区"。9 个经过生产验证的领域插件，覆盖 Figma 设计落地、Notion 知识管理、iOS/macOS/Web 应用构建、Expo RN 开发、Netlify 部署、Remotion 视频生成和 Google Slides 自动化。每个插件都内嵌了该领域的 lifecyle knowledge，让 Codex 不只是"写代码"而是"懂工作流"。

---

## 🏗️ 项目架构全景

### 目录结构与设计哲学

```
openai/plugins/
├── .agents/plugins/
│   ├── marketplace.json          # 🔑 默认市场清单（Codex OAuth 用户）
│   └── api_marketplace.json      # 🔑 API Key 登录用户的市场清单
├── plugins/                      # 9 个精选插件
│   ├── figma/                    # Figma 设计系统集成
│   ├── notion/                   # Notion 知识管理
│   ├── build-ios-apps/           # iOS SwiftUI 开发
│   ├── build-macos-apps/         # macOS SwiftUI/AppKit 开发
│   ├── build-web-apps/           # Web 全栈开发
│   ├── expo/                     # Expo & React Native
│   ├── netlify/                  # Netlify 部署
│   ├── remotion/                 # React 视频生成
│   ├── google-slides/            # Google Slides 自动化
│   ├── aiera/ airtable/ alation/ # 更多第三方插件...
│   └── actively/ apollo/ asana/  # ...持续增长中
├── .agents/skills/plugin-creator/ # 🆕 官方插件创建工具
└── README.md
```

**设计哲学**：**"每个插件 = plugin.json 清单 + 可选扩展面"**

```
插件核心骨架：
  .codex-plugin/plugin.json  ← 唯一入口，Codex 通过它发现插件
  skills/                    ← Markdown 描述的技能（可选脚本）
  agents/openai.yaml         ← 插件级 subagent
  commands/                  ← 斜杠命令
  hooks.json                 ← 生命周期钩子
  .mcp.json                  ← MCP Server 配置
  .app.json                  ← 应用元数据（名称/图标/分类）
  assets/                    ← 静态资源（logo/icon）
```

**关键洞察**：`plugin.json` 是 Codex 识别插件的**唯一入口**。没有它，Codex 不会把这个目录当插件。其他目录全是可选的"扩展面"——这种设计让插件可以极简（一个 plugin.json + 几个 skill markdown），也可以极丰富（完整的 subagent + MCP + hooks）。

### 技术栈与依赖图谱

| 层面 | 技术 | 说明 |
|------|------|------|
| 主要语言 | JavaScript（5.1MB） | 插件 manifests 和分析脚本 |
| 第二语言 | Python（3.2MB） | 插件创建工具、自动化脚本 |
| 第三语言 | TypeScript（88KB） | 类型定义 |
| IaC | HCL（53KB） | 基础设施即代码（可能用于部署） |
| 包管理 | 无需 npm/pip | 纯仓库，插件本质是配置文件 |
| 运行环境 | Codex CLI | 唯一运行时依赖 |

### 双市场机制

仓库维护了**两份 marketplace.json**：

1. **`.agents/plugins/marketplace.json`** — 面向 OAuth 登录的 Codex 桌面/Web 用户（默认市场）
2. **`.agents/plugins/api_marketplace.json`** — 面向 API Key 登录用户，只收录仅含 `skills`（无 `apps`/`mcpServers`）的插件

这个设计揭示了 OpenAI 在产品分发上的谨慎：**API Key 用户无法使用需要 MCP Server 或 App 权限的插件**，只能使用纯文本 skills。

---

## 🧠 核心源码解读

### 1. 插件清单（plugin.json）— 插件的"身份证"

以 Figma 插件为例，`plugin.json` 声明了：

```json
{
  "name": "figma",
  "version": "1.0.0",
  "skills": ["use_figma", "code_to_canvas", "code_connect"],
  "mcp_servers": [{"name": "figma", "transport": "stdio"}],
  "agents": [{"name": "figma-reviewer"}],
  "commands": [{"name": "figma-export"}]
}
```

**设计模式**：声明式配置 + 能力注册。插件不包含业务逻辑代码，而是"声明自己有什么能力"——Codex 运行时根据声明动态调度。

### 2. 市场清单（marketplace.json）— 插件的"应用商店"

```json
{
  "plugins": [
    {"name": "figma", "path": "plugins/figma"},
    {"name": "notion", "path": "plugins/notion"},
    // ... 9+ 个条目
  ]
}
```

市场清单就是"推荐列表"。用户安装市场后，Codex 遍历清单中的每个 `path`，读取 `plugin.json` 并注册能力。

### 3. plugin-creator 技能 — 官方"脚手架"

`/.agents/skills/plugin-creator/` 是仓库里最值得注意的内部工具：

- `SKILL.md` — Codex 理解如何创建插件的知识文档
- `agents/openai.yaml` — 插件创建的 subagent 定义
- `references/plugin-json-spec.md` — `plugin.json` 的完整规范文档
- `scripts/create_basic_plugin.py` — Python 脚本自动化创建插件骨架

**这实际上是一个"自举"机制**：用 Codex + plugin-creator skill 来创建新的 Codex 插件。

### 4. 精选插件能力矩阵（深度拆解）

| 插件 | 核心能力 | MCP 依赖 | 目标用户 | 复杂度 |
|------|---------|---------|---------|--------|
| **figma** | use_figma、Code to Canvas、Code Connect | Figma MCP | 前端/全栈 | 高 |
| **notion** | 计划、研究、会议、知识捕获 | Notion MCP | PM/研究员 | 中 |
| **build-ios-apps** | SwiftUI 实现、重构、性能、调试 | 无 | iOS 工程师 | 高 |
| **build-macos-apps** | SwiftUI/AppKit、build/run/debug 循环 | 无 | macOS 工程师 | 高 |
| **build-web-apps** | 部署、UI、支付、数据库 | 无 | Web 全栈 | 中 |
| **expo** | RN、SDK 升级、EAS、Codex Run | 无 | RN/Expo | 中 |
| **netlify** | 部署、Functions、表单 | Netlify MCP | 静态站开发者 | 低 |
| **remotion** | React 写视频 | 无 | 内容创作 | 低 |
| **google-slides** | 自动生成 Slides | Google API | 商务/营销 | 低 |

**设计模式观察**："构建类"插件（iOS/macOS/Web/Expo）不依赖 MCP——它们依赖 Codex 的代码生成能力。"集成类"插件（Figma/Notion/Netlify）依赖 MCP——它们是 Codex 与外部工具之间的"翻译层"。

---

## 📐 架构决策与设计哲学

### 关键设计决策

1. **插件 = 配置文件，不是代码包**：与传统 IDE 插件（需要可执行代码）不同，Codex 插件本质是"告诉 AI 你能做什么"的声明。代码执行由 Codex 或 MCP Server 完成。

2. **MCP 协议作为"万能接口"**：所有外部工具集成走 MCP（Model Context Protocol）。MCP 是 OpenAI 推动的 AI-to-API 标准，插件仓库的设计反过来推动 MCP 生态发展。

3. **双市场策略**：API Key 用户受限（无 MCP/App）但 OAuth 用户完整——这是 OpenAI 在"易用性"和"安全性"之间的妥协。

4. **仓库即市场**：不建 Web 应用商店，直接 GitHub 仓库分发。好处是开源透明、贡献方便；代价是发现机制弱（依赖搜索和口碑）。

### 未解决的问题（Issue 分析）

仓库 **Issues 功能被禁用**（`hasIssuesEnabled: false`），但 **36 个 PR** 活跃。这意味着：
- 所有反馈走 PR→Review→Merge 流程，而非 Issue 讨论
- 这是一种"贡献驱动"而非"讨论驱动"的治理模式
- 36 个 PR 说明外部贡献活跃，平均每天约 0.4 个 PR

### 版本演进节奏

- 294 次 commits，约 3 次/天
- 最近提交：2026-06-25（持续活跃）
- 无 Release（仓库本身不是"软件"，是"内容"）
- 最近大 PR #333：添加 API marketplace，这是架构层面的扩展

---

## 🌐 全网口碑画像

### 好评共识

1. **"即装即用"是最大卖点**（来源：txtmix.com 评测）——不需要自己写 plugin.json，克隆对应子目录即可
2. **官方维护质量有保障**——OpenAI 自己在用、自己在维护，不是社区玩具
3. **"Codex 终于不只是写代码了"**（来源：baeseokjae 博客）——插件让 Codex 能操作 Figma、Notion、Netlify 等真实工具
4. **"应用商店精选区"定位精准**——90+ 插件按 7 大类组织，覆盖主流工作流

### 差评共识与风险

1. **没有 LICENSE 文件**（来源：txtmix.com 评测明确标注）——商用前必须法务确认，这是最大的潜在地雷
2. **依赖 MCP 第三方**——Figma/Notion/Netlify/Google Slides 插件都依赖外部 MCP Server，稳定性不受 OpenAI 控制
3. **生态太新**——2026 年 3 月才创建，规范还在迭代，可能有 breaking change
4. **Issues 被禁用**——用户无法直接提 bug，只能走 PR，门槛较高
5. **API Key 用户受限**——双市场机制意味着 API 用户得不到完整体验

### 争议焦点

- **"这是真正的插件生态还是 OpenAI 的捆绑策略？"** — 中文社区（aitoolly.com）指出，仓库的多语言代码占比（Python 3.2MB + JS 5.1MB + TS 88KB）暗示背后有大量自动化管道，不只是"精选合集"
- **"vs Claude Code Plugins"** — 两个阵营的开发者已在争论谁的插件架构更好

---

## ⚔️ 竞品对比

| 维度 | openai/plugins | Claude Code Plugins | 社区 MCP 生态 | 自研插件 |
|------|---------------|-------------------|-------------|---------|
| **维护方** | OpenAI 官方 | Anthropic 官方 | 社区/厂商 | 你 |
| **插件数** | 9+ 精选 | ~100+ | 数百 | 1 |
| **质量** | 高（官方验证） | 高（官方 + 社区） | 参差不齐 | 可控 |
| **安装复杂度** | 克隆仓库即可 | `claude plugin install` | 手动配置 | 完全自建 |
| **覆盖范围** | Figma/Notion/iOS/macOS | 更广泛的 DevOps/工具链 | 各种 | 定制 |
| **风险** | 无 License、依赖 MCP | Anthropic 锁定 | 安全性不确定 | 维护成本高 |
| **发现机制** | GitHub 仓库浏览 | `claude plugin marketplace` | npm/MCP registry | 无 |

### 选择建议

- **用 Codex → 必装 openai/plugins**：官方精选，质量最高
- **用 Claude Code → Claude Code Plugins 生态更成熟**（100+ 插件）
- **需要自定义能力 → 自研 + 参考 openai/plugins 的 plugin.json 格式**

---

## 🎯 核心研判

### 不可替代的价值点

1. **Codex 插件开发的"参考实现"**：plugin.json 格式、skill 写法、MCP 集成模式都在这里示范
2. **"官方认证"的信任背书**：9 个插件每个都代表 OpenAI 对"高质量 Codex 工作流"的定义
3. **降低 Codex 学习曲线的"快捷方式"**：不需要理解 Codex 底层，装上插件就能用

### 潜在风险

1. **⚠️ 无 License 是最大的商业风险** — 仓库根目录没有 LICENSE 文件，但子插件可能各自有许可证。商用必须逐项确认
2. **⚠️ MCP 依赖链脆弱** — Figma MCP、Notion MCP 等由第三方维护，它们挂了你插件也废
3. **⚠️ Issues 被禁用的信息不透明** — 你不知道其他用户遇到什么问题，只能自己踩坑
4. **生态早期的不稳定** — Codex 本身还在快速迭代，插件规范可能随时变

### 适用场景与不适用场景

**✅ 适合：**
- 已在用 OpenAI Codex 的开发者
- 想快速接入 Figma/Notion/Netlify 等工具链
- iOS/macOS/Web/RN 开发者（build-* 系列插件）

**❌ 不适合：**
- 不用 Codex 的人（这套插件就是给 Codex 用的）
- 需要严格 License 审查的商用项目
- MCP Server 不可用的环境（内网/离线）

### 趋势判断：🚀 快速上升期

3.6K stars（3 个月内）说明社区在密切跟踪。但真正的爆发取决于：
1. Codex 的用户规模增长
2. 更多企业级插件加入（Jira、GitHub、Slack 等）
3. License 问题解决后的商用化

---

## 📂 关键文件路径速查

| 文件 | 作用 | 备注 |
|------|------|------|
| `.agents/plugins/marketplace.json` | 默认插件市场清单 | OAuth 用户入口 |
| `.agents/plugins/api_marketplace.json` | API Key 用户市场清单 | #333 PR 新增 |
| `plugins/*/plugin.json` | 各插件能力声明 | 唯一必选文件 |
| `.agents/skills/plugin-creator/` | 官方插件创建工具 | 自举机制 |
| `.agents/skills/plugin-creator/references/plugin-json-spec.md` | plugin.json 规范文档 | 插件开发者必读 |

---

> **调研方法**：GitHub API 全量采集 + WebFetch 抓取 3 篇中文评测 + 1 篇英文评测 + 源码结构分析 + 36 个 PR 审查 + 竞品对比。报告不含大段 README 搬运。
