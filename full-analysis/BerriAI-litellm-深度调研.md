# BerriAI/litellm 深度调研

> 调研日期：2026-10-10 | 来源：GitHub Trending（当日新增）| Stars：60,569 | 语言：Python（Rust core）| 许可：NOASSERTION（OSS 多元许可，企业版闭源）

## 1. 项目定位（一句话）

开源 AI 网关 + 统一 LLM SDK——把 100+ 大模型提供商（OpenAI / Anthropic / Gemini / Bedrock / Azure…）归一为一套 OpenAI 格式的调用接口，既可作库直连，也可作中心化网关部署。

## 2. 项目亮点（差异化）

- **统一接口 + OpenAI 格式 drop-in**：`from litellm import completion`，换 provider 不重写业务代码，是多云多模型场景的事实标准之一。
- **生产级网关开箱即用**：虚拟密钥（virtual keys）、花费追踪、guardrails、负载均衡、rate limit、admin dashboard 全部内建，团队/企业可一键自托管。
- **性能硬指标**：官方 benchmark 称 1k RPS 下 P95 延迟 8ms；支持 Rust core（`litellm-rust/`）加速。
- **`litellm-core` 独立分发**：把 Python SDK 拆成无可选依赖、无 CLI、无 dashboard 的纯净 wheel，按环境分别安装 `litellm`（网关/CLI/extras）与 `litellm-core`（SDK）。
- **顶级采用背书**：README 列 Stripe、Netflix、OpenAI Agents SDK、Google ADK、OpenHands、Greptile 等；YC W23 背景。

## 3. 核心架构

两层分离：`litellm/`（SDK，负责真实 provider 调用、请求/响应变换、流式）+ `proxy/`（AI Gateway，在 SDK 之上叠加鉴权、限流、预算、路由）。

- **Provider 抽象**：每个提供商一个 `litellm/llms/<provider>/chat/transformation.py`，实现 `ProviderConfig.transform_request()` / `transform_response()`，把 OpenAI 格式与目标 provider 格式互转。
- **请求流**：Client → `proxy/proxy_server.py` → `proxy/auth/user_api_key_auth.py`（Redis 缓存密钥与额度）→ `router.py route_request()` → `main.py` + `utils.py`（acompletion）→ `llms/custom_httpx/llm_http_handler.py` → `ProviderConfig.transform` → Provider API。
- **成本归因**：`utils.py` 包装里用 `cost_calculator.py` 的 `_response_cost_calculator()` 算 `tokens × price`，写入 `ModelResponse._hidden_params["response_cost"]`，响应头回传 `x-litellm-response-cost`；异步日志批量写 Postgres + Redis 队列。

## 4. 应用场景与启发

- **多模型路由/降级**：用 `router.py` 做 provider 故障转移、按价格/延迟负载均衡——自建 LLM 中台的「统一接入层」。
- **成本治理**：`model_prices_and_context_window.json`（仓库根，含 100+ 模型价格与上下文窗口）是 litellm 的核心数据资产，可单独复用做成本预估。
- **Agent 框架后端**：OpenAI Agents SDK / Google ADK 等直接把 litellm 当统一调用层，避免各框架重复适配 provider。

## 5. 源码深度解读

**① Provider 转换契约（`litellm/llms/<provider>/chat/transformation.py`）**
每个 provider 一个 transformation 模块，是「OpenAI 格式 ↔ 厂商格式」唯一变点。新增一个 provider 几乎零侵入：

```python
# litellm/llms/anthropic/chat/transformation.py（范式）
class AnthropicConfig(BaseConfig):
    def transform_request(self, model, messages, ...):  # OpenAI->Anthropic
        ...
    def transform_response(self, model, raw_response, ...):  # Anthropic->OpenAI
        ...
```

**② 成本计算（`litellm/utils.py` + `litellm/cost_calculator.py`）**
`_response_cost_calculator()` 读取 `model_prices_and_context_window.json`，把 token 数 × 单价注入 `_hidden_params`，网关据此写回响应头与数据库——这是「按调用计费/限额」能力的根。

**③ 网关序列（`litellm/proxy/proxy_server.py` + `proxy/auth/user_api_key_auth.py`）**
鉴权把密钥信息（含 spend limit）缓存进 Redis，限流用 parallel_request_limiter 命中 Redis 计数器，形成无阻塞高并发入口。

## 6. 社区口碑

- YC W23，GitHub 60k+ stars，PyPI 月下载量巨大（精确值数据不可用），Discord/Slack 社区活跃。
- 被多家头部科技公司公开采用（Stripe/Netflix/OpenAI Agents SDK/Google ADK/OpenHands/Greptile），是 LLM 调用层最主流的开源选项之一。
- 争议点：版本迭代快、breaking change 较多；企业功能（预算/团队）偏向商业版与托管版。

## 7. 竞品对比 + 核心研判

| 维度 | litellm | LangChain | Portkey / Helicone | 云厂商网关（OpenAI/Cloudflare/Vercel） |
|------|---------|-----------|-------------------|----------------------------------------|
| 定位 | 网关 + SDK 一体 | 编排框架 | 可观测/路由 | 托管入口 |
| 自托管 | ✅ 开源 | ✅ | 部分 | ❌ |
| provider 数 | 100+ | 多 | 中 | 少 |
| 成本治理 | ✅ 内建 | 弱 | ✅ | 弱 |

**研判**：需要多云多模型、成本可控、自建 LLM 网关的团队，litellm 是首选之一；对纯单模型/托管场景则偏重。注意许可为 NOASSERTION（OSS 实际为 MIT/Apache 混合 + 闭源企业版），企业合规需审阅 `LICENSE` 与 enterprise 目录边界。

## 8. 关键文件路径速查

- `ARCHITECTURE.md` / `AGENTS.md`：架构与贡献入口
- `litellm/`：SDK 核心（`main.py`、`utils.py`、`router.py`、`cost_calculator.py`）
- `litellm/llms/<provider>/chat/transformation.py`：provider 格式转换（核心扩展点）
- `litellm/proxy/`：`proxy_server.py`、`auth/user_api_key_auth.py`、`hooks/`
- `litellm-rust/`：Rust core
- `model_prices_and_context_window.json`：100+ 模型价格/上下文窗口数据资产
- `proxy_server_config.yaml`、`mcp_servers.json`：网关与 MCP 配置
