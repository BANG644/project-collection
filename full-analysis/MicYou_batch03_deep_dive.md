# 📊 MicYou 深度调研报告

> **仓库**: [LanRhyme/MicYou](https://github.com/LanRhyme/MicYou)  
> **Stars**: 2,740 | **Forks**: 124 | **语言**: Kotlin | **License**: GPL-3.0  
> **创建时间**: 2026-02-10 | **最后推送**: 2026-06-08  
> **Batch**: batch_03 (#44) | **调研日期**: 2026-06-17

---

## 一、项目定位

MicYou 是一款**将 Android 手机变为 PC 麦克风**的开源工具。它利用手机内置麦克风采集高质量的音频，通过 Wi-Fi 或 USB 传输到电脑，充当系统级音频输入设备。

### 解决了什么痛点
- 💰 **无需购买独立麦克风**：利用已有的 Android 手机即可获得高质量音频
- 🎙️ **移动端麦克风质量常优于 PC 内置麦**
- 🔄 **跨平台**：Android 客户端 + Windows/Linux/macOS 桌面服务器

---

## 二、技术架构

### Android 客户端
- **框架**: Kotlin Multiplatform + Jetpack Compose + Material 3
- **语言**: Kotlin（~1.3MB 源码）
- **音频能力**:
  - 内置噪声抑制（Noise Suppression）
  - 自动增益控制（AGC）
  - 去混响/回声消除（Dereverberation）
  - 可调采样率、声道数、音频格式

### 桌面服务器
- **平台**: Windows / Linux / macOS
- **安装方式**: 从 GitHub Releases 下载，平台无关
- **虚拟麦克风**: 通过 VB-Cable（Windows）或 BlackHole（macOS）模拟系统麦克风输入

### 连接模式

| 模式 | 方式 | 特点 |
|------|------|------|
| Wi-Fi | 无线网络传输 | 便捷，无需线缆 |
| USB ADB | Android Debug Bridge | 稳定低延迟 |
| USB AOA | Android Open Accessory | 无需 ADB 驱动 |

---

## 三、社区与生态

- **Stars**: 2,740，属于快速增长的开源音频工具
- **多渠道**: 
  - GitHub Releases 提供下载
  - AUR 包（Arch Linux 用户可直接安装 `micyou-bin`）
  - QQ 群 + Telegram 频道支持
- **赞助**: 爱发电（Afdian）平台
- **HelloGitHub 推荐**: 获得该平台推荐标签
- **镜像**: CQU 开源镜像站 + MirrorChyan 提供高速下载

---

## 四、关键优势与不足

### 优势
- 📱 **零硬件成本**：利用现有手机，免去购买独立麦克风的费用
- 🎧 **音频处理**: 集成降噪/AGC/回声消除，适用会议/直播/录制
- 🔌 **双连接模式**：USB 保障延迟，Wi-Fi 保障便利性
- 🖥️ **全平台桌面端**：Win/Mac/Linux 全覆盖

### 不足
- 🐛 **iOS 不支持**：仅 Android 客户端
- 📦 **依赖虚拟声卡驱动**：需额外安装 VB-Cable / BlackHole
- 📝 **中文为主**：国际化文档有待完善
