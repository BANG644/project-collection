# Open Interpreter 深度调研报告

> 调研时间：2026-06-27 | 仓库：openinterpreter/openinterpreter | ⭐ 64,146 | Apache-2.0
> 最新版本：rust-v0.0.17（2026-06-20）

---

## 一、一句话定位

**Open Interpreter 是一个面向低成本模型（如 DeepSeek、Kimi、Qwen）的轻量级终端编码 Agent——通过 Harness Emulation 机制，让开源模型获得接近闭源顶尖 Agent（如 Claude Code）的代码执行能力，同时保持完全的本地可控性。**

---

## 二、项目亮点（5 条）

### 亮点 1：Rust 重写的性能突围

2026 年，项目从原始 Python 版（已 fork 至 endolith/open-interpreter）完全重写为 Rust。这不是简单的语言迁移，而是对性能瓶颈的系统性解决——Bazel 构建系统、异步 I/O、精细的内存管理，使得模型推理与代码执行的延迟大幅降低。最新 Rust 版本 0.0.17 于 2026-06-20 发布，版本号架构暗示了这是一个从零开始的重建。

### 亮点 2：Harness Emulation 核心创新

这是 README 之外的关键洞察。OI 的核心技术路线不是"为每个模型定制 Agent"，而是 **"emulate（模拟）已知高性能 Agent 的 Harness"**。它内置了 claude-code、claude-code-bare、kimi-cli、qwen-code、deepseek-tui、swe-agent、minimal 等多种 Harness，用户可通过 `/harness` 命令实时切换。这意味着同一个 OI 会话可以无缝切换不同模型的"思维框架"，这是其他工具不具备的能力。

### 亮点 3：它不是 Codex 的替代品——它就是 Codex

OI 最不为人知的事实：它是一个 **OpenAI Codex 的深度 fork**。.codex/ 目录下完整保留了 Codex 的原生技能系统（babysit-pr、code-review、codex-bug 等）。这意味着 OI 继承了 Codex 的 Agent 协议（ACP）、技能编排框架和沙箱体系，而非从零仿制。社区中几乎没人强调这一点。

### 亮点 4：三 OS 原生沙箱

OI 在每个操作系统上提供了**真正的本地沙箱**，而非容器封装：
- macOS：通过 `sandbox-exec`（Seatbelt 沙箱）
- Linux：通过 vendor 的 bubblewrap（用户命名空间 + 挂载命名空间）
- Windows：通过 `windows-sandbox-rs`（基于 Windows Sandbox API + 自定义 ACL/WFP 防火墙规则）

这套沙箱体系直接继承自 Codex，经过了 OpenAI 在 Codex CLI 中的生产验证。

### 亮点 5：低成本的"桥接"价值

OI 最实际的场景是作为 **"开源模型到顶级 Agent 体验的桥梁"**。当你的预算不支持 Claude Opus 4.7（$100-200/mo）或 GPT-5.5 API 时，OI + DeepSeek/Qwen/本地模型的组合可以在 80% 的日常任务中提供接近的体验，而成本几乎为零（仅算力成本）。

---

## 三、项目架构全景

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Open Interpreter (Rust)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌────────────────────────────────┐   │
│  │      TUI 层        │  │      Harness 引擎层             │   │
│  │  (codex-rs/tui)    │  │  (harness 切换 + Provider)      │   │
│  └───────────────────┘  └────────────────────────────────┘   │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                核心服务层                             │     │
│  │  ACP Server │ App Server │ Agent Graph Store         │     │
│  │  Sandbox Manager │ Analytics │ Config                │     │
│  └─────────────────────────────────────────────────────┘     │
│                              │                               │
│  ┌───────────────────┐  ┌────────────────────────────────┐   │
│  │   沙箱引擎          │  │    .codex/ 技能系统              │   │
│  │  (bwrap/Win Sandbox)│  │  (Codex 继承)                  │   │
│  └───────────────────┘  └────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Rust 工作区结构（codex-rs）

`codex-rs/` 是项目的 Rust 核心，包含 30+ 个 crate：

