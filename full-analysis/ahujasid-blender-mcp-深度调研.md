# 🔬 ahujasid/blender-mcp - 全方位深度调研

## 📌 一句话定位

**通过 MCP 协议让任何 LLM（Claude/Gemini/Cursor 等）直接操控 Blender 3D 建模的开源桥梁**——Blender 端作为 TCP Socket 服务端接收指令（`addon.py`），MCP Server 端作为标准 MCP 工具暴露层（`server.py`），LLM 通过 MCP 客户端调用工具 → Server 转发 Socket → Blender Addon 执行。本质是"AI 用自然语言操控 3D 建模软件"的最成熟开源实现。

## ⭐ 项目亮点

- **首创 Blender ↔ MCP 协议桥**：作为首个（也是同品类 Star 最多的）Blender-MCP 项目，定义了"Blender Addon TCP Server + MCP Server 客户端"的双层架构模式。后续的 Blender-MCP 竞品基本都是此架构的变体。
- **30+ 个暴露给 AI 的 Blender 工具**：涵盖场景信息、物体操控、Poly Haven 资产下载、Rodin/Hunyuan3D/Sketchfab 三维模型生成与导入、纹理设置、截图等。不是"只能做简单操作"的玩具，而是可以完成从生成到导入到布景的完整 3D 工作流（[addon.py 工具列表](https://github.com/ahujasid/blender-mcp/blob/main/addon.py)）。
- **四大 AI 三维生成引擎集成**：内置 Rodin（Hyper3D）、Hunyuan3D（腾讯混元）、Sketchfab 搜索、Poly Haven（PBR 材质）——AI 可以"先让 Rodin/Hunyuan 生成 3D 模型 → 下载 → 导入 Blender → 自动清理 → 放置到场景"。这是 README 没展开的亮点。
- **零配置 MCP 兼容**：标准的 `mcp[cli]` 依赖 + `mcp.run()` 入口，兼容 Claude Desktop、Cursor、VS Code、Windsurf、Cline 等所有 MCP 客户端。不绑定特定 AI 平台。
- **双向 Socket 通信 + 3 分钟超时**：`BlenderConnection` 用 TCP 长连接 + 180 秒超时 + 分块接收完整 JSON 响应，处理 Blender 执行复杂建模指令的耗时场景（[server.py 源码](https://github.com/ahujasid/blender-mcp/blob/main/src/blender_mcp/server.py)）。

## 🏗️ 项目架构全景

```
blender-mcp/
├── addon.py                              # Blender 插件（运行在 Blender 内）
│   └── BlenderMCPServer 类                # TCP Socket 服务端
│       ├── start()/stop()                # 启动/停止 Socket 服务
│       ├── execute_command()             # 指令调度中心（50+ 方法路由）
│       ├── get_scene_info()              # 场景快照
│       ├── get_object_info()             # 选中物体信息
│       ├── execute_code()                # 执行任意 Python 代码
│       ├── search_polyhaven_assets()     # Poly Haven 材质搜索
│       ├── download_polyhaven_asset()    # 下载 PBR 纹理
│       ├── create_rodin_job()            # Rodin AI 3D 生成
│       ├── create_hunyuan_job()          # 腾讯混元 3D 生成
│       ├── search_sketchfab_models()     # Sketchfab 模型搜索
│       └── ... （总计 30+ 公开方法）
├── src/blender_mcp/
│   ├── server.py                         # MCP Server（运行在外部）
│   │   └── BlenderConnection 类          # TCP Client 连接 Blender
│   │       ├── 50+ @mcp.tool() 装饰器    # MCP 工具暴露
│   │       └── call_blender()            # Socket 转发核心
│   ├── telemetry.py                      # 遥测（启动记录）
│   └── __init__.py                       # 版本号 + 导出
├── main.py                               # CLI 入口 → server.main()
└── pyproject.toml                        # 依赖: mcp[cli]>=1.3.0, httpx
```

### 双层架构详解

**Layer 1: Blender Addon（addon.py）**
- 运行在 Blender 内部的 Python 3.11 环境（Blender 自带的 Python 解释器）
- 启动后监听 `localhost:9876` 的 TCP Socket
- 每个收到的 JSON 指令包含 `{"type": "command_name", "params": {...}}`
- 通过 Python `eval()` 风格的 `getattr(server, command_type)` 路由到对应处理方法
- 结果通过 Socket 返回 JSON 响应

**Layer 2: MCP Server（server.py）**
- 运行在外部 Python 环境（用户系统 Python 3.10+）
- 使用 FastMCP 框架声明 50+ 个 `@mcp.tool()` 装饰器工具
- `BlenderConnection` 类作为 TCP Client 连接到 Blender 内部的 Addon
- 每个工具调用通过 Socket 转发指令 → 等待 Blender 执行 → 返回结果
- 支持 Image 返回（viewport 截图）

### 配置优先级链

`addon.py` 的 `_get_config_value()` 方法实现了三层配置读取：
1. Addon Preferences（Blender 界面设置）
2. Scene 属性（blendermcp_xxx 自定义属性）
3. 环境变量（`BLENDERMCP_xxx`）
这种"界面优先 > 脚本 > 环境变量"的链式回退机制，让普通用户可以在 Blender 界面上设置 API Key，同时也支持 CI 环境通过环境变量注入。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 描述 | 推荐指数 |
|------|------|---------|
| **AI 辅助 3D 建模原型** | 用自然语言描述场景，AI 快速搭建基础几何体并放置 | ⭐⭐⭐⭐⭐ |
| **文本→3D 生成流水线** | LLM 判断何时调用 Rodin/Hunyuan3D 生成模型 → 自动导入并清理 | ⭐⭐⭐⭐ |
| **AI 驱动的材质设计** | 用 Poly Haven + AI 分析场景后自动匹配 PBR 材质 | ⭐⭐⭐⭐ |
| **教育与培训** | AI 解释建模步骤并在 Blender 中同步操作演示 | ⭐⭐⭐ |
| **参数化批量建模** | AI 执行 Python 脚本批量生成变体（如建筑楼层布局） | ⭐⭐⭐ |

### 可借鉴的解决方案模式

1. **双向 Socket 桥接模式**：Blender Addon 作为 TCP 服务端（运行在 Blender 内），MCP Server 作为 TCP 客户端（运行在外部）——这个模式优雅地解决了"外部 AI 如何与内部软件交互"的问题。MCP 只负责工具暴露和参数校验，实际执行交给桥接层。

2. **方法路由 + 执行包装器**：`execute_command()` 通过 `getattr(self, command_type)(**params)` 实现反射式调用，而 `execute_wrapper()` 给每条指令包裹了 try/except 和 traceback 输出。这种模式使新增一个 Blender 操作只需添加一个方法，不需要改动路由逻辑。

3. **多 AI 3D 生成引擎的 Provider 模式**：Rodin（Hyper3D）、Hunyuan3D（腾讯混元）、Sketchfab 各自有不同的 API 签名方式。addon.py 为每个 Provider 实现了 `_get_xxx_status()` + `create_xxx_job()` + `poll_xxx_job_status()` + `import_generated_asset_xxx()` 的完整四阶段生命周期。这是"异构 API 统一抽象"的有效模式。

### 同类需求的可参考思路

- **MCP 不做执行，只做桥接**：blender-mcp 的 MCP Server 层非常薄——它只是把 Blender Addon 的 Socket API 翻译成 MCP 工具。真正的执行层在 Blender 内部。这让 MCP Server 可以快速迭代（新增工具只需加 @mcp.tool()），而不会影响 Blender 内的稳定性。
- **先上手后优化的安装策略**：项目推荐通过 `uvx blender-mcp` 运行（零安装），高级用户再通过 pip 安装或 Docker 部署。这种"先零配置试用，再按需升级"的策略降低了决策成本。

## 🧠 核心源码解读

### MCP 工具注册（server.py）

```python
@mcp.tool()
@telemetry_tool("get_scene_info")
async def get_scene_info(ctx: Context) -> str:
    """Get comprehensive information about the current Blender scene"""
    response = await call_blender(ctx, "get_scene_info", {})
    return response

@mcp.tool()
@telemetry_tool("create_rodin_job")
async def create_rodin_job(
    ctx: Context,
    prompt: str,
    style: str = "realistic",
    ...
) -> str:
    """Generate a 3D model from text using Rodin (Hyper3D)"""
    response = await call_blender(ctx, "create_rodin_job", {...})
    return response
```

每个工具用 `@mcp.tool()` + `@telemetry_tool()` 双层装饰器。前者注册为 MCP 工具，后者记录使用统计。`call_blender()` 负责 TCP Socket 通信。

### TCP Socket 通信核心（server.py 的 call_blender）

```python
async def call_blender(ctx: Context, command: str, params: dict) -> str:
    connection = get_blender_connection()
    if not connection.connect():
        raise BlenderConnectionError(...)
    
    message = json.dumps({"type": command, "params": params})
    connection.sock.sendall(message.encode('utf-8'))
    
    response = connection.receive_full_response(connection.sock)
    result = json.loads(response.decode('utf-8'))
    
    if result.get("status") == "error":
        raise BlenderExecutionError(result.get("message", ""))
    return json.dumps(result.get("result", {}))
```

关键设计：
- **`sendall()` + `receive_full_response()`**：发送用 `sendall` 确保完整发送，接收用循环 + 分块 + JSON 解析验证完整性
- **180 秒超时**：适配 Blender 执行复杂操作（如 AI 模型生成）的耗时
- **`BlenderExecutionError`**：Blender 端的错误会传递到 MCP 层，让 LLM 可以理解错误并修正指令

### Blender 端的指令执行（addon.py 的 execute_command）

```python
def execute_command(self, command_type, **kwargs):
    command_map = {
        "get_scene_info": self.get_scene_info,
        "get_object_info": self.get_object_info,
        "get_viewport_screenshot": self.get_viewport_screenshot,
        "execute_code": self.execute_code,
        "search_polyhaven_assets": self.search_polyhaven_assets,
        "download_polyhaven_asset": self.download_polyhaven_asset,
        "create_rodin_job": self.create_rodin_job,
        "create_hunyuan_job": self.create_hunyuan_job,
        "search_sketchfab_models": self.search_sketchfab_models,
        ...
    }
    handler = command_map.get(command_type)
    if not handler:
        return {"status": "error", "message": f"Unknown command: {command_type}"}
    return handler(**kwargs)
```

显式 `command_map` 而非 `getattr` 反射——增加了安全校验（防止传入恶意方法名），同时也便于代码静态分析工具理解。

### Telemetry 系统（telemetry.py + telemetry_decorator.py）

```python
def telemetry_tool(tool_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            record_tool_usage(tool_name)
            return result
        return wrapper
    return decorator
```

一个无侵入的调用计数系统。`record_startup()` 在 Server 启动时记录一次，`telemetry_tool` 每次工具调用递增计数。数据通过 HTTP POST 上报（仅含工具名和计数，不传参数值）。这在 MCP 生态中属于较完善的遥测实践。

## 🌐 全网口碑画像

### 好评共识

1. **"AI 建模入门门槛大幅降低"** — 知乎用户评测称"用 Claude 说'在场景中心放一个红色的立方体'，Blender 里就直接生成了，再也不用记快捷键"（[知乎](https://zhuanlan.zhihu.com/p/1921134696798070537)）。
2. **集成 Rodin/Hunyuan 3D 生成为亮眼功能** — 技术博客 WatermelonWater 的深度评测称"文本到 3D 模型的生成 + 自动导入 Blender，这个流程以前需要多步手动操作，现在 AI 一句话完成"（[watermelonwater.tech](https://watermelonwater.tech/insights/aiblendermcp%E5%AE%9E%E6%B5%8B%E7%AB%9E%E5%93%81%E5%B7%A5%E6%B5%81/)）。
3. **安装简单** — `uvx blender-mcp` 一行命令启动，被社区评价为"MCP 生态中安装体验最好的工具之一"。
4. **兼容所有 MCP 客户端** — Claude Desktop + Cursor + VS Code + Windsurf 都能用，不绑定生态。

### 差评共识

1. **Server 启动时若 Blender 未运行会挂起** — Issue #275 报告："Server initialization causes context deadline exceeded in MCP clients if Blender is not running"。这本质是架构问题：MCP Server 启动时尝试连接 Blender Socket，若 Blender 未打开则连接失败待修复。
2. **Hunyuan3D 接口兼容性** — Issue #274 指出腾讯混元官方 API 已更新，但 blender-mcp 仍使用旧端点。反映了第三方 API 集成类项目的维护挑战。
3. **复杂操作的稳定性** — 大规模场景操作或长时间 AI 模型生成时，Socket 连接可能因 Blender 卡死而超时。
4. **缺少 undo/rollback** — AI 操作 Blender 缺乏事务性，一个错误的建模指令可能导致整个场景被修改且无法自动回滚。

### 社区活跃度

- 截至 2026 年 7 月有 270+ 个 Issue，但大量为安装/配置相关（Blender 版本兼容性、Python 路径问题）
- 维护者（ahujasid）响应较为积极
- 社区贡献活跃：多个第三方 PR 增加 Gemini 支持、改进文档

## ⚔️ 竞品对比

| 维度 | blender-mcp | Blender AI (官方) | blender_artist | GPT-Engineer Blender Agent |
|------|-----------|-------------------|---------------|---------------------------|
| 技术路线 | MCP Server + Blender Addon | Blender 内置 | 独立 CLI | Agent 编排 |
| AI 集成 | 所有 MCP 客户端 | 仅 GPT | Claude API | GPT-4 |
| 3D 生成引擎 | Rodin/3D/Hunyuan3D/Sketchfab | — | — | — |
| 工具数量 | 50+ | 基础操作 | ~20 | 可扩展 |
| 安装复杂度 | 低（uvx/pip） | 内置 | 中等 | 高 |
| 维护状态 | 活跃（v1.6.0） | 官方未发布 | 低频 | 低频 |
| Stars | 23,410 | — | 5K+ | 8K+ |

### 选择建议

- **想用 Claude/Cursor 操控 Blender** → **blender-mcp**（唯一成熟选项）
- **只需要 AI 生成 3D 模型** → Rodin/Hunyuan3D 原生工具（blender-mcp 作为补充）
- **希望 Blender 内置 AI 功能** → 等待 Blender 官方 AI 路线图（目前仅有实验性功能）

## 🎯 核心研判

### 项目优势

- **品类锁定者**：blender-mcp 是 Blender-MCP 桥接领域的事实标准，23K⭐ 远超竞品。任何 LLM 想要操控 Blender，理论上都可以通过 MCP 协议接入。
- **AI 3D 建模的"最后一公里"**：Rodin/Hunyuan3D 生成 3D 模型只是第一步，把模型导入 Blender 并调整场景才是完整工作流。blender-mcp 填补了这个缺口。
- **架构设计干净**：双层架构（Blender Addon TCP Server + MCP Server Client）清晰分离关注点，单点 Socket 通信让 MCP 层可独立部署和升级。

### 项目风险

- **架构性能瓶颈**：所有操作通过 TCP Socket 转发 + JSON 序列化，高频操作（多物体移动、批量材质修改）延迟较高。
- **第三方 API 依赖**：Rodin/Hunyuan3D/Sketchfab 的 API 变更直接影响功能，需持续维护。
- **Blender 版本兼容性**：Blender 4.x→5.x 的 Python API 变化（如 bpy 模块变动）可能导致 addon 不兼容。
- **安全风险**：`execute_code` 工具可以让 LLM 执行任意 Python 代码，存在潜在安全隐患（已通过 `Terms and Conditions` 文档声明使用风险，但技术上无沙箱限制）。

### 趋势判断：爆发增长期 → 稳定期过渡

blender-mcp 在 2025 年 Q1 发布后经历快速增长，2026 年 Q1 达到 20K⭐。随着 MCP 协议标准化和 AI 3D 生成能力提升，其作为"3D AI 中间件"的价值会持续增加。但单一看似"套壳"的本质（技术边界较薄），也意味着竞品容易复制核心功能。

## 📂 关键文件路径速查

| 文件 | 路径 | 作用 |
|------|------|------|
| Blender 插件 | `addon.py` | Blender 内运行的 TCP Socket 服务，所有建模操作的实际执行层 |
| MCP Server | `src/blender_mcp/server.py` | MCP 工具定义 + TCP Client 转发层，50+ @mcp.tool() |
| CLI 入口 | `main.py` | 调用 server.main() 启动 MCP Server |
| 包配置 | `pyproject.toml` | 依赖: mcp[cli]>=1.3.0, httpx |
| 遥测 | `src/blender_mcp/telemetry.py` | 启动计数 + 工具使用统计 |
| Telemetry 装饰器 | `src/blender_mcp/telemetry_decorator.py` | @telemetry_tool 装饰器定义 |
| 使用条款 | `TERMS_AND_CONDITIONS.md` | 免责声明（execute_code 安全风险） |
