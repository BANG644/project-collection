# Cursor plugins 深度调研

> 调研日期：2026-08-16 ｜ 星标：2,922 ⭐ ｜ 协议：MIT（README 与插件 manifest 声明；根目录 LICENSE 文件缺失，GitHub API 未识别）｜ 语言：TypeScript（规范与 CLI）/ 多语言（各插件）
> 仓库：`cursor/plugins` ｜ 默认分支：`main` ｜ 官网：cursor.com ｜ 最近活跃：2026-08-13
> 定位：**Cursor 插件规范（specification）+ 官方插件市场（official marketplace）**

## 一、项目定位（一句话）

**Cursor 官方给出的「Agent 插件」标准与官方插件集合**——它既定义了一套插件 manifest 规范（一个目录 + 一份 `.cursor-plugin/plugin.json` + skills/rules/hooks/mcp 约定），又亲手维护了 30+ 个遵循该规范的官方插件（开发者工具 + 框架规则 + 第三方 MCP 集成），并配套 ajv schema 校验 CI 保证生态一致性。

## 二、项目亮点（差异化）

1. **规范与实现同源**：官方自己先用规范把 30+ 插件写出来，规范不是「纸上标准」，而是被真实插件持续打磨的活文档。
2. **多插件市场仓库（mono-marketplace）**：根 `.cursor-plugin/marketplace.json` 列出所有插件，每个插件独立目录、独立 manifest、独立版本——既可整体安装，也可按 `source` 单拉。
3. **插件能力四件套统一约定**：`skills/`（SKILL.md）、`rules/`（.mdc 规则）、`hooks/`（hooks.json，如 stop 钩子）、`mcp.json`（MCP server 定义），把「Agent 可调用的能力」标准化。
4. **schema 驱动的质量门禁**：`.github/workflows/validate-plugins.yml` 用 ajv + ajv-formats 跑 `scripts/validate-plugins.mjs`，任何改动 `marketplace.json` / `plugin.json` / `schemas/` 的 PR 都会被校验——生态不会因随意 manifest 腐化。
5. **一手第三方 MCP 集成**：`third_party/` 下直接收纳 Gmail / Google Drive / GitHub / Salesforce / Slack 系 / Playwright 等官方远程 MCP server 连接，等于「Cursor 版连接器目录」。

## 三、核心架构

仓库是两层的「市场 + 规范」：

```
plugins/
├── .cursor-plugin/
│   └── marketplace.json          # 市场清单（列出所有插件 name/source/desc）
├── plugin-name/                  # 每个官方插件一个独立目录
│   ├── .cursor-plugin/
│   │   └── plugin.json           # 该插件 manifest（被 schema 校验）
│   ├── skills/                   # Agent skills（SKILL.md + frontmatter）
│   ├── rules/                    # Cursor rules（.mdc 文件）
│   ├── mcp.json                  # MCP server 定义
│   ├── hooks/                   # hooks.json（生命周期钩子）
│   ├── README.md / CHANGELOG.md / LICENSE
├── third_party/<saas>/           # 第三方 MCP 集成（同上结构）
├── schemas/                      # manifest JSON Schema
└── scripts/validate-plugins.mjs # CI 校验脚本
```

**插件 manifest（`plugin.json`）字段**（来自 `continual-learning` / `thermos` 真实样例）：

```json
{
  "name": "continual-learning",
  "displayName": "Continual Learning",
  "version": "1.0.0",
  "description": "Incrementally learns durable user preferences ...",
  "author": { "name": "Cursor", "email": "plugins@cursor.com" },
  "homepage": "https://github.com/cursor/plugins",
  "repository": "https://github.com/cursor/plugins",
  "license": "MIT",
  "logo": "assets/avatar.png",
  "keywords": ["continual-learning", "agent-memory", "transcripts", "hooks"],
  "category": "developer-tools",
  "tags": ["automation", "memory", "transcripts"],
  "agents": "./agents/",
  "skills": "./skills/",
  "hooks": "./hooks/hooks.json"
}
```

注意 `agents` / `skills` / `hooks` 都是**指向目录的相对路径**——manifest 只声明「能力在哪」，具体实现散落于 skills/rules/hooks 子目录，符合「配置与实现分离」。

## 四、应用场景与启发

**典型场景**：团队把内部工作流（CI、code review、发布、本地自动化、验证）打包成 Cursor 插件分发；把常用 SaaS（Gmail/GitHub/Salesforce）以 MCP 形式接入 Cursor Agent；把项目规则（.mdc）与技能（SKILL.md）随仓库分发。

**架构启发（可复用）**：
- **「规范 + 官方样板库 + schema 校验」三位一体**是任何插件生态防腐化的黄金组合——光有规范不够，必须有「官方先吃自己的狗粮」+「CI 强制校验」两道保险。值得任何想做插件/技能市场的团队（包括本调研库自身的 skills 体系）借鉴。
- **manifest 只声明能力位置、实现散落子目录**：让「一个插件」既是可版本化的单元，又由多个关注点（skill/rule/hook/mcp）组合而成，扩展性与可读性兼顾。
- **生命周期钩子（hooks.json）**让插件能非侵入式介入 Agent 的关键节点（如 `stop`），是「能力增强」而非「流程重写」的成熟设计。

## 五、源码深度解读

### 1. 市场清单：`marketplace.json`

根 `.cursor-plugin/marketplace.json` 是「市场索引」，结构极简——`owner` + `metadata` + `plugins[]`，每个插件只给 `name` / `source`（目录路径）/ `description`：