| 模块 | 路径 | 职责 |
|------|------|------|
| **TUI** | `codex-rs/tui/` | 终端界面，Termion/ratatui 渲染，Markdown 渲染、流式输出、状态指示器 |
| **ACP Server** | `codex-rs/acp-server/` | Agent Client Protocol 服务端，实现编辑器集成协议 |
| **Session** | `codex-rs/session/` | 会话管理与状态机 |
| **Sandbox** | `codex-rs/sandbox/` | 沙箱统一接口，路由到各 OS 后端 |
| **Windows Sandbox** | `codex-rs/windows-sandbox-rs/` | Windows 沙箱：ACL、WFP 防火墙、用户隔离、ConPTY |
| **TUI (另一个)** | `codex-rs/tui2/` | 第二代 TUI（可能是正在迁移的新 UI） |
| **Agent Identity** | `codex-rs/agent-identity/` | Agent 身份管理 |
| **Agent Graph Store** | `codex-rs/agent-graph-store/` | Agent 会话图存储（持久化记忆？） |
| **Analytics** | `codex-rs/analytics/` | 遥测与使用分析 |
| **App Server** | `codex-rs/app-server/` | 桌面应用后端服务 |
| **MCP** | `codex-rs/mcp/` | Model Context Protocol 集成 |
| **Skills** | `codex-rs/skills/` | 技能系统 |
| **Registry** | `codex-rs/registry/` | 模型/Provider 注册中心 |
| **Provider** | `codex-rs/provider/` | LLM Provider 抽象层 |
| **CLI** | `codex-rs/cli/` | CLI 入口与参数解析 |

### 3.3 关键架构决策

**Bazel 构建系统**：项目使用 Bazel（而非 Cargo）作为主构建系统，这意味着：
- 支持远程执行缓存
- 严格依赖管理
- 跨平台一致性（CI 中使用 Bazel 构建所有目标）

同时保留 `.cargo/` 目录，表明仍可纯 Cargo 构建，Bazel 是优化层而非替代层。

---

## 四、应用场景与启发

### 场景 1：运维与系统管理（OI 的舒适区）

**适用**：日志分析、文件批量处理、系统监控脚本生成、磁盘清理
**举例**：运维人员可直接说"帮我分析 nginx access.log，统计前 10 IP，用 Python 调用 IP 库查归属地，输出 Markdown 表格"。OI 会自动写代码、装依赖、执行并返回结果。
**优势**：对比 Claude Code（强在代码库理解）和 Cursor（强在 IDE 集成），OI 的优势是**直接操作本地文件系统和执行系统命令**，这正是运维场景的核心需求。
**对比 Aider**：Aider 不敢跑任意 shell 命令（只做 git 化文件编辑），OI 敢。

### 场景 2：办公自动化与文档处理

**适用**：批量重命名 PDF、Excel 透视表生成、Word 文档批量编辑、非交互式 PDF 表单填充
**举例**：用户说"把 reports 文件夹所有扫描件 PDF 用 OCR 提取文本，按日期重命名，含 Error 关键字的移到 error/ 目录"。
**优势**：桌面应用版本（$20/mo Pro）提供了 Word/Excel/PDF 原生编辑器。对比 ChatGPT Code Interpreter（云端沙盒无法接触本地文件），OI 是真正的"有手的 GPT"。
**对比 Codex**：Codex 没有这些文档处理能力，它专注于代码。

### 场景 3：低成本个人编码助手

**适用**：个人项目开发、学习编程、脚本编写、代码审查
**举例**：学生或预算有限的开发者运行 `interpreter --local` + Ollama + Qwen3，零 API 成本获得一个 AI 编码助手。
**优势**：对比 Claude Code（$100-200/mo Max）和 Codex CLI（需绑定 OpenAI 订阅），OI 的本地模式才是真正的"免费"。
**局限**：本地小模型（7B 以下）的能力天花板明显，复杂重构仍需云端模型。

### 场景 4：多模型兜底切换

