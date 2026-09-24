# 🔬 duixcom/Duix-Avatar - 全方位深度调研

## 📌 一句话定位
`duixcom/Duix-Avatar` 是鬼谷智能（duix.com）开源的 **AI 数字人工具包**——完全离线、本地运行的「形象 + 声音」克隆与视频合成框架：输入文本/语音即可驱动虚拟分身生成口播视频，无需联网、隐私可控，面向 Windows / Ubuntu 22.04 桌面。

## ⭐ 项目亮点
- **真·开源 + 离线优先**：区别于 HeyGen/D-ID 等 SaaS，本项目**全离线**（本地 Docker 服务 + Electron 客户端），数据不出本机；宣称服务过 1 万+ 企业、生成 50 万+ 数字人。
- **克隆成本革命性下探**：官方叙述——把数字人生产成本从数十万美元级降到约 $1,000，普通人用一台带 N 卡的主机即可免费造自己的 AI Avatar。
- **一键 Docker 部署**：`deploy/docker-compose*.yml` 拉起三容器（ASR / TTS / 视频合成），lite 版单容器；客户端提供 Windows `.exe` 与 Linux `.AppImage`。
- **多语言 + 开放 API**：脚本支持 8 种语言（中/英/日/韩/法/德/阿/西）；合成/训练接口走本地 `127.0.0.1`，方便二次开发。
- **商用友好（有条件）**：支持全球免费商用；但**企业用户 >10 万人 或 年营收 >1000 万美元需签商业许可**（许可为仓库内 `Duix.Avatar model community Licensing Agreement`，SPDX 标为 NOASSERTION，需自行审阅）。

## 🏗️ 项目架构全景
### 仓库结构（main 树，关键部分）
- `package.json` + `electron.vite.config.mjs` + `electron-builder.yml`：**Electron + electron.vite** 客户端（管理界面、一键启动包）。
- `deploy/`：`docker-compose.yml` / `-linux.yml` / `-lite.yml` / `-5090.yml`（50 系显卡预览版 PyTorch）。
- `src/main/service/`：`model.js`（模型训练）、`voice.js`（音频合成）、`video.js`（视频合成）——**本地 HTTP API 实现**。
- `resources/ffmpeg/`：内置 ffmpeg/ffprobe（含 GPLv3 声明）。
- `doc/常见问题.md`、`README_zh.md`：中英双语文档。

### 运行模型（三段式服务矩阵）
- **ASR**：`guiji2025/fun-asr`（语音识别）
- **TTS**：`guiji2025/fish-speech-ziming`（声音克隆合成）
- **视频合成**：`guiji2025/duix.avatar`（唇形同步 + 视频渲染）
客户端发请求到本地端口，服务端容器负责算力（**必须 NVIDIA GPU + 正确驱动**）。

## 💡 应用场景与启发
- **口播 / 知识类视频批量生产**：教育、法律、医疗、自媒体从业者可用自己的形象声音克隆，文本驱动批量产出视频——把"出镜"从人力成本变成算力成本。
- **隐私敏感场景**：完全离线意味着医疗/法律等受监管行业可在内网部署，不触云。
- **对本地 AI 应用架构的启发**：「Electron 客户端 + Docker 算力服务 + 本地 REST API」是典型的"重算力本地化"拆分范式，和本地 LLM 桌面端（如 LM Studio）思路一致，可借鉴到其它需要 GPU 的本地 AI 工具。

## 🧠 核心源码解读
### 1. 开放 API 三段（本地端口）
```text
音频合成:  POST http://127.0.0.1:18180/v1/invoke
           { speaker, text, format:"wav", topP, temperature, reference_audio, reference_text ... }
视频合成:  POST http://127.0.0.1:8383/easy/submit
           { audio_url, video_url, code, chaofen:0, watermark_switch:0, pn:1 }
进度查询:  GET  http://127.0.0.1:8383/easy/query?code=${taskCode}
```
流程：模型训练（视频拆静音视频+音频 → 音频训练拿 `reference_audio`/`reference_text`）→ 音频合成 → 视频合成（提交 + 轮询进度）。

### 2. 数据与镜像耦合
音频训练数据约定落在 `D:\duix_avatar_data\voice\data`，与 `fish-speech-ziming` 服务共享卷；镜像名（`guiji2025/*`）硬编码在 README，`docker-compose` 中可改。说明项目本质是**对鬼谷已有模型服务的"开源编排前端"**，模型权重仍在镜像内、非本仓库源码。

### 3. 客户端技术栈
`electron.vite.config.mjs` + `electron-builder.yml` 表明：UI 用 Web 技术（疑似 Vue/React），主进程负责调起 Docker、管理项目数据；`build/` 下的 `entitlements.mac.plist` / `icon.*` 表明已做 macOS 签名与多平台打包准备。

## 🌐 全网口碑画像
- **社区信号**：15.6k⭐ / 2.6k fork（2024-12 创建，2026-04 仍有更新）；README 自称"社区非常活跃、issues 日清"，并给出标准问题模板与日志获取指引，工程支持力度较强。
- **定位共识**：被视作"最易上手的开源数字人方案"，与 SadTalker/LivePortrait 同属口型驱动路线，但补齐了"产品级客户端 + 一键部署 + 声音克隆"闭环。
- **注意点**：项目新开源、文档以图文步骤为主，源码深度有限（核心模型在镜像内）；50 系显卡已适配（CUDA 12.8 预览 PyTorch）。

## ⚔️ 竞品对比
| 维度 | Duix.Avatar | HeyGen / D-ID（SaaS） | SadTalker / LivePortrait（研究） |
|------|-----------|----------------------|--------------------------------|
| 运行位置 | 全离线本地 | 云端 | 本地（需自搭推理） |
| 声音克隆 | ✅（fish-speech） | ✅ | 通常仅口型 |
| 上手成本 | 中（需 GPU+Docker） | 低（开箱） | 高（研究代码） |
| 商用门槛 | 免费（大体量需签许可） | 订阅 | 看原许可 |

## 🎯 核心研判
- **优势**：唯一把"离线 + 开源 + 免费商用（有条件）+ 产品级客户端"凑齐的数字人方案，对想做口播/数字人视频的用户极具吸引力。
- **风险**：硬件门槛高（RTX 4070 级、C 盘 >100GB、首次下载 ~70GB）；许可对大体量企业有约束需审阅；非实时交互（实时需 duix.com 平台）；核心模型权重在外部镜像、本仓库偏"编排前端"。
- **趋势**：数字人赛道"开源本地化"代表，随 GPU 普及与模型轻量化，长期价值上升。

## 📂 关键文件路径速查
- `package.json` / `electron.vite.config.mjs` — Electron 客户端技术栈
- `deploy/docker-compose.yml`（及 `-linux`/`-lite`/`-5090` 变体）— 服务编排
- `src/main/service/model.js` / `voice.js` / `video.js` — 本地合成 API 实现
- `doc/常见问题.md`、`README_zh.md` — 中英文档
- `Duix.Avatar model community Licensing Agreement.pdf` — 许可（务必自阅）
- 仓库：`https://github.com/duixcom/Duix.Avatar`
