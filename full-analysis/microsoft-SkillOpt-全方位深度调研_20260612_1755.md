# 🔬 microsoft/SkillOpt - 全方位深度调研

## 📌 一句话定位
SkillOpt 不是一个普通的 prompt 优化仓库，而是把 **agent skill 文档本身当成“可训练参数”** 来做文本空间优化：目标模型冻结不动，由独立 optimizer 根据 rollout 轨迹提出有边界的文档编辑，再通过 held-out gate 决定是否采纳，最终产出可直接部署的 `best_skill.md`。

## 🧭 项目速览
- 仓库：`microsoft/SkillOpt`
- URL：https://github.com/microsoft/SkillOpt
- 创建时间：2026-05-08
- 默认分支：`main`
- License：MIT
- Stars：5853
- Forks：578
- Open issues：7
- 首个 release：`v0.1.0`（2026-06-02）
- 主题标签：`agent-skills`、`self-evolving-agents`
- 主页：`https://aka.ms/skillopt`
- 论文：arXiv `2605.23904`

## 🏗️ 项目架构全景

### 1. 目录骨架
从仓库树看，核心代码可分成 4 层：

1. **训练主循环层**：`skillopt/engine/trainer.py`
2. **优化器层**：`skillopt/gradient/*`、`skillopt/optimizer/*`
3. **后端适配层**：`skillopt/model/*`
4. **部署期延伸层**：`skillopt_sleep/*`

这说明它不是“一个脚本 + 一个 prompt”的玩具实现，而是已经拆成：
- rollout / reflect / aggregate / select / update / evaluate 六阶段训练系统
- 多模型/多执行器后端路由
- 训练期 SkillOpt 与部署期 SkillOpt-Sleep 两条产品线

### 2. 训练哲学：把 skill 当成外部状态，而不是上下文碎片
README 与论文都强调“train skill like train neural networks”，但真正落地在代码里的，是：
- skill 文档是唯一被持续修改的状态载体
- 修改是 **bounded edit**（add/delete/replace），不是任意重写
- 只有通过 selection set 验证的 candidate 才能进入当前 skill
- 推理部署时 **不增加额外 optimizer 调用**，只用产出的 skill 文本

这让它更像“LoRA for agent behavior”，但训练对象从权重矩阵换成了 Markdown skill 文档。

## 🧠 核心源码解读

### 1. `trainer.py`：真正的核心，不在 README，在主循环
`skillopt/engine/trainer.py` 文件头直接把流程写死为六阶段：
1. Rollout
2. Reflect
3. Aggregate
4. Select
5. Update
6. Evaluate

这不是口号，而是工程化 pipeline。它说明 SkillOpt 的核心贡献不只是“让 LLM 改 prompt”，而是把 prompt/skill 编辑组织成一个 **可重复、可缓存、可审计** 的训练过程。

### 2. `gate.py`：验证门是项目的灵魂，而不是附属功能
`skillopt/evaluation/gate.py` 提供三种 gate metric：
- `hard`
- `soft`
- `mixed`

`evaluate_gate()` 的逻辑很直接：candidate 的 gate score 必须严格超过 current score，才会 accept；若再超过 best score，则成为 new best。

这意味着 SkillOpt 的真正护城河不是“会提 patch”，而是 **会拒绝看起来聪明但在 held-out 上没变好的 patch**。

### 3. `reflect.py`：它不是单样本反思，而是 minibatch 反思
`skillopt/gradient/reflect.py` 明确写了：
- 轨迹按 minibatch 组织，而不是一条一条分析
- 支持 failure analyst 与 success analyst
- 可把 target system prompt、user prompt、trace summary 一起喂给 optimizer

这件事很关键：它让 SkillOpt 学到的不是单条 case 的修补，而是 **跨多条失败轨迹提炼规则**。从优化视角看，这更接近梯度估计，而不是单题复盘。

### 4. `skill.py` + `slow_update.py`：这是 SkillOpt 最容易被低估的地方
从 `skillopt/optimizer/skill.py` 和 `skillopt/optimizer/slow_update.py` 看，skill 实际上被拆成了 3 层状态：