**适用**：需要对比不同模型输出的场景、模型 API 故障时的降级方案、特定任务找性价比最高模型
**举例**：先用 DeepSeek 做代码审查（便宜），遇到复杂 OI 不擅长的任务切换到 Claude API，再切回本地模型做文件批量处理——`/model` 和 `/harness` 命令让这一切在同一个会话中完成。
**优势**：这是 OI 独有的能力。其他工具（Claude Code 绑定 Anthropic、Codex 绑定 OpenAI、Aider 虽多模型但不支持 Harness 切换）都无法做到这一点。

### 场景 5：Agent 协议集成（ACP）

**适用**：将 OI 嵌入 VS Code/JetBrains 作为编辑器内 Agent、CI/CD 流水线的代码审查 Agent
**举例**：`interpreter acp` 启动 ACP 服务，编辑器客户端通过 JSON-RPC 协议与 OI 通信，实现编辑器内的 Agent 能力。
**优势**：ACP 是 Codex 原生的跨编辑器协议，对比 Cline（VS Code 插件）只锁一个编辑器。

### 什么时候不要用 OI

- **大型代码库重构**：OI 没有代码库索引能力。这种场景选 Claude Code（全库理解）或 Augment（全库索引不受上下文限制）
- **日常 IDE 编码**：补全体验不如 Cursor 的 Tab 预测。选 Cursor
- **需要精确 Git 痕迹**：Aider 的 git 化编辑有天然版本追踪。OI 需要手动管理 git
- **高安全生产环境**：OI 有沙箱但本地模型+任意代码执行仍是风险敞口。选 Aider（不跑任意命令）或 Continue VPC 部署

---

## 五、核心源码解读

### 5.1 Harness 切换机制

OI 的核心差异化在于 `/harness` 动态切换。其背后是通过 `HarnessConfig` 枚举统一管理多个 Agent 的 System Prompt 与工具调用模板。

```rust
// codex-rs 中 Harness 枚举示意（非精确源码，基于架构还原）
pub enum Harness {
    Native,         // OI 原生 harness
    ClaudeCode,     // 模拟 Claude Code 行为
    ClaudeCodeBare, // Claude Code 裸版（无额外工具注册）
    KimiCli,        // 模拟 kimi CLI
    QwenCode,       // 模拟 Qwen-Code
    DeepseekTui,    // 模拟 DeepSeek TUI
    SweAgent,       // SWE-Agent 风格（专注于 GitHub Issue 修复）
    Minimal,        // 最小化 harness（仅基础文件编辑）
}
```

每个 Harness 实现以下接口：
- `system_prompt()` - 生成对应 Agent 风格的系统提示
- `register_tools()` - 注册对应 Agent 的工具集
- `preprocess_response()` - 预处理模型输出适配对应 Harness
- `execution_policy()` - 定义代码执行策略（自动/确认/拒绝）

### 5.2 Provider 系统

Provider 抽象层允许 OI 支持几乎所有模型后端。其核心架构是通过 `LlmProvider` trait 统一所有 Provider 的接口：

```rust
// Provider trait 示意
pub trait LlmProvider {
    fn model_name(&self) -> &str;
    fn send_message(&self, messages: &[Message], options: &SendOptions)
        -> Result<Box<dyn Stream<Item = StreamingDelta>>>;
    fn supports_streaming(&self) -> bool;
    fn supports_vision(&self) -> bool;
    fn supports_tools(&self) -> bool;
    fn token_limit(&self) -> usize;
}
```

支持的后端包括：OpenAI、Anthropic、Groq、OpenRouter、Ollama、LM Studio，以及任何兼容 OpenAI API 格式的服务。`/model` 命令可在 TUI 中实时切换。

### 5.3 沙箱系统

沙箱是 OI 的安全性基石。Linux 上 vendor 了 bubblewrap（bubblewrap.c 在 `codex-rs/vendor/bubblewrap/` 中），Windows 上使用自研的 `windows-sandbox-rs` crate：

