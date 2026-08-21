# mahlernim/google-timeline-visualizer 深度调研

> 调研日期：2026-08-22 ｜ 调研方式：gh API 抓取 README + 仓库树 + 源码路径核验
> 星标：2,154 ⭐ ｜ 语言：Kotlin（Android）/ Python（桌面版）｜ 协议：MIT ｜ 默认分支：main
> 定位：把 Google Maps Timeline 导出文件变成可分享的旅行动画视频

## 一、项目定位

google-timeline-visualizer 是一个**隐私优先的 Google 地图时间线可视化工具**：导入你自己的 `Timeline.json`（Android/iOS 导出），在地图上选时间段、预览动画、导出 MP4 旅行视频。提供 **Android App（Kotlin）** 与 **iPhone 网页版（Safari PWA）**，外加一个 **桌面 Python 生成器**。

一句话：你的位置历史只属于你——文件**绝不上传**，渲染全程在本地设备完成。

## 二、项目亮点（差异化）

1. **隐私零上传**：无 Google 登录、无定位权限、无分析、无宽泛存储权限；仅地图底图（CARTO/OpenStreetMap）会收到"你查看区域"的请求，**Timeline JSON 本身永不离开设备**。
2. **三端覆盖**：Android 原生 App（Kotlin，含完整 Service/渲染管线）、iPhone Safari PWA（免安装）、桌面 Python 脚本，同一份数据三入口。
3. **本地视频渲染**：Android 用 `Mp4Exporter` + `VideoExportService` 在设备内编码；可切后台/锁屏继续；完成自动存 `Movies/Timeline Visualizer`。
4. **智能动画处理**：长距离（跨洋航班）沿**大圆路径插值**平滑过渡；通勤等密集本地轨迹用"稳定中心区 + 延迟跟随"抑制地图抖动；旧轨迹在移动标记后淡出保持清晰。
5. **多格式/多语言/容错**：输出 480p~1080p 方/竖/横预设；支持 9+ 语言；兼容新旧 Timeline 导出格式（`semanticSegments`、raw、E7/geo:/latLng 坐标、跨国际日期变更线）。

## 三、核心架构

Android 端是标准 `app/src/main/java/dev/mahlernim/timelinevisualizer/` 分层：

- **data 层**（解析与清洗）：`TimelineParser.kt`（解析多格式 Timeline）、`RawSignalProcessor.kt`（原始信号）、`LocationOutlierFilter.kt`（保守 GPS 离群点过滤，仅剔除孤立不合理往返坐标）、`TimelineCache.kt` / `TimelineSourceStore.kt`（文档引用 + 存储权限保持）、`TileRepository.kt`（地图瓦片仓库）。
- **model 层**：`TimelineModels.kt`（数据模型）、`TitleTemplate.kt`（标题模板，支持 `{year}`/`{name}`）、`VideoDuration.kt`（10~300s）。
- **render 层**（动画与绘制）：`TimelineAnimation.kt`、`TimelinePainter.kt`、`CameraSettings.kt`（固定/动态相机）、`JourneyTiming.kt`（旅程时序）、`RenderText.kt`。
- **export 层**（视频导出）：`VideoExportService.kt`（前台/后台导出服务）、`Mp4Exporter.kt`（MP4 编码）、`MapTilePreparer.kt`（渲染前预取瓦片）、`VideoEncoderSupport.kt`（Safari 16.4+/H.264 能力探测）、`ExportEtaEstimator.kt`、`VideoExportRequest/State/ViewModel`。
- **ui / videos 层**：`TimelineView.kt`、各 Preferences；`VideoStore.kt`/`VideoLibraryViewModel.kt`/`GeneratedMediaRepository.kt` 管理"我的视频"库。

桌面 Python 版 `visualizer.py` 提供 `--input/--year/--camera-movement/--long-trip-compression/--output` 参数化入口，依赖 `requirements.txt`（FFmpeg + 绘图库）。

## 四、应用场景与启发

- **个人年度/旅程回顾**：把一年通勤或一次长途旅行的位置历史变成可分享视频，隐私不泄露。
- **隐私合规工具范式**：对"用户敏感数据可视化"类需求，本项目的「本地优先 + 文件不上传 + 仅底图请求最小化」是可复制的合规模板。
- **给同类需求的解决思路**：
  - 把"大文件解析/清洗/插值/渲染"严格分层（data→model→render→export），使 GPS 离群点过滤、大圆插值等算法可独立单测（仓库含 `androidTest` 设备级冒烟/大文件导入/视频格式测试）；
  - 同一数据源多端复用（Android/iOS PWA/桌面 Python）说明：核心算法与 UI 解耦后，可低成本铺多平台。

## 五、源码深度解读

### 1. 数据解析与清洗 `data/TimelineParser.kt` + `LocationOutlierFilter.kt`
解析新旧多种 Timeline 导出格式，并把原始坐标规整为统一模型：

```kotlin
// 简化骨架：多格式解析 + 保守离群过滤
class TimelineParser {
    fun parse(json: TimelineJson): List<Visit> { /* semanticSegments / raw / E7 / geo: */ }
}
class LocationOutlierFilter {
    fun filter(points: List<LatLng>): List<LatLng> {
        // 仅剔除孤立的、不可能的 out-and-back 坐标，保留原文件不变
        return points.filterNot { isImplausibleOutAndBack(it) }
    }
}
```

