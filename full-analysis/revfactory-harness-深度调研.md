# revfactory/harness — Claude Code 的「Agent 团队架构工厂」深度调研

> **调研更新**: 2026-07-31（重写：旧报告目录结构系臆测，本次全部基于真实仓库树）
> **Stars**: 8,562⭐ | **语言**: HTML（实际核心是 Markdown 技能包）| **许可**: Apache-2.0（旧报告误标 MIT）
> **仓库**: https://github.com/revfactory/harness | **最近推送**: 2026-07-24

## 项目定位（一句话）

一个 Claude Code 插件形态的**元技能（meta-skill）**：说一句「build a harness for this project」，它就把你的领域描述编译成一支 Agent 团队（`.claude/agents/`）加配套技能（`.claude/skills/`）——README 自我定位为 Claude Code 生态 **L3 Meta-Factory 层的 Team-Architecture Factory**。

## 项目亮点（差异化）

1. **首创生态分层自我定位** — README 给出 L2/L3 生态坐标系，并诚实列出邻居：Archon（Runtime-Configuration Factory）、SaehwanPark/meta-harness（Codex 移植版）、affaan-m/ECC（L2 跨 Harness 工作流），主动教用户「什么时候不该用我」
2. **6 种团队架构模式内置** — 管道 / 扇出扇入 / 专家池 / 生成-检验 / 监督者 / 层级委托，选型逻辑写进技能而非文档
3. **Phase 0 现况审计先行** — 不是每次都从零生成：先读现有 `.claude/agents/`、`.claude/skills/`、CLAUDE.md，检测 drift（定义与记录不一致），再按「新建 / 扩展 / 运维」三模式分支——把哈内斯当作**持续演化系统**而非一次性脚手架
4. **Agent 团队优先原则** — 明确规定 2 个以上 Agent 协作时默认用 Agent Teams（TeamCreate + SendMessage + 共享任务表），仅在纯结果传递场景降级为 SubAgent，并给出决策顺序
5. **全 Markdown 实现零代码依赖** — 整个「工厂」由 SKILL.md + 6 份 references 文档构成，无任何运行时代码，天然跨版本稳定

## 核心架构（真实仓库树）

```
harness/
├── .claude-plugin/                # Claude Code 插件清单（marketplace.json + plugin.json）
├── skills/harness/
│   ├── SKILL.md                   # 核心：Phase 0-7 完整工作流（韩语原文）⭐
│   └── references/                # 渐进式加载的知识库
│       ├── agent-design-patterns.md   # 6 架构模式 + 执行模式决策树 + Agent 分离 4 轴
│       ├── skill-writing-guide.md     # 技能撰写 + 技能复用设计
│       ├── qa-agent-guide.md          # QA Agent 专项（增量 QA + 边界面交叉比对）
│       ├── skill-testing-guide.md     # with-skill vs without-skill 对比测试
│       ├── orchestrator-template.md   # 编排器模板
│       └── team-examples.md           # 实际团队定义全文示例
├── docs/quickstart.md
├── _workspace/                    # 项目自身用 harness 管理自己的产出（吃自己的狗粮）
└── index.html                     # 项目主页（这就是语言显示 HTML 的原因）
```

**工作流**：Phase 0 现况审计 → 1 领域分析 → 2 团队架构设计（先选执行模式，再选架构模式）→ 3 Agent 定义生成 → 4 技能生成 → 5 集成与编排 → 6 验证测试 → 7 运维（含 7-5 审计/同步子流程）。

## 应用场景与启发

**可用场景**：
- 新项目冷启动时自动生成一套领域专属 Agent 团队配置（替代手写 agents/skills）
- 已有 `.claude/` 配置混乱时的审计与去重（Phase 0 drift 检测 + 3-0/4-0 重复检查）
- 学习「多 Agent 团队什么时候拆、怎么拆」的最佳参考教材

**给同类需求的启发**：
1. **配置生成器必须先审计后生成**——Phase 0 的「新建/扩展/运维」三分支 + Phase 选择矩阵（按变更类型决定跳过哪些 Phase），是所有「AI 生成配置」类工具避免重复堆积的通用解法
2. **「Agent 定义必须落文件」的铁律**：禁止把角色直接塞进 Agent prompt——理由是跨会话复用、协作协议显式化、Agent(谁)与 Skill(怎么做)分离。自建多 Agent 体系时值得直接采纳
3. **QA Agent 的两条反直觉经验**：QA 用 general-purpose 而非只读类型（要跑验证脚本）；QA 的核心是「边界面交叉比对」（同时读 API 响应和前端 hook 比较 shape）而非存在性检查，且每模块完成即增量执行而非最后一次性检查
4. **元技能自举**：`_workspace/` 里是它用自己生成的 auditor/content/scout/strategist 团队做自己的发布运营——meta 工具的最佳可信度证明

