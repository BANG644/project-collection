# 🔬 Dicklesworthstone/destructive_command_guard (dcg) — 深度调研

> 调研日期：2026-07-15 | 数据来源：GitHub API + README + 源码树
> ⭐ Stars：**4,285**（+481 当日 Trending） | 🍴 Forks：162 | 📅 创建：2026-01-07 | 🔤 语言：Rust | 📜 协议：MIT（README/LICENSE 标注；GitHub API 返回 NOASSERTION，疑似 LICENSE 非标准 SPDX 头） | 🏷️ topics：ai-agents / cli / developer-tools / git / rust / safety

## 一、项目亮点（差异化）

1. **Agent 原生拦截，而非通用 hook**——专为 AI 编码 Agent 设计，原生支持 Claude Code、Codex CLI 0.125+、Gemini CLI、GitHub Copilot CLI、Cursor、Hermes、Grok、Antigravity、OpenCode、Pi、Aider 等 12+ 工具，自动注入各自 hook 配置。
2. **AST 匹配 > 正则**——用 `ast_matcher.rs` 把 shell 命令解析成 AST 再判定破坏性行为，比纯正则更抗绕过（如换行、变量拼接、heredoc 内联脚本）。
3. **模块化 Pack 系统（50+ 安全包 / 30 类）**——按 database/kubernetes/cloud/containers/windows 等场景分装，分类 ID 可一键展开全部子包，默认只开最致命的 `core.*`。
4. **双正则引擎 + SIMD 加速**——快速过滤层（SIMD 加速）+ 惰性编译的精确正则，亚毫秒级拦截，对 Agent 每个命令零感延迟。
5. **置信度评分 + 分级响应 + 逃生舱**——`confidence.rs` 打分，配合 allowlist、scan 模式、allow-once 短码、`DCG_BYPASS=1` 等机制，在"安全"与"不碍事"间留足回旋空间。

## 二、项目全景

dcg（Destructive Command Guard）是一个**高性能 Agent hook**，在 AI 编码 Agent 真正执行破坏命令前拦截它——防止 `git reset --hard`、`rm -rf ./src`、`DROP TABLE users` 这类灾难在几秒内摧毁数小时未提交的工作。

项目 2026 年 1 月由 **Jeffrey Emanuel（Dicklesworthstone）** 以 Python 脚本起步，后由 **Darin Gordon（Dowwie）** 移植为 Rust 并做 SIMD 性能优化，Jeffrey 再大幅扩展出模块化 pack 系统、AST 匹配、上下文分类、置信度、scan 模式与双正则引擎。属于"Agent 安全 guardrail"这一 2026 年快速升温的细分方向。

## 三、核心架构

```
dcg (Rust binary)
├── hook.rs / agent.rs       Agent hook 注入与多 Agent 适配层
├── ast_matcher.rs           命令 → AST 解析匹配（抗绕过）
├── evaluator.rs             命中判定 + 置信度聚合
├── confidence.rs            风险置信度评分
├── normalize.rs / heredoc.rs 命令归一化 + heredoc/内联脚本扫描
├── context.rs / config.rs   上下文分类 + TOML 配置
├── allowlist.rs / cli.rs    白名单 + CLI 入口
├── git.rs                    git 语义感知
├── mcp.rs                   MCP server（供 Agent 主动查询）
├── history/                 审计历史（schema.rs）
├── output/                  console/denial/escalation/suggestions/tree/...
└── packs/                   50+ 模块化安全包（按场景分类）
    ├── core.{git,filesystem}
    ├── database.{postgresql,mysql,mongodb,...}
    ├── kubernetes / cloud / containers / windows / storage / secrets ...
```

- **三层架构**（README 提及 three-tier architecture）：快速过滤（SIMD 正则）→ AST 语义匹配 → 上下文/置信度裁决。
- **默认只开最致命包**：无配置文件时仅启用 `core.filesystem`(rm -rf 出临时区)、`core.git`(丢未提交/改历史)、`system.disk`(mkfs/dd/wipefs)；Windows 额外默认开 `windows.filesystem`/`windows.system`。其余（如 `database.postgresql`、`containers.docker`）需显式开启。
- **Agent 画像（profiles）**：自动识别调用方 Agent，按 `trust_level`（仅记录、不改判定）、`disabled_packs`/`extra_packs`、`additional_allowlist`/`disabled_allowlist` 差异化配置。
- **跨 Agent 兼容性层**：如检测到 Codex 负载的 `turn_id` 非空，只回吐 Codex 文档规定的 denial 字段，避免 hook 因未知字段被拒。

## 四、应用场景与启发

> 这个仓库可以用在哪些场景 / 给同类需求带来什么解决思路

- **Agent 护栏的范式样本**：任何让 LLM 直接执行命令的系统（CI Agent、运维 Copilot、内部自动化）都应借鉴"hook 拦截 + 语义匹配 + 分级响应"三层模型，而不是信任模型"不乱来"。
- **AST 而非正则做命令安全**：dcg 的核心启发是——对"破坏性行为"的判定应建立在**语法树**层面（含 heredoc/变量展开/管道），纯黑名单正则极易被换行、别名、内联脚本绕过。
- **"分类 ID 展开子包"的配置 UX**：`enabled = ["database"]` 自动展开全部 `database.*`，是大规模规则集可维护性的好设计，可复用到任何策略引擎。
- **逃生舱设计**：`DCG_BYPASS`、`allow-once` 短码、永久 allowlist 三层逃生机制，平衡了"严格"与"可操作性"，是安全工具避免被用户一怒卸载的关键。

