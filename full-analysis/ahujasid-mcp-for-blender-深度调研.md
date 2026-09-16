# 🔬 ahujasid/mcp-for-blender - 全方位深度调研

> 调研日期：2026-09-17 ｜ 来源：GitHub 仓库 `ahujasid/mcp-for-blender` 真实 README / 目录树 + `addon.py` 源码抓取（stars 28,779，forks 2,651，pushed 2026-09-16，MIT，Python）

## 一、项目定位（一句话）

**MCP for Blender**（原名 `blender-mcp`）是一个第三方集成：用 **Model Context Protocol** 把任意 LLM 客户端（Claude / Cursor / Codex / VS Code / OpenCode）连到 Blender，让 AI 通过自然语言在 Blender 里建模、改材质、查场景、跑 Python、导入模型与生成 3D 资产。

## 二、项目亮点（差异化）

1. **双组件桥接**：Blender 侧是可被 `uvx mcp-for-blender install-addon` 注入的插件（`addon.py`，在 Blender 内起 socket server），LLM 侧是标准 MCP server（`src/blender_mcp/server.py`，走 stdio）。两端解耦，Blender 版本与 MCP 客户端互不影响。
2. **任意 Python 即能力**：核心工具 `execute_blender_code` 能在 Blender 内执行任意 Python，因此「能做的」远超预定义工具集——上限等于 `bpy` API。
3. **资产生态预集成**：内置 Poly Haven（HDR/模型/纹理）、Sketchfab、Poly Pizza（低多边形）、Hyper3D Rodin、Hunyuan3D（腾讯混元 3D）的搜索/下载/生成通道，AI 一句话拉模型进场景。
4. **安全护栏务实**：socket 无鉴权（强制 localhost），但提供 `BLENDER_MCP_SAFE_MODE=1` 在跑脚本前做风险校验，并默认开启遥测（可 `DISABLE_TELEMETRY=true` 关闭）。
5. **零配置升级**：PyPI 包从 `blender-mcp` 改名为 `mcp-for-blender`，旧配置 `uvx blender-mcp` 继续可用，无需改客户端配置。

## 三、核心架构

```text
LLM 客户端 (Claude/Cursor/…)
   │  stdio (MCP)
   ▼
src/blender_mcp/server.py          # MCP Server：注册工具、转发调用
   │  TCP socket (JSON, 默认 127.0.0.1:9876)
   ▼
Blender 内 addon.py                # socket server：收到命令 → bpy 执行 → 回结果
   │
   ▼
Blender (bpy) 场景 / 建模 / 渲染
```

- **MCP Server 包**（`src/blender_mcp/`）：`server.py` 实现 MCP 工具与协议；`safe_mode.py` 脚本风险校验；`telemetry.py` / `telemetry_decorator.py` 匿名用量上报；`trajectory.py` 轨迹捕获（旧 addon 的 `execute_code` 回退）；`consent_prompt.py` 授权提示；`addon_manager.py` 管理 addon 安装；`bundled/` 内置资产。
- **Blender Addon**（`addon.py`）：在 Blender 进程内起 TCP socket server，导入 `bpy/socket/threading/queue/requests`，把 JSON 命令转成 `bpy` 调用并回传结果；侧边栏「Start MCP Server」按钮开启。
- **连接**：`BLENDER_HOST`(默认 localhost) / `BLENDER_PORT`(默认 9876) 可配，亦支持 `--port` 多实例并存。

## 四、应用场景与启发

- **提示词驱动建模**：「建一个地牢场景，龙守着一锅金子」「把这辆车改成红色金属漆」「把相机调成等距视角」——AI 调工具直接改场景。
- **场景→Web**：`export_scene` 导出 GLB/FBX，配合「读场景信息做 three.js 草图」形成 Blender→Web 链路。
- **资产检索增强**：让 AI 先查节点 schema / `bpy` API 参考再生成代码，避免瞎猜 socket 顺序或枚举名。
- **给同类需求的思路**：① 把「桌面专业软件」暴露给 LLM，最稳的模式是「软件内 socket server + 独立 MCP server（stdio）」双进程，而非在软件内嵌大模型；② 用 `execute_*` 任意代码工具当「逃生舱」，预定义工具只覆盖高频操作，长尾能力交给代码执行；③ 无鉴权本地 socket 必须显式声明只绑 localhost，并提供 safe-mode 校验——AI 可执行代码的合规底线。

## 五、源码深度解读