## 源码深度解读

### SKILL.md 的执行模式决策表（核心创新点）

```
| 模式 | 何时使用 |
| Agent 团队（默认）| ≥2 Agent 协作、需实时协调/反馈交换、中间产物相互引用 |
| SubAgent（备选）  | 单 Agent、只需返回结果、团队通信开销大于收益 |
| 混合             | Phase 特性不同时——如并行收集(Sub) → 共识整合(团队) |
```

配套硬性规定：所有 Agent 一律 `model: "opus"`（质量优先）；一个会话只能一支活跃团队，管道式多阶段需「产出落盘 → 解散 → 重建」。

### 用户熟练度感知（Phase 1 第 5 条）

从对话措辞推断用户技术水平并调整沟通语气——「对编码经验少的用户不要不加解释地用 assertion、JSON schema 这类词」。把 UX 适配写进技能正文而非交给模型自觉，属于少见的成熟做法。

### 渐进式披露

SKILL.md 只保留决策骨架，细节全部下沉到 references/ 按需加载——与 Anthropic 官方 Skills 最佳实践一致（约 100 token 名称常驻，命中才载正文）。

## 全网口碑

- 独立深度评测少（数据不可用），主要传播渠道为 Claude Code 插件 marketplace 与 Agent Skills 社区策展清单
- README 提供三语（EN/KO/JA），核心 SKILL.md 为韩语——韩国开发者社区背景，非英语内核对部分用户是理解门槛
- 8.5K⭐ 且 2026-07 仍在活跃更新（v1.2.0），处于健康增长期

## 竞品对比

| 维度 | harness | coleam00/Archon | affaan-m/ECC | SaehwanPark/meta-harness |
|------|---------|----------------|--------------|--------------------------|
| 生态层 | L3 团队架构工厂 | L3 运行时配置工厂 | L2 跨 Harness 工作流 | L3（Codex 移植） |
| 产出物 | Agent 团队 + 技能 | 确定性运行时配置 | 标准化 skills/rules/hooks | 同 harness |
| 架构模式库 | ✅ 6 种显式 | ❌ | ❌ | 继承 harness |
| 审计/运维流程 | ✅ Phase 0 + 7-5 | ⚠️ | ⚠️ | 继承 |
| 实现形态 | 纯 Markdown 技能 | 带代码运行时 | 配置集 | 纯 Markdown |

README 自己给出的选型建议：要运行时确定性选 Archon，要团队架构选 harness，两者可组合。（注：ECC 已入库本仓库 `affaan-m-ECC-深度调研.md`，可交叉阅读。）

## 核心研判

**优势**：生态位定义清晰且诚实；Phase 0 审计 + drift 检测解决了「生成器反复用会堆垃圾」的真实痛点；QA 指南与执行模式决策树有独立参考价值，即使不装插件也值得读。

**风险/局限**：
1. 核心 SKILL.md 为韩语，跨语言用户依赖模型翻译理解，细节保真度存疑
2. 强绑定 Claude Code 的 Agent Teams 能力（TeamCreate/SendMessage），Claude Code API 一变即需跟随维护
3. 强制 `model: "opus"` 成本高昂，未给预算敏感场景留降级路径
4. 元层工具的固有风险：生成的团队质量最终受限于用户领域描述质量

**启发即价值**：对本调研体系而言，harness 的 Phase 0 审计思想（先盘点现况→检测 drift→再决定动作）与本仓库每日巡检工作流同构，其「变更类型 × Phase 选择矩阵」可借鉴用于报告维护分级。

## 关键文件路径速查

| 路径 | 作用 |
|------|------|
| `skills/harness/SKILL.md` | 核心工作流 Phase 0-7 ⭐ |
| `skills/harness/references/agent-design-patterns.md` | 6 架构模式 + 执行模式决策树 ⭐ |
| `skills/harness/references/qa-agent-guide.md` | 增量 QA + 边界面交叉比对 |
| `skills/harness/references/team-examples.md` | 团队定义文件全文示例 |
| `.claude-plugin/plugin.json` | 插件清单（marketplace 安装入口） |
| `_workspace/` | 项目自举产出（狗粮证明） |
