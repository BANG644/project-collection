# osmdroid/osmdroid 深度调研

> 调研日期：2026-10-01 ｜ 数据源：gh API（README / 目录树 / osmdroid-android/.../tileprovider/modules/ / views/MapView.java）｜ 定位：Android 平台开源地图视图库（OpenStreetMap 工具集，Apache-2.0，**已于 2024-08 归档停更**）

## 一、项目定位（一句话）

**osmdroid** 是 Android 上 **MapView（v1 API）的（近乎）完整免费替代品**：自带可插拔的瓦片（tile）提供系统，支持众多在线/离线瓦片源，并提供图标、定位、绘制图形等 overlay——自 Android 1.0 起就作为 Google Maps 的开源替代。

## 二、项目亮点（差异化）

1. **16 年历史、75+ 贡献者**：与 Android 同寿启动的开源地图库，沉淀极其成熟，F-Droid + Play Store 双分发，社区规模大。
2. **模块化瓦片系统**：把「瓦片从哪来、怎么存、怎么画」拆成可替换的 provider/cache/archive 模块，在线/离线（MBTiles/GEMF/SQLite/Zip）通吃。
3. **overlay 体系**：内置图标、轨迹、位置追踪、图形绘制等 overlay，扩展点清晰。
4. **产物规范**：以 AAR 形式发 Maven Central（`org.osmdroid:osmdroid-android:6.1.20`），`minSdk 8` 起即可用，接入成本低。
5. **配套工具**：`OSMMapTilePackager`（离线瓦片打包）、`osmdroid-geopackage`（GeoPackage 支持）。

> ⚠️ **重要状态**：仓库顶部明确声明 **项目已归档（archived），不再更新或发版**。源码与文档保留供 fork/自维护，最近正式版 6.1.20（2024-08）。选用前需评估长期无人维护的风险。

## 三、核心架构

- **技术栈**：Java / Android（Gradle 7.4.2 + JDK11 构建）/ Maven Central AAR。
- **模块拆分**：
  - `osmdroid-android`：核心库（MapView、tileprovider、overlays、utils）。
  - `osmdroid-geopackage`：GeoPackage 矢量/栅格支持。
  - `OSMMapTilePackager`：离线瓦片批量打包工具。
- **瓦片子系统 `osmdroid-android/.../tileprovider/`**：
  - **提供模块 `modules/`**：`MapTileDownloader`（在线下载）、`MapTileFileArchiveProvider`（档案源）、`MapTileFilesystemProvider`（文件缓存）、`MapTileSqlCacheProvider`（SQLite 缓存）、`OfflineTileProvider`（纯离线）、`MapTileApproximater`（降采样近似）、`MapTileAssetsProvider`（APK 内置资源）。
  - **档案格式 `modules/`**：`ArchiveFileFactory` + `MBTilesFileArchive` / `GEMFFileArchive` / `ZipFileArchive`，以及 `SqliteArchiveTileWriter` / `SqlTileWriter`（写入离线库）。
  - **缓存/池**：`MapTileCache`、`BitmapPool`、`ExpirableBitmapDrawable`、`ReusableBitmapDrawable`、`MapTilePreCache`。
  - **基类**：`MapTileProviderBase` / `MapTileProviderArray` / `MapTileModuleProviderBase` / `MapTileFileStorageProviderBase` / `IFilesystemCache`。
- **视图层**：`views/MapView.java`（**1922 行**，核心地图视图，承载缩放/平移/overlay 管理）。

## 四、应用场景与启发

- **场景**：需要「不依赖 Google Play 服务」的 Android 地图 App（隐私/合规/离线优先场景）；想完全控制瓦片来源（自建瓦片服务器、离线包）的开发者；研究成熟 Android 地图架构的学习者。
- **启发**：
  - 它是「**可插拔瓦片管线**」的经典范本：下载/缓存/档案/近似各成一个 `MapTileProvider` 模块，通过 `MapTileProviderArray` 组合——这种「数据源可替换 + 缓存分层 + 位图对象池」的组合，比把瓦片逻辑写死在视图里健壮得多，至今仍是地图 SDK 的主流架构范式。
  - `BitmapPool` + `ReusableBitmapDrawable` 做位图复用，是移动端「避免 GC 抖动」的老牌优化手法，对任何高频创建/销毁图像对象的场景都值得借鉴。

## 五、源码深度解读（核心模块）

