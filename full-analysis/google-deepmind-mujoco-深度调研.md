# google-deepmind/mujoco 深度调研

> 调研日期：2026-11-11 ｜ 编号：#582 ｜ Stars：⭐ 17,274（抓取日）｜ 语言：C（运行时）+ Python 绑定 ｜ License：Apache-2.0
> GitHub：https://github.com/google-deepmind/mujoco ｜ 文档：https://mujoco.readthedocs.io ｜ 官网：https://mujoco.org

## 一、项目定位（一句话）

由 **Google DeepMind** 维护的通用物理引擎（**Mu**lti-**Jo**int dynamics with **Co**ntact）：面向机器人、生物力学、图形动画与机器学习，追求「快速且精确的铰接结构 + 环境交互仿真」；用 ANSI C 写就、手工优化、数据预分配，专为**基于模型的优化（尤其经接触优化）**从零设计。

## 二、项目亮点（差异化，开篇呈现）

1. **广义坐标 + 解析接触**：在最小化坐标下仿真以杜绝关节违例；接触用**凸优化统一公式**（软接触 / 限位 / 干摩擦 / 等式约束一网打尽），摩擦锥可选金字塔或椭圆、雅可比为稠密或稀疏——逆动力学在接触下仍良定义。
2. **引擎内核分层极清晰**：`smooth dynamics`（正向运动学 → 复合刚体惯性 CRB → L'DL' 分解 → 递归牛顿欧拉 RNE）→ `constraint solver`（PGS / NoSlip / CG / Newton，且支持**分岛 island 并行**）→ `collision`（GJK / 凸 / 盒 / SDF / 连续 / 柔体），模块边界明确。
3. **分析微分 MJD（核心杀手锏）**：`engine_derivative` 的 `mjd_*` 给出平滑力对速度的**解析导数**，使 **MJX（JAX 分支）的可微物理**能用物理 step 的解析梯度直接训练 locomotion 策略——这是 MuJoCo 在「可微仿真」上不可替代的根基。
4. **MJCF + 内置编译器**：直观的 XML 模型格式（MJCF），编译器在加载期**预分配**出 `mjModel`（静态）/ `mjData`（每步状态），支持 URDF 导入；可读模型是 RL 社区事实标准。
5. **多后端绑定矩阵**：官方 Python（`dm_control` / PyMJCF）、WASM/JS、Unity/C#；社区 MATLAB/Swift/Java/Julia/Rust；MJX 还能跑在 GPU/TPU 上，3.3.5 起加 MJX-Warp 针对 NVIDIA GPU 优化。

## 三、核心架构（克制代码量）

**两大核心数据结构**（贯穿所有 engine 函数）：

- `mjModel`：静态模型，由 XML 编译器一次性预分配——几何体、关节、约束、 actuator、材质等全在其中，仿真期只读。
- `mjData`：每步可变状态——`qpos`/`qvel`/`qacc`、雅可比、约束力、传感器输出等，仿真期读写。

**仿真一步 `mj_step` 的管线**（`src/engine/`）：

```
engine_core_smooth  →  正向运动学(mj_kinematics1/2) + CoM(mj_comPos) + 复合刚体惯性(mj_crb)
                     + 惯性矩阵装配/分解(mj_makeM/mj_factorM) + 递归牛顿欧拉(mj_rne) + 速度项(mj_comVel)
engine_collision_*  →  宽相→窄相：GJK / 凸 / 盒 / 原始体 / SDF / 连续 / 柔体 接触对生成
engine_core_constraint + engine_solver → 软接触约束求解（PGS/NoSlip/CG/Newton，分岛并行 + mj_dualFinish）
engine_derivative  →  解析雅可比/导数（mjd_*），供 MJX 可微与灵敏度分析
xml/               →  MJCF/URDF 解析 → 预分配 mjModel/mjData
```

**设计哲学**：运行时模块为性能极致手工优化、操作预分配的低层数据结构；上层 Python/JS 绑定只做薄封装。可视化有原生桌面（OpenGL）与浏览器（WASM）两套。

## 四、应用场景与启发

