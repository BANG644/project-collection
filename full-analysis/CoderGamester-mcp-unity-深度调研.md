# CoderGamester/mcp-unity 深度调研

> 调研日期：2026-09-23 ｜ 定位：把 Unity Editor 通过 MCP 协议暴露给 AI 编码助手的桥接器（C# Editor 包 + Node.js 服务） ｜ Stars：1,909 ｜ 语言：C# / TypeScript ｜ 许可：MIT ｜ 默认分支：main ｜ 最近活跃：2026-09-03

## 一、项目定位（一句话）

mcp-unity 是 Unity Editor 的 **Model Context Protocol 实现**：在 Unity 内起一个 WebSocket 服务，再用一个 Node.js 服务（作为 WebSocket 客户端 + MCP Server）把 Editor 能力（场景/物体/组件/材质/播放模式/测试/控制台）封装成 MCP 工具，让 Cursor、Claude Code、Codex、Copilot、OpenCode 等任意 MCP 客户端用自然语言驱动 Unity。

## 二、项目亮点（差异化）

- **双向桥接而非单端插件**：Unity 侧是 WebSocket **服务端**（C# Editor 包），Node 侧是 WebSocket **客户端 + MCP Server**，JSON-RPC 在两者间往返，天然适配所有支持 stdio MCP 的客户端（命令即 `node build/index.js`）。
- **~40 个开箱即用工具**：覆盖 `create_scene / update_gameobject / update_component / create_material / batch_execute / run_tests / set_play_mode_status / recompile_scripts` 等，外加 7 类 `unity://` 资源（菜单项、场景层级、GameObject、日志、包、资产、测试）。
- **生产级健壮性**：断线自动重连 + 离线命令队列（`CommandQueue`）+ 重连后回放、请求超时与 `pendingRequests` 映射、WSL2 网络兼容（mirrored mode / `UNITY_HOST`）。
- **安全护栏到位**：每项目 256-bit 认证 token（`Library/McpUnity/bridge-token`）、HTTP Basic（用户名 `mcp-unity`）、拒绝带 `Origin` 的 WebSocket 握手、`add_package` 默认关闭（防止 Editor 代码自动执行）、远程 `ws://` 明确不加密需 VPN/隧道。
- **强可扩展**：C# 侧继承 `McpToolBase` 即可加工具，TS 侧在 `Server~/src/tools/` 加 Zod schema handler 并在 `index.ts` 注册。

## 三、核心架构

```
AI MCP Client (Cursor/Claude Code/Codex…)
        │ stdio: MCP (tools/resources/prompts)
        ▼
Node.js MCP Server  (Server~/src/index.ts)
   ├─ McpUnity 桥 (mcpUnity.ts)：JSON-RPC over WebSocket 客户端
   │     ├─ pendingRequests 映射 + 超时
   │     ├─ CommandQueue 离线排队 + 重连回放
   │     └─ authToken / UNITY_PORT / UNITY_HOST 解析
   ▼ ws://localhost:8090/McpUnity
Unity Editor WebSocket 服务端  (Editor/UnityBridge/McpUnityServer.cs)
   ├─ McpUnitySocketHandler：分发 JSON-RPC → 工具
   ├─ Editor/Tools/*.cs（每个工具继承 McpToolBase）
   ├─ Editor/Resources/*.cs（unity:// 资源）
   └─ McpUnityEditorWindow（Server Window：配置/启停/端口/超时）
```

- **C# 侧（Editor/）**：`UnityBridge/McpUnityServer.cs` + `McpUnitySocketHandler.cs` 是 WebSocket 服务端；`Tools/` 下每个能力一个文件（如 `UpdateGameObjectTool.cs`、`BatchExecuteTool.cs`、`MaterialTools.cs`），统一继承 `McpToolBase`；`Resources/` 暴露只读 `unity://` 资源；`Utils/McpBackgroundTick.cs` 处理后台心跳。
- **TS 侧（Server~/）**：`src/index.ts` 注册全部工具/资源/提示词（Zod 校验入参），`src/tools/*.ts` 是各工具的转发 handler，`src/unity/mcpUnity.ts` 是核心桥，`src/unity/unityConnection.ts` 管 WebSocket 连接与重连。

## 四、应用场景与启发

- **AI 辅助 Unity 开发闭环**：当你想让 Claude Code「帮我建 10 个 Enemy 空物体并改名」「跑一遍 EditMode 测试」「把 Player 的 tag 改成 Enemy」，mcp-unity 提供了现成的工具集合——可直接抄它的工具清单与 `McpToolBase` 注册范式。
- **自研编辑器 MCP 的参考样本**：它把"本地重型 GUI（Unity/Blender/IDE）暴露成 MCP"的桥接模式做得很完整（token 鉴权 + 离线队列 + 重连回放），对做 Blender/Maya/VS Code 类 MCP 桥都有借鉴。
- **企业级协作**：Server Window 支持把 MCP 配置写进项目根 `.mcp.json`（相对路径）随仓库走，团队共享 AI 工作流。

