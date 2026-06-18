# 🔍 深度调研报告：Jane-xiaoer/xiaoer-videolab

> **调研日期**: 2026-06-18
> **Stars**: 464 ⭐ (2026-06-08 Trending)
> **语言**: JavaScript + Python
> **简介**: 一键工具栏按钮，把当前页面的视频抓到 ~/Downloads——本地 yt-dlp 守护进程，支持 1800+ 网站

---

## 一、项目概述

Xiaoer VideoLab（小耳抓视频）是一个极简主义的浏览器视频下载工具。它采取与主流视频下载扩展完全相反的设计哲学：扩展几乎什么都不做，下载在本地发生，没有任何数据离开你的机器。

**反对"烂泥潭"**: 主流浏览器视频下载扩展往往要求"读取所有网站的所有数据"权限，并存在数据回传问题。Xiaoer VideoLab 的回应是：扩展只做一件事——读取当前标签页 URL，然后 POST 到 127.0.0.1。

## 二、核心架构

```
┌─────────────────────┐ click    ┌──────────────────────────┐    ┌──────────┐
│ 浏览器工具栏按钮     │ ─────►   │ daemon @ 127.0.0.1:7788 │ ──► │  yt-dlp  │ ──► ~/Downloads
│ (Chrome MV3 扩展)   │ POST url │ (Python stdlib, launchd) │ spawn └──────────┘
└─────────────────────┘          └──────────────────────────┘      │
                                  ▲ badge: … ✓ ✕ !               │ macOS 通知
                                  └───────────────────────────────┘ "✅ <filename>"
```

### 组件明细
- **守护进程** — Python 标准库 http.server，监听 127.0.0.1:7788，通过 launchd/macOS 或 Task Scheduler/Windows 在登录时自动启动
- **扩展** — Chrome MV3，单一工具栏按钮，读取 tab.url 并 POST 给守护进程
- **输出** — ~/Downloads/\<platform\>_\<title\>_\<date\>.mp4（默认 ≤1080p mp4，可配置）
- **日志** — ~/Library/Logs/xiaoer-videolab.log 或 Windows 等效路径

## 三、技术支持站点

| 类型 | 站点 |
|------|------|
| ✅ 已验证 | YouTube · Vimeo · Bilibili · 抖音 · 小红书 |
| ✅ 支持 | X/Twitter · 西瓜视频 · Instagram · Reddit · Dailymotion · Facebook · TikTok* … ~1860 个 |
| ⚠️ 仅免费内容 | 优酷 · 爱奇艺（VIP/DRM 保护内容不可下载） |
| ❌ 不支持 | 快手 · 腾讯视频 · 视频号（应用内加密传输） |

**注**: 抖音和小红书使用特殊的页面内抓取方式（yt-dlp 无法读取），需要在视频打开/播放时点击按钮。

## 四、核心设计理念

1. **最少权限** — 扩展仅在点击时读取当前标签 URL，无内容脚本、无页面抓取、无远程服务器
2. **本地优先** — 下载在本地通过 yt-dlp 完成，不依赖任何第三方下载服务
3. **可审计** — 全部代码公开，Python 守护进程基于标准库，无黑盒
4. **跨平台** — macOS（launchd）+ Windows 10/11（Task Scheduler），5 分钟安装

## 五、安装流程

**macOS:**
```bash
brew install yt-dlp ffmpeg
git clone https://github.com/Jane-xiaoer/xiaoer-videolab.git
cd xiaoer-videolab && ./scripts/install.sh
# 然后在 chrome://extensions/ 加载 extension/ 目录
```

**Windows:**
```powershell
winget install Python.Python.3.11 yt-dlp.yt-dlp ffmpeg
git clone https://github.com/Jane-xiaoer/xiaoer-videolab.git
cd xiaoer-videolab
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

## 六、与同类工具对比

| 特性 | Xiaoer VideoLab | 传统下载扩展 | IDM | yt-dlp CLI |
|------|----------------|-------------|-----|-----------|
| 一键操作 | ✅ | ✅ | ✅ | ❌ |
| 无数据泄露 | ✅ | ❌（常有） | ❓ | ✅ |
| 1800+ 站点 | ✅ | 几十个 | 有限 | ✅ |
| 无需额外软件 | ❌（需 yt-dlp） | ✅ | ❌ | ❌（CLI 工具） |
| 开源可审计 | ✅ | 不一定 | ❌ | ✅ |

## 七、核心结论

Xiaoer VideoLab 解决了一个被长期忽视的问题：视频下载工具在"易用性"和"安全性"之间如何平衡。它的方案很聪明——用浏览器按钮的"点击"事件作为触发，把全部下载逻辑委托给 yt-dlp。扩展本身几乎没有权限也不需要权限，消除了隐私泄露的最大风险点。

**局限**: 需要先安装 yt-dlp 和 ffmpeg（对非技术用户有门槛）；微信视频号等应用内视频不支持；腾讯视频和快手因缺乏 yt-dlp extractor 而不可用；海外站点需要网络可达（代理）。