- **最适合**：接触丰富的机器人控制基线（四足/人形步态、操作）、基于模型的优化（最优控制、状态估计、系统辨识、机构设计）、生物力学与动画、以及 RL 的训练环境（经典 MuJoCo 或 MJX GPU 版）。
- **启发 1（最小化坐标 + 解析雅可比 = 可微物理基石）**：MuJoCo 不靠有限差分求梯度，而是直接提供 `mjd_*` 解析导数——把「物理」本身变成可微层，这正是 MJX 能用 JAX 端到端训练策略的关键。任何「仿真即可微」的需求都应学这套。
- **启发 2（数据预分配 + 单帧状态）**：`mjModel` 静态、`mjData` 单步，仿真循环无任何运行时分配——这是高吞吐 RL 采样（尤其多线程 `rollout`）能跑满 CPU 的工程前提。
- **启发 3（统一凸优化接触模型）**：把软接触/限位/摩擦/等式约束收进一个连续时间凸公式，比「分而治之的 penalty/impulse 法」更易做优化与灵敏度分析。

## 五、源码深度解读

### 1. 平滑动力学管线 — `src/engine/engine_core_smooth.h`

头文件把「一步动力学」拆成可独立调用的纯函数，职责边界一目了然（节选声明）：

```c
// 正向运动学：刚体位姿
void mj_kinematics(const mjModel* m, mjData* d);
void mj_kinematics1(const mjModel* m, mjData* d);   // 阶段1：bodies
void mj_kinematics2(const mjModel* m, mjData* d);   // 阶段2：惯性/geom/site

// 复合刚体惯性 (CRB) 与惯性矩阵
void mj_crb(const mjModel* m, mjData* d);            // composite rigid body inertia
void mj_makeM(const mjModel* m, mjData* d);         // 装配 M
void mj_factorM(const mjModel* m, mjData* d);       // 稀疏 L'*D*L 分解 (spd)

// 递归牛顿欧拉 (RNE): M(qpos)*qacc + C(qpos,qvel)
void mj_rne(const mjModel* m, mjData* d, int flg_acc, mjtNum* result);
void mj_comVel(const mjModel* m, mjData* d);        // cvel, cdof_dot
```

`mj_crb` + `mj_factorM` 用复合刚体算法算稀疏惯性矩阵并做 L'DL' 分解，`mj_rne` 是经典递归牛顿欧拉（可去掉惯性项算偏置力）——这就是「快速精确」的来源。

### 2. 解析微分 — `src/engine/engine_derivative.h`

`MJD`（Minimal Coordinates + Analytical Derivative）核心。下列声明展示了「平滑力对速度的解析导数」如何被模块化地累加（节选）：

```c
// 平滑力对速度的解析导数: d->qDeriv = d(qfrc_actuator+qfrc_passive-[qfrc_bias])/d qvel
void mjd_smooth_vel(const mjModel* m, mjData* d, int flg_bias);
void mjd_actuator_vel(const mjModel* m, mjData* d);   // + d qfrc_actuator / d qvel
void mjd_passive_vel(const mjModel* m, mjData* d);    // + d qfrc_passive  / d qvel
void mjd_rne_vel_dense(const mjModel* m, mjData* d);  // - d qfrc_bias     / d qvel

// 自由关节刚子树的 6x6 块: A = M - h*(d qfrc_smooth/d qvel)
int  mjd_freeMhat(const mjModel* m, const mjData* d, int jnt, mjtNum h, mjtNum A[36], int flg_discrete);
// 柔体(flex)隐式刚度装配到 dof 级 CSR
void mjd_flexBend_mul(...);  void mjd_flexStretch_mul(...);
```

这些函数把动力学对状态的解析雅可比显式算出，MJX 据此用自动微分外的「解析梯度」做反向传播训练——比纯数值差分稳且快。

### 3. 约束求解器 — `src/engine/engine_solver.h`

软接触用「单体求解器」+「分岛求解器」双套接口，分岛是为了并行（节选）：

```c
// 单体求解器
void mj_solPGS(const mjModel* m, mjData* d, int maxiter);      // 投影高斯赛德尔
void mj_solNoSlip(const mjModel* m, mjData* d, int maxiter);   // 改进 PGS (无滑移)
void mj_solCG(const mjModel* m, mjData* d, int maxiter);       // 共轭梯度
void mj_solNewton(const mjModel* m, mjData* d, int maxiter);   // 牛顿
// 分岛求解器（一个 island，dualFinish 由调用方处理）
void mj_solPGS_island(const mjModel* m, mjData* d, int island, int maxiter);
void mj_solCG_island(...);  void mj_solNewton_island(...);
void mj_dualFinish(const mjModel* m, mjData* d);   // 把 efc_force 映射回关节空间
```

`island` 分解把互不接触的约束簇分到独立岛并行求解，再 `mj_dualFinish` 汇回——是 MuJoCo 在大规模多接触场景保持实时性的关键。

## 六、全网口碑