### 2. 动画与绘制 `render/TimelineAnimation.kt` + `CameraSettings.kt`
把时间线映射为相机运动；长距离走大圆插值，本地密集轨迹延迟跟随以减少抖动：

```kotlin
// 简化骨架
class TimelineAnimation(private val timing: JourneyTiming,
                        private val camera: CameraSettings) {
    fun frameAt(t: Double): Frame {
        val pos = if (isLongHaul) greatCircleInterp(from, to, t)  // 大圆路径
                  else camera.followLocal(markerPos, t)            // 稳定中心区延迟跟随
        return TimelinePainter.paint(pos, route, t)
    }
}
```

### 3. 视频导出 `export/VideoExportService.kt` + `Mp4Exporter.kt`
前台/后台 Service 承载编码，预取瓦片后逐帧编码，`VideoEncoderSupport` 在 iOS 端探测 Safari H.264 能力：

```kotlin
class VideoExportService : Service() {
    fun export(req: VideoExportRequest) {
        MapTilePreparer.prepare(req.period)      // 渲染前预取底图瓦片
        Mp4Exporter.encode(this, req) { progress -> notify(progress) }
    }
}
```

## 六、社区口碑

- MIT 许可、文档详尽（隐私说明 `docs/privacy.md`、恢复指南 `docs/restore-google-maps-timeline.md`、多语言 README ko/ja），工程透明度高。
- 定位为"个人/家庭工具"，非商业产品：Android 未上 Google Play（侧载 APK），iPhone 走自托管网页 PWA（`ahn-lab.org/google-timeline-visualizer/`）。
- 隐私叙事清晰（"file is never uploaded" + 底图请求透明告知 + 可取消），对隐私敏感用户有强吸引力。
- 数据不可用：外部评测/下载量具体数字本次未抓取，未编造。

## 七、竞品对比 + 核心研判

| 维度 | google-timeline-visualizer | Google 原生 Timeline 回放 | 第三方地图足迹 App |
|------|---------------------------|--------------------------|-------------------|
| 数据上传 | ❌ 永不 | 在 Google 云端 | 多数需上传 |
| 视频导出 | ✅ MP4（本地） | ❌ 仅查看 | 部分 |
| 多端 | Android/iOS PWA/桌面 | 仅官方 App | 单一 |
| 开源 | ✅ MIT | ❌ 闭源 | 多闭源 |

**核心研判**：
- **优势**：隐私零上传 + 本地视频导出 + 三端覆盖，是"想留念又怕泄露位置历史"用户的最优解；算法分层清晰、测试完备，可维护性强。
- **风险**：① 依赖 Google 导出格式，Google 改 Timeline 数据结构即可能 break（已用多格式兼容缓解）；② 未上架应用商店，分发靠侧载/PWA，触达受限；③ 卫星/底图依赖 CARTO，严格离线场景不完全可用。
- **趋势**：隐私本地化工具（local-first）持续受捧；若加"轨迹编辑/配乐/字幕模板"会更接近消费级产品。
- **启发**：处理用户敏感数据可视化时，"默认不上传 + 仅必要最小网络请求 + 透明告知"应作为架构基线而非附加项。

## 八、关键文件路径速查

- `app/src/main/java/dev/mahlernim/timelinevisualizer/data/`
  - `TimelineParser.kt`（多格式解析）、`RawSignalProcessor.kt`、`LocationOutlierFilter.kt`（保守离群过滤）、`TimelineCache.kt`、`TimelineSourceStore.kt`、`TileRepository.kt`
- `app/src/main/java/.../model/` — `TimelineModels.kt`、`TitleTemplate.kt`、`VideoDuration.kt`
- `app/src/main/java/.../render/` — `TimelineAnimation.kt`、`TimelinePainter.kt`、`CameraSettings.kt`、`JourneyTiming.kt`、`RenderText.kt`、`DistanceUnit.kt`
- `app/src/main/java/.../export/` — `VideoExportService.kt`、`Mp4Exporter.kt`、`MapTilePreparer.kt`、`VideoEncoderSupport.kt`、`ExportEtaEstimator.kt`、`VideoExportRequest/State/ViewModel.kt`
- `app/src/main/java/.../ui/` — `TimelineView.kt`、各 Preferences（CameraSettings/LocationFilter/DistanceUnit/AppLanguage/Settings）
- `app/src/main/java/.../videos/` — `VideoStore.kt`、`VideoLibraryViewModel.kt`、`GeneratedMediaRepository.kt`、`VideoMedia.kt`
- `app/src/androidTest/java/.../` — `DeviceSmokeTest.kt`、`LargeTimelineImportDeviceTest.kt`、`export/VideoFormatDeviceTest.kt`
- `visualizer.py` + `requirements.txt`（桌面 Python 版入口）
- `docs/privacy.md` / `docs/restore-google-maps-timeline.md` — 隐私说明 / 恢复指南
- `play-store/assets/screenshots/` — 商店截图