#### A. 主体 skill 正文
- 由 step-level patch 更新
- 支持 append / insert_after / replace / delete

#### B. 受保护的 `SLOW_UPDATE` 区
- 标记：`<!-- SLOW_UPDATE_START --> ... <!-- SLOW_UPDATE_END -->`
- 只能由 slow update 覆盖
- step-level analyst 编辑被显式禁止触碰

#### C. optimizer-side meta skill
- 在 `meta_skill.py`
- 不写入 target skill
- 只作为未来 optimizer prompt 的跨 epoch 记忆

**这是整个仓库最有价值的隐藏设计。**
README 虽然提到 slow update / meta update，但如果不读源码，很难意识到它实际上把“经验”拆成了：
- 给 target 模型看的长期规则
- 给 optimizer 模型看的长期教训
- 给当前 step 用的短期 patch

这是一种典型的“控制面 / 数据面”分层：
- target skill = 数据面
- meta skill = 控制面
- gate = 仲裁器

### 5. `slow_update.py`：慢变量不是附会，它真的是受保护的 epoch 级变量
`slow_update.py` 的实现说明 slow update 有三个鲜明特征：
1. 比较的是 **相邻 epoch** 的同一批 sample
2. 会构造成 `improved / regressed / persistent_fail / stable_success` 四类对照
3. optimizer 最终写入的是自由文本 guidance block，而不是 patch list

换句话说，slow update 更像“高层策略注释”而不是“局部补丁”。它承担的是类 momentum / meta-rule 的角色。

### 6. `meta_skill.py`：优化器也被训练，只是不改 target skill
`run_meta_skill()` 会把：
- 上一 epoch 的最后 skill
- 当前 epoch 的最后 skill
- longitudinal comparison
- 先前的 meta skill

一起交给 optimizer，生成新的 `meta_skill_content`。

这等于说：**SkillOpt 不只是训练 skill，也在训练“如何训练这个 skill”**。这点比 README 呈现得更深。

## 📐 架构决策与设计哲学

### 1. 论文版 vs GitHub `main`：仓库默认值并不等于论文复现值
这是最值得用户注意的一条。

在 `configs/_base_/default.yaml` 中：
- `optimizer.use_slow_update: true`
- `optimizer.slow_update_gate_with_selection: false`

而 `trainer.py` 中会打印 slow update acceptance 模式：
- `gated (selection-set validation)`
- 或 `force-accept (unconditional)`

默认值是 `false`，即 **force-accept**。

这与论文描述存在历史差异。Issue #22 中维护者明确解释：
- **论文与论文结果使用的是 gated slow update**
- GitHub `main` 后来切换成了 force-inject / force-accept 语义
- 原因是 gated 版本中 slow update 经常“写不进去”，导致高层 guidance 机制沉默
- 后续才补上 config flag，使两种行为都可复现

**结论：默认 `main` 更偏工程实用，不是纯论文快照。**
如果你的目标是严谨复现实验，必须显式把 `slow_update_gate_with_selection: true` 打开。

### 2. SkillOpt 的核心赌注：强 optimizer + 冻结 target
从论文摘要与仓库实现看，SkillOpt 的世界观很明确：
- target 可以弱
- optimizer 应该强
- 优化成本是离线一次性成本
- 最终产物是可转移、可部署的 skill 文本

这和很多“让目标模型自己反思自己”的方法完全不同。Issue #12 的争议也正源于此：社区质疑它是否在比较中默认享受了更强 optimizer 的优势。维护者的回应是：**这不是偶然设置，而是方法设计的一部分。**

### 3. 它的边界不是“通用 agent 自动进化”，而是“skill 层适配”
Issue #11 有人问它与 Meta Harness 的关系，维护者答复很明确：
- SkillOpt 不主要修改 harness code
- 更关注可迁移、可部署的 skill artifact
- 它与改 harness 的路线是互补关系

这定义了它的红线：
- 它想学的是“规则层”
- 不是“整个 agent runtime 自举重写”

## 🌐 社区口碑画像

### 1. 好评共识
从 README、release 和 PR 动向综合看，社区最认可的点主要有四个：

