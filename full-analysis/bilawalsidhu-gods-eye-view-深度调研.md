# God's Eye View 深度调研

> 仓库：`bilawalsidhu/gods-eye-view` ｜ 语言：JavaScript（Vanilla + CesiumJS + Vite）｜ 许可：MIT ｜ Stars：≈51.3k（2026-10-10 抓取，Trending 日榜 #1）
> 定位一句话：**浏览器内运行的「上帝视角」实时空间情报地球——把公开航班/船舶/卫星/地震/摄像头等信号融合进一个可探索的真实 3D 地球，并支持语音实时 AI 操控。**

---

## 1. 项目亮点（差异化）

1. **真实数据 + 真实地球**：基于 CesiumJS 与 Google Photorealistic 3D Tiles，图层是真实公开信号，不是模拟（交通除外——沿真实路网模拟）。
2. **20+ 数据层、17 层零 key 可用**：OpenSky 匿名、USGS、CelesTrak、adsb.lol、城市 CCTV、Radio Browser、GBFS、NOAA/ECMWF 天气等开箱即用。
3. **实时语音 Agent**：OpenAI Realtime API 驱动 30 个语音工具，自然语言操控相机/标注/查询（"Take me to LAX and select the nearest airborne aircraft"）。
4. **MCP server**：可被 Claude Desktop / Codex / ChatGPT 桌面端唤起真实地球，对话里直接「show a place」。
5. **零框架、可读可改**：Vanilla JS + CesiumJS + Vite，无重型前端框架，上手快、利于 hack。
6. **边界伦理声明到位**：只建模事件/资产/系统（飞机、船舶、卫星、火灾、城市），**明确不做人脸/个人追踪**，越线 PR 不合并。

---

## 2. 核心架构

- **渲染层（浏览器）**：CesiumJS 真实地球 + Google Photorealistic 3D Tiles；`src/main.js` 引导，`src/ui.js` 运行时面板/HUD/样式，`src/hud.js` 情报 HUD + AI 场景摘要，`src/mapStackController.js` 底图切换（Google 3D / Esri / OSM / ion）。
- **数据层（模块化）**：`src/layers/` 每类信号一个组件（weather / wind / cyclones / transit / ALPR…）；`src/data/` 每类一个模块 + 编排 + 上下文 store；`src/data/iconOrientation.js` 做屏幕空间航向投影。
- **语音层**：`src/voice/` 是 OpenAI Realtime 会话 + 30 个语音工具。
- **服务端代理（关键安全设计）**：任何触碰私钥的 API（OpenAI、AISStream、OpenSky OAuth、摄像头帧）都经**加固的 server-side proxy**——带 SSRF 防护、响应大小上限、错误脱敏；浏览器只持有 Google Maps / Cesium ion 两个可在 provider 侧限制的 key。

关键技术点（Under the Hood）：
- 飞机/船舶**屏幕空间航向投影**——任意相机角度下沿真实世界航向指向，无自旋/无视口锁定；
- 直播数据 15–30s 一跳，渲染「慢一帧」并做已知 fix 间插值 + 航位推算补洞；
- 卫星 **SGP4 传播 + GMST realignment** 锁定轨道环，无漂移；
- 实体高度对齐 Google 3D Tiles，飞机停停机坪、摄像头立街角不悬空；
- OpenSky 信用调控 / TomTom 每日 tile 预算 / TLE 磁盘缓存控制请求量。

---

## 3. 应用场景与启发（重点）

- **OSINT / GEOINT 教学与科普**：把「公开信号融合成可探索产品」做成现象级示范，适合地理、情报分析、数据新闻教学。
- **应急/交通/城市可视化**：实时航班、港口船舶、火灾、雷达、气旋同屏，给城市与应急场景提供可交互底板。
- **给同类需求的解决思路**：
  - 「**每个数据源 = 一个 layer 模块**」是可复用的公开数据接入范式，加层就是加一个 `src/layers/` 组件；
  - 「**私有 key 一律 server-side 代理 + 浏览器只持受限 key**」是做公开数据产品的正确安全基线；
  - 「**零框架 + CesiumJS + Vite**」让地理可视化项目保持可读、易 hack，比堆 React 更轻。

