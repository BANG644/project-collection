# Modly 深度调研

> 调研日期：2026-08-15 ｜ 星标：5,857 ⭐ ｜ 协议：MIT（app 代码；默认模型 Hunyuan3D-2 Mini 为腾讯非 OSI 许可）
> 仓库：`lightningpixel/modly` ｜ 默认分支：`main` ｜ 官网：modly3d.app
> 调研来源：当日 GitHub Trending

## 一、项目定位（一句话）

完全本地、开源的 **AI 图像转 3D 网格桌面应用**——在消费级 GPU 上跑 Hunyuan3D 等开源模型，**无云、无账号、隐私优先**。

## 二、项目亮点（差异化）

1. **本地 GPU 推理，隐私优先**：不联网、不依赖云 API、无生成上限，适合在意隐私/成本的创作者。
2. **扩展式模型架构**：每个 AI 模型是一个独立 GitHub 仓库（`manifest.json` + 生成入口），核心二进制零改动即可加模型。
3. **两阶段管线**：几何网格生成 → 高分辨率纹理合成（默认 Hunyuan3D-2 Mini，0.6B 参数，消费级显存可跑）。
4. **标准格式导出 + 内置查看器**：GLB / OBJ / STL / PLY；内置 3D 查看器与集合管理；支持网格平滑/抽稀后写回工作区。
5. **Agent 可编排**：stdlib-only CLI（`tools/modly-cli/agent.py`）+ `SKILL.md` 契约，脚本/Agent 无需 UI 即可驱动。

## 三、核心架构

Modly 是 **Electron + TypeScript 前端 + Python FastAPI 后端 + 外部模型扩展仓库** 的组合：

- **`src/` 前端（React + Vite + Tailwind，Electron 壳）**
  - `src/areas/`：`generate`（生成）/ `models`（模型管理）/ `settings` / `setup` / `workflows`（工作流图）
  - 工作流图：Image → Generate Mesh → Add to Scene，**运行前校验连线**，非法图保留原位并以内联/弹窗警告提示（不静默丢视图）。
- **`api/` Python 后端（FastAPI）**
  - `main.py`：入口；`routers/`：REST 路由；`runner.py`：工作流运行器；`services/`：业务逻辑
  - `texture_baker/`、`uv_unwrapper/`：纹理烘焙与 UV 展开
  - `mcp_server.py`：暴露 **MCP** 能力（Agent 可经 MCP 调用）
  - `schemas/`：请求/响应模型
- **扩展系统**：用户在 "Models" 页点 "Install from GitHub"，输入扩展仓库 HTTPS URL 即可拉取；每个扩展含 `manifest.json` + 运行入口（如 `generator.py`）。
- **官方扩展**：Hunyuan3D 2 Mini / Mini Turbo / Mini Fast、TripoSG、Trellis2 GGUF。
- **架构决策文档**：`arch/decisions/`（`APPLE-SILICON-SUPPORT.md` 等）记录平台取舍。

## 四、应用场景与启发

**典型场景**：独立设计师/手作人把实物照片转 3D 展示图发 Shopify/小红书；游戏资产快速原型；不想上传隐私图片到云端 3D 服务的用户。社区已提需求：多图参考输入、glTF 导出优化、节点重命名（对接下游引擎）。

**架构启发（可复用）**：
- **桌面 AI 应用"核心 + 可插拔模型扩展"范式**：把"模型逻辑"与"核心界面/管线"彻底解耦，新增模型只加一个符合 `manifest.json` 规范的仓库——避免核心二进制随模型膨胀，社区可独立贡献。
- **本地优先 + MCP 暴露**：既保隐私又让 Agent 能编排（mcp_server.py），是"本地 AI 生产力工具"的标准答案之一。
- **工作流图 + 运行前校验**：把生成流程可视化并前置校验，降低用户试错成本。

## 五、源码深度解读

### 1. 后端入口与路由：`api/main.py` + `api/routers/`

FastAPI 应用从 `main.py` 引导，业务路由集中在 `routers/`（如 `/workflow-runs/from-image` 触发图像转 3D 工作流）。`runner.py` 是工作流执行器，负责串联"图像→网格→场景"各阶段并管理运行状态/取消/恢复。