#### （1）终于把“skill 优化”做成了像训练一样的流程
这不是一句 marketing，而是很多 agent 用户长期缺的工程化抽象：
- skill 可版本化
- patch 可追踪
- gate 可验收
- artifact 可迁移

#### （2）兼容多执行器，而不锁死在单一家族模型
仓库不仅支持 OpenAI/Azure，还加了：
- Qwen backend（PR #29）
- MiniMax backend（PR #26）
- Codex / Claude Code exec backend

这让它更像“agent skill optimizer 平台”，而不是某家模型的 showcase。

#### （3）对 Codex / Claude Code 这类 agent harness 有直接价值
论文摘要直接给出 direct chat、Codex、Claude Code 三种 harness 结果；README 也把这一点写在最显眼的位置。这很打中现在实际用 agent 写代码的人群。

#### （4）`SkillOpt-Sleep` 把论文能力延长到了真实工作流
2026-06-08 的 README 更新把 Sleep 插件推到前台：
- Claude Code 插件
- Codex 插件
- Copilot 插件
- nightly sleep cycle

这不是简单 demo，而是在把“离线 skill 训练”变成“个人 agent 的夜间巩固机制”。这一步非常像从研究代码走向产品形态。

### 2. 差评共识 / 踩坑高发区

#### （1）论文、README、默认代码之间存在语义错位
Issue #22 是最典型例子：
用户指出论文写 slow update 应经过 validation gate，但 `main` 中实际是 force inject。

维护者承认：
- 论文结果对应 gated 版本
- `main` 是 post-submission 的新行为
- 开源时没有明确标出这一点，是仓库发布失误

这说明 SkillOpt 当前最明显的风险不是算法没想法，而是 **研究版、复现版、工程版三者没有完全分层标记清楚**。

#### （2）可复现性材料一开始不完整
Issues #13、#14、#21、#35 都围绕 split manifest、dataset 切分、baseline 含义展开。社区质疑点包括：
- SearchQA split 的精确来源
- 其他 benchmark 的 split 清单何时发布
- `initial.md` 与 no-skill baseline 是否被混淆
- SpreadsheetBench 结果解释是否一致

维护者后来陆续补了 manifests 和说明，但这说明仓库早期在“论文可复现包装”上并不成熟。

#### （3）本地/兼容后端在真实使用中容易踩格式坑
Issue #28 与 PR #40 暴露了典型问题：
- 本地 vLLM/Qwen 路由下 timeout 没转发
- `enable_thinking` 被无条件注入
- 导致返回 `<think>` 内容，解析不到 `<answer>`，最终 `acc=0`

这类问题说明：SkillOpt 的抽象虽统一，但 **不同推理后端的响应 schema 与模板偏差，仍然会在 evaluator 处炸开**。

#### （4）默认配置里有“实验期遗留参数”
Issue #13 里维护者承认某些 config 值更像 vibe coding 遗留，而不是真正用于论文 runs 的值。这对重现实验的人是个警讯：
- 不要把默认 config 当作论文金标准
- 必须同时看 issue 澄清与 release 说明

### 3. 争议焦点

#### 争议一：公平性是否建立在强 optimizer 上？
Issue #12 的用户认为：
- GEPA / Trace2Skill / EvoSkill 等方法原论文强调 self-contained
- SkillOpt 若给所有 baseline 强行接入 GPT-5.5 reflector，比较并不完全等价

维护者的立场是：
- Table 1 比较的是 shared-optimizer protocol
- 问的是“在同样强 optimizer 条件下，哪种 loop 更能产出好 skill”
- 不是严格保留每个 baseline 原始资源约束

我的判断：**两边都没错，但讨论的是两个不同问题。**
- 学术复现视角：需要 protocol fidelity
- 工程实用视角：shared strong optimizer 更符合真实使用

#### 争议二：slow update 到底是 deployable content 还是 optimizer metadata？
Issue #38 明确问到了这点。维护者的回答很关键：
- `SLOW_UPDATE` block 是会跟着 skill 一起部署给 target 的
- `Meta Skill` 才是 optimizer-side memory
- 当前默认 slow update 未经过 selection gate，而论文版经过