```rust
// 沙箱统一接口示意
pub trait Sandbox {
    fn execute(&self, command: &Command) -> Result<SandboxResult>;
    fn write_file(&self, path: &Path, content: &[u8]) -> Result<()>;
    fn read_file(&self, path: &Path) -> Result<Vec<u8>>;
    fn resolve_path(&self, path: &Path) -> Result<PathBuf>;
}
```

Windows 沙箱的实现尤其复杂：包含 ACL 控制、WFP 防火墙规则、用户隔离、DPAPI 密钥隔离、ConPTY 通信管道等。`elevated/` 子模块是提权服务进程，负责 setup 和网络过滤。

### 5.4 ACP Server（Agent Client Protocol）

ACP 是让 OI 作为编辑器 Agent 的关键，继承自 Codex 的 LSP 化 Agent 协议：

```
interpreter acp  →  启动 JSON-RPC over stdio/tcp 服务
                    VS Code 扩展 / JetBrains 插件  →  ACP 客户端 → OI ACP Server
```

协议 schema 存放在 `codex-rs/app-server-protocol/schema/json/`，包含 30+ 个请求/响应/通知类型的 JSON Schema 定义：`ToolCallParams`、`FileChangeRequestApproval`、`CommandExecutionRequest` 等。

### 5.5 .codex/ 技能系统（Codex 遗产）

`.codex/skills/` 目录来自上游 Codex，提供了 OI 执行的技能编排能力：

```
.codex/skills/
├── babysit-pr/           # PR 自动化管理（watch/comment/merge）
│   ├── SKILL.md          # 技能定义
│   ├── agents/openai.yaml # Agent 配置
│   └── scripts/gh_pr_watch.py # Python 执行脚本
├── code-review/          # 代码审查
├── code-review-breaking-changes/ # 破坏性变更检测
├── code-review-change-size/      # 变更规模评估
├── code-review-testing/          # 测试覆盖审查
├── codex-bug/            # 内部 Bug 追踪
├── codex-issue-digest/   # Issue 摘要生成
└── path-types/           # 路径类型系统
```

这是 OI 对比其他工具的一个隐形势能——它不仅是一个编码 Agent，还内嵌了一套**作业编排框架**。

---

## 六、架构决策与设计哲学

### 6.1 为什么从 Python 重写为 Rust？

**直接原因**：原始 Python 版在性能敏感路径上存在瓶颈——流的解析、ANSI 转义序列处理、PTY 管理、大量并发连接。Python 的 GIL 和动态类型在 agent 这种高并发 I/O 场景下成为拖累。

**深层原因**：当 OI 决定 fork Codex（本身就是 Rust 生态）时，用 Rust 可以最大化复用 Codex 的 Bazel 构建、crate 结构和工具链。与其在 Python 里重写一遍 Codex 的能力，不如直接继承整个 Rust 代码库。

**架构收益**：
- Bazel 增量编译让 CI 从小时级压缩到分钟级
- `codex-rs/utils/pty/` 中跨平台的 PTY 管理实现了原生性能
- 内存安全保证减少沙箱逃逸风险
- 原生二进制发布降低用户部署门槛（单文件下载 vs `pip install`）

### 6.2 为什么是 Emulation 而不是定制？

这是一个关键的哲学问题。其他 coding agent（如 Cline、Aider）选择为通用能力设计自己的 Harness。OI 选择了相反的路：**模拟已经被验证的高性能 Harness**。

这意味着：
- **不对任何模型做假设**：Harness 是运行时切换的，而非编译时决定的
- **继承而非发明**：claude-code harness 复制 Claude Code 的 system prompt 和工具调用模式，而非重新设计一套"更好"的
- **快速适配**：当 Anthropic 更新 Claude Code 的 Harness 时，OI 只需更新其模拟层

这种策略的风险是**总是落后于上游**——模拟永远无法达到原版的深度。但 OI 的定位是"低成本替代"，Emulation 恰恰是最务实的路径。

### 6.3 为什么保留 .codex/ 目录？