```json
{
  "name": "cursor-plugins",
  "owner": { "name": "Cursor", "email": "plugins@cursor.com" },
  "metadata": { "description": "Official Cursor plugin marketplace: ..." },
  "plugins": [
    { "name": "teaching", "source": "teaching", "description": "Skill mapping, practice plans, ..." },
    { "name": "continual-learning", "source": "continual-learning",
      "description": "Incremental transcript-driven memory updates for AGENTS.md ..." },
    { "name": "gmail", "source": "third_party/gmail",
      "description": "Connect to Gmail via Google's remote MCP server ..." },
    ...
  ]
}
```

`source` 字段直接对应仓库内目录路径，**市场与代码同仓**——没有额外的registry服务，降低分发复杂度。当前清单覆盖约 14 个第一方插件（teaching / continual-learning / cursor-team-kit / thermos / create-plugin / ralph-loop / agent-compatibility / cli-for-agent / pr-review-canvas / docs-canvas / cursor-sdk / orchestrate / pstack 等）与约 18 个 `third_party` MCP 集成（gmail / google-drive / google-calendar / gong / salesforce / apollo-io / ashby / hubspot / intercom / circleback / docusign / navan / profound / x / clay / zoom / playwright / github）。

### 2. 插件 manifest 样例：`continual-learning`

上文已展示其 `plugin.json`：通过 `agents` / `skills` / `hooks` 三个相对路径把「记忆更新 Agent + 技能 + stop 钩子」串成一个插件。`thermos`（深度代码审查）的 manifest 则只声明 `skills` + `agents`（未挂 hooks），说明字段是按需可选的——schema 校验的是「填了的字段合规」，而非「必须全填」。

### 3. 质量门禁：`validate-plugins.yml`

`.github/workflows/validate-plugins.yml` 是生态防腐化的关键——**任何改 `marketplace.json` / `**/plugin.json` / `schemas/**` 的 PR 都触发 ajv 校验**：

```yaml
name: Validate plugins
on:
  pull_request:
    paths:
      - ".cursor-plugin/marketplace.json"
      - "**/plugin.json"
      - "schemas/**"
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm install --no-save ajv ajv-formats
      - run: node scripts/validate-plugins.mjs
```

`scripts/validate-plugins.mjs` 用 ajv + ajv-formats 把每个 `plugin.json` 对 `schemas/` 下的 JSON Schema 做结构校验。**这是「规范≠空话」的工程落点**：规范被写成机器可验的 schema，CI 强制，任何不合规 manifest 无法合入主分支。

## 六、全网口碑

- **定位**：作为 Cursor 官方的插件规范与样板库，是「Cursor Agent 能力扩展」的权威参考源；其 `skills` / `rules` / `hooks` / `mcp` 的目录约定，正逐渐成为社区做 Cursor 插件的「事实标准模板」。
- **生态信号**：`third_party/` 收纳了大量一线 SaaS 的官方远程 MCP server，相当于 Cursor 官方帮你维护了一份「可信 MCP 连接器目录」，降低了 Agent 接入外部服务的信任成本。
- **客观评价**：价值在「规范 + 样板 + 校验」的组合，而非单个插件功能；对「想标准化 Agent 插件分发的团队」参考价值最高。注意根 LICENSE 文件缺失（GitHub API 未识别协议），但 README 与各插件 manifest 均声明 MIT，单插件可独立合规使用。

## 七、竞品对比与核心研判

| 维度 | cursor/plugins（官方规范） | Claude Skills 生态（库内多份报告） | VS Code 扩展市场 | npm/pip 包生态 |
|------|--------------------------|-----------------------------------|------------------|----------------|
| 定位 | Agent 插件规范 + 官方市场 | Agent 技能合集（无统一校验 CI） | 通用编辑器扩展 | 通用代码包 |
| 校验机制 | ✅ ajv schema + CI 强制 | 多为约定，少强制门禁 | ✅ 发布审核 | ⚠️ 弱（靠社区） |
| 能力单元 | skill+rule+hook+mcp 四件套 | skill 为主 | command+view+api | function/CLI |
| 官方样板 | ✅ 30+ 官方插件 | 混合 | 第三方为主 | 第三方为主 |
| 跨工具复用 | 绑定 Cursor | 绑定 Claude Code/Codex 等 | 绑定 VS Code |

**核心研判**：
- **优势**：「规范 + 官方样板 + schema 校验 CI」三位一体是插件生态防腐化的教科书做法；`third_party` MCP 目录降低外部接入信任成本。
- **风险/边界**：强绑定 Cursor 生态，跨 IDE 复用有限；根 LICENSE 缺失是小瑕疵；规范仍在演进（hooks/agents 字段组合未完全固化）。
- **启发**：任何「插件/技能市场」都应借鉴其「官方先吃狗粮 + 机器可验 schema + CI 强制」——这正是本调研库自身 skills 体系也应补强的方向（规范文档 + 自动化校验）。

## 八、关键文件路径速查

| 关注点 | 路径（仓库根） |
|--------|---------------|
| 市场清单 | `.cursor-plugin/marketplace.json`（列出全部 30+ 插件 name/source/desc） |
| 插件 manifest 规范 | `<plugin>/.cursor-plugin/plugin.json`（字段样例见 continual-learning / thermos） |
| 校验 CI | `.github/workflows/validate-plugins.yml`（PR 触发 ajv 校验） |
| 校验脚本 | `scripts/validate-plugins.mjs` |
| manifest Schema | `schemas/`（被 ajv 引用） |
| 第一方插件 | `teaching/` `continual-learning/` `cursor-team-kit/` `thermos/` `create-plugin/` `orchestrate/` `pstack/` `cursor-sdk/` 等 |
| 第三方 MCP 集成 | `third_party/<saas>/`（gmail / github / salesforce / playwright / zoom / x / clay …） |
| 插件结构说明 | `README.md`（多插件市场仓库结构图） |