这进一步证明：slow update 不是注释，而是 **可部署策略层**。

## ⚔️ 竞品对比

### 1. 主要竞品
结合论文与 issue 讨论，SkillOpt 的直接参照系主要是：
- **TextGrad**：把文本优化看成“语言梯度”问题
- **GEPA**：反思驱动的 prompt evolution
- **Trace2Skill**：从轨迹蒸馏 skill
- **EvoSkill**：进化式 skill 迭代
- **Meta Harness**：改 harness / runtime，而不是只改 skill

### 2. 对比矩阵

| 维度 | SkillOpt | TextGrad | GEPA / Trace2Skill / EvoSkill | Meta Harness 类方案 |
|---|---|---|---|---|
| 优化对象 | 单一 skill 文档 | prompt / text | prompt / skill / trace summary | harness 代码/工作流 |
| 更新粒度 | bounded patch + slow/meta memory | textual gradient | 反思/蒸馏/进化 | runtime 级修改 |
| 验证机制 | held-out gate 很强 | 视实现而定 | 有反思但 gate 纪律不一定同等严格 | 依赖 end-to-end eval |
| 部署成本 | 低，仅带 skill 文本 | 低 | 低到中 | 高，常需改运行环境 |
| 跨 harness 迁移 | 强调支持 | 一般 | 取决实现 | 往往较弱 |
| 工程复杂度 | 高 | 中 | 中 | 高 |

### 3. 我对定位的判断
SkillOpt 的差异化不在“谁先想到让 LLM 改 prompt”，而在三点组合：
1. **文本空间优化器** 的训练纪律
2. **验证门** 的强约束
3. **slow/meta 双记忆结构**

如果只拿“会自动改 skill”来说，它不是唯一；但如果看 **可部署、可复验、可迁移、可分层记忆** 这四点合起来，它目前确实有比较鲜明的独特性。

## 😴 SkillOpt-Sleep：真正值得额外关注的第二产品线
这部分是很多人只看 README 前半段会错过的重点。

`docs/sleep/FINAL_REPORT.md` 显示，SkillOpt-Sleep 已经不是论文附属脚本，而是在试图解决：
- 本地 agent 的长期使用经验如何夜间巩固
- 如何在不训练权重的前提下，让 Claude/Codex/Copilot 越用越好
- 如何把 memory + skill 的演化放到 held-out gate 后面

它给出的结果包括：
- Claude Sonnet → Haiku：多个 seed 从 `0.00 -> 1.00`
- Codex → Codex：text seed 也能 `0.00 -> 1.00`
- 关键结论：**强 optimizer 对弱 target 的离线优化最有效**
- 甚至跨 runtime transfer 也为正

这说明 SkillOpt 已经从“benchmark 训练器”扩展到“agent nightly consolidation engine”。

## 🎯 核心研判

### 1. 项目真正的不可替代价值

#### 价值一：把 skill 优化从玄学变成了有纪律的训练回路
很多 agent 系统都在做“复盘→改 prompt”，但大多缺少：
- 明确的状态对象
- 清晰的 gate
- 长短期记忆分层
- 迁移型 artifact

SkillOpt 是少数把这四件事同时做出来的项目。

#### 价值二：它适合做“弱 target 的离线增益器”
如果你的生产 target 很贵、很慢或不方便训练，那么用更强 optimizer 离线打磨一个 skill，再把 skill 部署回 target，这条路线很有现实价值。

#### 价值三：它为“agent skill engineering”建立了术语和工程框架
它把很多松散概念统一成了可操作对象：
- best skill
- gate metric
- slow update
- meta skill
- held-out selection set

这会影响后续很多 agent tooling 的设计语言。

### 2. 主要风险

#### 风险一：研究叙事与工程默认值仍有错位
如果用户不仔细读 issue，很容易把 `main` 默认行为误当成论文严格复现版本。

#### 风险二：后端兼容层会持续吞噬维护成本
随着：
- OpenAI-compatible provider
- Qwen
- MiniMax
- Codex CLI
- Claude CLI
- Copilot MCP

