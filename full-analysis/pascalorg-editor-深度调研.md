# 🔬 pascalorg/editor - 全方位深度调研

- GitHub: https://github.com/pascalorg/editor
- 调研时间: 2026-07-30
- 仓库规模: ⭐ 19.5K / Fork 2.6K / 语言 TypeScript / 协议 MIT
- 官方定位: Create and share 3D architectural projects（浏览器内免费开源 3D 建筑编辑器）
- 一句话: Pascal 把「建筑/BIM 建模」搬进浏览器，用 React Three Fiber + WebGPU 做实时 3D 引擎，配一个自然语言草模生成器，让建筑师/学生/业主零门槛出 3D 方案并能一键分享/嵌入/导出。

## 🌟 项目亮点（差异化）

1. **浏览器原生 3D BIM**：无需安装，打开即建；React Three Fiber + WebGPU 渲染复杂多层场景仍流畅。
2. **自然语言草模**：输入「两层家庭住宅 / 有泳池的别墅」即生成结构骨架，官方称减少约 60% 初始布局时间。
3. **扁平字典数据模型**：项目以 `Site → Building → Level → {Walls, Slabs, Ceilings, Roofs, Zones, Scans, Guides}` 组织，用**扁平字典而非嵌套树**存储节点，便于版本化与协作。
4. **本地优先 + 零注册**：编辑态数据存浏览器 IndexedDB，无需服务器/账号即可用；云端（Google/邮箱登录、自动保存）可选。
5. **可分发 & 可嵌**：导出 GLB/OBJ/STL/PDF 平面图；一条链接分享并可 fork；live 3D viewer 用一个 iframe 嵌到任意网站；核心引擎与组件以 npm 包发布。

## 🏗️ 核心架构

Turborepo + Bun 管理的 monorepo：

- `packages/nodes/`：建筑构件定义系统，每个构件（wall / slab / ceiling / roof / zone / stair / window / door / structural-grid / turbine-vent）都是独立「node」：含 `definition.ts`、`schema.ts`、`floorplan.ts`、`parametrics.ts`、`renderer.tsx`、`panel.tsx`、`tool.tsx`、`system.tsx`、`*.test.ts`。
- `packages/viewer/`：基于 R3F/Three.js 的场景渲染器（`scene-renderer.tsx`、`node-renderer.tsx`、`glb-scene.tsx`、`bvh-ecctrl.tsx` walkthrough 控制器、`snapshot-pipeline.ts`），BVH 加速、KTX2 纹理、后处理、性能监控。
- `packages/ui/`：共享 UI（button/card/code）。
- `wiki/architecture/`：极详尽架构文档（`node-definitions`、`node-schemas`、`renderers`、`systems`、`tools`、`plugin-authoring`、`viewer-isolation`、`vertical-model`、`spatial-queries`）——说明它是认真做「可扩展建筑引擎」而非演示。
- 几何布尔运算经 `three-bvh-csg`；多层可视化支持 stacked / exploded / solo-level 三种模式。

## 🧠 源码深度解读

### 1. 构件即「node 系统」的统一抽象（目录结构）
```text
packages/nodes/src/wall/
  definition.ts   # 构件语义定义
  schema.ts       # 参数 schema（可序列化）
  floorplan.ts    # 平面图投影/贴合
  parametrics.ts  # 参数化驱动
  renderer.tsx    # 3D 渲染
  tool.tsx        # 交互工具（画/移/量）
  system.tsx      # 系统级协调（如开门洞）
```
每个建筑元素都是「定义 + schema + 渲染 + 工具 + 系统」五件套，新增构件只需照搬这套模板——这是它能快速扩展门窗/楼梯/屋顶的原因，也是插件化（plugin-authoring）的基础。

### 2. 扁平字典而非嵌套树（架构文档 + 第三方综述）
> 项目以「Site → Building → Level → {…}」的阶层结构组织数据，采用**扁平字典而非嵌套树状结构**来存储节点

