# img2threejs/img2threejs 深度调研

> 调研日期：2026-10-30 ｜ 数据来源：GitHub API（README / `SKILL.md` / `forge/` 源码树 / `ROADMAP.md`）+ 第三方实测（ai-bot.cn / hysenlabs / heatdrop / productcool）
> 许可证：**Apache-2.0** ｜ 形态：给 Claude Code / Codex / OpenCode / Hermes 用的 Agent Skill（纯 Python 3.10+ 标准库脚本 + 分阶段 sculpt 流水线）

## 项目亮点（差异化）

- **「用代码重建，而非网格」**：喂一张参考图，产出的是**可运行的 `THREE.Group` TypeScript 工厂函数**（由 primitive + 程序化 shader + 生成几何构成），带 pivot/socket/collider 运行时层级，直接可动画——不是 photogrammetry、不是 mesh 抽取、不是下载素材包。
- **质量门 + AI 自纠循环**：分阶段 `blockout → structural → form → material → surface → lighting → interaction → optimization`，每阶段渲染与参考图**对照打分**，身份特征不过阈值的 pass 一律判 fail；`--strict-quality` 在生成一行代码前就挡住浅规格。
- **刻意 token 高效**：所有机械活（校验/规格撰写/PBR 抽取/比对表打包/状态机）都压进**确定性纯标准库 Python 脚本**（无 pip、无 PIL、无 numpy、PNG 用 `struct`+`zlib` 读写），模型 token 只花在「看一张对照表、判过/不过」上。
- **Agent 无关 + 可恢复**：Claude Code / Codex / OpenCode / Hermes 皆可；`forge/state.py` 把 intake/pass 清单物化为 `.img2threejs/state.json`，`forge/next.py` 从清单续跑，规格/渲染/评审门始终是权威。
- **强诚实边界**：明确声明「单图无法揭示背面、不保证几何」，未见区域标 low-confidence 而非编造；提供 per-region 置信度，必要时主动要更多视角。

## 项目定位（一句话）

img2threejs 是一个**把参考图重建成「代码化、质量门控、动画就绪」的 Three.js 模型**的 Agent Skill——它做的是「用代码重建物体」，刻意放弃网格保真以换取可编辑、可差分、token 高效与可动画的产物。

> 版本 **v2.0.0**（The Plugin Update）；**19.8k⭐**（第三方测 19.3k、日增约 +144★ 且加速），Apache-2.0，Python+TypeScript，**最近推送 2026-10-28 活跃**。

## 核心架构

- **入口 `SKILL.md`**：始终加载的「路由器」，只持操作顺序与硬规则一行化；每条规则指向 `grimoire/` 或 `docs/` 里对应的契约文件（用到才读）。
- **`forge/` 约 90 个标准库模块**，按阶段分：
  - `stage1_intake/`：图像探针、detail inventory、landmark、camera pose、delight albedo；
  - `stage2_spec/`：分类+复杂度评估、`ObjectSculptSpec` 撰写与校验（`--strict-quality` 挡浅规格）；
  - `stage3_build/`：`generate_threejs_factory.py` 只发当前解锁的 pass；
  - `stage4_review/`：材质视图、`material_comparator`、对照表、`*_gate` 阻断门；
  - `stage5_rig/`（角色）：从组件树派生骨骼、测地蒙皮、payload 完整性门。
- **`grimoire/`**：每个门引用的 rubric（校验/预规格/程序化图案/材质光照真实感/绑定正确/自纠）。
- **产物**：`ObjectSculptSpec` JSON（完整组件树+材质+重复系统+socket+评审史）+ `createObjectNameModel(spec)` 工厂返回 `THREE.Group`，`root.userData.sculptRuntime` 暴露节点/socket/collider/`destruction groups`；角色构建额外带 `root.userData.rig`。
- **插件生态（v2.0）**：`img2` harness 管理 `character` / `cs2` / `environment` / `hello-cube` / `img2glb` 等插件，每个贡献 checklist、质量下限（raise-only）与阻断评审门；base 自带 `generic`+`character`，缺插件**显式报错不静默降级**。

## 源码深度解读（核心模块：状态门 + fail-closed 工厂）

**1. 本地状态门是流程权威（`SKILL.md`「Mandatory Local State Gate」）**

```bash
python3 forge/state.py init --state .img2threejs/state.json \
    --reference <img> --profile <generic|character|installed-domain> --spec object-sculpt-spec.json
python3 forge/next.py --state .img2threejs/state.json [object-sculpt-spec.json]
python3 forge/state.py mark <step-id> --state .img2threejs/state.json --evidence <path>
```

`next.py` 打印当前 step/pass、未完成必做项、精确下一条命令与 `loop/max`；**退出码 3 或 `status=stopped` 是硬停止**——必须从状态机续跑，绝不凭聊天记忆重建进度。这是把「软流程」固化成可机器检查不变量的典型做法。

**2. 工厂生成 fail-closed（`README` 描述的 `generate_threejs_factory.py` 契约）**

> The factory generator repeats the strict-quality gate and is fail-closed: on failure it returns `BLOCKED` with the spec artifact, failure metrics, causes, and next action, and **does not write a factory**. `--allow-nonstrict` is only for explicit legacy test fixtures, never production output.

