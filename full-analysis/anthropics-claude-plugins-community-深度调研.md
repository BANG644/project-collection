# anthropics/claude-plugins-community 深度调研

> 调研日期：2026-08-26 ｜ 星标：1,660 ⭐ ｜ 语言：Python ｜ 协议：Apache-2.0 ｜ 默认分支：main
> 定位：面向 Claude Cowork 与 Claude Code 的**社区插件市场（只读镜像）**——所有插件经 Anthropic 内部安全扫描并审批后夜间同步

## 一、项目亮点（差异化）

1. **Anthropic 背书的「信任锚」**：这是官方维护的社区插件目录，列出的每个插件都**经过自动安全扫描 + 审批**才进入分发，解决了「社区插件从哪装才安全」的核心信任问题。
2. **只读镜像 + 受控提交**：仓库本身是内部审核流水线的夜间同步产物，直接对仓库开 PR 会被自动关闭，所有变更只从 `clau.de/plugin-directory-submission` 流入——治理干净，避免恶意 PR 污染。
3. **一键安装体验**：`claude plugin marketplace add anthropics/claude-plugins-community` + `claude plugin install <name>@claude-community` 即可消费，与 Claude Code / Cowork 的插件体系原生打通。
4. **与官方/垂直市场互补**：与 `anthropics/claude-plugins-official`（官方维护）、`anthropics/knowledge-work-plugins`（角色向知识工作插件）形成三层市场结构。

## 二、核心架构

本质是一个**插件目录清单仓库**，不是运行时代码。其权威资产是 `.claude-plugin/marketplace.json`（约 1.5MB，列出所有社区插件），仓库内还放了若干示例插件作为模板参考：

```
anthropics/claude-plugins-community/
├── .claude-plugin/
│   └── marketplace.json        # 社区插件列表（夜间从内部流水线同步）
├── eli5/                       # 示例插件：Explain Like I'm 5
│   ├── .claude-plugin/          # 插件 manifest
│   ├── skills/                 # 插件内含的 Agent Skills
│   └── README.md
├── quickdesign/                # 示例插件
├── testdino/                   # 示例插件（测试相关）
├── tres-finance-plugin/        # 示例插件（金融相关）
├── LICENSE  README.md
```

每个示例插件结构一致：`.claude-plugin/`（manifest）+ `skills/`（可复用 Agent Skills），与 Agent Skills 规范（anthropics/skills、ComposioHQ/awesome-claude-skills 同生态）对齐。

**分发链路**：提交（clau.de）→ Anthropic 内部审核流水线（自动安全扫描）→ 审批通过 → 夜间同步进本仓库 `marketplace.json` → 用户 `claude plugin install` 消费。

## 三、应用场景与启发

- **安全消费社区插件**：想给 Claude Code / Cowork 装社区能力时，优先从这里取——比从任意 GitHub 仓库拉未审插件风险低得多。
- **插件作者标杆**：示例插件（eli5/quickdesign/testdino/tres-finance）展示了「合规插件」的标准结构（manifest + skills），是作者提交前的模板。
- **对同类需求的启发**：「市场 + 受控审核 + 只读镜像」是一种可复用的**信任层设计**——尤其适合 Agent 插件/技能这类「执行任意代码」的高风险分发场景。任何 Agent 生态（OpenCode / Cursor / Codex）都可借鉴「官方安全扫描闸门 + 夜间同步清单」模式。

## 四、源码深度解读

**1. marketplace.json 即「信任清单」**
1.5MB 的 `.claude-plugin/marketplace.json` 是仓库唯一权威运行时资产——它不存代码，只存「哪些社区插件已被 Anthropic 批准可安装」的名单。消费端 `claude plugin` 读取它来决定可用性。

**2. 示例插件的 manifest + skills 结构（以 `eli5/` 为代表）**
```
eli5/
├── .claude-plugin/   # 插件 manifest（名称/入口/权限声明）
└── skills/           # 该插件贡献的 Agent Skills
```
与 Agent Skills 规范一致，证明「插件 = manifest + 一组 skills」是 Claude 插件生态的通用封装单位。

**3. 提交即走外部管线（README 明示）**
> Pull requests opened directly against this repo are closed automatically — all changes flow from the internal review pipeline.

这从协议层杜绝了「镜像仓库被直接投毒」的可能，是整个信任模型的基石。

## 五、社区口碑

- 作为 Anthropic 官方信任锚，定位清晰、权威性强；对担心「社区插件供应链安全」的用户价值明确。
- ⚠️ 本身是**只读镜像**，不是可研究的代码库——作为「调研对象」信息量有限，其价值在「生态意义」而非「实现细节」。
- 社区讨论多集中在其与 `claude-plugins-official` 的关系，以及「为什么社区插件也要过 Anthropic 审核」的治理争议（中心化 vs 开放）。

## 六、竞品对比与核心研判

| 维度 | claude-plugins-community | claude-plugins-official | awesome-claude-skills(Composio,70K⭐) | OpenCode/Cursor 插件市场 |
|------|------------------------|------------------------|----------------------------------------|--------------------------|
| 维护方 | Anthropic（社区提交） | Anthropic（官方） | 社区策展 | 各自厂商/社区 |
| 安全审核 | ✅ 自动扫描+审批 | ✅ | ❌ 未审 | 各异 |
| 规模 | 中小 | 小 | 极大(1000+) | 中 |
| 只读镜像 | ✅ | ❌ | ❌ | ❌ |

**核心研判**：
- ✅ **生态意义大于代码价值**：作为「官方信任锚」，它填补了 Claude 插件生态的供应链安全空白——这是 awesome-claude-skills 等未审大清单做不到的。
- ⚠️ **作为调研标的偏薄**：只读镜像、无实质代码，本报告价值在于「讲清其信任层设计」，而非深挖实现。
- 🔭 **启发**：任何执行任意代码的 Agent 插件/技能分发，都应有一个「官方安全闸门 + 只读清单镜像」的信任层。可复用于 OpenCode / Cursor / Codex 等生态的插件市场治理。

## 七、关键文件速查

| 文件 | 作用 |
|------|------|
| `.claude-plugin/marketplace.json` | 社区插件信任清单（夜间同步，~1.5MB） |
| `eli5/` `quickdesign/` `testdino/` `tres-finance-plugin/` | 合规插件示例（manifest + skills 模板） |
| `README.md` | 市场使用方式、提交与审核治理说明 |
| 关联：`anthropics/claude-plugins-official` `anthropics/knowledge-work-plugins` | 官方/垂直插件市场 |