---

## 4. 源码深度解读

**`src/` 核心布局**（来自仓库 README 权威结构）：

```
src/
├── main.js                 # 引导：Google 3D tiles、layer 注册
├── ui.js                   # 运行时 UI：面板、HUD、样式、控制门面
├── hud.js                  # 情报 HUD + AI 场景摘要
├── keySetup.js             # POWER UP 面板——应用内 provider key（仅 dev server）
├── mapStackController.js    # 底图切换——Google 3D / Esri / OSM / ion stacks
├── voice/                  # OpenAI Realtime 会话 + 30 个语音工具
├── layers/                 # 图层组件——weather、wind、cyclones、transit、ALPR…
├── data/                   # 每层一个模块 + 编排 + 上下文 store
│   └── iconOrientation.js  # 屏幕投影航向 + 地平线剔除
└── scenes/                 # 电影级场景导演
```

`src/data/iconOrientation.js` 是「朝向不随视口乱转」的核心：每帧把实体真实世界 heading 投影到屏幕空间，配合 horizon cull 决定可见性，是让数千架飞机在任意缩放/倾角下都「指对方向」的关键算法。CCTV 等模块通过 `src/layers/streetLevel/registry.js` 实现 provider 契约后注册进 `src/app/layers/streetLevel.js`，扩展点清晰。

---

## 5. 全网口碑

- GitHub ≈51.3k stars，**2026-08 登顶 Trending 日榜与周榜 #1**；Product Hunt **#8 Product of the Day**（由 hashtag 发明者 Chris Messina 发布）。
- 获 JavaScript 之父 **Brendan Eich** 公开点赞（"pretty cool"）；入驻 Pinokio；背靠作者 Bilawal Sidhu 的 **5M+ YouTube / 25M+ 社媒**「God's Eye View」系列。
- 团队：Bilawal Sidhu + Sameh Khamis（Halfpixel）。正在做官方托管版（halfpixel.ai）。

---

## 6. 竞品对比 + 核心研判

| 维度 | God's Eye View | 商业 GEOINT / flight tracker | Cesium 官方 demo |
|---|---|---|---|
| 数据 | 公开信号融合 | 专有/付费源 | 单点示例 |
| 开源 | MIT，可读可改 | 否 | 部分 |
| AI 语音 | OpenAI Realtime 30 工具 | 少 | 无 |
| 起步成本 | 零 key 即可用 17 层 | 高 | 中 |

**核心研判**：GEV 是「公开数据 + 强叙事 UI + 实时 AI 语音 + 零 key 起步」的现象级组合，示范了如何把零散公开信号熔成一个让人「哇」的可交互产品。技术栈刻意求薄（vanilla JS）利于二次开发；安全与伦理边界声明到位（server-side 代理、不追踪个人）。注意点：数据是延迟/建模/推断的，README 明确**不可用于导航/应急/投资等安全关键用途**；商用需逐一核对各 provider 条款与配额；部分高精度层（Google 3D、OpenAI 语音）仍有计费。值得地理可视化、OSINT 教学、数据融合方向的学习者精读。

---

## 7. 关键文件路径速查

- `src/main.js` / `src/ui.js` / `hud.js` / `mapStackController.js` —— 引导、UI、HUD、底图
- `src/layers/` —— 各数据层组件（weather / wind / cyclones / transit / ALPR / streetLevel…）
- `src/data/iconOrientation.js` —— 屏幕空间航向投影核心算法
- `src/voice/` —— OpenAI Realtime 会话 + 30 语音工具
- `server/` —— 加固的 server-side key 代理（SSRF 防护、响应上限、错误脱敏）
- `docs/MCP_SETUP.md` / `DATA_SOURCES.md` / `SECURITY.md` —— MCP 接入、数据源与威胁模型
- `package.json` + `vite.config.js` —— Node 24/26、Vite 构建、本地 4173 端口