即：严格质量门不过 → 返回 `BLOCKED`（带规格、失败指标、原因、下一步）且**绝不写出工厂文件**。`--allow-nonstrict` 仅限遗留测试夹具，永不用于生产。这条「先门后码、失败即停」是 token 高效的根——绝不为欠规格的几何浪费渲染 token。

## 应用场景与启发

- **Web 演示 / 低多边形游戏 / 电商产品可交互 3D**：输出是代码，可改参数、加动画逻辑、直接塞进 Three.js / React Three Fiber 场景，且体积远小于贴图网格——适合「要快、要可迭代、要小」的场景。
- **「脚本做苦力、模型做判断」的 token 工程范式**：把所有可确定化的校验/比对/状态推给纯标准库脚本，把昂贵模型上下文留给「看一张对照表判 pass/fail」。任何 agent 长循环都应学这套节流设计。
- **可恢复 + 强门控的工作流**：`state.json` 物化进度 + 硬停止 + 失败即停，避免 agent 「凭记忆续做」导致的状态漂移——可迁移到任何多 pass 生成任务。
- **诚实边界设计**：主动声明能力上限与置信度、不编造隐藏面，是「AI 生成内容需可信/可复核」场景的范本。

## 社区口碑

- **增长强劲**：约 **19.3k–19.8k⭐**，日增 ~+144★、趋势加速；v1.4→v1.5→**v2.0** 迭代快（武器/角色/材质/插件生态），Apache-2.0，有 MiniMax / Atlas Cloud / Tripo / Hyper3D 赞助（compute 赞助，非覆盖性）。
- **实测褒贬分明（ai-bot.cn 真人 5 例：电钻/茶壶/风扇/背包/香水瓶）**：部件层级（夹头、电池、壶嘴、拉链、喷头）普遍完整、一眼可辨同类；**但大轮廓/比例常偏**（机身偏长方、手柄过直、连接处缺连续曲面），表面近似而非保真。
- **共识评价**：代码化、可差分、可编辑、动画就绪、token 高效、质量门是差异化优点；**短板是「非照片级、丢表面细节」**——硬表面物体最佳，角色是风格化重建而非写实；质量门「防垃圾被标 final」但不保证 final 一定高质量，且门槛标准对 agent 不透明。
- **采用前提**：依赖宿主 agent 具备图像读取/预览（或人工截图）才能推进评审循环；缺浏览器/图像输入时需手动补截图，增加摩擦。
- **主观满意度数据不可用**：精确 NPS 无第三方统计；上述基于公开实测与 README 自述。

## 竞品对比

| 维度 | img2threejs | Tripo3D / Hyper3D（网格生成） | Meshroom（摄影测量） | 手工 Blender |
|------|-------------|------------------------------|---------------------|--------------|
| 产物 | 可运行 TS 代码 + JSON 规格 | 文本化网格（GLB/OBJ，2M 面） | 照片重建网格 | 手模网格 |
| 可编辑/动画就绪 | 强（pivot/socket 内建） | 需额外绑定 | 静态、需再绑定 | 完全可控 |
| 表面保真 | 弱（刻意放弃） | 强 | 强 | 强 |
| token/成本 | 刻意高效（脚本做苦力） | API 按次 | 算力重 | 人力重、慢 |
| 依赖 | agent 需有视觉 | 云端 API | 多图+算力 | 专业技能 |

## 核心研判

- **价值清晰**：在「要代码化、可编辑、可动画、小体积」的 Web 3D 场景里几乎没有对等物；其 token 工程与 fail-closed 工作流是 agent 长循环设计的优质范本。
- **边界明确**：**不是 3D 艺术家替代品**，也不适合「要照片级/物理精确几何」的需求（产品配置器、精确比例场景慎用）。单图天然看不到背面，靠镜像可见面+标 low-confidence 处理，不编造。
- **采用建议**：做 Web 演示 / 电商可交互模型 / 低多边形游戏资产时优先试；生产前到 `img2threejs.io` 画廊看真实生成代码、避开标 `placeholder` 的未完成 demo；确识宿主 agent 有图像/预览能力再引入。

## 关键文件路径速查

- `SKILL.md` — 始终加载的路由器（操作顺序 + 硬规则一行化）
- `forge/state.py` · `forge/next.py` — 本地状态门（进度权威、硬停止、续跑）
- `forge/stage2_spec/validate_sculpt_spec.py` — `--strict-quality` 规格门（生成前挡浅规格）
- `forge/stage3_build/generate_threejs_factory.py` — fail-closed 工厂生成（BLOCKED 不写文件）
- `forge/stage4_review/{material_comparator,make_comparison_sheet,material_gate}.py` — 对照表/门控
- `forge/_shared/{chirality,pipeline_routing,feature_acceptance_policy}.py` — 手性/路由/fail-closed 辅助
- `grimoire/` — 各门引用的 rubric（校验/材质/绑定/自纠）
- `ROADMAP.md` · `CHANGELOG.md` — 版本路线（v2.1 角色拆分 → v3.0 程序化世界）
