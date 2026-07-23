# 📡 ruvnet/RuView — 用 WiFi 信号"看见"墙后的世界（无摄像头的空间智能）

> **仓库地址**: https://github.com/ruvnet/RuView  
> **Stars**: 85,030 | **语言**: Rust / Python / C / TypeScript | **许可证**: MIT  
> **组织**: ruvnet（Cognitum）  
> **抓取日期**: 2026-07-24（GitHub Trending 当日上榜）

---

## 一、项目定位（一句话）

RuView 是一个**基于 WiFi CSI（信道状态信息）的无摄像头空间感知平台**：用廉价 ESP32 节点读取人体扰动无线电波的反射，实时推断出"谁在房间里、在做什么、呼吸/心率多少、是否跌倒"——穿透墙壁、黑暗、无需任何摄像头或可穿戴设备。

---

## 二、项目亮点（差异化）

1. **隐私优先的"穿透感知"** — 核心卖点是"See through walls with WiFi"：完全靠无线电物理信号，零像素、零摄像头，天然规避隐私/合规雷区（与摄像头方案形成根本差异）。
2. **9 美元硬件跑通** — ESP32-S3/C6 CSI 节点单价约 $9，Cognitum Seed 边缘协处理器约 $140 整机 BOM，把传统需要雷达/深度相机才能做的感知压到消费级成本。
3. **端侧脉冲神经网络（SNN）** — 模型在本地 30 秒内自适应学习环境，预训练权重 4-bit 量化后仅 8KB，在树莓派上微秒级推理，无云、无联网。
4. **密码学可证明的可信感知** — 每次测量都经 **Ed25519 witness chain** 签名见证，解决"传感数据能否被信任"这一 IoT 老大难问题。
5. **105 个开箱即用的"边缘模块"（Cog）** — 从 `app-registry.json` 动态加载的健康/安防/建筑/零售/工业/研究等模块目录，外加 Home Assistant / Apple Home / Google Home / Alexa / Matter 主流智能家居全桥接（每节点暴露 21 个实体）。

---

## 三、核心架构

整体是"**硬件采集 → 边缘推理 → 可信见证 → 平台集成**"四层流水线：

```
ESP32 CSI 节点 ($9)
   │  6 频段信道跳变 + TDM 时隙调度（邻居路由器当免费雷达照明源）
   ▼
CSI 处理 (core/csi_processor.py：相位净化 → 包裹相位 → 循环方差)
   │
   ▼
Spiking NN 本地学习 (<30s) + 预训练 8KB 量化模型（HuggingFace: wifi-densepose-pretrained）
   │  ├─ 呼吸/心率（带通滤波 + 过零 BPM）
   │  ├─ 存在检测（82.3% 时序三元组精度 head + 相位方差兜底）
   │  ├─ 17 关键点姿态（Cog: pose_v1.safetensors，Candle 加载）
   │  └─ OccWorld 世界模型（TransVQVAE，15 帧未来占用预测）
   ▼
Ed25519 Witness Chain 签名见证
   │
   ▼
FastAPI 后端 (archive/v1/src/api：pose/stream/auth/health 路由 + WebSocket)
   │  + 3D 点云融合（MiDaS 相机深度 + WiFi CSI + mmWave 雷达）
   ▼
智能生态桥接（HA --mqtt / Matter / Apple-Home / Alexa）
```

**关键技术选择**：
- **Rust crate `wifi-densepose-ruvector`**（已上 crates.io）：128 维对比学习 CSI 编码器，4-bit 量化版仅 8KB，M4 Pro 上 **164,183 emb/s**。
- **多频 Mesh 扫描**：跨 6 个 WiFi 信道跳变，用邻居路由器信号当"免费雷达照明源"，感知带宽 ×3。
- **3D 点云融合**：MiDaS 深度 + CSI + mmWave，22ms 流水线、19K+ 点/帧，把异质传感统一成空间模型。

---

## 四、应用场景与启发

- **适老化 / 独居监护**：跌倒检测 <200ms、呼吸/心率非接触监测、长时间无活动异常告警——比摄像头方案更易被老人接受（无监视感）。
- **智能家居存在感知**："某人在睡觉/浴室占用/会议进行中"等语义状态直接进 HA 自动化，比 PIR 人体传感器信息量大一个量级。
- **零售/工业计数**：专门的 learned counter Cog（occupancy-zones / queue-length / customer-flow），实时自校准。
- **给 AI/IoT 构建者的启发**：
  1. **CSI 是一种全新的传感器模态**——当你的项目需要"存在/动作/生命体征"但装不了摄像头时，这是现成方案。
  2. **可信感知的范本**：Ed25519 witness chain 把"数据可信"做成默认能力，值得任何传感/IoT 项目借鉴。
  3. **诚实的度量是信任资产**：RuView 主动撤回了早期"100% 存在检测"的夸大数字，改为诚实的 82.3% 留出基准——这种"自纠"文化在 AI 硬件项目里极少见，反而是它最值钱的工程信号。