**1. 瓦片提供模块组合：`MapTileProviderArray` + 各 Provider**

```java
// 概念结构（非逐字）：tileprovider/modules/ 下每个 Provider 实现同一接口
// MapTileDownloader        —— 在线下载（带 INetworkAvailablityCheck）
// MapTileFilesystemProvider —— 读本地文件缓存
// MapTileSqlCacheProvider  —— 读 SQLite 缓存
// MapTileFileArchiveProvider—— 读 MBTiles/GEMF/Zip 档案
// MapTileApproximater      —— 用低 zoom 瓦片放大近似，省流量
// OfflineTileProvider      —— 纯离线档案源
// 它们被 MapTileProviderArray 组合，MapView 只面对统一的 provider 接口
```

视图层完全不关心瓦片来自网络还是离线档案——数据来源通过 `MapTileProviderArray` 的组合在构造期注入，是依赖倒置的教科书级实现。

**2. 缓存与位图复用：`MapTileCache` + `BitmapPool`**

`MapTileCache` 按瓦片坐标缓存 `Drawable`；`BitmapPool` 维护可复用位图对象，`ReusableBitmapDrawable` / `ExpirableBitmapDrawable` 管理生命周期与过期——高频滚动地图时避免反复分配位图，显著降低 GC 压力。

**3. `views/MapView.java`：1922 行的核心视图**

`MapView` 聚合 `MapController`、`overlay` 列表、`tileprovider` 引用，处理缩放手势（含 README 提到的 floating-point zoom、free draw）、overlay 绘制与地图状态持久化——是整个库的展示与交互中枢。

## 六、社区口碑

- 3.1k⭐（GitHub 计数偏低因部分历史在 Google Code）、Apache-2.0、16 年、75+ 贡献者；F-Droid/Play 长期分发，Stack Overflow 与 Google Group 有大量历史问答。
- 现状：2024-08 归档，**不再维护**。作者直言「完全社区志愿、无公司赞助、地图很难做对」，并提醒「抱怨慢/无支持会被 ban」。

## 七、竞品对比 + 核心研判

| 维度 | osmdroid | Google Maps / MapView | Mapbox Maps SDK | MapLibre Android |
|---|---|---|---|---|
| 开源/免费 | ✅ Apache-2 | ❌ 闭源+条款 | ⚠️ 商用计费 | ✅ MIT |
| 不依赖 GMS | ✅ | ❌ 需 Play 服务 | ⚠️ | ✅ |
| 离线/自建瓦片 | ✅ 极强 | ❌ | ⚠️ | ✅ |
| 维护状态 | ❌ 已归档(2024) | ✅ | ✅ | ✅ 活跃 |
| 现代矢量/3D | ❌ 偏旧 | ✅ | ✅ | ✅ |

**研判**：作为「离线优先、不依赖 Google 服务、瓦片源完全可控」的 Android 地图方案，osmdroid 的**架构设计至今仍有极高学习价值**，其可插拔瓦片管线是同类 SDK 的鼻祖级范式。但**已归档停更**是决定性短板：新 Android 版本/安全修复不会有官方支持，新项目应优先考虑活跃分支或 MapLibre Android；老项目若已深度集成，可 fork 自维护。与用户的「移动/离线工具」兴趣契合，宜作为**架构参考**而非生产依赖。

## 八、关键文件路径速查

- 仓库根：`https://github.com/osmdroid/osmdroid`（已归档）
- 核心库：`osmdroid-android/`
- 瓦片提供：`osmdroid-android/src/main/java/org/osmdroid/tileprovider/MapTileProviderBase.java`、`MapTileProviderArray.java`
- 瓦片模块：`osmdroid-android/src/main/java/org/osmdroid/tileprovider/modules/`（MapTileDownloader / MapTileFilesystemProvider / MapTileSqlCacheProvider / MapTileFileArchiveProvider / MapTileApproximater / OfflineTileProvider / ArchiveFileFactory / MBTilesFileArchive / GEMFFileArchive / ZipFileArchive）
- 缓存/池：`tileprovider/MapTileCache.java`、`BitmapPool.java`、`ReusableBitmapDrawable.java`
- 视图：`osmdroid-android/src/main/java/org/osmdroid/views/MapView.java`（1922 行）
- 辅助：`osmdroid-geopackage/`、`OSMMapTilePackager/`
- 文档：`https://github.com/osmdroid/osmdroid/wiki`
