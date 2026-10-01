# cpaczek/skylight 深度调研

> 调研时间：2026-10-02 ｜ 数据来源：gh API 真实抓取 README / server/src/index.ts / datasource.ts / shared/src/config.ts
> 定位：用 RTL-SDR 实时解码 ADS-B、把头顶飞机投射到天花板的开源艺术装置——Node/Express/ws 服务端 + React 渲染 + 卫星/TLE 天象层 + 可选 PTZ 相机追踪

## 一、项目亮点（差异化）

1. **真实天空穿透屋顶**：RTL-SDR（~$30）解码飞机，渲染到朝天的投影仪，听到头顶的喷气机同一刻正掠过天花板，标注航司/机型/目的地——纯黑背景让"飞机+星星"浮在暗处。
2. **60fps 平滑运动**：~1Hz 的 ADS-B 定位通过"渲染在略微过去 + 在真实位置间补间"插值到 60fps，飞机不跳变；带彗星尾迹、高度分级配色、距离环与罗盘。
3. **真·天空层**：太阳/月亮（含月相）/亮星+星座线/肉眼行星/卫星与 ISS（由 TLE 计算），可手机拖时间轴前后 scrub，或直跳下一次 ISS 过境。
4. **手机控制面板 + LAN 可达**：所有设置（旋转/主题/调色板/过滤/天象开关）在局域网手机端实时调，且持久化跨重启；服务端显式做 DNS-rebinding 防护。
5. **可选"会拍飞机的相机"**：VISCA-over-IP PTZ + RTSP，融合经典 blob 检测 + 大目标检测 + track-before-detect（按运动像 ADS-B 预测那样区分云与飞机）+ 可选 YOLOX-Nano ONNX 语义确认，并**持续自标定**云台。

## 二、核心架构

