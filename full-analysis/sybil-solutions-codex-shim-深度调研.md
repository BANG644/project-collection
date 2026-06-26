# 🔬 sybil-solutions/codex-shim - 全方位深度调研

## 📌 一句话定位

`codex-shim` 是一个本地 Python/aiohttp 适配层：它在 `127.0.0.1` 暴露 OpenAI Responses-compatible 接口，让 Codex Desktop/CLI 可以使用 BYOK 模型、ChatGPT/Codex passthrough、Cursor/Composer passthrough 或本地代理，而不需要重编 Codex。

> 核心判断：它不是模型服务，而是“Codex 客户端协议适配器”。价值在于保留 Codex 原生 UX，同时把模型路由权拿回本地；风险在于 Codex Desktop 的 allowlist/ASAR patch、订阅 token、上游协议变化都可能让它失效。

## 🏗️ 项目全景

| 维度 | 观察 |
|---|---|
| 仓库 | `sybil-solutions/codex-shim` |
| GitHub | https://github.com/sybil-solutions/codex-shim |
| Stars / Forks | 约 959 stars / 91 forks（2026-06-19 抽样） |
| 默认分支 | `main` |
| 主要语言 | Python |
| License | MIT |
| Open issues | 约 10 |

## 🧠 核心架构

### 运行链路

```text
Codex Desktop / Codex CLI
  -> 本地 provider 指向 http://127.0.0.1:8765/v1
  -> codex-shim aiohttp server
  -> router 选择 ChatGPT passthrough / OpenAI-compatible / Anthropic / Cursor Composer / Auto Router
  -> translator 把流式响应翻译回 Codex 期望的 Responses API 形态
```

### 关键模块

现有报告和 README 显示：

- `codex_shim/`：主包，包含 CLI、server、router、translator、settings/catalog 等逻辑。
- `tests/test_router.py`：路由策略回归测试。
- `tests/test_translate.py`：协议翻译行为测试。
- `tests/test_cursor_passthrough.py`：Cursor/Composer passthrough 的专项测试。
- `tests/test_hostguard.py`：本地 loopback/安全边界相关测试。
- `bin/` 与 Windows `.bat`：跨平台启动包装。

**架构判断**：项目真正难点不是启动 HTTP server，而是保持 Codex agent loop 的结构不被“压平成纯文本”：function calls、tool outputs、reasoning blocks、image-capable metadata、SSE streaming 都要翻译。

## 🔍 源码深度解读

### Router 层

Router 根据 `~/.codex-shim/models.json` 或传入 settings，把不同 model slug 映射到不同 upstream。这个设计让用户能在 Codex model picker 中看到自定义模型，但也引入一个现实问题：Codex Desktop 自身可能会限制可选 slug。

### Translator 层

README 强调“native Codex agent loops stay intact”，说明 translator 需要把上游 OpenAI chat completions、Anthropic Messages、OpenAI-shaped endpoint 的流式响应翻译成 Codex 的 Responses API 语义。这是项目最有技术含量的部分。

### Patch / Config 层

macOS 可选 ASAR patch 是高风险高价值功能：它绕过 Desktop 模型选择器隐藏自定义 catalog 的问题，但也意味着升级 Codex Desktop 后 patch 可能失效。Windows MSIX 又有自己的限制，README 已明确提示。

## 🌐 社区口碑画像

没有可靠第三方长评可引用，因此不编造外部评价。GitHub 一手信号显示：

- 仓库创建时间较新（2026-05），但 stars 接近千级，说明需求明显。
- Open issues 约 10，项目处于快速验证期。
- README 反复强调“benchmark 请自己测”，说明维护者没有把内部经验包装成可复现结论，这是诚实但也意味着效果不可直接外推。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| codex-shim | 保留 Codex 原生体验，本地路由 BYOK | 依赖 Codex 协议/桌面限制，维护成本高 |
| LiteLLM | 成熟多模型网关，可自托管 | 不能直接解决 Codex Desktop picker/Responses 适配 |
| OpenRouter | 上手快，模型多 | 平台依赖强，本地订阅 passthrough 不透明 |
| 直接改 Codex 配置 | 简单 | 遇到 Desktop allowlist 和响应格式差异就失效 |

## 🎯 核心研判

### 优势

1. **抓住 Codex 用户真实需求**：想用 Codex UX，但不想被单一模型/官方 catalog 限制。
2. **协议适配价值高**：Responses API、Anthropic Messages、SSE translation 是实际工程难点。
3. **测试覆盖方向正确**：router、translator、server、settings、cursor passthrough 都有测试信号。

### 风险

1. **上游协议易变**：Codex Desktop alpha 版本、ChatGPT/Codex passthrough、Cursor 订阅接口都不是稳定公共 API。
2. **桌面 patch 敏感**：ASAR patch、codesign、Windows MSIX 限制会让普通用户望而却步。
3. **安全边界必须明确**：本地 loopback server 不应暴露到公网；模型配置里可能有 API key。

### 适用场景

- Codex power user 想接入 BYOK/本地/订阅模型。
- 需要比较多模型在同一 Codex agent loop 下的效果。
- 愿意处理本地配置、代理和升级兼容的高级用户。

### 不适用场景

- 不想碰配置文件/本地 daemon 的普通用户。
- 企业强管控桌面应用与凭证的环境。
- 需要长期稳定 SLA 的生产 agent 平台。

## 📂 关键文件路径速查

- `codex_shim/`：核心实现目录。
- `tests/test_router.py`：路由行为。
- `tests/test_translate.py`：协议翻译。
- `tests/test_server.py`：本地 server。
- `tests/test_cursor_passthrough.py`：Cursor 订阅 passthrough。
- `README.md`：安装、Windows/macOS 限制、Auto Router 与 benchmark 说明。

## ⭐ 三条关键发现

1. codex-shim 最大价值是“协议保真翻译”，不是简单反向代理。
2. 它处在 Codex Desktop allowlist 与用户 BYOK 需求之间，定位很明确但天然脆弱。
3. README 对 benchmark 和平台限制相对诚实，采用时应把它当高级用户工具而非稳定产品。

## 🧪 研究方法与数据来源

- GitHub API：仓库元数据、stars、forks、issues、license。
- README：架构说明、Windows/macOS 限制、Auto Router、passthrough。
- 现有报告文件树：`codex_shim/` 与 tests 分布。
- 外部搜索：未发现可靠第三方长评。