---

## 五、源码深度解读

### 5.1 CSI 处理内核（`archive/v1/src/core/csi_processor.py`）
放射信号进入后的第一道工程化处理：相位净化（phase_sanitizer）→ 包裹相位解卷 → 循环方差计算。这是后续一切生命体征提取的物理基础，决定了 BPM 估计的稳健性。

### 5.2 推理服务（`archive/v1/src/api/routers/pose.py` + `stream.py`）
FastAPI 把姿态/流数据通过 REST + WebSocket 双通道暴露；`websocket/pose_stream.py` 的 connection_manager 负责多客户端并发推送，是上层桥接（HA/Matter）取数的统一入口。

### 5.3 本地校准与学习（`aether-arena/calibration/model.py` / `infer.py` / `cog_calibrate.py`）
SNN 自适应学习的核心：30 秒内用环境样本微调，把通用预训练模型校准到具体房间。配合 `aether-arena/ledger/ledger_tools.py` 做不可篡改的记录。

> 注：仓库顶层大量 `.claude/`、`.claude-flow/` 是 Agent 协作脚手架（agent 定义、metrics、horizons），非运行时代码；真实源码在 `archive/`、`aether-arena/`、`firmware/` 三处。

---

## 六、全网口碑

- **增长极快**：85K⭐ 在登上 Trending 后短期内冲到高位，是当日 Trending 头部项目，说明"无摄像头穿墙感知"叙事击中了强需求。
- **工程可信度信号强**：1463 个测试通过、crates.io 正式发布、多架构 Docker、HuggingFace 公开权重、并**主动撤回夸大指标**——这些在"vibe-coded 爆款"里相当罕见，社区口碑偏正面。
- **需警惕的噪音**：星标增速与项目实际成熟度存在落差（核心仍是研究型原型 + 大量 Agent 脚手架），"85K⭐"含一定 Trending 流量水分，落地仍需具体硬件与调参。

---

## 七、竞品对比 + 核心研判

### 竞品对比
| 维度 | RuView | mmWave 雷达(TI IWR) | 微软 Soundwave(研究) | 摄像头方案(Nest/HomePod) | 商用量身感知(Origin Wireless) |
|------|:------:|:-------------------:|:--------------------:|:------------------------:|:----------------------------:|
| 硬件成本 | ~$9 ESP32 | 中高 | 研究 | 高 | 高 |
| 摄像头/隐私 | ✅ 无像素 | ✅ 无 | ✅ 无 | ❌ 有 | ✅ 无 |
| 穿墙能力 | ✅ ~5m | ⚠️ 有限 | ✅ | ❌ | ✅ |
| 端侧推理 | ✅ SNN 8KB | ⚠️ 部分 | ❌ 云 | ❌ 云 | 厂商黑盒 |
| 可信 attestation | ✅ Ed25519 | ❌ | ❌ | ❌ | ❌ |
| 开源程度 | ✅ MIT | ❌ | ❌ | ❌ | ❌ |
| 智能家居集成 | ✅ HA/Matter/Apple/Alexa | ❌ | ❌ | ✅ | 部分 |

### 核心研判
- **优势**：隐私原生 + 极致低成本 + 端侧可信感知 + 主流生态全桥接，叙事与工程完整性在同类里罕见。
- **风险**：CSI 对环境（多径、家具变动）高度敏感，实际精度依赖调参；85K⭐ 含 Trending 流量水分，成熟度为研究原型级；"穿墙感知"在部分地区触及监控/法律的灰色地带，部署需合规评估。
- **趋势**："无摄像头感知"正从论文走向消费级（Apple/Google 也在做存在感知），Matter 标准化让这类设备能无缝进智能家居；端侧 SNN 是边缘 AI 的明确方向。
- **启发**：把 RuView 当作"传感即代码"的范本——当你需要存在/动作/生命体征数据又不想上摄像头时，CSI 是现成路径；其 witness chain + 诚实基准的做法，值得任何"AI 给出关键判断"的项目抄作业。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `archive/v1/src/core/csi_processor.py` | CSI 相位净化与特征提取内核 |
| `archive/v1/src/api/routers/pose.py` | 姿态 REST 接口 |
| `archive/v1/src/api/websocket/pose_stream.py` | 姿态 WebSocket 推送 |
| `aether-arena/calibration/model.py` / `infer.py` | SNN 本地校准与推理 |
| `app-registry.json` | 105 个边缘 Cog 模块目录 |
| `firmware/esp32-csi-node/` | ESP32-S3/C6 CSI 固件与烧录 |
| crates.io `wifi-densepose-ruvector` | Rust CSI 编码器核心库 |