## 五、源码深度解读（关键片段）

`Server~/src/unity/mcpUnity.ts` 中的 `McpUnity` 类是桥的核心——它用 JSON-RPC over WebSocket 与 Unity 通信，并用 `CommandQueue` 解决"Editor 未启动/重连期间命令丢失"问题：

```ts
// 断线时：命令入队而非直接失败
if (queueIfDisconnected && this.connectionState === ConnectionState.Reconnecting) {
  return new Promise((resolve, reject) => {
    const result = this.commandQueue.enqueue({ id: requestId, request: message, resolve, reject, timeout });
    if (result.success) this.logger.info(`Command ${requestId} queued at position ${result.position}`);
  });
}
// 重连成功后：回放队列
private async replayQueuedCommands() {
  const commands = this.commandQueue.drain();
  for (const command of commands) {
    const result = await this.sendRequestInternal(command.request, command.timeout);
    command.resolve(result);   // 重连后补发，保证 at-least-once 交付
  }
}
```

Unity 侧 `Editor/UnityBridge/McpUnityServer.cs` 通过 WebSocket-Sharp 监听并解析 JSON-RPC，再反射/分发到 `Editor/Tools/` 下各 `McpToolBase` 子类；`Server~/src/index.ts` 把每个工具以 Zod schema 注册到 MCP，使客户端拿到结构化入参。

## 六、全网口碑

- **正面**：覆盖客户端最广的 Unity MCP 实现之一（README 列了 8+ 个 MCP 宿主），文档详尽（含 WSL2、安全、FAQ），社区活跃（Discord、多语言 README、持续发版至 2026-09）。被多个 Unity + AI 工作流文章引用为"让 AI 写 Unity"的标配桥。
- **风险/争议**：强依赖 Unity 6+（2024 后的 tab/Editor API），旧版本不支持；`add_package` 默认关闭需手动开（安全但增加上手成本）；远程 `ws://` 明文，跨机需用 VPN/SSH 隧道；与 Unity 6.2 原生 AI 功能定位互补而非替代。

## 七、竞品对比与核心研判

| 维度 | mcp-unity | Unity-MCP(IvanMurzak) | 纯 VSCode 扩展 |
|------|-----------|----------------------|----------------|
| 桥接方式 | C# Editor WS 服务 + Node MCP | C# 反射驱动 + 运行时 | 不接入 Editor |
| 工具粒度 | ~40 工具 + 7 类资源 | 70+ 工具 | — |
| 健壮性 | 队列/重连/鉴权 | 主线程护栏 | — |
| 客户端覆盖 | 8+ MCP 宿主 | OpenAI Agents 等 | 仅编辑器内 |

**竞品**：`IvanMurzak/Unity-MCP`（反射驱动、运行时内游戏 AI，偏游戏内 agent）、各类一次性脚本。**mcp-unity 的差异化**在于"Editor 自动化"定位 + 最完整的工具/资源覆盖 + 生产级桥接健壮性。

**核心研判**：⭐⭐⭐⭐ — 想把"AI 编码助手"接入 Unity Editor 工作流的团队，这份仓库是当下最省心的开箱方案，其 **JSON-RPC over WebSocket 桥 + 离线队列 + token 鉴权** 范式对做任意重型 GUI 的 MCP 化都有复制价值；但作为生产系统偏"个人/小团队"维护节奏，企业落地前建议补一套 CI 对多 Unity 版本的回归测试。

## 八、关键文件路径速查

- `Editor/UnityBridge/McpUnityServer.cs` / `McpUnitySocketHandler.cs` — Unity 侧 WebSocket 服务端
- `Editor/Tools/*.cs`（如 `UpdateGameObjectTool.cs`、`BatchExecuteTool.cs`、`MaterialTools.cs`）— 各 MCP 工具（继承 `McpToolBase`）
- `Editor/Resources/*.cs` — `unity://` 只读资源
- `Server~/src/index.ts` — MCP 工具/资源/提示词注册入口
- `Server~/src/unity/mcpUnity.ts` — 核心桥（JSON-RPC + 队列 + 重连）
- `Server~/src/unity/unityConnection.ts` / `unityConnectionConfig.ts` — 连接与配置解析
- `Server~/src/tools/*.ts` — TS 侧工具转发 handler
- 上游依赖：[CoderGamester/mcp-unity](https://github.com/CoderGamester/mcp-unity) ｜ 协议标准：[Model Context Protocol](https://modelcontextprotocol.io)