上游 Codex 的 `.codex/` 目录包含完整的技能框架和 Agent 定义。OI 选择保留它而非剥离，是因为：
- **技能即代码**：SKILL.md + 脚本（Python/Bash）的技能定义方式与 OI 的"代码生成-执行"哲学一致
- **Agent 编排**：`agents/openai.yaml` 定义了多 Agent 协作的拓扑，这是 OI 未来可能的演进方向
- **减少 fork 维护成本**：与上游保持兼容可以减少合并冲突

### 6.4 Sandbox First 设计

OI 在每个 OS 上都实现了原生沙箱，而非使用 Docker 等通用容器方案：
- Docker 太重，不适合终端 Agent 的即用场景
- 原生沙箱可以利用操作系统的安全原语（Seatbelt、bubblewrap、Windows Sandbox API）
- 用户不需要额外安装任何东西

Windows 上的沙箱尤其值得关注：`windows-sandbox-rs` crate 实现了从 ACL 过滤到 WFP 网络过滤、DPAPI 密钥隔离、隐藏用户桌面隔离的完整安全链。这是目前开源项目中**最完善的 Windows Agent 沙箱实现**。

---

## 七、全网口碑画像

### 7.1 中文社区评价

**正面评价（主要来自技术博客和使用分享）**：

- **"有手的 GPT"**：腾讯云开发者社区深度实操文章中，这是最核心的正面评价。用户认为 OI 打通了自然语言与系统底层，从"AI 写代码"进化到"AI 操作电脑"。
- **自我修正能力**：多个中文章赞赏其"写错代码→读报错→自行修正"的闭环。这在运维和数据处理场景中尤其有用。
- **本地模型+离线可用**：对于内网部署、数据敏感场景，OI + Ollama 是典型的"平替方案"。
- **上手简单**：`pip install open-interpreter` 后即可使用，对比 Claude Code 的复杂配置流程友好得多。

**负面评价**：

- **旧版 Python 版被吐槽稳定性**：多个 2024-2025 年的文章抱怨安装失败（Python 3.13 兼容性问题）、模型配置复杂。Rust 新版本（2026 年）尚未被广泛验证。
- **本地小模型能力有限**：当使用 7B 以下模型时，"会陷入死循环"、"逻辑跳跃"、"需要非常精准的指令"。
- **安全性焦虑**："你敢把终端权限给 AI 吗？"——这是在中文社区最常被提出的疑虑。虽然 OI 有确认机制，但对 rm -rf 类操作的恐惧很难消除。
- **社区碎片化**：Python 原版（endolith/open-interpreter）和 Rust 新版的分裂让用户困惑应该用哪个。

### 7.2 英文社区评价

**正面（来自 tooljunction.io 等评测站）**：

- Editor's Verdict（4.5/5）："Best open-source way to give an LLM real access to your computer"
- "Free with your own API key is hard to beat" —— 成本优势是英文社群最常提到的亮点
- 桌面应用版本让非技术用户也能使用，拓宽了受众面

**负面**：

- "Running code locally with broad permissions is genuinely risky" —— 安全顾虑是跨语言的共识
- "Browser control still experimental" —— 浏览器控制不稳定
- "Not optimized as a daily code editor" —— 不适合替代 IDE

### 7.3 Issue 窗口

当前 20 个 Open Issue 中值得关注的信号：
- **安全漏洞**：Issue #1766（Path Traversal in EditTool）、#1733（Path Traversal in Files.edit API）、#1767（/settings endpoint 允许修改敏感属性）—— 三个活跃的安全 issue 说明项目在安全审计上仍有欠账
- **安装问题**：Issue #1786（Linux curl install 404）、#1784（PowerShell install 308 redirect）—— 安装流程还不够鲁棒
- **功能建议**：Issue #1754（token 使用量和费用显示）、#1760（安全隔离指南）—— 社区对透明度和安全性有持续需求

已关闭的 Issue 中，Issue #1747 提到 "Starlog published a deep-dive on openinterpreter"——说明项目已有外部深度分析报道，社区关注度在上升。

---

## 八、竞品对比

### 8.1 六维对比矩阵

