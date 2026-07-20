# 🚀 FastMCP — The Fast, Pythonic Way to Build MCP Servers

> **仓库**: [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp)
> **Stars**: 26,470⭐ | **Forks**: 2,159 | **Issues**: 257 | **今日 Trending**: +77⭐
> **语言**: Python | **许可证**: Apache-2.0 | **创建**: 2024-11-30 | **最近提交**: 2026-07-20
> **官网/文档**: [gofastmcp.com](https://gofastmcp.com) | **定位**: MCP 生态事实标准的 Python 框架——"FastMCP is to MCP what Express is to Node.js"

## 项目亮点

- **装饰器即工具**：一个 Python 函数 + `@mcp.tool()`，自动从类型提示推断 JSON Schema、解析 docstring 生成描述、做输入校验与错误处理，省掉约 70% 的样板
- **三支柱架构**：Servers（暴露 tools/resources/prompts）、Clients（连任意 MCP Server）、Apps（工具返回可交互 UI，渲染在对话里）——覆盖 MCP 全链路
- **组合与代理**：可把多个 Server 组合成一个、在 Server 间做 proxy、运行时动态改写工具，是构建 MCP 网关的基础能力
- **OpenAPI → MCP 一键生成**：指向一个 OpenAPI spec 自动产出可运行的 MCP Server，是"已有 API 上车 MCP"最快路径
- **代码模式（Code Mode）**：v3.1 把 1000 个工具的目录"折叠"成 2 个工具，token 占用最多降 99%，直接解决"工具太多撑爆上下文"的生产痛点

## 核心架构

```
fastmcp_slim/fastmcp/
├── server/            # 核心：FastMCP 类 + 传输/中间件/缓存
│   ├── server.py      #   class FastMCP — .tool()/.resource()/.prompt() 装饰器
│   ├── middleware/     #   请求级中间件管道
│   ├── caching.py      #   工具结果缓存
│   ├── auth/           #   OAuth / Bearer 鉴权
│   ├── elicitation.py  #   向用户索取缺失参数
│   ├── sampling/       #   Server 反向调用 LLM
│   ├── tasks/          #   长任务 / 后台执行
│   └── transforms/     #   运行时工具改写
├── tools/ resources/ prompts/   # 三类 MCP 原语的实现
├── client/            # Client 支柱：传输探测/会话/重连
├── apps/              # App 支柱：MCP Apps（交互式 UI）
├── cli/               # fastmcp run / dev / inspect
└── mcp_config.py      # 配置与依赖装配
```

采用 monorepo（`fastmcp_slim` + `fastmcp_remote` 两个 wheel 成员），`fastmcp_slim` 是核心包；v3.3 "Slim Reaper" 引入 `fastmcp-slim`，移除 client-only 场景下的 Starlette/Uvicorn 依赖。底层复用官方 `modelcontextprotocol/python-sdk`，FastMCP 1.0 曾直接并入官方 SDK。

## 应用场景与启发

- **把内部 API 变成 Agent 工具**：OpenAPI → MCP 生成，让存量后端零改造接入 Agent
- **构建企业生产网关**：多 Server 组合 + proxy + 工具级 RBAC + OTEL 观测，配合 Prefect Horizon 做 SSO/审计
- **降低 token 成本**：Code Mode 渐进式披露，避免 43 工具（如 GitHub MCP）一次性灌满上下文
- **对同类需求的启发**：FastMCP 的成功本质是"用框架抽象吃掉协议样板"。**当你要设计面向 Agent 的接口层时，应把 schema 生成、校验、传输协商做成框架能力而非手写**——开发者只写业务函数，协议细节交给框架。这与本项目已调研的 `github/copilot-sdk`（JSON-RPC + BYOK 的可嵌入 SDK）思路互补：一个管"怎么写 MCP"，一个管"怎么把 Agent 运行时嵌进产品"。

## 源码深度解读

**1. 装饰器即工具（框架核心抽象）**
`fastmcp_slim/fastmcp/server/server.py` 的 `FastMCP` 类用重载的 `.tool()` 同时支持 `@mcp.tool`、`@mcp.tool()`、`@mcp.tool("name")`、`@mcp.tool(name=...)` 四种写法（源码 1772–1862 行）：
```python
# server/server.py（节选）
class FastMCP(...):
    @overload
    def tool(self, name_or_fn=None, *, name=None, description=None, tags=None):
        ...
    def tool(self, name_or_fn=None, **kwargs):
        # 根据传入是函数还是字符串，路由到注册逻辑
        ...
        def decorator(fn):
            self.add_tool(Tool.from_function(fn, name=..., **kwargs))
            return fn
        return decorator(fn) if callable(name_or_fn) else decorator
```
`Tool.from_function` 用 `inspect` + 类型提示自动产出 `inputSchema`，开发者零配置。

**2. 中间件管道（横切关注点的统一入口）**
`server/middleware/` 提供请求级中间件，可在 tool 调用前后做鉴权、日志、限流、改写；与 `server/auth/`、`server/caching.py` 配合，把"协议周边的琐事"从业务逻辑里剥离。

**3. Code Mode（上下文压缩）**
v3.1 的 Code Mode 把大量工具收敛为少量"元工具"，由 Agent 按需展开——源码层面通过 `server/transforms/` 在运行时重写工具列表实现。这是"渐进式披露"在生产 MCP 上的工程落地，对应本项目已入库的 `headroomlabs-ai/headroom`（Agent 上下文压缩中间层）同源问题。

## 全网口碑

- **统治级采用**：README 自称"日下载百万次"，第三方统计约 190 万次/日，估计驱动全语言 70% 的 MCP Server；7,819 个 dependents，208+ 贡献者，84% issue 关闭率
- **正面**：装饰器 API 被赞"genuinely elegant and straightforward"；v3.2 "Show Don't Tool" 的 MCP Apps（工具返回图表/表单/地图）被视为范式升级；社区普遍认为"用 Python 写 MCP Server 就该用 FastMCP，除非有低层传输需求"
- **痛点**：OAuth 集成被多篇评测列为头号摩擦点（错误可观测性差、文档碎片化）；单 Server 在工具数/多客户端鉴权上会遇到扩展墙，需上网关（Prefect Horizon）；版本迭代快导致 v2→v3 升级有认知负担
- **第三方评分**：ChatForest 4.5/5，列为"MCP 生态里仅次于规范本身最重要的项目"

## 竞品对比 + 核心研判

| 维度 | FastMCP (Py) | 官方 python-sdk | mcp-go | punkpeye/fastmcp (TS) |
|------|-------------|----------------|--------|----------------------|
| 抽象层级 | 高层框架 | 低层 SDK | 高层框架 | 高层框架 |
| 写法 | 装饰器 | 显式类型+asyncio | 装饰器 | 装饰器 |
| 依赖数 | 7,819 | 0(传递) | 高 | 1,303 |
| 维护方 | PrefectHQ | Anthropic/Agentic | mcp-go 社区 | 社区 |
| 语言 | Python | Python | Go | TypeScript |

**核心研判**
- **优势**：踩中 MCP 爆发窗口，用 Express 式的"少写代码"抽象成为事实标准；Prefect 背书带来机构级维护，迭代速度（96 个 release、3,400+ commits）远超竞品
- **风险**：Python-only 限制多语言团队；OAuth/扩展性痛点把商业价值导向 Prefect Horizon（潜在锁定）；Code Mode 的沙箱边界仍待完善；版本快速演进带来升级成本
- **趋势**：MCP 正从"工具协议"走向"应用协议"（Apps 规范由 Anthropic+OpenAI 共推），FastMCP 已率先支持，护城河在加深
- **启发**：做开发者框架时，**先占"默认选择"心智比功能全面更重要**——FastMCP 靠极简上手成为入口，复杂能力（网关/鉴权/观测）再向后端产品收敛。这种"薄核心 + 厚生态"的框架演进路径，值得任何想做 Agent 工具层参考

## 关键文件速查

| 路径 | 作用 |
|------|------|
| `fastmcp_slim/fastmcp/server/server.py` | `FastMCP` 类与 `.tool()/.resource()/.prompt()` 装饰器 |
| `fastmcp_slim/fastmcp/server/middleware/` | 请求级中间件管道 |
| `fastmcp_slim/fastmcp/server/caching.py` | 工具结果缓存 |
| `fastmcp_slim/fastmcp/server/auth/` | OAuth / Bearer 鉴权 |
| `fastmcp_slim/fastmcp/server/transforms/` | 运行时工具改写（Code Mode 基础） |
| `fastmcp_slim/fastmcp/tools/` `resources/` `prompts/` | 三类 MCP 原语实现 |
| `fastmcp_slim/fastmcp/client/` | Client 支柱 |
| `fastmcp_slim/fastmcp/apps/` | MCP Apps（交互式 UI） |
| `fastmcp_slim/fastmcp/cli/` | `fastmcp run/dev/inspect` |
| `pyproject.toml` | 包布局（fastmcp_slim + fastmcp_remote 双 wheel） |