扁平字典让「引用/覆盖/版本 diff」变简单（每个节点独立寻址），天然契合浏览器端协作与「fork 他人项目」的 GitHub 式工作流。

### 3. 引擎即 npm 包（官方证据）
> Every Pascal surface ships on npm — drop the viewer or the full editor straight into your own product.

把 viewer / 完整 editor 作为可嵌入包发布，意味着 Pascal 不只是「一个网站」，而是一层**可被产品复用的 3D 建筑引擎**——这是它区别于普通 Web CAD demo 的关键。

## 💡 应用场景与启发

- **快速草模推敲**：建筑师客户会议前几分钟出 3D 方案，专注迭代而非手摆坐标。
- **房产可视化**：中介生成可交互 3D 漫游链接发给买家。
- **建筑教学**：学生零门槛学 BIM 概念，替代 Revit/ArchiCAD 的陡峭学习曲线。
- **自家装修规划**：业主可视化改造效果再施工。
- **对同类需求的启发**：做专业领域编辑器时，**先把领域构件抽象成「node 系统 + 扁平字典」**，再叠 UI/AI；「引擎发包 + iframe 嵌入」比「做一个封闭 SaaS」更有生态杠杆；自然语言草模用于「降门槛」而非「替代专业」，定位克制反而好用。

## 🌐 全网口碑

- **媒体关注**：被 koc.com.tw 以「AutoCAD 危险！开源建筑编辑器」为题报道；aisharenet、utilo.io 均有评测，共识是「浏览器原生、零注册、AI 辅助、免费开源」。
- **社区机制**：官网 Featured projects 带浏览/点赞/fork 指标，借鉴 GitHub fork 文化做设计协作；Discord 活跃。
- **活跃度**：2026-07-29 仍在提交，wiki 架构文档极其完整，工程严谨度高。
- **反馈面**：面向「快速原型」而非工业级 BIM（无 IFC 深度互操作、结构计算等）；AI 草模是起点而非终稿，专业建筑师仍需下游精修。

## ⚔️ 竞品对比 + 核心研判

| 维度 | Pascal Editor | AutoCAD/Revit | SketchUp Web | Floorplanner |
|---|---|---|---|---|
| 安装 | 浏览器零装 | 重装 | 浏览器 | 浏览器 |
| 开源 | ✅ MIT | ❌ | ❌ | ❌ |
| AI 草模 | ✅ 自然语言 | ❌ | 弱 | 弱 |
| 可嵌/发包 | ✅ npm+iframe | ❌ | ❌ | ❌ |
| 工业 BIM | ❌ | ✅ | 中 | 中 |

**核心研判**：
- **最强**：浏览器原生 + 开源 MIT + AI 草模 + 引擎可嵌，把「建筑可视化」的门槛打到极低，且生态打法（npm 包 + fork 文化）有长期杠杆。
- **风险**：定位在「快速原型/教学/业主」，离工业 BIM（IFC、结构、算量）有距离；WebGPU 兼容性依赖客户端显卡。
- **趋势**：专业工具「浏览器化 + AI 辅助 + 开源」是明确方向，Pascal 卡位好。
- **启发**：垂直领域编辑器想破圈，**「零门槛 + 可分发 + 开源引擎」** 三件套比堆功能更重要。

## 📂 关键文件速查

- `README.md` / `wiki/architecture/README.md`（架构总览）
- `packages/nodes/src/{wall,slab,ceiling,roof,zone,stair,window,door,structural-grid}/`（构件 node 系统）
- `packages/viewer/src/components/viewer/`（场景渲染、walkthrough、GLB）
- `packages/viewer/src/lib/`（csg-utils、materials、snapshot-pipeline、ktx2-loader）
- `packages/viewer/src/systems/`（door/wall/zone/level 等系统协调）
- `turbo.json` / `pnpm-workspace.yaml`（monorepo 编排）
- 在线：`https://editor.pascal.app`；文档：`https://editor.pascal.app/docs`