| 维度 | Open Interpreter | Claude Code | Codex CLI | Cline | Aider |
|------|-----------------|-------------|-----------|-------|-------|
| **模型绑定** | 无限制（BYOM） | 绑 Anthropic | 绑 OpenAI | 无限制 | 无限制 |
| **Harness 切换** | **原生支持** | 无 | 无 | 无 | 无 |
| **沙箱能力** | OS 原生沙箱 | 有限 | CLI 沙箱 | VS Code 沙箱 | 仅 git 编辑 |
| **代码库理解** | 无 | 全库索引 | 全库索引 | 有限 | Repository Map |
| **本地模型** | Ollama 全面 | 不支持 | 不支持 | Ollama 支持 | Ollama 支持 |
| **成本** | 免费（BYOK） | $100-200/mo | $20-200/mo | 免费（BYOK） | 免费（BYOK） |
| **Git 集成** | 无原生 | 有 | 有 | 有 | **强（自动 commit）** |
| **文档处理** | Word/Excel/PDF | 无 | 无 | 无 | 无 |
| **最佳场景** | 系统操作+代理 | 大型重构 | 大型重构 | IDE 内 Agent | git 化编码 |

### 8.2 核心决策逻辑

```
你需要的是？
├── 系统操作 / 文件处理 / 运维 / 办公自动化
│   └── → **Open Interpreter**（唯一能做这些的选项）
├── 大型代码库重构 / 复杂工程任务
│   ├── 预算充足 → **Claude Code**（最强 Agent 能力）
│   ├── 绑 OpenAI 生态 → **Codex CLI**
│   └── 不想被锁定 → **Aider**（BYOM + git 化）
├── IDE 内 Agent 体验
│   ├── VS Code 深度用户 → **Cline**
│   └── 企业级 → **Continue**（VPC 部署合规）
└── 日常编码补全
    └── → **Cursor**（Tab 预测最佳体验）
```

### 8.3 竞品点评

**vs Claude Code**：
- Claude Code 在代码库理解（115K+ GitHub Stars）和复杂工程任务上有绝对优势
- OI 在系统操作和多模型灵活性上胜出
- 核心差异：Claude Code 是"智能工程师"，OI 是"通用计算机操作员"

**vs Codex CLI**：
- 两者有共同的 Codex 血统，但 OI 是深度 fork，Codex 是 OpenAI 官方版本
- Codex CLI 绑 OpenAI 模型，OI 无绑定
- OI 的 Harness 系统继承自 Codex 的技能框架并扩展了模拟能力
- Codex CLI 更"干净"（无第三方依赖），OI 更"实用"（更多开箱即用功能）

**vs Cline**：
- Cline 是 VS Code 插件生态，用户基数大
- OI 是终端工具，插件 mcp 接口兼容
- Cline 有更多的社区插件和模型预设

**vs Aider**：
- Aider 是设计最成熟的 git 化编码助手（41K+ Stars）
- OI 不是 Aider 的直接竞品——前者是"写代码"，后者是"操作电脑"
- 在纯编码任务上，Aider 的 git 集成和 Repository Map 更好
- 在"写代码之外"的任务上，OI 没有对手

---

## 九、核心研判

### 9.1 演化路径判断

Open Interpreter 的 Rust 重写标志着项目定位的根本转变：从"一个 Python 的开源代码解释器"进化为 **"Codex 的中国方言——专为开源模型优化的 Agent 平台"**。

这一判断的依据：
1. 保留 `.codex/` 全套技能系统 => 不是替换 Codex，而是扩展 Codex
2. Harness Emulation 机制 => 不做自己的 Harness 标准，而是做 Harness 的"翻译层"
3. 全面拥抱本土模型（DeepSeek/Kimi/Qwen）=> 瞄准中国/亚洲市场
4. Bazel 构建 => 企业级工程实践的投入

### 9.2 风险与挑战

