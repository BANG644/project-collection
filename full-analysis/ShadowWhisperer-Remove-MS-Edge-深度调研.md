# Remove-MS-Edge 深度调研报告

> **仓库**: ShadowWhisperer/Remove-MS-Edge  
> **Stars**: 5,210 | **语言**: Batchfile / Python | **许可**: 未明确 (MIT 风格)  
> **标签**: windows, edge, uninstaller, batch, python, removal  
> **调研日期**: 2026-06-19

---

## 项目全景

Remove-MS-Edge 是一个帮助用户**彻底卸载 Microsoft Edge 浏览器**的工具集，提供 EXE 可执行文件、批处理脚本和 Python 打包版本三种分发方式。

### 背景
Edge 深度集成于 Windows 系统，普通卸载方式不彻底，且可能导致 Windows Update 循环失败。该工具通过批量脚本 + pyinstaller 打包的 EXE 提供完整的 Edge 移除方案。

### 核心数据
- **5.2K⭐** GitHub Stars（Windows 用户刚需）
- **3 种分发方式**：EXE / No Terminal / Edge+WebView 三合一
- **WebView 依赖警告**：明确指出哪些应用依赖 WebView
- **更新修复脚本**：配套 `Fix-WinUpdates` 批处理

---

## 功能架构

### 三种 EXE 版本

| 版本 | 说明 | 适用场景 |
|------|------|----------|
| `Remove-Edge.exe` | 仅移除 Edge | 只卸载浏览器 |
| `Remove-EdgeTerm.exe` | 无终端窗口版本 | 任务计划程序（静默执行） |
| `Remove-EdgeWeb.exe` | Edge + WebView 一并移除 | 彻底清理 |

### 批处理脚本

| 脚本 | 功能 |
|------|------|
| `Both.bat` | 移除 Edge + WebView |
| `Edge.bat` | 仅移除 Edge (含 Appx) |
| `Edge-Appx.bat` | 仅移除 Appx 版 Edge（保留系统 Chrome 内核） |

### WebView 依赖警告

> **Requires WebView**  
> - Eclipse IDEs
> - Gmpublisher (Garry's Mod)
> - ImageGlass
> - Lenovo USB Recovery Creator Tool
> - Microsoft Photos App (Edit)
> - PowerToys File Explorer add-ons
> - Quicken
> - Rex Atmos for MSFS 2020
> - Roblox
> - Safing Portmaster
> - Windows Mail
> - Xbox App

---

## 使用方式

### 方法一：下载 EXE（推荐）

从 [Releases](https://github.com/ShadowWhisperer/Remove-MS-Edge/releases/latest) 下载对应版本运行。

### 方法二：从源码构建

```bash
pyinstaller --onefile --noconsole -i icon.ico -n Remove-Edge.exe edge.py \
  --add-data "setup.x64.exe;." --add-data "setup.x86.exe;."
```

### 方法三：批处理脚本

直接下载运行 `Both.bat` / `Edge.bat` / `Edge-Appx.bat`（需管理员权限）。

---

## 注意事项

### ⚠️ 更新失败循环

> Removing Edge may cause update failure loop.  
> Install Edge, install all Windows updates, then remove Edge.

工具明确告知：卸载 Edge 后可能导致 Windows Update 循环失败。推荐流程：
1. 先安装 Edge
2. 安装所有 Windows 更新
3. 再运行 Remove-MS-Edge

### WebView 兼容性

如果依赖 WebView 的应用（如 PowerToys、Xbox App）出现问题，需重新安装 WebView2 Runtime。

---

## 竞品对比

| 特性 | Remove-MS-Edge | EdgeRemover | Winget 卸载 |
|------|-----------------|-------------|--------------|
| 开源 | ✅ | ❌ 闭源 | — |
| EXE 打包 | ✅ | ✅ | ❌ |
| WebView 可选 | ✅ | ❌ | ❌ |
| 依赖警告 | ✅ | ❌ | ❌ |
| 更新修复 | ✅ | ❌ | ❌ |
| 静默模式 | ✅ (No Terminal) | ❌ | ❌ |

---

## 核心研判

### 优势
1. **真正的刚需**：大量 Windows 用户希望彻底移除 Edge
2. **多版本分发**：EXE / 脚本 / 静默版，覆盖所有场景
3. **安全意识**：明确警告 WebView 依赖和更新循环风险
4. **配套工具**：提供更新修复脚本

### 不足
1. **功能单一**：仅卸载 Edge，无更多系统优化功能
2. **风险警告不足**：普通用户可能不理解 WebView 依赖
3. **更新维护**：Edge 新版本可能绕过脚本

### 适用场景
- Windows 用户希望使用 Chrome/Firefox 替代 Edge
- 系统精简、去广告的 Power User
- 企业环境需要静默移除 Edge

---

## 关键文件路径

| 文件 | 说明 |
|------|------|
| `README.md` | 主文档 + 下载链接 |
| `Batch/Both.bat` | 双移除脚本 |
| `Batch/Edge.bat` | Edge 移除脚本 |
| `Batch/Edge-Appx.bat` | Appx Edge 移除脚本 |
| `edge.py` | Python 主脚本 |
| `icon.ico` | EXE 图标 |
| Releases | 预编译 EXE 下载 |
