# pollen-robotics/microduck 深度调研

> 调研日期：2026-10-25 ｜ Stars：10,847 ｜ 语言：Rust ｜ 许可：Apache-2.0 ｜ 创建：2026-07-29 ｜ 默认分支：main ｜ 定位：开源双足小鸭机器人的「大脑」（控制软件）

## 一、项目定位（一句话）

Pollen Robotics 开源的**双足小鸭机器人控制软件**——25cm / 800g 机器人上跑一组 Rust 守护进程，以 50Hz 控制环驱动 15 个舵机执行强化学习步态策略；「本仓库是鸭子的脑子」，策略在隔壁 `microduck_rl` 训练。

## 二、项目亮点（差异化，开篇呈现）

1. **把「为什么」写进代码库的架构文档**：`docs/design/architecture.md` 等设计文档罕见地记录了每一项技术取舍（为何用 Unix socket 而非 HTTP、为何 JSON-RPC 而非 D-Bus、依赖数对比表），是嵌入式 agent 可靠性工程的范本。
2. **单一 JSON-RPC 契约，所有客户端发同样的调用**：app / 控制台 / 手柄 / 脚本 / 远端都走同一套 `duck-ipc-proto` 类型与操作，跨 BLE / Unix socket / WebRTC 多传输只是薄适配层。
3. **恢复路径与故障隔离优先**：`robotd` 死了，`configd` / `updaterd` / `btd` 仍能工作（无 systemd 依赖、无 ML 运行时、无媒体栈）——这正是「机器人坏了才需要重配/回滚」的场景。
4. **签名发布 + 健康检查门 + 自动回滚**：更新是整目录原子替换而非打补丁，`updaterd` 验签→换 `current` 软链→重启→问 `robot.health`，不健康就自动回退。
5. **RL 与运行时解耦**：步态策略在 `microduck_rl`（MuJoCo + PPO）训练并导成 ONNX，本仓只加载，权重存 Hugging Face Hub（v8），「重训步态不必发 daemon 版本」。

## 三、核心架构（克制代码量）

`Cargo.toml` 是 26 crate 的单一 workspace（`resolver = "3"`），**一个服务一个 crate**，与架构文档 §1 的服务切分一一对应：

```
btd · configd · duck-ble · duck-control · duck-detect · duck-ipc-proto · duckctl
kinematics · mediad · netpadd · nfc · odometry · pad-imu · pad-map · padd
pet-detect · sounds · tof · updater · robotctl · robotd · robotd-params
test-support · uyvy · xtask
```

七个常驻守护进程职责（摘自 architecture.md）：

| 服务 | 拥有 | 监听 |
|---|---|---|
| `robotd` | 电机控制 / 运动学 / 里程计 / 步态策略 / 安全（`robot.*`，50Hz 环） | `/run/robotd.sock` |
| `configd` | wifi / 机器人身份 / 配对 PIN / 重启 | `/run/configd.sock` |
| `updaterd` | 发布：验签 / 安装 / 换链 / 健康门 / 回滚 | `/run/updaterd.sock` |
| `mediad` | 相机/麦 + 编码 + 感知 + WebRTC 远控门 | TCP :8080 / :8443 |
| `btd` / `padd` / `tofd` | 无状态传输 / 手柄 / ToF 深度传感 | 各自 socket |

**控制面 vs 数据面分离**是核心不变量：命令走 Unix socket 上的 JSON-RPC 2.0（NDJSON，一行一对象，`tokio_util::codec::LinesCodec` + `serde`），视频/音频帧**绝不过 socket**——`robotd` 只订阅 `mediad` 推导出的「球在 (x,y)」这类特征（last-value-wins 缓存），感知贴近传感器而非跨进程传帧。

## 四、应用场景与启发（重点）