```
RTL-SDR ─USB─▶ dump1090-fa ─▶ aircraft.json(:8080)  ┐ poll ~1Hz (+ API 补充)
                                                      ▼
server/ (Node·Express·ws) :3000
  • Poller: 归一化+富化(航司/机型表+adsbdb 航线)        ├─ shared/ 纯数学: ECEF az/el, 云台模型+标定求解, α-β 跟踪, FOV/缩放
  • 代理 TLE(Celestrak) / 地理编码(Nominatim)           ├─ web/    Vite+React 四页: 显示(canvas)/控制/电视仪表盘/追踪调试
  • 持久化 config, 广播 WebSocket                      └─ tracker/: 选目标→预测(修正 fix 年龄+解码延迟+电机延迟)→速度追踪+缩放→VISCA→PTZ
```
技术栈：TypeScript·React·Vite·Express·ws·pnpm workspaces·[astronomy-engine](https://github.com/cosinekitty/astronomy)·[satellite.js](https://github.com/shashwatak/satellite-js)。

## 三、应用场景与启发

- **桌面装置/科普/极客礼物**：把"空中交通 + 天文"做成可投影的沉浸式体验，比屏幕看 FlightRadar 更有仪式感；参考构建以 SFO 为中心但任意地点设坐标+ICAO 导入跑道即可。
- **实时数据管线的工程启发**：
  - `Poller` 的 `mergeSources(radio, api)` 用 hex 做主键、按新鲜度偏好——radio 领先几秒赢、API 在 radio 丢信号时接管——是"多源冗余"的经典实现，可借鉴到任何传感器融合场景。
  - `describeFetchError` 把 `ENOTFOUND/ECONNREFUSED/ETIMEDOUT...` 翻译成人话（"DNS 查不到/连接被拒/超时"），并在状态栏暴露真实失败原因——把"可观测性"做进了用户能看到的 UI，而不是只留日志。
  - 429 退避（`RATE_LIMIT_BACKOFF_MS=15_000`）而非硬刚限流，避免"冻结/消失/重现"循环——对调用外部 API 的服务是默认该有的克制。

## 四、源码深度解读

**① 入口与 DNS-rebinding 防护**（`server/src/index.ts`）
```ts
// 所有请求先过 Host 头校验: 否则恶意网页把 attacker.com 解析到用户 LAN IP 即可绕过 CORS
const hostMatcher = buildHostMatcher(process.env);
app.use((req, res, next) => {
  const host = req.headers.host;
  if (!hostMatcher.test(host)) {
    return res.status(403).type("text/plain")
      .send("Forbidden: Host header not in allowlist...");
  }
  next();
});
// REST 与 WS 双通道: /api/* 调试用, WebSocket 推 aircraft/status
```
服务端 bind `0.0.0.0` 以便手机控制，但用 allowlist（loopback/RFC1918/`*.local` 默认放行，自定义域名需 `ALLOWED_HOSTS`）抵御 DNS 重绑定——把"便利（LAN 控制）"与"安全（防重绑定）"同时做对。

**② 数据源归一化与多源合并**（`server/src/datasource.ts`）
```ts
// dump1090 与 airplanes.live 都用 readsb JSON schema → 一个 normalizer 通吃
function normalize(raw: RawAircraft, ts): Aircraft | null {
  if (!raw.hex) return null;
  const onGround = raw.alt_baro === "ground";
  return { hex: raw.hex, flight: raw.flight?.trim() || undefined,
           lat: raw.lat, lon: raw.lon, altBaro: onGround?null:raw.alt_baro??null, ... };
}
// 按 hex 合并 radio(主)+api(辅): radio 领先时赢, 丢信号时 api 接管
function mergeSources(radio: Aircraft[], api: Aircraft[]): Aircraft[] { ... }
```
`describeFetchError` 把底层 `e.cause.code` 映射成可操作文案，是"把网络错误讲人话"的范例。

**③ 配置即真相源**（`shared/src/config.ts`）
```ts
export type Theme = "ambient" | "telemetry" | "focus";
export type DataSource = "radio" | "api";
export interface TrackerConfig {
  driver: "sim" | "visca";          // 真实相机 vs 软件模拟器(零硬件可跑通全追踪管线)
  cameraIp: string; viscaPort: number;
  // ... 目标选择/预测/tracking/缩放/视觉行为, 全部可实时调
}
// 整个对象 server 端持久化到 config.json, 显示端与控制端共享 → 改一处全局生效
```
`TrackerConfig.driver: "sim"` 让相机追踪整套"选目标→预测→缩放→标定"可在**无硬件**下用模拟器跑通并确定性回放——这是把"难测的硬件链路"做成可单测的聪明做法。

## 五、全网口碑

- 3,311⭐，README 细节密度极高（硬件 BOM、最低配置、Docker、排错树、配置表一应俱全），社区在众筹期（skylightceiling.com 候补名单）；被视为"把 ADS-B + 天文 + 计算机视觉玩出花"的标杆级业余工程。

## 六、竞品对比

| 项目 | 形态 | 实时渲染 | 天象层 | 相机追踪 |
|---|---|---|---|---|
| **skylight** | 开源装置 | ✅ 天花板投影+60fps | ✅ 日/月/星/ISS | ✅ VISCA+YOLOX 自标定 |
| FlightRadar24 / ADSBExchange | 网页地图 | ❌ | ❌ | ❌ |
| dump1090 + 自制前端 | 半开源 | 需自写 | ❌ | ❌ |
| 商业"星空投影"玩具 | 闭源 | 预录 | 有限 | ❌ |

**研判**：它是"业余硬件 + 严肃软件工程"的结合范本，代码质量（错误处理、配置 schema、模块化、可无硬件测试）远超多数玩具项目。短板：依赖外部免费 API（airplanes.live 有 429 限流）、RTL-SDR 与 Pi 5 有门槛，且视觉追踪的 ONNX 模型需自下载。整体**值得收藏学习实时数据管线与边缘视觉系统**。

## 七、核心研判

对想做"实时传感器→可视化→可交互装置"的开发者，skylight 是不可多得的全栈样本：它把 ADS-B 解码、WebSocket 实时推送、canvas 渲染插值、天文计算、PTZ 视觉追踪、DNS-rebinding 安全全部串成可运行系统，且处处体现"让错误可被看见、让硬件可被模拟"的工程素养。最适合当"实时系统 + IoT + CV"的综合教科书。

## 八、关键文件路径速查

- `server/src/index.ts` — 入口：config store / Poller / WebSocket hub / REST / DNS-rebinding 防护
- `server/src/datasource.ts` — ADS-B 归一化 + 多源合并 + 可读错误
- `server/src/config-store.ts` — 配置持久化与校验
- `shared/src/config.ts` — 全量配置 schema（显示/天象/追踪）
- `web/src/display/` — canvas 渲染器 + 天体引擎 + 机场叠加
- `tracker/` — 相机大脑：选目标/预测(ECEF)/速度追踪/视觉检测/VISCA
- `pi-setup/` / `compose.yaml` — 树莓派家电化与 Docker 部署