### 2. Agent CLI 契约：`tools/modly-cli/agent.py`

```bash
python tools/modly-cli/agent.py health
python tools/modly-cli/agent.py model list
python tools/modly-cli/agent.py workflow-run status <run_id>
python tools/modly-cli/agent.py generate --image ./input.png --output ./export.glb
```

规范根命令为 `health` / `model` / `workflow-run` / `capability` / `process-run`；`generate` 是友好封装，内部启动 `POST /workflow-runs/from-image`、轮询 run、按需导出网格并带恢复元数据（status/cancel）。`tools/modly-cli/SKILL.md` 定义了 Agent 工作流与输出契约——这是 Modly "可被 Agent 编排"的官方入口。

### 3. 扩展即仓库：`manifest.json` + 生成入口

每个扩展是独立 GitHub 仓库，核心通过 HTTPS URL 校验拉取，模型节点按需下载。这一设计使 Trellis2、TripoSG 等新模型的接入**无需修改核心**，天然支持社区分发。

## 六、全网口碑

- **热度**：beta（v0.4.0）阶段，Reddit r/MachineLearning 与 HackerNews 热议"离线 AI 生产力"，被部分媒体称为 **"Stable Diffusion for 3D"**；Blender 社区大量转发其免建模流程。
- **⚠️ 关键 caveat（许可）**：默认模型 **Hunyuan3D-2 Mini 是腾讯 `tencent-hunyuan-community` 非 OSI 许可**（含商业/地域限制），所以"开源"仅干净覆盖 **app 代码**，不覆盖你生成所用的**模型权重**。app 本身为 MIT（因附加署名条款，GitHub 显示为 `NOASSERTION`）。
- **其他**：GPU 依赖（无强 GPU 者不可用）；beta 阶段输出质量依赖第三方模型，团队不控制；Windows/Linux 有装包，macOS 仅 Apple Silicon。
- **总体**：方向正确、UX 友好、扩展式架构优雅；主要权衡在模型许可与 GPU 门槛。

## 七、竞品对比与核心研判

| 维度 | Modly | Meshy | Tripo | Hyper3D | Trellis/Hunyuan3D（裸模型） |
|---|---|---|---|---|---|
| 本地/云 | ✅ 本地 | ☁️ 云 | ☁️ 云 | ☁️ 云 | ✅ 本地（需自搭） |
| 开源 app | ✅ MIT | ❌ | ❌ | ❌ | ✅ 模型开源 |
| 模型可换 | ✅ 扩展式 | ❌ | ❌ | ❌ | — |
| 隐私 | ✅ | ❌ | ❌ | ❌ | ✅ |

**核心研判**：
- **优势**：本地优先 + 可换模型 + 桌面 UX + Agent/MCP 可编排，是隐私敏感 3D 创作者的优质入口；"核心+扩展"架构值得其它本地 AI 应用临摹。
- **风险**：① 默认模型许可非 OSI，商用需谨慎；② GPU 硬门槛；③ beta 成熟度。
- **启发**：如果做"本地 AI 生产力工具"，Modly 证明了"开源 app + 可插拔（含受限制）模型 + MCP 暴露"是兼顾隐私、可维护性与社区扩展的可行形态；但**模型许可的透明度**必须向用户讲清楚，否则"开源"会被误解。

## 关键文件速查

| 路径 | 作用 |
|---|---|
| `src/areas/workflows` | 工作流图（Image→Mesh→Scene） |
| `src/areas/generate` `src/areas/models` | 生成 / 模型管理 UI |
| `api/main.py` | FastAPI 入口 |
| `api/routers/` `api/runner.py` | REST 路由 / 工作流运行器 |
| `api/services/` `api/schemas/` | 业务逻辑 / 数据模型 |
| `api/mcp_server.py` | MCP 能力暴露 |
| `api/texture_baker/` `api/uv_unwrapper/` | 纹理烘焙 / UV 展开 |
| `tools/modly-cli/agent.py` `SKILL.md` | Agent CLI 与契约 |
| `arch/decisions/` | 平台架构决策文档 |
