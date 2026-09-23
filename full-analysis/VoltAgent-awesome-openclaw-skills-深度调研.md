# VoltAgent/awesome-openclaw-skills 深度调研

> 调研日期：2026-09-24 | 星标：52,746⭐ | 语言：null（纯 Markdown 策展） | 许可：未声明（awesome list，内容链接第三方） | 默认分支：main | 最近活跃：2026-09-22

## 一、项目定位

OpenClaw 技能精选合集（awesome list）。它不是代码库，而是从 OpenClaw 官方技能 registry **ClawHub** 中筛选、分类出来的"技能黄页"——把官方 registry 上数万个社区技能沉淀成一份可浏览、可检索、带质量门禁的目录，同时充当 OpenClaw 用例灵感库。

> 关联背景：OpenClaw 是本地运行的 AI 助手（与用户长期使用的 QClaw/WorkBuddy 同属"本地 agent"生态），技能（Skill）是其能力扩展单元。本仓库对用户的 skill 体系建设有直接参照价值。

## 二、项目亮点

1. **规模巨大且经过治理**：收录 **5,300+** 技能，全部来自 ClawHub 官方 registry，并非随意收集。
2. **明确的质量过滤流水线**：从 registry 原始池里**排除 7,215 个**劣质技能（详见下表），相当于做了一次"反垃圾"清洗。
3. **细粒度分类 + 计数**：约 30 个领域分类，每个分类标注技能数量，便于按需求定位。
4. **多种安装路径**：CLI、ClawHub CLI、手动复制、聊天窗口粘贴 GitHub 链接四种方式，覆盖不同使用习惯。
5. **安全审计意识**：明确列出"恶意技能 373 个被剔除"，并设 Security Notice 章节提示权限/密钥风险。

## 三、核心架构：registry → 过滤 → 分类 → 呈现

```
ClawHub 官方 registry（原始 ~12,500 技能）
        │
        ▼  过滤流水线（5 道闸门）
  ┌─────────────────────────────────────────┐
  │ 垃圾账号/机器人   4,065                  │
  │ 重名/相似         1,040                  │
  │ 低质/非英文描述    851                  │
  │ 加密/金融/交易     886                  │
  │ 恶意（安全审计）   373  ── 合计 7,215   │
  └─────────────────────────────────────────┘
        │
        ▼
  精选 5,300+ 技能 → 按 ~30 个领域分类 → README 内嵌 + categories/<cat>.md 分文件
```

安装优先级（来自 README）：Workspace `> ` Local `> ` Bundled。技能目录：
- 全局：`~/.openclaw/skills/`
- 工作区：`<project>/skills/`

## 四、应用场景与启发

1. **给"自建 skill 体系"提供质量门禁范本**：用户维护 WorkBuddy skill 体系时，可借鉴其"五道过滤闸门 + 计数分类"思路——不要只做加法，要设淘汰规则。
2. **技能泛滥时代的治理样本**：agent 生态正经历"技能通胀"，本仓库证明"策展 + 审计"比"全量收录"更有长期价值。
3. **灵感挖掘**：Coding Agents & IDEs（1,184）、Web & Frontend（920）、DevOps & Cloud（393）、Browser & Automation（323）、Search & Research（343）是最大几类，反映社区真实需求集中在"研发提效 + 自动化"。
4. **可嵌入工作流**：`openclaw skills install <slug>` 或把 GitHub 链接直接丢进聊天窗口即可安装，零摩擦。

## 五、源码/内容深度解读

### 1. 过滤统计表（README 内真实数据）
```
| Filter | Excluded |
| 垃圾账号/机器人     | 4,065 |
| 重名/相似           | 1,040 |
| 低质/非英文描述      | 851  |
| 加密/金融/交易       | 886  |
| 恶意（安全审计）     | 373  |
| 合计未收录           | 7,215 |
```
> 价值：这是少见的"registry 治理透明度"披露，直接给出淘汰量级，比空喊"精选"更具参考性。

### 2. 分类计数体系（README Table of Contents 节选）
| 分类 | 数量 | 分类 | 数量 |
|---|---|---|---|
| Coding Agents & IDEs | 1,184 | Web & Frontend Dev | 920 |
| DevOps & Cloud | 393 | Browser & Automation | 323 |
| Search & Research | 343 | CLI Utilities | 180 |
| Git & GitHub | 167 | AI & LLMs | 176 |
| Communication | 146 | Productivity & Tasks | 207 |

每个分类在 `categories/<cat>.md` 有独立分文件（如 `categories/git-and-github.md`），README 内用 `<details>` 折叠展示样例条目，如：
```
- [agent-team-orchestration](https://clawskills.sh/skills/...) - 多 agent 团队协作编排
- [arc-security-audit](https://clawskills.sh/skills/...) - 全栈技能的安防审计
```

### 3. 安装契约
```bash
openclaw skills install <skill-slug>        # OpenClaw CLI
npx clawhub install <skill-slug>            # ClawHub CLI（registry 托管）
# 或复制技能文件夹到 ~/.openclaw/skills/ 或 <project>/skills/
# 或直接把 GitHub 链接粘贴进聊天窗口，助手后台自动安装
```

## 六、全网口碑

- 由 **VoltAgent**（知名 AI Agent 公司，主打 agent 基础设施）出品，品牌背书强，52.7k⭐ 属同类 awesome list 顶流。
- 定位为"OpenClaw 技能发现入口"，配套 `clawskills.sh` 网站与 Discord 社区，形成"list + 站点 + 社区"三位一体。
- 争议点：README 含多处赞助横幅（Crawlbase / SerpApi / trentclaw 等），策展立场可能受赞助影响，引用时需注意中立性。

## 七、竞品对比与核心研判

| 维度 | awesome-openclaw-skills | awesome-opencode/awesome-opencode | 各 agent 官方市场（clawhub.ai 等） |
|---|---|---|---|
| 覆盖对象 | OpenClaw 技能 | OpenCode 插件/主题/agent | 单一平台原生 |
| 治理 | 5 道过滤闸门，透明披露 | 人工策展，未披露过滤量 | 平台审核，黑盒 |
| 安装闭环 | CLI + 链接粘贴 | 多为源码仓，需手动 | 平台内一键 |
| 定位 | 发现 + 灵感 | 发现 | 分发 |

**核心研判**：
- ✅ 对 agent 生态参与者（尤其在做 skill 体系的人）是高质量"选型参考 + 治理范本"，值得收藏。
- ⚠️ 本质是"指向第三方 registry 的索引"，自身不含技能代码；价值随 ClawHub 兴衰浮动，且赞助 bias 需打折看待。
- 📌 建议用户：把它当作"OpenClaw 技能生态地图"定期浏览，但自建 skill 时以"质量门禁"思路为主，不盲从收录量。

## 八、关键文件路径速查

- 仓库根：`https://github.com/VoltAgent/awesome-openclaw-skills`
- 官方 registry：`https://clawhub.ai`
- 技能站点：`https://clawskills.sh`
- 分类分文件：`<repo>/categories/<category>.md`
- 贡献规范：`CONTRIBUTING.md`（仅收已在 ClawHub 发布的技能）
- 安装文档：README "Installation" 章节

> 数据来源：gh API 仓库元数据 + README 全文（过滤表、TOC 分类计数、安装契约）。本报告超出 README 的部分为架构抽象、竞品研判与应用启发。