## 五、源码深度解读

### 1) AST 语义匹配（`src/ast_matcher.rs` 思路）

```rust
// 不靠正则逐行扫，而是把命令解析为 AST 后判定语义
// 例：能识别 `find . -name x -exec rm -rf {} \;`、
//     heredoc 内嵌的 `rm`、`VAR="rm -rf"; $VAR /` 等变形
// 匹配层在快速 SIMD 过滤层（lazy-compiled regex）之后，
// 只对疑似命令做 AST 解析，保证亚毫秒级
```

### 2) 判定与置信度（`src/evaluator.rs` + `src/confidence.rs`）

```rust
// evaluator：对命令跑启用 pack 的规则，聚合命中
// confidence：依据"是否出临时区 / 是否有恢复手段 / 上下文"
//   给出置信度，驱动 graduated-response（警告→拦截→升级）
// 输出经 output/ 分层渲染：denial（拒绝载荷）、
//   suggestions（给安全替代命令）、escalation（升级人工）
```

### 3) 模块化 Pack（`src/packs/database/postgresql.rs` 等）

```rust
// 每个 pack 是一组声明式破坏模式 + 建议替代
// 分类 ID 映射：database → database.postgresql / .mysql / .mongodb ...
// 安装期 `dcg init` 生成 starter config，仅开常见示例包，
// 非配置即默认仅 core.* —— 避免"开箱即拦截一切"劝退用户
```

## 六、社区口碑

- **质量信号**：README 挂 **Codecov 覆盖率**徽章，文档极其完善（docs/packs、docs/agents、docs/codex-integration、docs/graduated-response 等），是同期 Agent 安全工具里工程完成度最高的之一。
- **生态适配广**：一次性覆盖 12+ 主流 Agent 工具的原生 hook，Windows 还提供 PowerShell 安装器（SHA256 + Sigstore/cosign 校验），降低了采用门槛。
- **作者权威**：Jeffrey Emanuel 在 Agent 工程圈有影响力，原始 Python hook 方案被广泛引用；Rust 版由 Darin Gordon 做性能底座。

## 七、竞品对比 + 核心研判

| 维度 | dcg | 通用 pre-commit / git hooks | safe-rm / trash-cli | gitleaks(密钥) | annoying(python) |
|------|-----|------------------------------|---------------------|----------------|------------------|
| 面向 Agent hook | ✅ 原生 | ❌ 通用 | ❌ | ❌ | ⚠️ |
| 语义(AST)匹配 | ✅ | ❌(正则/脚本) | ❌ | ❌ | ⚠️ |
| 多 Agent 适配 | ✅ 12+ | ❌ | ❌ | ❌ | ❌ |
| 模块化规则包 | ✅ 50+/30类 | ⚠️ 需自写 | ❌ | 单一 | ❌ |
| 置信度/分级响应 | ✅ | ❌ | ❌ | ❌ | ⚠️ |

**核心研判**：
- **价值成立**：随着 Claude Code / Codex / Cursor 等 Agent 普及，"Agent 误删生产数据"已从段子变成真实事故。dcg 把"命令级护栏"做成开箱即用的跨 Agent 工具，切中刚需，且 AST 匹配的工程深度领先于纯正则方案。
- **护城河**：① 对 12+ Agent 的 hook 适配层（含 Codex 协议兼容、Windows 原生）是苦活壁垒；② 50+ pack 的覆盖率形成网络效应；③ 亚毫秒性能让 Agent 无感。
- **风险**：① 依赖各 Agent 的 hook 协议稳定，上游改协议需快速跟进；② "拦截型"工具天然处在"安全 vs 打扰"的张力中，误拦会劝退用户；③ Rust 单二进制分发虽好，但规则集演进速度赶上生态变化是长期挑战。
- **结论**：Agent 安全 guardrail 方向最值得关注的 Rust 实现之一，可直接用于任何"让 LLM 跑命令"的生产系统；其 AST 匹配 + 分级响应 + 模块化 pack 的三段式设计是可复用的安全工具范式。

## 八、关键文件速查

| 路径 | 说明 |
|------|------|
| `README.md` | 安装、配置、Agent 适配、pack 系统总览 |
| `src/ast_matcher.rs` | 命令 AST 语义匹配核心 |
| `src/evaluator.rs` / `src/confidence.rs` | 判定与置信度 |
| `src/hook.rs` / `src/agent.rs` | hook 注入与多 Agent 适配 |
| `src/packs/` | 50+ 模块化安全包（按场景分类） |
| `docs/packs/README.md` | 全部 pack ID 索引 |
| `docs/codex-integration.md` | Codex 协议兼容细节 |
| `src/mcp.rs` | 供 Agent 主动查询的 MCP server |
| `install.sh` / `install.ps1` | Linux/macOS/WSL 与 Windows 原生安装器 |
