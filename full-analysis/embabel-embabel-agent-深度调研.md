# Embabel Agent 深度调研

> 调研日期：2026-08-13 | 星标：4,195（2026-08-12）| 协议：Apache-2.0 | 语言：Kotlin / Java | 出品：Rod Johnson（Spring 之父）

## 一、项目定位

Embabel 是 **JVM 上的 agentic flow 框架**，无缝混合 LLM prompt 交互与代码/领域模型，支持**面向目标的智能路径规划**。Kotlin 编写、Java 自然用法，基于 Spring。它不是"再写一个 LangChain"，而是把游戏 AI 的规划算法（GOAP）引入 agent 编排。

## 二、项目亮点

1. **真正的规划（GOAP / Utility AI）**：非有限状态机/顺序执行，系统**动态 formulated plan**，每步后 replan（OODA 循环），能组合已知步骤完成未编程任务。
2. **强类型 + 领域模型**：Action/Goal/Condition 由领域对象支撑，全重构支持，无 magic map。
3. **两种编排方式**：注解模型（`@Agent`/`@Goal`/`@Condition`/`@Action`，类 Spring MVC）+ Kotlin DSL（`agent{}`/`action{}`）。
4. **平台抽象**：`AgentPlatform` 三种执行模式 Focused / Closed / Open（Open 最强大，能用全部资源自定义 agent）。
5. **Spring/JVM 生态**：易接入企业能力；Maven Central；30+ starter（anthropic/bedrock/openai/ollama/mcp/...）。
6. **模块化**：embabel-agent-core / -rag / -shell / -skills / -starters 多模块 Maven。

## 三、核心架构

- **编程模型**：Actions（步骤）、Goals（目标）、Conditions（前后置条件，每次 action 后重估）、Domain model（支撑对象）。
- **规划器**：默认 **GOAP**（Goal Oriented Action Planning，游戏 AI 算法），可插拔；另支持 **Utility AI**（按效用分选 action）。
- **执行**：`AgentPlatform` 实现，Focused/Closed/Open 三模式；Blackboard 共享状态。
- **模块**：
  - `embabel-agent-core` — 核心领域（`agent/domain` / `agent/core` / `agent/api`）
  - `embabel-agent-rag` — RAG 服务（`rag-pipeline` / `rag-tika` 文档解析）
  - `embabel-agent-shell` — CLI shell（多 personality：colossus/hitchhiker/montypython/severance/starwars）
  - `embabel-agent-skills` — Skill 定义/加载/校验（Claude/Cursor/GitHub frontmatter formatter，Docker/Process 脚本执行引擎）
  - `embabel-agent-starters` — 30+ starter（各 LLM 厂商 + mcp + observability）

## 四、应用场景与启发

- **场景**：企业级 agent（需强类型、可测试、可组合、接入 Spring 生态）；复杂多步业务流（如 Tripper 旅行规划）。
- **启发 1**：把"规划"从硬编码工作流提升为**运行时 GOAP 搜索**，是 agent 框架的范式升级（类比游戏 AI）。
- **启发 2**：强类型领域模型 + LLM 混合，让 agent **既灵活又可维护可测试**。
- **启发 3**："Open 模式"让平台能发现开发者未预见的路径——但用 `GoalChoiceApprover` 限制，兼顾能力与安全。

## 五、源码深度解读

### 1. `embabel-agent-core/src/main/kotlin/com/embabel/agent/`
核心领域：`domain/`（Action/Goal/Condition/Blackboard）、`core/`（AgentProcess、规划器）、`api/`（AgentPlatform）。GOAP 规划器在此实现"动态 replan 的 OODA 循环"——这是 Embabel 与"顺序链"框架的根本分野。

### 2. `embabel-agent-skills/src/main/kotlin/com/embabel/agent/skills/`
Skill 体系：`SkillDefinition.kt` / `SkillMetadata.kt`、多 frontmatter formatter（Claude/Cursor/GitHub）、`script/DockerSkillScriptExecutionEngine.kt` + `ProcessSkillScriptExecutionEngine.kt`（`ConfinedInputResolver` 限制输入），把"技能"做成可跨 Claude/Cursor/本地执行的产物。

### 3. `embabel-agent-rag/embabel-agent-rag-pipeline/`
RAG 服务：`RagServiceSearchTools` / `FacetedRagService` / `RagResponseEnhancement`，将 RAG 作为 agent 的**可组合工具**，体现"agent + RAG 原生融合"。

## 六、社区口碑

- 4.2k⭐，Spring 之父 Rod Johnson 出品，Maven Central 发布，SonarCloud 质量门禁，Discord。
- 口碑：被 JVM/Spring 开发者视为"**agent 框架的 Spring 时刻**"；差异化在强类型 + 真规划 + 企业集成。
- 不足：相对早期（2024 起），生态/文档相比 LangChain/Python 仍成长中，示例以 Tripper 为主。

## 七、竞品对比 + 核心研判

| 维度 | Embabel | LangChain/LangGraph（已入库） | Spring AI | Autogen/CrewAI |
|------|---------|------------------------------|-----------|----------------|
| 规划 | GOAP 真规划（运行时） | 图/顺序 | LLM 调用抽象 | 多角色扮演 |
| 类型 | 强类型领域模型 | 弱类型 | 弱类型 | 弱类型 |
| 生态 | JVM/Spring | Python 为主 | JVM | Python |

- **核心护城河**："GOAP 真规划 + 强类型领域模型 + Spring/JVM 企业基因"，填补 JVM 生态高质量 agent 框架空白。
- **风险**：相对早期（4k⭐）、Java/Kotlin 受众小于 Python、需 Spring 心智。
- **研判**：最适合已有 JVM/Spring 技术栈、追求**可测试可维护 agent** 的团队；是 LangChain/Python 框架的强替代而非补充。

## 八、关键文件速查

- `embabel-agent-core/src/main/kotlin/com/embabel/agent/` — domain / core / api
- `embabel-agent-rag/` — RAG 服务
- `embabel-agent-shell/` — CLI（含 personality）
- `embabel-agent-skills/` — Skill 定义/加载/执行
- `embabel-agent-starters/` — 30+ LLM/MCP starter
- `pom.xml` — Maven 多模块根
