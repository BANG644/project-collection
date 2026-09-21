# IvanMurzak/Unity-MCP 深度调研

> 调研日期：2026-09-22 ｜ 定位：把任意 LLM 客户端桥接进 Unity Editor 与运行时（含游戏内 AI）的 MCP 工具/技能平台 ｜ Stars：4,313 ｜ 语言：C# ｜ 许可：Apache-2.0 ｜ 默认分支：main ｜ 最近活跃：2026-09-17

## 一、项目定位（一句话）

Unity-MCP（"AI Game Developer"）是 Ivan Murzak 维护的 **Unity ↔ LLM 桥**：以 MCP 协议把 Unity Editor 的操作（建场景、改脚本、跑测试、做性能分析）和**运行时内游戏逻辑**全部暴露成工具，让 Claude、Cursor、Codex、Copilot、Gemini、OpenCode 等任意支持 MCP/Skills 的客户端直接"用自然语言做游戏"。

## 二、项目亮点（差异化）

- **Editor + Runtime 双模**：不止编辑期——还能把 MCP 编译进**已发布的游戏**，让 LLM 在运行时驱动 NPC 行为或在线调试（chess bot 样例）。
- **70+ 内置工具 / 4 大类**：Project & Assets、Scene & Hierarchy、Scripting & Editor、Profiling & Diagnostics，覆盖从资源到性能剖析的全链路。
- **反射驱动（Reflection-Powered）**：`reflection-method-find/call` 能发现并调用项目里**任意 C# 方法（含私有）**；`script-execute` 用 Roslyn 动态编译执行；`type-get-json-schema` 反射出类型 schema——LLM 几乎拥有"完整 Unity API 视野"。
- **一行注解即工具**：`[AiToolType]` + `[AiTool]` 属性声明，方法自动注册为 MCP Tool，支持主线程/后台线程切换。
- **成熟交付链**：OpenUPM 包 + Docker 镜像（aigamedeveloper/mcp-server）+ `unity-mcp-cli`（install/login/open 一条龙，OAuth 设备流）+ 10+ 官方扩展（AI-Animation/AI-Cinemachine/AI-Navigation…）。

## 三、核心架构

```
MCP Client (Claude/Cursor/...)  ──stdio / streamableHttp──▶  MCP Server (gamedev-mcp-server)
                                                                    │  (port 8080, auth none/oauth/token)
                                                                    ▼
                                                          Unity MCP Plugin (per-project Library/mcp-server)
                                                                    │  MainThread.Instance.Run(...)
                                                                    ▼
                                                  Unity Editor API / 运行时 GameObject·Component·Asset
```

- **MCP Server**：独立二进制或 Docker（`aigamedeveloper/mcp-server`），支持 `stdio` 与 `streamableHttp` 两种 transport；`MCP_AUTHORIZATION` 控制 none/oauth/token。
- **Unity Plugin**：装在项目 `Library/mcp-server/<arch>/` 下，按平台提供 exe（Win）或 executable（macOS/Linux）；通过环境变量/命令行覆盖（如 `UNITY_MCP_TOOLS` 仅启用指定工具、`UNITY_MCP_TRANSPORT`）。
- **CLI**：`unity-mcp-cli` 负责安装插件、OAuth 登录（`~/.ai-game-dev/credentials.json`）、打开工程并自动生成 skills；支持 `--enroll` 团队邀请码。

## 四、应用场景与启发

- **游戏开发提效**：自然语言"建 3 个半径 2 的环排立方体"→ 直接落场景；批量改材质、程序化布关卡、配灯光后处理，全部工具化。
- **游戏内 AI**：用 `UnityMcpPluginRuntime.Initialize` 把决策逻辑外包给 LLM（棋类 bot、动态 NPC），是"AI 原生游戏"的轻量落地路径。
- **给 MCP 工具设计的启发**：它展示了"用属性声明 + 反射自动发现"把大型原生应用暴露成 LLM 工具的标准姿势——对想把任何桌面软件/引擎接 MCP 的团队是范本。

## 五、源码深度解读（关键片段）

自定义工具只需一个类 + 一个方法注解，框架自动反射注册：

```csharp
[AiToolType]
public class Tool_GameObject {
    [AiTool("MyCustomTask", Title = "Create a new GameObject")]
    [Description("Explain here to LLM what is this, when it should be called.")]
    public string CustomTask([Description("input")] string inputData) {
        return MainThread.Instance.Run(() => { /* 与 Unity API 交互 */ return "[Success]"; });
    }
}
```

运行时把 MCP 插件编译进游戏并连接：

```csharp
var mcpPlugin = UnityMcpPluginRuntime.Initialize(b => b
    .WithConfig(c => { c.Host = "http://localhost:8080"; c.Token = "your-token"; })
    .WithToolsFromAssembly(Assembly.GetExecutingAssembly())).Build();
await mcpPlugin.Connect();
```

`MainThread.Instance.Run(...)` 是 Unity API 调用的关键护栏——所有 Unity 对象操作必须回主线程。

## 六、全网口碑

- **正面**：OpenUPM 持续下载、Docker 镜像 + 多客户端（Claude/Codex/Cursor/Gemini/OpenCode/Cline…）广泛兼容、Discord 活跃；"Runtime 内 AI"卖点独特，被不少 AI 游戏/数字人教程引用。
- **风险/注意**：工程路径**不能含空格**（硬性要求）；云端登录默认指向 `ai-game.dev`（需 OAuth，团队可按 enrollment code 分发）；插件二进制随工程走、体积不小。

## 七、竞品对比与核心研判

| 维度 | IvanMurzak/Unity-MCP | CoplayDev/unity-mcp | CoderGamester/mcp-unity |
|------|----------------------|---------------------|-------------------------|
| 工具数 | 70+（4 大类） | ~47 | 较少 |
| 运行时(in-game) | ✅ | ❌ | ❌ |
| 扩展生态 | 10+ 官方扩展 | 无 | 无 |
| 交付 | OpenUPM+Docker+CLI | 插件+反射发现 | 插件 |

**核心研判**：⭐⭐⭐⭐⭐ — 目前**最成熟的 Unity↔LLM 桥**，Runtime 支持与反射驱动是明显代差优势，适合任何"用 AI 做/改 Unity 游戏"的场景。若只需编辑期轻量桥接，CoplayDev/unity-mcp 也够用；要做游戏内 LLM，则 Unity-MCP 是唯一现成选择。注意 AGPL 之外的 Apache-2.0 许可对商用友好，但云端账号体系是厂商绑定点。

## 八、关键文件路径速查

- `Unity-MCP-Plugin/` — Unity 编辑器插件主体（AiTool 反射注册）
- `cli/` — `unity-mcp-cli`（install/login/open/wait-for-ready）
- `docs/default-mcp-tools.md` — 全部 70+ 工具说明
- `docs/mcp-server.md` / `DOCKER_DEPLOYMENT.md` — Server 配置与容器部署
- 扩展生态：[Unity-AI-Animation](https://github.com/IvanMurzak/Unity-AI-Animation) 等 10+ 仓库 ｜ OpenUPM：`com.ivanmurzak.unity.mcp`