越来越多，SkillOpt 的真正难点可能会逐渐从“优化算法”转移到“跨后端行为一致性”。

#### 风险三：benchmark 成功不等于复杂真实任务同样稳
Sleep 报告也坦承：
- 当前 seed 规模小
- skill flaw 单一
- 深层 multi-tool / multi-turn 工作流仍是未来工作

所以它已经证明“机制成立”，但还没完全证明“大型生产 skill 演化也同样稳”。

### 3. 适用场景
- 你已经有一个固定 agent/harness，希望通过离线训练把行为稳定提升
- 你想为 Codex / Claude Code / 其他 agent 建立可迁移的 skill artifact
- 你希望保留 target 冻结，只在外部 skill 层演化
- 你关心可审计、可复盘、可 gate 的 agent 适配流程

### 4. 不适用场景
- 你想直接改 agent runtime / harness 逻辑，而不是 skill
- 你需要端到端自动重写工具链或代码执行框架
- 你没有可量化的 held-out eval，只有主观“看起来更好”
- 你希望极简上手，不想承担多 backend / benchmark 的配置复杂度

### 5. 趋势判断
我判断 SkillOpt 目前处于 **快速上升期的研究工程化项目**，而不是成熟稳定平台：
- 上升信号：stars 增长快、release 节奏紧、PR/issue 活跃、Sleep 产品线扩展
- 不成熟信号：复现说明仍在补、默认配置与论文语义需读 issue 才能对齐、兼容层 bug 频出

**一句话判断：它已经证明了“skill as trainable artifact”这条路线是成立的，但离“傻瓜式稳定平台”还有明显工程距离。**

## 🔥 5 条最重要的独家发现（超出 README）
1. **`main` 默认并不等于论文默认**：slow update 默认是 `force-accept`，不是 gated paper mode。
2. **SkillOpt 实际上把经验拆成三层状态**：正文 skill、deployable slow update、optimizer-side meta skill。
3. **真正的抽象核心不是 prompt，而是“带保护区的 skill 文档”**。
4. **Sleep 已经演化成独立产品线**：它在把论文的离线优化思想转成面向真实用户工作流的夜间自进化工具。
5. **最大的现实风险不在算法，而在协议对齐与后端兼容**：issue 里暴露的大多数痛点都不是“方法失效”，而是复现语义、schema、router 和 config 的错位。

## 📂 关键文件路径速查
- `skillopt/engine/trainer.py` — 六阶段训练主循环
- `skillopt/evaluation/gate.py` — held-out gate 判定
- `skillopt/gradient/reflect.py` — minibatch 轨迹反思
- `skillopt/optimizer/skill.py` — patch 应用与 protected region 保护
- `skillopt/optimizer/slow_update.py` — epoch 级慢变量写入
- `skillopt/optimizer/meta_skill.py` — optimizer-side 跨 epoch 记忆
- `configs/_base_/default.yaml` — 默认配置（含 slow update gate 默认值）
- `docs/sleep/FINAL_REPORT.md` — SkillOpt-Sleep 真实实验结果
- `data/README.md` — split manifest 与复现说明

## 📚 证据来源
### 代码
- `skillopt/engine/trainer.py`
- `skillopt/evaluation/gate.py`
- `skillopt/gradient/reflect.py`
- `skillopt/optimizer/skill.py`
- `skillopt/optimizer/slow_update.py`
- `skillopt/optimizer/meta_skill.py`
- `configs/_base_/default.yaml`
- `docs/sleep/FINAL_REPORT.md`
- `data/README.md`

### GitHub Issues / PRs
- Issue #12 — optimizer fairness discussion
- Issue #22 — slow update gated vs force-accept clarification
- Issue #28 + PR #40 — local vLLM/Qwen `acc=0` 与 timeout / thinking 修复
- Issue #33 / #35 — baseline、initial skill 与 SpreadsheetBench 解释
- Issues #13 / #14 / #21 — split manifests / reproducibility materials
- PR #26 / #29 — MiniMax / Qwen backend 扩展

### 外部
- arXiv: `2605.23904` — *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*