- **「让 agent 碰真实物理世界」的可靠性工程样板**：签名更新、自动回滚、死人开关（deadman/heartbeat）、「意图而非电机写入」（客户端发速度/凝视目标，`robotd` 权威决定可执行性）这套设计，对任何做具身/机器人 agent 的团队都是可直接借鉴的安全基线。
- **配置即状态、单写者原则**：每个值恰好一个拥有服务，他人只读或订阅；wifi 凭据交给 NetworkManager 而非自己存——「少写代码、边界更清、更安全」的取舍哲学值得在任意多进程系统复用。
- **对用户的借鉴**：用户做错题归因等「搜索空间内归因」研究偏算法，但 microduck 展示的「策略与运行时解耦 + 模型权重外置 Hub + 原子更新回滚」同样是任何长周期在线系统的工程必修课。

## 五、源码深度解读（2 个核心模块）

**1. `Cargo.toml` —— 版本 pin 即「单一事实源」**

```toml
[workspace.metadata.onnxruntime]
floor  = "1.23"      # ort 低于此会 panic
target = "1.28.0"
[workspace.metadata.policies]
repo    = "pollen-robotics/microduck-policies"
version = "v8"        # 官方策略集存 HF Hub，daemon 只加载
[workspace.metadata.rknpu]
runtime = "v2.3.2"   # Rockchip NPU 运行时，模型转换产出须 ≤ 此
```

注释反复强调「脚本里带字面量、仓库里带 pin，测试断言两者一致」——用一次声明 + 测试守门，杜绝「板子上的 ONNX Runtime 和 ort 依赖漂移导致 panic」这类真实事故。

**2. `robotd` 安全权威（架构文档 §6）**

> 远程客户端发 velocity / gaze target / "sit"——**绝不发原始关节指令**。`robotd` 对防跌检测、关节/热保护、安全姿态保持权威。混乱的 agent 不能命令机器人撞墙。

配合 `configd/src/store.rs`（文件 + `flock` + `rename(2)` 原子写）、`robotd/src/vetbook.rs`（机器人终身记录），把「配置可读当 robotd 死时」「状态单写者」两条不变量落到代码。

## 六、全网口碑

Pollen Robotics（Reachy 双臂机器人背后的团队）出品，硬件开源 + 文档质量在机器人项目里属第一梯队；机器人爱好者与 RL 研究者口碑好。README 诚实标注「no duck was harmed」，并把「哪些决策经过权衡、哪些 open question 未决」写进 `docs/project/`。属年轻但工程成熟度高的实物项目。

## 七、竞品对比 + 核心研判

| 维度 | microduck | Unitree Go / CyberDog（四足） | 桌面级教育机器人 |
|---|---|---|---|
| 定位 | 桌面级开源「可修可更新」软件平台 | 高性能四足硬件 | 教学套件 |
| 软件工程重点 | 签名更新 / 回滚 / 故障隔离 | 运动性能 | 易上手 |
| 策略来源 | MuJoCo+PPO→ONNX，Hub 外置 | 厂商闭源/半开源 | 预设 |
| 开放度 | 大脑全开源 + 设计文档 | 部分 | 视厂商 |

**核心研判**：microduck 的价值不在「跑得最快」，而在把**物理世界 agent 的可靠性工程**（更新安全、失败可恢复、权限仲裁、感知就近）做成可学习的开源样本。适合：① 做具身/机器人 agent 的团队参考其架构与文档范式；② 教育者/爱好者作为低成本双足平台。对个人纯算法研究者直接复用价值有限，但其「策略外置 + 原子更新」的工程纪律可迁移到任意在线系统。Apache-2.0，可商用可改。

## 八、关键文件路径速查

- 架构正本：`docs/design/architecture.md` · `docs/design/updater-design.md` · `docs/design/robotd-design.md`
- workspace 定义：`Cargo.toml`（26 crate members + `[workspace.metadata.*]` pin）
- 控制环/安全：`robotd/`（src/vetbook.rs）｜ 配置存储：`configd/src/store.rs`
- IPC 契约：`duck-ipc-proto/src/`（led.rs 等共享类型）
- 更新引擎：`updater/`（验签 / 健康门 / 回滚）
- 策略训练（独立仓）：`pollen-robotics/microduck_rl`（MuJoCo + PPO + ONNX 导出）
- 官方页：pollen-robotics.com/microduck
