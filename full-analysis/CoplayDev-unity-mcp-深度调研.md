# CoplayDev/unity-mcp 深度调研

> 调研日期：2026-09-21 | 星标：14,361⭐ | 语言：C#（Unity Editor 包）+ Python（uv 服务）| 许可：MIT | 默认分支：beta | 最近提交：活跃（v10.0.0，2026-06-30）

## 一句话定位
MCP for Unity 用 Model Context Protocol 把 Claude / Codex / Cursor / VS Code / 本地 LLM 等 AI 助手桥接到 Unity Editor，提供 47 个聚焦的 MCP 工具入口（建场景、改 C# 脚本、管资源、跑测试、构建），免费且 MIT。

## 项目亮点
- **属性驱动的工具声明**：用 `[McpForUnityTool]` 标注 C# 类即自动注册为 MCP 工具，无需手写 schema；`[ToolParameter]` 描述参数即自动生成 JSON Schema。
- **反射自动发现 + 缓存**：基于 Unity `TypeCache` 在 domain reload 时一次性扫描带属性的类型，缓存到 `Dictionary`，修复了早期「每次工具切换都全量走查程序集」的性能 bug（issue #1336 / #1364）。
- **工具分组 + 长任务轮询中间件**：工具分 core/vfx/animation/ui/scripting_ext/testing/menu 组，非核心组默认隐藏，可经 `manage_tools` 元工具按会话启用；`RequiresPolling` 让 Unity 先回 `PendingResponse`，Python 侧轮询 `status` 直到完成（构建类长任务）。
- **跨客户端零配置**：内置 27 个客户端配置器（ClaudeDesktop / Cursor / Codex / OpenClaw / Cline / Rider…），`Configure All Detected Clients` 一键写入。
- **学术背书**：被 SIGGRAPH '25 SA Technical Communications 收录（MCP-Unity: Protocol-Driven Framework for Interactive 3D Authoring），Wiki + Discord 文档完善。

## 核心架构
双端协作：
- `MCPForUnity/Editor/`（C#，741 文件）：Unity 编辑器内实现 MCP 工具与服务器宿主，含 `Tools/`（动画/资源/场景/测试…）、`Clients/Configurators/`（各 IDE 配置）、`Services/ToolDiscoveryService.cs`（反射发现）。
- `Server/`（Python，uv 管理）：stdio 传输 + 工具路由，把 LLM 调用转发给 Unity 编辑器内的 C# 端执行。
- 声明式注册：工具类打 `[McpForUnityTool(Name, Group, RequiresPolling)]`，参数用嵌套 `Parameters` 类 + `[ToolParameter]`。

## 应用场景与启发
- 给「用自然语言控制桌面 IDE / 创作工具」类需求提供范式：把 GUI 操作封装成 MCP 工具，比训练专用 GUI agent 便宜得多。
- 属性 + 反射自动注册模式可直接借鉴到任何 MCP server（C#/Java/TS），省去手写 tool schema。
- `ToolGroup` + 轮询中间件的设计同时解决「工具爆炸」与「长任务阻塞」两个通用痛点。

## 源码解读
**1) 工具属性（`MCPForUnity/Editor/Tools/McpForUnityToolAttribute.cs`）**

```csharp
[AttributeUsage(AttributeTargets.Class, AllowMultiple = false)]
public class McpForUnityToolAttribute : Attribute {
    public string Name { get; set; }          // 为 null 时由类名推导
    public string Description { get; set; }    // 给 LLM 的描述
    public bool AutoRegister { get; set; } = true;
    public string Group { get; set; } = "core"; // core/vfx/animation/ui/testing/menu
    public bool RequiresPolling { get; set; } = false; // 长任务走轮询
    public string PollAction { get; set; } = "status";
    public int MaxPollSeconds { get; set; } = 0;
}
```

**2) 反射发现（`MCPForUnity/Editor/Services/ToolDiscoveryService.cs`）**

```csharp
foreach (var type in InRegistrationOrder(
    TypeCache.GetTypesWithAttribute<McpForUnityToolAttribute>()))
{
    var toolAttr = type.GetCustomAttribute<McpForUnityToolAttribute>();
    var metadata = ExtractToolMetadata(type, toolAttr); // 类名→snake_case、参数→JSON Schema
    _cachedTools[metadata.Name] = metadata;             // 缓存，domain reload 仅一次
}
```

## 全网口碑
GitHub 14.3k⭐、Discord 活跃；被 SIGGRAPH '25 收录并有正式 BibTeX 引用；Wiki 文档完善。是 Unity+MCP 方向社区事实标准之一，个人/小团队可免费商用（Aura 公司赞助维护，另有付费 Aura for Unity）。

## 竞品对比 + 核心研判
- 竞品：`IvanMurzak/Unity-MCP`（更早的 Unity MCP 桥，~4.3k⭐）、Unity 官方 Muse / Aura（闭源商业）。
- 研判：MCP for Unity 凭「属性声明 + 反射自动发现 + 学术背书 + 27 客户端配置器」成为 Unity+LLM 首选开源桥；`beta` 为开发主线（贡献需从 beta 切出），v10 引入资产生成与升级。适合「让 AI 帮我搭场景/改脚本」的 Unity 开发者与游戏方向研究者。

## 关键文件路径速查
- `MCPForUnity/Editor/Tools/McpForUnityToolAttribute.cs` — 工具属性定义
- `MCPForUnity/Editor/Services/ToolDiscoveryService.cs` — 反射发现与缓存
- `MCPForUnity/Editor/Tools/` — 各域工具实现（Animation / Asset / Scene / Testing…）
- `MCPForUnity/Editor/Clients/Configurators/` — 27 个客户端配置器
- `Server/src/cli/commands/` — Python CLI 工具命令
- 官方文档：https://coplaydev.github.io/unity-mcp/