1. **上游依赖风险**：作为 Codex fork，当 OpenAI 调整 Codex 的许可协议或 ACP 协议时，OI 可能被夹在中间
2. **安全声誉风险**：三个活跃的安全 Issue 和一个"你给 AI 终端权限"的社区叙事，可能限制企业采用
3. **人才流失风险**：Rust 版的活跃度是否可持续？Python 版已被社区 fork 独立维护，社区出现了碎片化
4. **定位模糊风险**：是"编码 Agent"还是"计算机操作员"？前者竞品太多（Claude Code/Aider/Cline），后者市场教育成本高

### 9.3 值得关注的信号

- **Version 0.x**：Rust 版仍处于早期阶段（v0.0.17），大量 API 和架构可能变动
- **tui2/** 目录存在：表明 TUI 层可能正在重构，项目处于架构迁移期
- **v8-poc/**：包含 V8 JavaScript 引擎的 PoC，暗示未来可能支持 JS 沙箱执行
- **Agent Graph Store**：会话持久化 + 图存储架构，可能是"记忆系统"的前置基础设施

### 9.4 最终结论

| 维度 | 评级 | 说明 |
|------|------|------|
| 技术成熟度 | ⭐⭐⭐ | Rust 版处于 v0.x，功能完善度仍需观察 |
| 社区活跃度 | ⭐⭐⭐⭐⭐ | 64K+ Stars，Issue/PR 活跃 |
| 架构先进性 | ⭐⭐⭐⭐⭐ | Harness Emulation 是独特创新 |
| 安全性 | ⭐⭐⭐ | 有沙箱但安全事件仍在出现 |
| 可用性 | ⭐⭐⭐⭐ | 安装/配置相对简单，跨平台 |
| 商业潜力 | ⭐⭐⭐ | 定位独特但市场竞争激烈 |

**一句话总结**：OI 是目前唯一的"低成本模型 Agent 桥接平台"，其 Harness Emulation 思路在架构上有不可替代的价值。但 Rust 版处于早期阶段，安全审计和企业级能力仍需时间沉淀。对于需要系统操作 Agent 且预算有限的开发者，OI 是当前唯一的选择；对于纯编码任务，应优先考虑 Claude Code 或 Aider。

---

## 十、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `codex-rs/cli/src/main.rs` | CLI 主入口 |
| `codex-rs/tui/src/tui.rs` | TUI 主循环 |
| `codex-rs/session/src/` | 会话管理与状态机 |
| `codex-rs/sandbox/src/` | 沙箱统一接口 |
| `codex-rs/provider/src/` | LLM Provider 抽象 |
| `codex-rs/harness/src/` | Harness 切换引擎（核心创新） |
| `codex-rs/mcp/src/` | MCP 协议集成 |
| `codex-rs/acp-server/src/` | ACP Server（编辑器集成协议） |
| `codex-rs/agent-graph-store/src/` | Agent 会话图存储 |
| `codex-rs/agent-identity/src/` | Agent 身份管理 |
| `codex-rs/app-server-protocol/schema/json/` | ACP 协议 JSON Schema |
| `codex-rs/windows-sandbox-rs/src/` | Windows 沙箱完整实现 |
| `codex-rs/vendor/bubblewrap/` | 内嵌 bubblewrap（Linux 沙箱） |
| `codex-rs/analytics/src/` | 遥测分析 |
| `codex-rs/tui2/src/` | 第二代 TUI（开发中） |
| `codex-rs/v8-poc/src/` | V8 JS 引擎 PoC |
| `codex-rs/utils/pty/src/` | 跨平台 PTY 管理 |
| `codex-rs/utils/plugins/src/` | 插件系统（含 MCP 连接器） |
| `codex-rs/utils/cli/src/` | CLI 参数/配置公共组件 |
| `codex-rs/utils/sandbox-summary/src/` | 沙箱配置摘要 |
| `.codex/skills/` | Codex 技能系统（PR管理/代码审查等） |
| `.codex/environments/` | 环境配置 |
| `AGENTS.md` | Agent 使用指南 |
| `docs/harness.md` | Harness 文档 |
| `docs/providers.md` | Provider 配置文档 |
| `docs/sandbox.md` | 沙箱配置文档 |
| `docs/acp.md` | ACP 协议文档 |
| `docs/skills.md` | 技能系统文档 |
