# ⌚ NoopApp/noop — 深度调研报告

> **调研时间**: 2026-06-15  
> **仓库**: [NoopApp/noop](https://github.com/NoopApp/noop)  
> **Stars**: ~4,500+（2026-06）  
> **语言**: Swift + Kotlin  
> **当前版本**: v3.0.0 "Titanium & Gold"  
> **定位**: WHOOP 手环的离线开源伴侣 App  

---

## 一、项目概览

NOOP 是一个**完全离线的 WHOOP 手环伴侣应用**，覆盖 iPhone、Android、macOS 三大平台。它的核心理念非常激进：

> **你的手环。你的数据。你的设备。离线、本地、无云。**

WHOOP 官方需要每月订阅费（约 $30/月）才能使用，所有数据强制同步到云端。NOOP 通过逆向 WHOOP 的 BLE 协议，让用户可以直接用蓝牙从手环读取数据，全部保存在本地设备——不需要账号、不需要订阅、不需要联网。

---

## 二、核心功能

### 📊 三大核心数据面板
- **Today（今日）**：实时心率、活动、恢复状态
- **Sleep（睡眠）**：深睡/浅睡/REM 各阶段分布、睡眠评分
- **Stress（压力）**：日间压力曲线、HRV 趋势

v3.0.0 重新设计了 UI，iPhone、Android、Mac 三端统一的 "Titanium & Gold" 设计语言。

### 🔗 BLE 协议逆向
这是 NOOP 最技术性的成就。项目完整开源了 WHOOP 4.0 和 5.0 的 BLE 通信协议（见 [PROTOCOL.md](https://github.com/NoopApp/noop/blob/main/docs/PROTOCOL.md)），包括：
- 服务 UUID 和特征值映射
- 数据帧格式解析
- 心率、HRV、加速度、皮肤温度等传感器数据的原始帧结构

### 🔒 隐私优先设计
- 零云架构：没有任何服务器端
- 无账号系统：无法追踪用户
- 数据全部存本地（iOS 用 Core Data / Android 用 Room）
- 可导出原始数据

---

## 三、技术架构

```
┌─────────────────────┐
│  WHOOP Band (BLE)   │
│  4.0 / 5.0 / MG     │
└──────┬──────────────┘
       │ BLE GATT
       ▼
┌─────────────────────┐
│   BLE 协议层         │  ← 开源 PROTOCOL.md
│   帧解析 + 校验      │
└──────┬──────────────┘
       │ decoded data
       ▼
┌─────────────────────┐
│   数据存储层         │
│   Core Data / Room   │
└──────┬──────────────┘
       │ query
       ▼
┌─────────────────────┐
│   UI 展示层          │
│   Today/Sleep/Stress │
└─────────────────────┘
```

**平台分端**：
- **iOS**: Swift + Core Data
- **Android**: Kotlin + Room
- **macOS**: 基于 Catalyst 或独立 SwiftUI

---

## 四、安装与使用

### macOS
```bash
brew install --cask noopapp/noop/noop
# 或从 Releases 下载 NOOP.app
```

### Android
从 Releases 下载 `NOOP-full.apk` 直接安装。

### iOS
通过 TestFlight 或 sideload 安装。

### 首次使用
1. 打开 NOOP，确保 WHOOP 手环在附近
2. 自动通过 BLE 搜索并配对
3. 配对后自动开始同步数据
4. 数据全部存本地，无需注册

---

## 五、社区与商业模型

### 完全免费（无任何付费墙）
作者明确声明：NOOP 永久免费——无账号、无云、无订阅、无功能锁定、无骚扰提示。但项目本质上由一个人自费维护，依赖社区捐赠（仅接受加密货币，以保持匿名性）。

### 媒体覆盖
被 AOL、Yahoo、Android Authority、TechRadar、BGR、Android Central、Android Police、Notebookcheck、Trusted Reviews 等多家科技媒体报道。

### 社区贡献
- Reddit: r/NOOPApp
- Git Issues 中列有详细 Roadmap 和 Help Wanted
- 特别需要用户提供不同固件版本的原始 BLE 抓帧数据

---

## 六、与 WHOOP 官方对比

| 维度 | WHOOP 官方 App | NOOP |
|------|---------------|------|
| 费用 | $30/月 订阅 | 完全免费 |
| 数据存储 | 云端 | 本地 |
| 账号需求 | 必须注册 | 无需 |
| 联网需求 | 必须联网 | 完全离线 |
| 平台 | iOS/Android | iOS/Android/macOS |
| 数据导出 | 有限 | 完整原始数据 |
| 硬件兼容 | WHOOP 4.0/5.0 | WHOOP 4.0/5.0/MG |
| 开源 | ❌ 闭源 | ✅ MIT License |

---

## 七、仓库质量评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术深度 | ⭐⭐⭐⭐⭐ | BLE 协议逆向，三端原生实现 |
| 产品完整性 | ⭐⭐⭐⭐⭐ | iOS + Android + macOS 三端全功能 |
| 文档质量 | ⭐⭐⭐⭐ | PROTOCOL.md 详尽，DONATIONS.md 透明 |
| 透明度 | ⭐⭐⭐⭐⭐ | 协议文档开源，财务透明单开发者 |
| 可扩展性 | ⭐⭐⭐ | 专注 WHOOP 生态，不通用 |

---

## 八、适合谁用

1. **WHOOP 用户**：不想付月费，又想用 WHOOP 手环
2. **数据隐私意识强的人**：不想把心率/睡眠数据上传到云
3. **BLE/可穿戴开发者**：PROTOCOL.md 是 WHOOP BLE 协议的最佳逆向参考
4. **iOS/macOS 开发者**：学习 Swift + Core Data + BLE 集成的优质参考项目

---

*报告基于 GitHub README、PROTOCOL.md、多家科技媒体报道综合整理。*
