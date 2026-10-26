# alchaincyf/huashu-design 深度调研

> 调研日期：2026-10-27 ｜ 数据来源：GitHub API（SKILL.md / 源码树 / references / assets）+ 当日 GitHub Trending 日榜
> 许可证：**MIT** ｜ 形态：Claude Code / Codex / Cursor 可用的 Agent Skill（HTML-native）

## 项目亮点（差异化）

- **"HTML-native design skill"**：在 agent 里打一句话，拿回**可交付的设计**——网页 / App 原型 / 可编辑 PPTX / 动画（MP4·GIF）/ 信息图，而非"一张好看的图"。
- **强制"三方向门"（100%）**：任何新视觉任务先出三个方向的真实初稿给用户选，**指定风格或品牌也不豁免**，选定后才执行——直接对抗"AI slop"。
- **84 种带样张的风格库 + "外观账本"（design ledger）** 记录反复出现的套路并主动避开，配合"设计体检"（`design_lint.py`）。
- **6 角色工作室心智模型**（艺术总监 / 品牌研究 / 视觉 / 动效 / 前端 / 文案），强调"你是设计师，不是写 HTML 的程序员"。
- **事实先于假设**：涉及具体产品/版本先 WebSearch 核实写 `product-facts.md`，不编造 logo 墙与数据。

## 项目定位（一句话）

Huashu Design 是一套**把设计品味与流程工程化为可复用 Skill** 的 agent 工具——用强约束（方向门 + Gate 文件 + 外观账本）让 agent 产出"认不出是 AI 做"的可交付设计。

## 核心架构

- **入口**：`SKILL.md`（YAML frontmatter `name/description/metadata`），声明触发词、适用范围、开工三件事、模块路由表。
- **模块手册**（`references/modules/{web,deck,infographic,app-prototype,motion}.md`）：每个媒介一个手册，共有"窄桥"规则（事实核实 / 从已有上下文出发 / 品牌资产协议 / 三方向门 / 素材分档 / Gate 文件）。
- **支撑参考**：`references/{design-styles,typography,brand-asset-protocol,workflow,materials,verification,critique-guide,directions}.md`。
- **脚本层**（`scripts/`）：`learn.py`（用户偏好 + 历史教训）、`design_lint.py ledger`（避免重复外观）、`capabilities.py`（素材分档）、`ref_board.py`（截参考图亲眼看）、`verify.py`（验证截图）；`design-gate-hook.sh` 做 ≥45s 长片的硬检查。
- **资产层**（`assets/`）：84 风格样张（`style-specimens/sheet-*.jpg`）、音效、showcase。

## 源码深度解读（SKILL.md 关键机制）

**1. 三方向门（核心反 slop 约束）**

> 任何会产出新视觉设计的任务，先出三个方向的**真实初稿**给用户选，用户选定后才执行。

六个候选先画成一页缩略图（备选）：`最佳设计师`（预算无上限时最适合该题材的设计师思维）、`现实参照`（核实过的出色作品，用 `ref_board.py` 截下来亲眼看再拆语言）、`秒数轮盘`（从风格库随机抽，先看样张）。挑最强、彼此最不一样、不撞外观账本的三张做完整版，摆出来就停、等用户选。豁免需写进 `direction-approved.md`（原话或理由）。

**2. 开工三件事（都不阻塞）**

```bash
python3 "$HD/scripts/learn.py" <主题词…>      # 用户偏好 + 过去项目教训
python3 "$HD/scripts/design_lint.py" ledger   # 最近交付过的样子，主动避开
python3 "$HD/scripts/capabilities.py"          # 手里有什么素材，走哪一档
```

`$HD` 是 skill 根目录，**不是用户项目目录**——这是新手最常踩的坑。

**3. Gate 文件（检查点物化成文件，文件不在 = 环节没做）**

| Gate 文件 | 对应环节 | 何时必须有 |
|-----------|---------|------------|
| `brand-spec.md` | 品牌资产协议产物 | 涉及具体品牌/产品的任何设计 |
| `direction-approved.md` | 展示哪几版 + 截图 + 用户选择原话 | 实现开工前；≥45s 长片渲染前硬检查 |
| `导演稿.md` | 分镜卡与视觉密度条款 | ≥20s 动画开工前 |

"用户说继续"授权进入下一步，不授权跳过当前步的 gate；跳过必须用户明说并写入 gate 文件。弱 runtime 也照写。

## 应用场景与启发

- **把"设计"当成有标准、有审美的工程活动**，而非"生成漂亮图"——对 AI 设计类 skill 是标杆范式。
- **约束机制可迁移**：三方向门 + 外观账本 + Gate 文件这套"可审计的控制面"，可用于任何"AI 生成内容需可控/可复核"的场景（如 PPT、UI、报告配图自动生成）。
- 与 WorkBuddy 的 skill/agent 体系同构：渐进披露 `references/`、脚本前置、`$HD` 根目录约定、用不变量（gate）约束弱模型行为。

## 社区口碑

- **26,656⭐**，MIT，2026-04 创建，最近推送 2026-10-23（活跃）；2026-10-27 登上 GitHub Trending 日榜，增速高。
- 属"设计类 agent skill"热门赛道（与 `diagram-design` / `hyperframes` / `female-portrait-director` / `ian-xiaohei-illustrations` 同期流行），口碑偏正面（强调反 AI slop、可交付、诚实内容）。
- **主观评价数据不可用**：精确用户满意度无第三方评测；从 trending 热度与 star 增速看受关注度高。

## 竞品对比

| 维度 | huashu-design | diagram-design / hyperframes | 通用"一句话出图" |
|------|---------------|------------------------------|------------------|
| 产出 | 网页/App/PPTX/动画/信息图 | 多为图表/插画/特定媒介 | 单图为主 |
| 反 slop | 三方向门 + 外观账本 + Gate | 部分有方向选择 | 弱 |
| 工程化 | 脚本 + references + gate 钩子 | 中等 | 低 |
| 许可 | MIT | 多 MIT | 各异 |

## 核心研判

- **价值**：把设计品味与流程工程化为可复用 skill，反 AI slop 立场鲜明；其"约束机制"设计值得所有内容生成类 agent 借鉴——尤其"Gate 文件 = 环节物化"的思路，把软流程变成可机器检查的不变量。
- **适用边界**：生产级 Web App / SEO 网站 / 需后端系统**不适用**（SKILL.md 明示）；纯机械操作（HTML 转 PDF/PPTX、截图、修 bug）不过三方向门。
- **采用建议**：作为 Claude/Codex Skill 直接装；其 `references/` + `scripts/` + gate 结构可作为"高质量 agent skill"模板复用。

## 关键文件路径速查

- `SKILL.md` — 入口与全部窄桥规则
- `references/modules/{web,deck,infographic,app-prototype,motion}.md` — 模块手册
- `references/{design-styles,typography,brand-asset-protocol,workflow,materials,verification,critique-guide,directions}.md`
- `scripts/{learn,design_lint,capabilities,ref_board,verify}.py` + `design-gate-hook.sh`
- `assets/style-specimens/sheet-*.jpg` — 风格样张
- `showcases/INDEX.md` — 样例集
