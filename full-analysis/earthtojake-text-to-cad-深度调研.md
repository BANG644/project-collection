# text-to-cad（让 Agent 拥有 CAD 超能力）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / pyproject.toml / apps/mcp/package.json），抓取日期 2026-10-05。许可：MIT。语言：Python（cadgen 运行时）+ TypeScript（apps/mcp、apps/web）。版本：0.7.11（Beta）。

## 一、项目定位（一句话）
把**自然语言转成可制造 CAD 工件**（STEP / GLB / DXF / 拓扑）的 **agent 工具链**：以 `cadgen` Python 运行时为核心，配 MCP Server + Web 查看器 + Claude/Codex/Cursor 插件，给 AI 编码 Agent 真正的「CAD 超能力」。

## 二、项目亮点（差异化）
1. **STEP-first（工业标准）**：产物是 STEP / GLB / DXF 等可制造格式，而非仅网格——区别于多数「text-to-3D 生成网格」方案。
2. **严肃的几何内核**：基于 `build123d` + `cadquery-ocp-novtk`（OpenCASCADE），支持装配（assembly）、运动学（kinematics）、干涉（interference）、SDF 校验。
3. **cadgen 运行时丰富**：40+ 模块覆盖 生成 / 装配 / 分析 / 校验 / 渲染 全链路。
4. **验证闭环**：`drawing_checks` / `sdf_validation` / `interference` 等后验校验 + 视觉快照（headless browser 渲染）。
5. **多 harness 插件**：`.claude-plugin` / `.codex-plugin` / `.cursor-plugin` 齐备，`apps/mcp` 暴露给任意 MCP 客户端。

## 三、核心架构
- **monorepo（pnpm）**：`apps/docs`（Next.js 文档）、`apps/mcp`（MCP Server + Web）、`apps/web`（查看器）；`packages/cadgen`（**Python 运行时**，`pyproject.toml`）、`packages/core`、`packages/ui`；`skills/` 与三套插件清单。
- **cadgen（Python）依赖**：`build123d>=0.11.1,<0.12`、`cadquery-ocp-novtk>=7.9,<8`、`ezdxf`、`matplotlib`、`pillow`、`shapely`；`[snapshot]` extra 含 Playwright（渲染）。
- **apps/mcp（前端）**：React 19.3 + `three@0.186`（3D 预览）+ `meshoptimizer@1.2`（网格优化）+ `lucide-react`。

## 四、应用场景与启发
- 「**Agent + 工业软件**」端到端落地样本：自然语言 → 参数化 CAD 生成 → 校验 → 可制造，闭环完整。
- **直接打内部库**的务实做法（见下源码）是「复用 vs 脆弱」权衡的典型案例，对「如何基于快速演进的几何库构建稳定产品」有启发。
- 多插件（Claude/Codex/Cursor）+ MCP 的分发方式，是「把专业工具嵌入 Agent 工作流」的范本。

## 五、源码深度解读
**`packages/cadgen/pyproject.toml`（依赖的工程权衡）**——注释明确 cadgen 不只调用 build123d，还**潜入其内部**：
```toml
# cadgen does not merely CALL build123d, it reaches into it: the determinism
# shim shadows `set` in three topology modules and replaces `Vertex.__hash__`,
# and the lazy store replaces `Compound.__init__` and reads its arguments BY POSITION.
"build123d>=0.11.1,<0.12",   # 上界锁死：小版本可能重排签名，失败模式是静默的
```
**`packages/cadgen/src/cadgen/` 关键模块**（40+ 文件节选）：
- `generation.py` — 文本→CAD 生成主流程
- `build123d.py` — 确定性 shim（shadow set / 替换 `Vertex.__hash__`）
- `glb.py` / `dxf.py` — 格式导出
- `assembly.py` / `kinematics.py` / `interference.py` — 装配 / 运动学 / 干涉分析
- `flatten.py` / `sdf.py` / `drawing_checks.py` — 展平 / SDF 校验 / 后验校验
- `render.py` / `assets.py` — 视觉渲染与运行时资源
**`apps/mcp/package.json`**（MCP 前端栈）：`three@0.186.1` + `meshoptimizer@1.2.0` + `react@19.3.0`，印证「3D 预览 + 网格优化」的查看器形态。

## 六、社区口碑
⭐**16,787**。定位清晰（agent CAD）、文档（`docs/`）与三套插件齐全，v0.7.11 Beta 阶段已获关注；作为「AI + 制造业」热门方向代表，社区正向。

## 七、竞品对比
| 维度 | text-to-cad | FreeCAD | CadQuery/build123d | OpenSCAD | 通用 text-to-3D |
|---|---|---|---|---|---|
| 交互 | Agent/自然语言 | 手动 GUI | 写 Python | 写 CSG | 文本→网格 |
| 产物 | STEP/GLB/DXF | STEP | STEP | SCAD→网格 | 多为网格 |
| 校验 | 内置（干涉/SDF） | 有 | 需自写 | 无 | 弱 |
| Agent | 原生 MCP/插件 | 否 | 否 | 否 | 部分 |

差异：把「参数化 CAD 生成 + 校验」封装为 **agent-native + 工业标准格式 + 多 harness 插件**。

## 八、核心研判
✅ 真正端到端的「大模型 Agent → 可制造 CAD」工具链，cadgen 运行时工程扎实（生成/装配/运动学/校验齐全），插件与文档完善，是「Agent + 工业软件」的优秀研究样本。
⚠️ 风险：直接潜入 build123d 内部（shadow set、替换 `Vertex.__hash__`、`Compound.__init__` 按位置读参）带来**脆弱性**——故依赖上界锁死 `<0.12`，升级需重跑测试套件；本质是「复用捷径 vs 升级脆弱」的典型权衡。
📌 推荐场景：研究「agent 接入专业工业软件」「参数化 CAD 生成与校验闭环」。不推荐作为 stable 生产依赖，除非锁定其 build123d 版本区间。

## 九、关键文件路径速查
- `packages/cadgen/pyproject.toml` — 运行时依赖与工程权衡说明
- `packages/cadgen/src/cadgen/generation.py` — 生成主流程
- `packages/cadgen/src/cadgen/build123d.py` — 确定性 shim（潜入内部）
- `packages/cadgen/src/cadgen/{glb,dxf,assembly,kinematics,interference,sdf,drawing_checks,flatten,render}.py` — 导出/分析/校验
- `apps/mcp/package.json` + `apps/mcp/` — MCP Server 与 3D 查看器
- `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json` / `.cursor-plugin/plugin.json` — 三 harness 插件
- `skills/` — Agent 技能定义
