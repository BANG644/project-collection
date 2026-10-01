# Salomondiei08/oh-my-hermes 深度调研

> 调研时间：2026-10-02 ｜ 数据来源：gh API 真实抓取 README / docs/architecture.md / skills / agents / AGENTS.md
> 定位：面向 Hermes Agent 的工程化工作流层——36 个 Skill + 7 个 Agent 角色 + 6 条 Workflow，编排 Understand→Design→Build→Check→Ship→Learn 产品全生命周期

## 一、项目亮点（差异化）

1. **"Oh My Zsh 之于 Zsh" 的产品化范式**：`install.sh` 一键把 36 个 skill、7 个 agent 角色、6 条 workflow 装进 Hermes，让一个通用 agent 变成能独立做产品的"CTO 副驾"。
2. **七角色产品生命周期**：CTO 统筹，下挂 Product / Designer / Builder / Reviewer / Security / Ops，各自只拥有一个关注点（one owner per concern），不把能力无限拆成新 agent。
3. **可逆自治 + 不可逆变 gate**：日常可逆工作带默认值自主推进；生产发布/回滚/公开/付费/破坏性等不可逆动作必须创始人（founder）审批——用"护栏"代替"全接管"。
4. **证据驱动而非总结驱动**：完成要求绑定验收标准证据，Security/QA 独立核查；两次同类失败即 block 任务并上报决策，杜绝无意义忙碌。
5. **自托管友好**：默认栈 Vercel + Supabase + GitHub + Slack，全部可替换；凭证按需懒加载进 `~/.hermes/.env`（用户权限），不把密钥塞进对话。

## 二、核心架构

```
oh-my-hermes/
├── skills/      ← 36 个 skill 文件  → ~/.hermes/skills/
├── agents/      ← 7 个角色定义     → ~/.hermes/agents/  (cto/pm/designer/dev/qa/security/ops)
├── workflows/   ← 6 条 workflow    → ~/.hermes/workflows/
├── templates/   ← AGENTS.md / .env / health endpoint
├── scripts/     ← install / bootstrap / setup-cto / ship-this-idea / verify ...
└── docs/        ← architecture.md 等
```
Hermes 提供 profile / Kanban / memory / cron / tools / approvals / computer-use 原语，OHM 只是把这些原语**编排成产品构建生命周期**，自身不是运行时、不是 daemon、不是路由。

## 三、应用场景与启发

- **给独立开发者/小团队当"AI CTO"**：一条 "set up the CTO loop" 消息，bot 自动理解项目、出 brief、设计、构建、审查、部署、写日报——适合 solo  founder 把重复的产品运营动作外包给 agent。
- **角色编排的方法论启发**：
  - 「能力不升格为 agent」原则值得所有多 agent 框架借鉴——很多人一上来就为每个工具建一个 agent，结果上下文爆炸；OHM 用 7 个稳定角色 + skill 分解任务，更可控。
  - 「最多问三个问题 + 给推荐默认值」的"先读后问、默认优先"交互约定，是降低 agent 打扰的关键设计。
  - `docs/architecture.md` 把状态（Kanban 为唯一真相源）、记忆键（`github-repo`/`current-task`/`pending-approval` 等）、审批边界全部显式文档化——这种"把 agent 协作契约写成代码+文档"的做法，是生产级 agent 系统的必修课。

## 四、源码深度解读

**① 生命周期与角色边界**（`docs/architecture.md`）
```text
Understand -> Design -> Build -> Check -> Ship -> Learn
CTO 协调 7 个 profile:
  cto  生命周期/路线图/委派/对外沟通
  pm   产品清晰度/优先级/定位/SEO/内容
  designer  UX/视觉校验/发布素材
  dev   可工作的产品增量
  qa    用户行为/视觉可访问性/PR 审查
  security 发布风险 + 定时评估
  ops   发布/健康/日志/事故
```
原则摘录：**"One owner per concern; capabilities do not become agents."**——能力不变成 agent，是它和多数"agent 农场"项目最本质的区别。

**② 旗舰 skill 示例**（`skills/ship-this-idea.md`）
```markdown
---
name: ship-this-idea
description: founder 给一句话，Hermes 自主设计/构建/验证/部署最小可用产品
---
1. 运行 ~/.hermes/scripts/ship-this-idea.sh "给家庭共享密码的候补名单页"
2. 仅在首次发布有实质影响时最多问三个问题
3. 默认跳过问题、用文档假设继续
4. 产出 PRODUCT_BRIEF.md / DESIGN.md / 可运行构建 / 验证证据 / URL
```
skill 用 frontmatter（`name`/`description`/`version`/`tags`）声明触发条件，与 Agent Skills 开放规范同构——可被任意兼容 harness 发现执行。

**③ CTO 角色约束**（`agents/cto.md`）
```markdown
## Approval Gates —— 必须 founder 批准：
1. 影响差异大的重大构建方向
2. 生产发布或回滚
3. 公开内容 / 发布视频 / 授权音乐选型
4. 破坏/付费/凭证/账号级动作
## Recovery：
- 一次失败 → 查证据改方法
- 两次同类失败 → 阻塞任务并说明需要的决策
```
"两次失败即上报"是防止 agent 空转的核心规则，很多 agent 系统缺这条就会陷入重试地狱。

## 五、全网口碑

- 868⭐（2026-09 后活跃），定位为 Nous Research `hermes-agent` 的"工作流增强层"，与 `garrytan/gbrain` 记忆骨干可组合。
- 在 agent 工作流/agentic 创业圈有一定讨论度；README 的"7 角色 + 36 skill"矩阵表是其招牌，被视为"把 agent 当 CTO 用"的较完整实现。

## 六、竞品对比

| 项目 | 形态 | 角色编排 | 审批护栏 | 可移植 |
|---|---|---|---|---|
| **oh-my-hermes** | Hermes 的 skill/agent/workflow 包 | 7 角色 + 36 skill | ✅ 不可逆 gate | 依赖 Hermes |
| Anthropic/AutoGen Crew | 框架内多 agent | 自定义 crew | 弱 | 框架绑定 |
| n8n/agent 编排 | 可视化工作流 | 节点式 | 手动 | 中 |
| smolagents/crewai | 代码内多 agent | 代码定义 | 无 | 代码绑定 |

**研判**：OHM 的价值不在"技术多新"，而在**把产品构建的治理规则（审批/证据/角色边界/失败上报）固化成可复用资产**。短板是强绑定 Hermes Agent 生态，离开 Hermes 这些 skill 文本需重写适配；且"36 skill 是否都经实战检验"未给量化证据，属于偏方法论、需自行验证的框架。

## 七、核心研判

适合想用 agent 跑通"从想法到上线"全链路的独立开发者借鉴其**治理架构**（而非照搬实现）。最值得摘走的三条：①能力不升格为 agent；②最多三问+默认值；③两次失败即上报。这三条直接决定了 agent 系统是可信任还是会失控。

## 八、关键文件路径速查

- `docs/architecture.md` — 边界/生命周期/状态/记忆键/审批/原则（**先读这个**）
- `AGENTS.md` / `INSTALL_FOR_AGENTS.md` — 安装与 agent 自举说明
- `skills/ship-this-idea.md` — 旗舰 skill 范本（frontmatter 触发式）
- `agents/cto.md` — CTO 角色约束（审批 gate / 恢复策略）
- `scripts/setup-cto.sh` / `ship-this-idea.sh` / `run-cron-safe.sh` — 安装与 cron 安全包装
- `templates/` — AGENTS.md 模板、`.env.example`、健康检查端点
