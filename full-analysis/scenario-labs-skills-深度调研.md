# scenario-labs/skills 深度调研

> 调研日期：2026-11-06 | 星标：2,931⭐（Trending 当日新增）| 语言：Python（Skills 仓库，含 .claude/.codex/.agents 配置）| 许可：MIT | 最近提交：2026-11-05 | 出品方：Scenario（scenario.com，AI 游戏/创意资产生成公司）| 协议：Agent Skills 规范（agentskills.io）

## 1. 项目定位（一句话）

Scenario 出品的**生产级 AI 媒体生成 Agent Skills 集合**——把「出图/视频/音频/3D/纹理/天空盒」等创意生产，封装成符合 [Agent Skills](https://agentskills.io) 规范的技能包，让 Claude Code、Cursor、Codex、Copilot 等 70+ 编码 Agent 通过 **Scenario MCP 服务器**调用，并内建「角色/品牌一致性」「质量闸门」「出价前先询价」等生产就绪机制；另含驱动本地 DCC 软件（Blender/Maya/ZBrush/Unreal/Unity/Godot/Roblox）的「专家工具」技能族。

## 2. 项目亮点（3-5 条差异化，开篇呈现）

- **不是 awesome-list，是真·技能工程**：每个 skill 是带 `SKILL.md`（YAML frontmatter: `name`/`description`/`license`）+ 脚本 + 参考资产的完整技能包，遵循 agentskills.io 格式，可被 `npx skills add` 直接装入任意兼容 Agent。
- **一致性「耐久度阶梯」是核心方法论**：`scenario-consistency` 把「让一个角色跨镜头/跨角度保持一致」拆成一条可操作的上升阶梯——基线提示词 → 参考图 → 风格参考 → 控制图（control map）→ 训练模型，并明确「seed 解决不了一致性，要靠喂给模型的东西」。
- **生产就绪：质量闸门 + 成本意识内建**：`scenario-quality-gate` 用 `asset_quality_gate_run` 返回 pass/warn/fail 与 0–100 分项评分；调用前可用 `dry_run: true` **免费探价**（`creativeUnitsCost`），已存结论则免费复用——把「先问价再花、失败封闭（Enterprise 未开则干净降级到 `asset_analyze`）」做成一等公民。
- **模型选择矩阵覆盖全栈**：技能横跨 gpt-image、gemini、ideogram、kling、runway、veo、seedance、elevenlabs、meshy、rodin 等数十家供应商，「按任务挑模型」而非绑定一家。
- **供应链卫生**：支持 `npx skills add ...#<commit>` 钉到已评审的 release commit；CI（release-please 自动发版）、OpenSSF Scorecard 徽章、CHANGELOG 齐备，工程成熟度高于多数个人技能仓。

## 3. 核心架构

仓库是「技能集合 + 清单 + 安装器入口」三层：

```
skills/                     # 全部技能（核心）
  scenario-*               # 经 Scenario MCP 的生产技能（出图/视频/音频/3D/一致性/质量闸门…）
  dcc/                     # 专家工具：驱动本地 DCC（zbrush/blender/maya/...）
  game-engines/            # 专家工具：Unreal/Unity/Godot/Roblox
skills.sh.json             # 安装器清单：把技能按「角色/目标」分组（Getting started / Images / Game art / Video…）
skills-lock.json           # 锁定版本，保证可复现安装
AGENTS.md / CLAUDE.md      # Agent 协作规约
scripts/ tests/ docs/      # 工程化配套
```

关键架构决策：
- **Scenario MCP 为后端，技能为前端**：所有 `scenario-*` 技能经 `https://mcp.scenario.com/mcp`（OAuth 或 API Key）调用真实生成能力；技能层只负责「把创意意图翻译成工具调用 + 控制质量/成本」。
- **「专家工具」族走本地应用而非 SaaS**：`dcc/*`、`game-engines/*` 需要本机装有 Blender/Maya/Unreal 等，技能 README 记录「如何构建、验证到哪一步」——这部分**不依赖 Scenario 账号，是相对厂商中立的价值**。
- **清单驱动分发**：`skills.sh.json` 用 `groupings` 把 80+ 技能按角色聚合，安装器据此给菜单；每个技能 `description` 精心设计成 Agent 的触发词（Triggers/Keywords），决定何时被自动调用。

## 4. 应用场景与启发

- **给「Agent 生产创意资产」需求提供可落地范式**：做游戏/短视频/营销素材时，不是「调一次模型出张图」，而是「基线+参考+控制图+质量闸门+成本护栏」的闭环——这条链路可直接复用到任何需要**可控、可复现、可审计**的 AIGC 工作流。
- **可借鉴的工程模式**：
  - **一致性阶梯**：任何「保持身份/风格一致」的 Agent（头像、品牌、数字人）都可用「提示词基线 → 参考 → 控制图 → 微调模型」的耐久度递增模型来组织，而不是寄希望于 seed。
  - **先询价后执行**：把 `dry_run` 探价 + 缓存结论做成工具层默认值，避免 Agent 在长任务里悄悄烧钱——是「Agent 经济护栏」的范本。
  - **质量闸门即门禁**：`pass/warn/fail` + 分项 `reasons/suggestions`，可嵌入 CI/批处理管线，让「AI 产出」过一道机器审查再放行。
- **局限提醒**：`scenario-*` 族强依赖 Scenario 商业 MCP（SaaS + API Key/OAuth），带有厂商绑定属性；真正厂商中立、可本地跑的只有 `dcc/*` `game-engines/*` 专家工具族。

## 5. 源码深度解读（2-3 个最核心模块，每段 5-15 行）

**① 一致性阶梯——`skills/scenario-consistency/SKILL.md`（核心方法论）**

不是代码而是「写给 Agent 的操作手册」，但它把一致性拆得非常工程化：

```markdown
| Technique                  | Holds                | Effort | Reach for it when        |
| Baseline-plus-delta prompt | identity, framing    | low    | always, it is the floor  |
| Reference image input      | identity and world   | low    | a set of scenes/angles   |
| Style reference input      | rendering style      | low    | icon sets, UI, series    |
| asset_detect control map   | pose, geometry       | medium | layout must not move     |
| Trained model              | house style at scale | high   | references stop scaling  |
```

关键洞见写得很直白：「seeds don't solve consistency; consistency comes from what you feed the model」。Agent 被教导「先 `asset_display` 看基线、再字节级枚举不变项、只在末句放 delta」，把一致性从玄学变成可枚举的输入约束。

**② 质量闸门与成本护栏——`skills/scenario-quality-gate/SKILL.md`**

```markdown
| Call                 | What happens                       | Cost                         |
| Plain call, verdict stored | Returns stored verdict        | Free                         |
| Plain call, no verdict    | Runs new analysis, stores it   | Billed (creativeUnitsCost)   |
| dry_run: true            | No run; returns price as cost  | Free  ← 先询价再花           |
| rerun: true             | Replaces stored verdict         | Billed                       |
```

闸门工具 `asset_quality_gate_run` 返回 `pass/warn/fail` + 0–100 分项；当团队未启用 Enterprise 插件时**调用干净失败**，技能指示降级到 `asset_analyze` 并显式说明——典型的 fail-closed 设计。读执行器拒 `asset_quality_gate_run`（按 lane 区分读写），须走 `scenario_tool_execute_write`，否则被拒并指错通道。

**③ 清单分组——`skills.sh.json`**

```json
{ "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "notGrouped": "bottom",
  "groupings": [ { "title": "Images",
    "description": "Generate and edit images: model choice, sizing, references…",
    "skills": ["scenario-image","scenario-multi-reference","scenario-product-shots", ...] } ] }
```

安装器据此把 80+ 技能聚成「入门 / 找方向 / 图像 / 游戏美术 / 视频音频 …」菜单，Agent 或人按角色选装——清单即分发契约。

## 6. 全网口碑

- 出品方 Scenario 是 AI 游戏资产生成赛道 known player（融资、与游戏工作室合作），仓库工程痕迹专业：CI、release-please 自动发版、OpenSSF Scorecard、CHANGELOG、pin 到 commit 的安装方式。
- 发布数日即 2.9k⭐，踩中「Agent + AIGC 生产化」热点；社区讨论集中在「终于有人把一致性/质量闸门做成技能」与「比单纯调图模型更 production」。
- 争议点（社区共识）：`scenario-*` 强绑 Scenario SaaS，被部分人视为「给自家 MCP 拉客户的技能市场」；离线可用的只有 DCC/引擎专家工具族。

## 7. 竞品对比 + 核心研判

| 项目 | 类型 | 差异 |
|------|------|------|
| **scenario-labs/skills** | 生产级媒体生成技能包（含 MCP 后端 + 一致性/质量闸门） | 最「production-ready」，工程化最深 |
| anthropics/skills、mattpocock/skills、google/skills、vercel-labs/skills | 通用技能集合 | 泛用、不绑定生成后端、无一致性/成本护栏 |
| ComposioHQ/awesome-claude-skills 等 | awesome-list 类 | 多为清单，非完整技能包 |
| ComfyUI / Stable Diffusion / Midjourney | 生成应用 | 是「工具」不是「Agent 技能封装」 |

**核心研判**：
- 它的真正价值不在「能出图」，而在**把 AIGC 生产化经验固化成可复用技能**：一致性阶梯、质量闸门、出价前询价——这三点对任何要「稳定产出可控创意资产」的 Agent 都可直接借鉴。
- 风险是厂商绑定：`scenario-*` 必须连 Scenario MCP（账号/API Key），更适合已用 Scenario 的团队；纯自建 Agent 应重点吸收其**方法论**，而非依赖其 SaaS。
- 对本索引的意义：它把「AI 编码/Skill」从「清单罗列」拉到「真实技能工程」的标杆样例，值得作为该领域的参考实现研读。

## 8. 关键文件路径速查

- `skills/scenario-consistency/SKILL.md` — 一致性耐久度阶梯（核心方法论）
- `skills/scenario-quality-gate/SKILL.md` — 质量闸门 + 成本护栏（dry_run 探价 / fail-closed 降级）
- `skills/scenario-image/`、`skills/scenario-video/` 等 — 各生成域技能
- `skills/dcc/`、`skills/game-engines/` — 本地 DCC/引擎专家工具族（厂商中立部分）
- `skills.sh.json` — 安装器分组清单（分发契约）
- `skills-lock.json` — 版本锁定，保证可复现安装
- `README.md` / `INSTALL.md` — 安装与按角色选技能指南
