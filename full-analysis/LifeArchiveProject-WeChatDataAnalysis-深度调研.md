# 🔬 WeChatDataAnalysis 深度调研

> **仓库地址**: https://github.com/LifeArchiveProject/WeChatDataAnalysis
> **Stars**: 1,843 ⭐ | **语言**: Python + Vue.js | **许可证**: 未声明（Disclaimer 仅"学习研究"）| **创建**: 2025-07-07
> **主页**: https://lifearchiveproject.github.io/WeChatDataAnalysis/
> **定位**: 微信 4.x 数据库解密与年度总结 / 聊天记录导出工具

---

## 一、项目定位

WeChatDataAnalysis 是一款**微信 4.x 本地数据解密与分析桌面工具**：解密本地 WCDB/SQLite 数据库，生成"高仿微信"界面、年度总结，并支持聊天记录 / 朋友圈 / 联系人等导出。定位为**个人微信数据的本地可视化与归档**。

---

## 二、项目亮点（差异化）

- 🔓 **4.x 数据库解密**：针对微信新版的 WCDB 加密库做本地密钥提取与解密（Windows 自动提取，macOS 手动填 64 位密钥）
- 📊 **年度总结 + 高仿微信 UI**：Vue 前端高度还原微信视觉，自动生成年度回顾
- 📤 **全量导出**：聊天/朋友圈/收藏/红包转账/小程序等十余类数据，支持 HTML/JSON/TXT/Excel(ZIP)
- 🔌 **MCP 服务**：设置页提供 endpoint + Bearer token，可直接作为 AI 客户端接入指令（让 Agent 读你的微信数据）
- 🖥️ **三端同源**：Python 后端（FastAPI）+ Vue 前端 + Electron 桌面端（PyInstaller 打包）

---

## 三、核心架构

```
Electron 桌面壳（desktop/）
   ├─ 前端 Vue.js  dev: localhost:3000
   └─ 后端 Python   uv run main.py → FastAPI :10392  (/docs 开放)
            │
            ├─ src/            ：WCDB/SQLite 解密与解析核心
            ├─ key_v4.py       ：4.x 数据库密钥处理
            ├─ analyze_wechat_databases.py ：数据库分析入口
            ├─ scan.py         ：本地微信实例扫描
            └─ skills/         ：MCP 接入相关
            │
            ▼ 解密后
       SQLite（明文）→ 生成年度总结 / 实时消息同步 / 各类导出
```

**数据流**：扫描本地微信 → 提取/填入密钥 → `src/` 解密 WCDB → 载入 SQLite → Vue 渲染"高仿微信"界面与年度总结。Windows 端可 Hook 微信进程内存扫图片密钥；macOS（Apple Silicon）支持实时 WCDB 但需手动填密钥。

---

## 四、应用场景与启发

| 场景 | 适配度 |
|------|--------|
| 个人微信聊天记录备份/导出 | ⭐⭐⭐⭐⭐ |
| 年度总结 / 数据回顾 | ⭐⭐⭐⭐⭐ |
| 朋友圈历史本地留存 | ⭐⭐⭐⭐ |
| 让 AI Agent 读取自己微信数据 | ⭐⭐⭐⭐（MCP 接入）|
| 合规/取证用途 | ⚠️ 法律灰区，慎用 |

> **架构启发**：①「重后端（Python 解密）+ 轻前端（Vue 高仿原 App）+ Electron 一键桌面端」是本类"本地数据工具"的低成本落地范式；② 把导出能力同时暴露为 **MCP 服务**，让个人数据工具天然成为 Agent 的数据源——这是 2026 年个人工具的新趋势。

---

## 五、源码解读（核心模块）

**1. 解密入口 — `key_v4.py` + `analyze_wechat_databases.py`**
`key_v4.py` 处理微信 4.x 的密钥派生/获取；`analyze_wechat_databases.py` 作为分析入口，定位并解密本地 WCDB 库。Windows 自动从进程内存提取密钥，macOS 需用户手动提供 64 位密钥。

**2. 后端服务 — `main.py`（FastAPI）**
`uv run main.py` 启动 REST API（默认 `:10392`，`/docs` 自动文档），前端通过它读取解密后的数据；设置页的"AI 接入提示词"包含 endpoint + Bearer token 供 MCP 客户端复制。

**3. 桌面打包 — `desktop/`**
`npm run dist` 自动 `nuxt generate → 拷贝静态资源 → PyInstaller 打包后端 → electron-builder 生成安装包`，一站式产出 Windows `Setup.exe` / macOS `dmg`。

---

## 六、社区口碑

- **中文社区小爆款**：作为 WeFlow（已 DMCA 下架）的精神续作，被大量微信用户与数据归档需求者关注；README 致谢明确标注"大量功能参考 WeFlow 实现"
- **优点**：UI 还原度高、导出维度全、MCP 接入前瞻、跨 Windows/macOS
- **风险/争议**：⚠️ **未声明开源许可证**（license 字段为 null），仅"学习研究"免责声明，商用/再分发权利不明确；属**法律灰区工具**（微信数据解密），WeFlow 已被 DMCA 下架，本项目可持续性存疑
- **维护**：2026-07 仍在更新，项目年轻（2025-07 创建）

---

## 七、竞品对比 + 核心研判

| 项目 | 平台 | 4.x 支持 | MCP | 状态 |
|------|------|---------|-----|------|
| **WeChatDataAnalysis** | Win/macOS | ✅ | ✅ | 活跃 |
| **WeFlow**（hicccc77）| Win | ✅ | ❌ | ⚠️ DMCA 下架 |
| **Memotrace**（社区继任）| 多 | ✅ | 部分 | 活跃 |
| **wechat-dump-rs** | 跨 | 部分 | ❌ | 库级 |
| **echotrace** | — | ✅ | ❌ | 参考实现 |

**核心研判**：
- ✅ **优势**：4.x 解密 + 高仿 UI + 全量导出 + MCP 接入，功能完整度在同类中领先；跨平台且活跃
- ⚠️ **风险**：无明确开源许可证、涉及微信数据解密的**法律灰区**、前车之鉴（WeFlow 被下架）说明政策风险真实存在；仅限个人自用，切勿商用或处理他人数据
- 💡 **启发**：①「本地数据解密 + 高仿原 App UI + 导出 + MCP」是个人数据工具的高完成度模板；② 把个人工具顺手暴露成 MCP 服务，是让"我的数据"成为 Agent 上下文的低成本路径

---

## 八、关键文件路径速查

| 路径 | 内容 |
|------|------|
| `main.py` | FastAPI 后端入口（:10392, /docs）|
| `src/` | WCDB/SQLite 解密与解析核心 |
| `key_v4.py` | 微信 4.x 密钥处理 |
| `analyze_wechat_databases.py` | 数据库分析入口 |
| `scan.py` | 本地微信实例扫描 |
| `skills/` | MCP 接入相关 |
| `frontend/` | Vue.js 前端（:3000）|
| `desktop/` | Electron 桌面端打包（PyInstaller + electron-builder）|