### 5.1 通信协议（README「Technical Details」真实契约）

```jsonc
// 命令：JSON 对象，带 type 与可选 params
{ "type": "create_object", "params": { "name": "cube" } }
// 响应：带 status 与 result / message
{ "status": "success", "result": { "id": 12 } }
```

传输层为 **TCP 上的 JSON**（非 HTTP），默认端口 `9876`；MCP server 与 LLM 客户端之间是标准 MCP stdio。

### 5.2 Blender 侧 addon（`addon.py` 头部真实 import）

```python
import bpy, socket, threading, queue, requests   # 在 Blender 进程内起 socket server
import mathutils, json, tempfile, zipfile, zlib
import hashlib, hmac, base64                       # 资产下载/校验
```

证据：addon 直接在 Blender 主进程里跑 `socket` + `threading`，接收 MCP server 转发来的命令并调用 `bpy` 执行——这是「LLM 改 3D 场景」能成立的物理基础。

### 5.3 MCP server 包结构（`src/blender_mcp/`）

```text
src/blender_mcp/
├── server.py            # MCP 工具注册 + 协议实现（核心）
├── safe_mode.py         # 执行前脚本风险校验（BLENDER_MCP_SAFE_MODE=1）
├── telemetry.py  telemetry_decorator.py   # 匿名遥测（默认开，可关）
├── trajectory.py        # 轨迹捕获（旧 addon 的 execute_code 回退）
├── consent_prompt.py    # 授权提示
├── addon_manager.py     # install-addon / addon-paths 管理
└── bundled/             # 内置资产
```

## 六、社区口碑

- GitHub 28.8k⭐、2.7k fork、32 open issues（pushed 2026-09-16，极活跃）；原名 `blender-mcp`，是 MCP + 创意工具赛道最早出圈的项目之一，Trendshift 榜单常客。
- PyPI `blender-mcp` 累计下载量「数据不可用」（README 徽章存在但未抓取明细）；Discord 社区活跃，被大量 AI 建模教程引用。
- 明确声明「第三方集成，非 Blender 官方出品」。

## 七、竞品对比

| 维度 | MCP for Blender | BlenderGPT | 直接写 bpy 脚本 | Unity/UE MCP |
|------|----------------|-----------|----------------|--------------|
| 接入方式 | MCP(stdio)+socket | 单一客户端 | 手动 | MCP |
| 任意代码执行 | ✅ execute_blender_code | 视实现 | ✅ | 视实现 |
| 资产生态 | Poly Haven/Sketchfab/Poly Pizza/Rodin/混元 | 少 | 自接 | 不同引擎 |
| 多客户端 | ✅ Claude/Cursor/Codex/VS Code | ❌ | — | 部分 |
| 安全护栏 | safe-mode + localhost 强制 | 弱 | 无 | 弱 |

**结论**：它是「Blender + MCP」事实标准入口，差异化在双组件解耦架构与资产生态预集成。

## 八、核心研判

- **定位精准**：不做「AI 建模算法」，只做「LLM↔Blender 的可执行通道 + 资产搬运」，因此能随任意 LLM 进步而进步，不绑死模型。
- **架构可借鉴**：双进程（软件内 socket + 外部 MCP server）是「给专业桌面软件接 LLM」的通用范式，比嵌入式方案更稳、更易分发。
- **风险点**：`execute_blender_code` 等同把 Blender 变成任意代码执行器，必须依赖 localhost + safe-mode + 用户知情；遥测默认开启是隐私争议点（已提供关闭开关）。
- **适合复用**：任何「AI 驱动专业桌面软件」需求（CAD/视频/音乐），都应参考其 socket+MCP 双组件与 safe-mode 护栏设计。

## 九、关键文件路径速查

```text
ahujasid/mcp-for-blender
├── addon.py                  # Blender 插件：进程内 TCP socket server（bpy 执行入口）
├── main.py                   # 入口
├── src/blender_mcp/
│   ├── server.py             # MCP Server（工具注册 + 协议）
│   ├── safe_mode.py  telemetry.py  trajectory.py  consent_prompt.py  addon_manager.py
│   └── bundled/              # 内置资产
├── pyproject.toml  uv.lock   # uv 分发（PyPI: mcp-for-blender）
└── README.md  TERMS_AND_CONDITIONS.md
```

🔗 仓库：https://github.com/ahujasid/mcp-for-blender ｜ 官网：https://mcp-for-blender.com ｜ 原包名：`blender-mcp`