- **地位**：接触力学研究的**事实金标准**，被 DeepMind/OpenAI 等 RL 基准、dm_control、众多 humanoid 基准广泛采用；小体积、易上手、可复现性好，研究基线「先把想法跑起来」首选。
- **优势共识**：接触精度与数值稳定性业界最高之一；广义坐标天然规避关节违例；MJCF 可读性远胜 URDF；确定性好，适合做算法 ablation。
- **短板共识（多方评测一致）**：
  - **经典 MuJoCo 仅 CPU**；MJX 补了 GPU/TPU 路线但仍在成熟中（MJX-Warp 自 3.3.5 起优化 NVIDIA GPU）。
  - **视觉/传感器仿真弱于 Isaac Sim**：RTX 级相机/LiDAR/接触/IMU 传感器不如 Isaac，做 VLA/合成数据偏向 Isaac。
  - **Sim2real 理想化假设**：完美齿轮、瞬时位置控制（MoCap）、简化弹簧接触、线性摩擦锥——**不含 stick-slip / Stribeck**、无关节回差/柔顺。实测策略在摩擦/质量微扰下成功率掉 **30–50%**，组合扰动 >75%。
- **License 澄清**：运行时为 **Apache-2.0**（部分对比表误写 MIT）；文档与图片为 CC BY 4.0。官方标注 *"not an officially supported Google product"*。

## 七、竞品对比 + 核心研判

| 仿真器 | 物理后端 | GPU 并行 | 接触模型 | License | 强项 / 弱项 |
|--------|---------|---------|---------|---------|------------|
| **MuJoCo** | 原生 MuJoCo | 经 MJX（JAX/Warp） | 软接触、弹簧-阻尼 | Apache-2.0 | 接触精度高、信任度高、足迹小；**经典仅 CPU**、传感器弱 |
| Isaac Lab / Sim | PhysX / Newton | 原生 GPU resident | PhysX 半隐式 | 免费(科研) | GPU 大规模并行 RL、RTX 传感器、系统化工作流；安装/依赖重 |
| PyBullet | Bullet | 仅 CPU(Python) | LCP/impulse | zlib | 易装、原型快；规模慢、渲染有限 |
| Gazebo | ODE/DART/Bullet | 无 | penalty | Apache-2.0 | ROS 集成、多机器人；物理偏慢 |
| Drake | 自有 | 无(用户态) | 自有 | BSD | 动力学正确性、符号推理、控制研究；RL 社区小、学习曲线陡 |
| Genesis | 自研(Taichi) | 原生 | 自研 | — | 新秀、吞吐高、纯 Python；资产库小 |

**核心研判**：
- ✅ **接触机制首选 + 研究基线信任度最高 + 可复现性强**：做接触丰富的控制/优化、需要把「物理变可微层」做 MJX 训练时，MuJoCo 仍是最稳的起点。
- ⚠️ **大规模 GPU 并行 RL 与 photoreal 传感器转向 Isaac Lab**：若目标是千级并行环境或 VLA/合成数据，Isaac 更自然；MuJoCo 适合「先把模型与策略基线跑对」。
- 📌 **Sim2real 始终是第一性约束**：无论选谁，都要从硬件短实验回标参数 + domain randomization；MuJoCo 的理想化接触模型尤需警惕「仿真里三倍真机速度」的自负。

## 八、关键文件路径速查

```
src/engine/engine_core_smooth.{c,h}     平滑动力学：运动学/CRB/factorM/RNE
src/engine/engine_core_constraint.{c,h}  约束装配
src/engine/engine_solver.{c,h}           软接触求解：PGS/NoSlip/CG/Newton + 分岛
src/engine/engine_derivative.{c,h}       MJD 解析微分 (mjd_*) —— 可微物理根基
src/engine/engine_collision_*.{c,h}      GJK / 凸 / 盒 / 原始体 / SDF / 连续 / 柔体 接触
src/engine/engine_inverse.{c,h}          逆动力学
src/engine/engine_forward.{c,h}          正向动力学推进
src/xml/xml.{cc,h}                       MJCF 编译器（预分配 mjModel/mjData）
src/xml/xml_urdf.{cc,h}                  URDF → MJCF 导入
src/xml/generated/mjcf.schema            MJCF schema
include/mujoco/{mjmodel,mjdata,mjtype}.h 核心数据结构定义
python/                                 dm_control / PyMJCF / tutorial.ipynb
mjx/                                    MuJoCo XLA（JAX 分支，可微 + GPU/TPU）
simulate / studio                       经典查看器 / MuJoCo Studio（原生 + WASM）
```
