# schollz/find3 深度调研

> 调研日期：2026-09-29 ｜ 数据源：gh API（README / 目录树）｜ 定位：高精度室内定位框架（v3 / FIND）

## 一、项目定位（一句话）

**FIND3**（Framework for Internal Navigation and Discovery）是一个用 Go 写的高精度**室内定位框架**——类似"室内 GPS"，仅凭智能手机/笔记本的蓝牙、WiFi、磁场等信号即可确定设备在建筑内的位置。

## 二、项目亮点（差异化）

1. **多信号源融合**：v3 相对 v2 最大变化是支持任意数据源（蓝牙/WiFi/磁场…），不再只靠 WiFi。
2. **被动扫描内建**：被动指纹采集内置于主服务（v2 需独立 `find-lf` 服务）。
3. **元学习分类器**：内置 10 种机器学习分类器（v2 仅 3 种），用 /learn 阶段采集的指纹做定位。
4. **轻量带宽**：客户端用 Websockets + React，降低带宽与编码复杂度。
5. **存储与许可优化**：磁盘数据库改用 SQLite（v2 为 BoltDB）并 rolling 压缩 MAC 地址（依赖作者 `stringsizer`）；许可从 AGPL 改为更商业友好的 MIT。

## 三、核心架构

这是一个**多组件框架**，本仓库只含两个服务端，其余在关联仓库：

- **数据存储服务 `server/main/`**（Go）：`main.go` 主程序，`src/` 处理 `/track`、`/learn` 等 API，`static/`、`templates/` 提供 Web 界面，`testing/`、`scratch/` 辅助。
- **机器学习服务 `server/ai/`**（Python）：`requirements.txt` + `src/` 实现 10 个分类器，向后兼容 `/track`、`/learn` 与 MQTT 端点。
- **关联组件（外部仓库）**：
  - `schollz/find3-cli-scanner` — 命令行指纹采集
  - `schollz/find3-android-scanner` — Android 采集 App
  - `DatanoiseTV/esp-find3-client` — ESP8266/ESP32 固件采集
- **部署**：`Dockerfile` + `doc/`（文档站 internalpositioning.com）+ `runner.conf`。

## 四、应用场景与启发

- **场景**：商场/博物馆室内导航、仓储资产追踪、养老院/医院人员定位、智能家居"人在哪个房间"感知。
- **启发（对同类需求）**：
  - "指纹采集(learn) + 实时定位(track)"两段式 + MQTT 解耦，是室内定位系统的经典可扩展范式，做 IoT 定位可照搬。
  - 把 ML 服务与数据服务分离（Go 服务管 I/O、Python 服务管模型），让算法迭代不拖累高并发采集——微服务切分的合理边界。
  - 多客户端(手机/ESP/CLI)统一上报同一 API，是"边缘多形态 + 中心服务"的典型结构。

## 五、源码深度解读（核心模块）

**1. 数据服务 `server/main/src`**
实现指纹的接收(/learn 存训练数据)与查询(/track 实时定位)，通过 MQTT 与 AI 服务解耦——采集高并发、推理可异步。

**2. ML 服务 `server/ai/src`**
10 个分类器做元学习：采集阶段按位置打标，定位阶段综合多信号预测坐标。这是 FIND3 "高精度"的来源（多分类器投票/加权）。

**3. 客户端采集（外部仓库）**
`find3-cli-scanner` / `find3-android-scanner` / `esp-find3-client` 负责把蓝牙/WiFi/磁场扫描成统一指纹上报，是框架"数据入口"多样性的体现。

## 六、社区口碑

- 4.8k⭐、372 fork，是室内定位领域知名度较高的开源方案（HelloGitHub 类榜单常客）。
- 文档站 `internalpositioning.com` 完整，Slack 社群与邮件列表运营多年。
- 作者 schollz 是 Go 生态活跃开源者（stringsizer 等配套工具）。

## 七、竞品对比 + 核心研判

| 维度 | find3 | WiFiRSSI 自研 | Apple UWB/FindMy | 商用 UWB 方案 |
|---|---|---|---|---|
| 硬件成本 | 低(复用现有 WiFi/BT) | 低 | 高(需 UWB 芯片) | 高 |
| 精度 | 中(房间级) | 中 | 高(亚米) | 高 |
| 维护状态 | ⚠️ 停滞(2022) | 自担 | 厂商维护 | 厂商维护 |

**研判**：FIND3 在"零额外硬件、纯软件室内定位"方向曾是标杆，架构（多源指纹 + 微服务 + 多客户端）至今仍有教学与 PoC 价值。**关键风险：仓库最后提交停留在 2022-12-30，已 3 年+ 未维护**，依赖与 ML 库可能已过期，生产采用需自行接手维护或 fork。适合作为"室内定位系统设计范本"研读，不建议直接上生产而不评估维护成本。

## 八、关键文件路径速查

- 仓库根：`https://github.com/schollz/find3`
- 文档站：`https://www.internalpositioning.com/doc`
- 数据服务：`server/main/main.go`、`server/main/src/`、`server/main/templates/`
- ML 服务：`server/ai/src/`、`server/ai/requirements.txt`
- 部署：`Dockerfile`、`runner.conf`
- 关联客户端：`schollz/find3-cli-scanner`、`schollz/find3-android-scanner`、`DatanoiseTV/esp-find3-client`
- MAC 压缩依赖：`schollz/stringsizer`
