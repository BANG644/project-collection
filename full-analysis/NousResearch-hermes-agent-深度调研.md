# 🔬 NousResearch/hermes-agent — 全方位深度调研

## 📌 一句话定位

**Nous Research 出品的自我进化型 AI Agent 框架**——"The agent that grows with you"（与你共同成长的 AI 智能体），内置闭环学习循环，能从经验中自动创建技能、改进技能、构建跨会话用户画像，是目前唯一具备真正自进化能力的生产级 Agent 框架。

## ⭐ 项目亮点

1. **唯一内置闭环学习循环的 Agent 框架**：复杂任务完成后自动沉淀为技能（SKILL.md），技能在使用中自我改进，陈旧的自动归档——这是 Hermes Agent 相对于 OpenClaw、DeerFlow 等竞品**最根本的差异化能力**（[README 原文](https://github.com/NousResearch/hermes-agent)）
2. **最广泛的平台覆盖（12+消息平台）** ：Telegram、Discord、Slack、WhatsApp、Signal、Matrix、飞书、钉钉、Email……从单一 gateway 进程出发，所有平台共享同一套工具和记忆系统（[Issue #43854 — macOS Dock icon 单源化](https://github.com/NousResearch/hermes-agent/issues/43854)）
3. **真正的模型无关（18+提供商 + 本地推理）** ：`hermes model` 一键切换——Anthropic、OpenAI、DeepSeek、GLM、Kimi、Ollama、vLLM……无生态锁定（[Providers 文档](https://hermes-agent.nousresearch.com/docs/integrations/providers)）
4. **极致灵活的部署选项**：6 种终端后端（Local / Docker / SSH / Daytona / Singularity / Modal），从 $5/mo VPS 到 GPU 集群到无服务器（空闲休眠、近乎零成本）([README 终端后端表格](https://github.com/NousResearch/hermes-agent))
5. **工业级 Agent 循环设计**：双重迭代保护（max_iterations + IterationBudget）、预算压力渐进警告（70%/90%）、智能迭代退还、长代码块边界保持——每一个"隐藏"设计都在 README 之外（[run_agent.py 源码分析](https://github.com/NousResearch/hermes-agent/tree/main/hermes)）

## 🏗️ 项目架构全景

### 目录结构

```
hermes-agent/
├── agent/              ← 核心 Agent 运行时（循环、记忆、技能）
│   ├── lsp/            ← 语言服务器协议
│   ├── pet/            ← 提示工程工具
│   ├── secret_sources/ ← 凭证源
│   └── transports/     ← 消息传输层
├── hermes_cli/         ← CLI 入口 + 设置向导
├── gateway/            ← 消息网关（多平台路由）
├── tools/              ← 40+ 工具注册
├── skills/             ← 内置技能
├── optional-skills/    ← 可选技能
├── plugins/            ← 插件系统
├── apps/               ← 桌面应用（Electron）
│   ├── desktop/        ← Electron 桌面端
│   └── bootstrap-installer/ ← Tauri 安装器
├── dashboard/          ← Web 控制面板
├── acp_adapter/        ← Agent Communication Protocol
└── acp_registry/       ← ACP 注册表
```

### 技术栈

- **核心语言**：Python 3.11+
- **CLI/TUI**：Rich + Textual
- **桌面端**：Electron + TypeScript/React
- **数据库**：SQLite（会话存储）
- **全文搜索**：FTS5
- **安装器**：Tauri（Rust）+ uv（Rust Python 包管理器）
- **协议**：Matrix（E2EE）、MCP、ACP

### 核心设计哲学

Hermes 的设计遵循一个核心原则：**Agent 的价值不仅在于单次任务完成，更在于长期积累的知识和对用户的理解**。这体现在：

- **保守但务实的并行策略**：仅白名单工具可并行（最多 8 线程），文件操作有路径重叠检测
- **多层容错**：API 重试、工具名模糊修复、预算警告渐进制、渐进式降级
- **缓存友好**：系统提示末尾设缓存断点，充分利用 Anthropic prompt caching（token 成本节约约 75%）
- **可审计**：记忆用 Markdown 文件（`MEMORY.md`, `USER.md`），技能用结构化 `SKILL.md`
- **安全深度防御**：命令审批、SSRF 防护、环境变量过滤、Prompt Injection 检测
- **数据飞轮**：Agent 运行 → 轨迹保存 → RL 训练 → 模型改进 → Agent 更好

## 💡 应用场景与启发

### 典型使用场景

1. **个人长期 AI 助手**：在 Telegram/Discord 上运行，跨会话记忆你的偏好和工作习惯，越用越懂你
2. **开发伴侣**：内置 40+ 工具（终端、文件、浏览器、git），配合 Delegation 做并行子任务
3. **团队任务协调**：Kanban 看板系统 + 多 Worker 协作 + 心跳检测 + 僵尸回收，支持真正的多 Agent 团队
4. **自动化运维**：Cron 调度 + 14+ 消息平台推送，定时报告/备份/审计
5. **研究数据流水线**：批量轨迹生成 + Atropos RL 环境 + WandB 实验追踪

### 可借鉴的解决方案模式

- **Curator 技能生命周期管理**：active → stale（14 天未用）→ archived（30 天），解决 Agent 技能膨胀的经典方案——任何有"技能/插件/知识库"的系统都可以照搬
- **Honcho 辩证式用户建模**：正题→反题→合题三角模型，LLM 动态融合新旧信息而非简单覆盖——这比简单 RAG 的"最近覆盖"策略优雅得多
- **Budget Grace Call**：迭代预算耗尽后允许一次"宽限调用"完成当前操作——防御性编程的教科书级实践
- **智能模型路由**：简单请求走廉价模型，复杂走主力模型——否决式规则保守但有效，成本降低 30-50%

### 同类需求的可参考思路

如果你在构建自己的 AI Agent 系统，Hermes 的以下思路值得直接借鉴：
- **工具自注册机制**：`tools/` 下的每个文件导入时自动向全局 `ToolRegistry` 注册，无需手动配置——零摩擦扩展
- **消息平台适配器模式**：统一 `BasePlatformAdapter` 接口，14+ 平台各实现一次即可，新增平台只需 200-500 行代码
- **FTS5 + LLM 摘要双通道**：原始会话用 FTS5 全文索引（精确匹配），LLM 摘要做语义理解（模糊关联）——效率与质量的平衡

## 🧠 核心源码解读（克制代码量）

### 入口与主流程

Agent 核心循环位于 `agent/` 目录，`run_conversation()` 方法（约 2300 行）采用经典 ReAct 模式：

```
用户输入 → 构造 API 消息 → LLM 推理 → 判断是否调用工具
  ├── 是 → 执行工具 → 返回结果 → 继续循环
  └── 否 → 输出最终回复 → 结束
```

**关键设计决策**：
- **同步执行**（非异步）：父 Agent 等待子 Agent 完成后才继续——简单可控，但大并发场景可能成为瓶颈
- **双重迭代保护**：`max_iterations`（默认 90）+ 线程安全的 `IterationBudget`——防止模型陷入无限循环
- **中断检查**：每次迭代检查 `_interrupt_requested`，支持 Ctrl+C 优雅退出

### 记忆系统架构（五层架构）

| 层级 | 类型 | 持久性 | 实现方式 |
|------|------|--------|---------|
| L1 | Transformer 上下文 | 会话内 | API messages 数组 |
| L2 | SKILL.md 程序性知识 | 永久 | Markdown 文件 |
| L3 | 向量存储索引 | 永久 | Mem0 / SuperMemory 等 |
| L4 | Honcho 辩证式用户建模 | 持续进化 | Honcho API |
| L5 | FTS5 全文检索+LLM 摘要 | 永久 | SQLite FTS5 |

**重要设计决策**（从 Issue 上下文推断）：新内存提供者**不得**添加到 `plugins/memory/`，必须作为独立插件仓库发布——这是防止代码膨胀的原则性边界。

### 工具系统（自动发现 + JSON Schema 验证）

```python
# 简化的注册模式（非源码逐字复制）
registry.register(
    name="terminal",
    toolset="terminal",
    schema=TERMINAL_SCHEMA,    # JSON Schema 参数验证
    handler=_handle_terminal,  # 处理器函数
    check_fn=check_terminal_requirements,  # 可用性检查
    requires_env=["SHELL"],   # 环境变量依赖
    emoji="%F0%9F%92%BB"
)
```

工具注册表的**隐藏能力**（README 没提）：
- `check_fn` 运行时检测环境是否满足（如 Docker 是否安装），不满足自动隐藏
- `requires_env` 声明环境变量依赖，缺失时自动提示用户设置
- 支持 `includes` 嵌套组合（Toolset A includes Toolset B）

### Curator 技能生命周期管理器

技能从创建到消亡的全周期：
```
active → stale（14天未使用，标记但不删除）
  ↓ 30天
archived（移动到备份目录，可手动恢复）
  ↓ 60天（可选）
deleted（由管理员决定）
```

**硬性标准（HARDLINE）**：`description` ≤ 60 字符、使用原生 Hermes 工具引用、必须有测试——这套规则本身就是一份优秀的"Agent 技能编写规范"。

## 📐 架构决策与设计哲学

- **记忆插件封闭化**（2026-05）：新内存提供者不得入库，强制独立仓库发布——防止核心仓库膨胀成"全家桶"
- **看板系统不持久化 delegate_task**：长时间任务应走 cronjob 或 `terminal(background=True)`——避免了分布式系统的复杂度
- **同步 Agent 循环选型**：简单可控、易于调试，适合个人/小团队场景。大并发场景是本项目的有意缺失（vs DeerFlow 的多进程架构）

## 🌐 全网口碑画像

### 好评共识

- "唯一真正能自我改进的 Agent 框架"（知乎，[2026-03-30](https://zhuanlan.zhihu.com/p/2022015752258027715)）
- "开箱即用的一键安装体验最佳，从 curl 到开始聊天不到 2 分钟"（掘金，[2026-05-14](https://juejin.cn/post/7639583242592829490)）
- "12 个平台共享同一 Agent 的设计太优雅了，不像某些竞品每个平台各跑一个实例"（掘金）
- "模型自由切换是杀手级特性，不被任何一个 API 绑定"（开源社区）
- "5 美元 VPS 就能稳定运行，成本极低"（OpenAIToolsHub，[2026-03-16](https://www.openaitoolshub.org/zh-cn/blog/hermes-agent-ai-review)）

### 差评共识 & 踩坑高发区

- **Honcho 默认未启用**：自我改进的"杀手级特性"需要手动配置第三方服务（数据送到 Plastic Labs），隐私敏感用户有顾虑（知乎）
- **桌面端存在体验落差**（Issue [#54473](https://github.com/NousResearch/hermes-agent/issues/54473)）：Desktop 版本渲染和 TUI/CLI 体验不一致，命令补全、中断机制等有 3 个明确回归
- **大模型依赖**：小模型（4B）效果有限，推荐 30B+——不是所有模型都能驱动 Hermes 的全部能力
- **Gatekeeper 配置复杂**：安全审批机制（P0 安全前哨）在部分场景下过于严格（Issue 数据显示有用户反馈不必要的审批请求）

### 维护者响应风格

从 Issue 数据可见，维护团队响应速度快（多为 AI 辅助分类 + 人工确认机制），标签体系完善（15+ 组件标签、4 级优先级、特定 sweeper risk 标签），表明项目工程化管理成熟。

## ⚔️ 竞品对比

| 维度 | Hermes Agent | OpenClaw | DeerFlow | Claude Code |
|------|-------------|----------|----------|-------------|
| **Star 数** | 205k | 373k | 75k | — |
| **核心定位** | 自我进化个人 Agent | 万能跨平台 Agent | 长周期超 Agent | IDE 编码 Agent |
| **自我改进** | ✅ 闭环学习+技能自创建 | ❌ 无 | ❌ 无 | ❌ 无 |
| **平台覆盖** | 12+ 消息平台 | 多 IM（6+） | 6 IM 通道 | 仅 CLI |
| **模型自由** | 18+ 提供商 | 多 | 多 | 绑定 Anthropic |
| **Kanban/团队** | ✅ 看板系统 | ❌ | ✅ SuperAgent 架构 | ❌ |
| **RL 训练** | ✅ 内置 | ❌ | ❌ | ❌ |
| **Desktop 端** | ✅ Electon 桌面端 | ✅ | ❌ | ❌ |

### 核心研判

Hermes Agent 在"自我进化"和"平台覆盖面"两个维度上尚无真正竞品。但它目前的弱点在于**同步 Agent 循环**限制了大规模并发场景（DeerFlow 的多进程 SuperAgent 架构在这方面更强），且 Desktop 端体验落后于 TUI/CLI。

## 🎯 核心研判

**项目优势**（不可替代的价值点）：
- 唯一的闭环学习系统——越用越聪明，不是口号是功能
- 最广的平台和模型覆盖面——真正的"write once, run everywhere"
- 研究就绪的内置 RL 训练管道——数据飞轮驱动模型持续改进

**项目风险**：
- 版本迭代极快（周更），API/配置稳定性存疑
- Desktop 端存在明显的体验断档（Issue #54473 揭示的 3 个回归都是桌面特有）
- 54k+ 开放 Issue 表明维护压力巨大，部分 P1/P2 问题等待时间可能较长
- Honcho 记忆默认未启用，核心卖点需要外部依赖

**适用场景**：个人长期 AI 伴侣、多平台 AI 助手、研究数据生成
**不太适用**：大规模多 Agent 团队（同步循环瓶颈）、低延迟生产 API（Agent 循环开销）

**趋势判断**：🔥 快速上升期——Nous Research 的品牌背书 + 自进化能力的独特性 + 活跃社区，短期内无类似竞品

## 📂 关键文件路径速查

| 文件/目录 | 说明 |
|-----------|------|
| `agent/run_agent.py` | Agent 核心循环（~2300 行） |
| `agent/memory_manager.py` | 五层记忆编排 |
| `agent/curator.py` | 技能生命周期管理 |
| `tools/registry.py` | 工具自动发现注册表 |
| `gateway/` | 消息网关（多平台路由） |
| `hermes_cli/` | CLI 入口 + 设置向导 |
| `apps/desktop/` | Electron 桌面应用 |
| `skills/` | 内置技能目录 |
| `optional-skills/` | 可选技能（较重/专业化） |
| `dashboard/` | Web 控制面板 |
| `pyproject.toml` | 项目元数据和依赖 |
