# EvoMap/evolver 深度调研

> 调研日期：2026-09-26 | 数据来源：GitHub API（README / 源码树 / 示例 / GEP 模块清单）| 许可：GPL-3.0 | Stars：9,118 | Forks：848 | 语言：JavaScript | 默认分支：main | 站点：evomap.ai

## 一、项目定位（一句话）

基于 **GEP（Genetic Evolution Protocol，基因进化协议）** 的 **AI Agent 自进化引擎**——用 Genes（能力基因）/ Capsules（封装）/ EvolutionEvents（进化事件）三件套，让 agent 在可审计的前提下自我演化、复用与共享技能。

## 二、项目亮点（差异化）

1. **可审计进化**：核心卖点是「可审计（Auditable）」——每次进化以 EvolutionEvent 记录，基因/封装可追溯，而非黑箱调参。
2. **完全离线可用**：Hub 仅用于网络功能（技能共享 / worker 池 / 进化榜），`node index.js` 本地即可跑，`--review` 人类在环、`--loop` 持续进化。
3. **技能蒸馏与基因化**：`skill2gep.js` 把现有 skill 转成 GEP 基因，`skillDistiller.js` 蒸馏技能，`conversationDistiller.js` 从对话提炼经验。
4. **记忆图谱**：`memoryGraph.js` / `narrativeMemory.js` / `epigenetics.js` 用「表观遗传」隐喻管理经验，呼应生物进化类比。
5. **网络层**：`a2a.js` / `a2aProtocol.js` 实现 A2A 协议接入 EvoMap Hub，支持节点注册与技能市场。

## 三、核心架构

```
index.js                      # 入口（--review / --loop）
src/evolve.js                 # 主进化循环
src/gep/                      # 基因进化协议核心（79 个模块）
   analyzer / candidates / mutation / selector / strategy / curriculum
   skill2gep / skillDistiller / conversationDistiller / memoryGraph
   reflection / epigenetics / crypto / validator / schemas/
src/atp/ src/ops/ src/proxy/ src/solo/ src/webui/ src/experiment/
examples/                     # hello-world.md / recipe.manifest.json / atp-consumer-quickstart.md
SKILL.md / CONTRIBUTING.md / README(中/日/韩)
```

`src/gep/` 模块极密，覆盖「候选评估（candidateEval）、突变（mutation）、选择（selector）、策略（strategy）、课程（curriculum）、反思（reflection）、技能发布（skillPublisher）、验证（validator）」——是一套完整的进化算法基础设施。

## 四、应用场景与启发

- **自我改进 agent**：agent 把成功轨迹蒸馏成基因，下次任务直接复用/变异。
- **技能市场**：Hub 上的进化榜 + 技能共享，类似「agent 能力众包进化」。
- **借鉴点**：「把经验/技能基因化 + 可审计事件日志 + 表观遗传式记忆」是构建「越用越聪明」agent 的可行骨架；离线优先 + 网络可选的设计也利于本地部署。

## 五、源码深度解读

**1. GEP 三件套（`src/gep/`）**

- **Genes**：可复用的能力单元（对应 skill/策略片段）。
- **Capsules**：把基因封装成可分发、可组合的单位。
- **EvolutionEvents**：每次变异/选择/采纳的事件记录，构成审计链。
- 桥梁文件 `skill2gep.js`（skill→基因）、`skillDistiller.js`（技能蒸馏）、`autoDistillLlm.js`/`autoDistillConv.js`（自动蒸馏 LLM/对话）体现「从实践中提炼基因」的闭环。

**2. 进化主循环（`src/evolve.js` + `index.js`）**

`examples/hello-world.md` 给出最简路径：
```bash
node index.js            # 单次进化，打印 GEP prompt 到 stdout
node index.js --review   # 人类在环审查
node index.js --loop     # 持续进化
```
即「生成 GEP prompt → 执行/审查 → 记录 EvolutionEvent → 下一轮」的循环。

## 六、社区口碑

- 9.1k⭐ / 848 fork，evomap.ai 有节点注册与协议 wiki；README 多语言（中/日/韩）。
- 概念新颖（基因进化隐喻 + 可审计），但属早期项目，真实「自进化」效果需实测验证，警惕营销成分。

## 七、竞品对比

| 维度 | EvoMap/evolver | AutoGPT | Darwin Gödel Machine | 普通 prompt 进化 |
|------|---------------|--------|----------------------|------------------|
| 可审计 | ✅ EvolutionEvents | ❌ | 部分 | ❌ |
| 协议化 | ✅ GEP | ❌ | ❌ | ❌ |
| 离线可用 | ✅ | ✅ | ✅ | ✅ |
| 网络共享 | ✅ Hub/技能市场 | ❌ | ❌ | ❌ |

**差异点**：把「进化」协议化、可审计化，并叠加 Hub 网络层做技能共享与排行。

## 八、核心研判

- **概念领先但需验证**：GEP 的「基因/封装/事件」抽象优雅，「可审计」是实打实的卖点；但「agent 自进化」领域普遍夸大，实际增益依赖基因质量与评估器，建议小范围实测后再投入。
- **GPL-3.0 许可**：与 AGPL 不同，GPL-3.0 对网络服务开源要求较宽松，但分发修改版仍需开源。
- **借鉴价值高**：其「经验基因化 + 事件审计 + 表观遗传记忆」的模块划分，对构建长期记忆/自我改进型 agent 很有参考价值，可抽离思路而不必直接依赖本项目。

## 关键文件路径速查

- `index.js` / `src/evolve.js` — 入口与主进化循环
- `src/gep/` — 基因进化协议核心（analyzer/candidates/mutation/selector/strategy…）
- `src/gep/skill2gep.js` / `skillDistiller.js` — 技能→基因与蒸馏
- `src/gep/memoryGraph.js` / `epigenetics.js` — 记忆图谱与表观遗传
- `src/a2a.js` / `src/atp/` — A2A 协议与 Hub 接入
- `examples/hello-world.md` — 最简上手示例
