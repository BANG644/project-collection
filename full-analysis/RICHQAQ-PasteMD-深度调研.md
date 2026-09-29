# RICHQAQ/PasteMD 深度调研

> 调研日期：2026-09-30 ｜ 数据源：gh API（README / 目录树 / 源码 app.py）｜ 定位：一键把 Markdown 与网页 AI 对话完美粘贴进 Word、WPS、Excel 的桌面效率工具

## 一、项目定位（一句话）

**PasteMD** 是一个 Python 桌面效率工具：复制一段 Markdown 或网页里的 AI 对话（ChatGPT/DeepSeek 等），按全局热键一键把它以「带样式的富文本」直接粘贴进 Word / WPS / Excel——保留标题、代码块、表格、列表的排版，而不是丢格式的纯文本。

## 二、项目亮点（差异化）

1. **「复制即富文本」**：把 Markdown/AI 回复转成带样式的富文本，通过 HTML 剪贴板格式直接粘进 Office，解决「从 ChatGPT 复制到 Word 全乱」的痛点。
2. **跨平台桌面集成**：Windows / macOS 托盘常驻 + 全局热键（默认 `Ctrl+Shift+B`）+ 单实例；macOS 用本地 IPC / Reopen 处理「再次点击图标唤起设置页」。
3. **本地优先 + 自托管**：可配置本地 LLM / 翻译端点，数据不出本机（隐私友好）；同时支持把结果导出到 Word/WPS/Excel。
4. **面向 AI 对话场景**：专门针对「网页 AI 对话」优化（代码块、表格、多级标题的样式还原），比通用 Markdown 粘贴更贴需求。

## 三、核心架构

- `PasteMD.py` — 历史遗留入口（仅 `from pastemd.app.app import main`）。
- `pastemd/app/app.py` — 应用主入口：DPI 感知、`check_single_instance()` 单实例锁、依赖注入容器 `Container`、`tk.Tk()` 隐藏主窗口 + `ui_queue` 把 UI 操作统一调度到主线程、热键监听、托盘运行、后台版本检查、macOS Dock/IPC/Reopen 适配。
- `pastemd/app/wiring.py`（`Container`）— 依赖注入装配：`hotkey_runner`、`tray_runner`、`notification_manager`、`tray_menu_manager` 等单例。
- `pastemd/core/`（state 全局状态、singleton 单实例锁）、`pastemd/service/notification/manager.py`（通知）、`pastemd/config/loader.py`（配置）、`pastemd/utils/`（dpi、system_detect、macos/{ipc,dock,reopen}）、`pastemd/i18n`（中英文）。
- 打包：`build_dist_dmg.sh`、`build_macos.sh`、`assets/`（图标、macOS InfoPlist）。

## 四、应用场景与启发

- **场景**：把 AI 对话/技术文档快速整理进 Word 周报、WPS 方案、Excel 清单；研究员/学生/职场人日常「复制 → 一键落盘到 Office」。
- **启发**：
  - 「全局热键 + 托盘 + 单实例 + UI 队列归主线程」是 Python 桌面小程序的标准骨架，PasteMD 的 `app.py` 把这套时序写得清楚，可当模板抄。
  - 它的价值不在算法，而在「把已有能力（Markdown 解析 + 剪贴板 HTML 格式）组合成顺手的工作流」——这正是个人效率工具的典型形态：做薄、做准、做进肌肉记忆。

## 五、源码深度解读（核心模块）

**1. `app.py` 的 `main()`：Python 托盘程序的经典时序**

```python
# pastemd/app/app.py (节选)
if not check_single_instance():           # 单实例锁
    log("Application is already running"); sys.exit(1)
container, _ = initialize_application()  # 加载配置 + 依赖注入
ui_queue: queue.Queue = queue.Queue(); app_state.ui_queue = ui_queue
root = tk.Tk(); root.withdraw()          # 隐藏主窗口，仅留托盘
hotkey_runner = container.get_hotkey_runner(); hotkey_runner.start()
# ... 启动托盘（macOS 主线程 setup，Windows 后台线程 run）
def process_ui_queue():                   # 100ms 轮询，确保 Tk 操作都在主线程
    while True:
        task = ui_queue.get_nowait();  ...; task(); break
    root.after(100, process_ui_queue)
root.after(100, process_ui_queue); root.mainloop()
```

把热键回调、托盘菜单、IPC 命令全部 `ui_queue.put(...)` 投递到主线程执行，规避了 Tk/UI 的跨线程崩溃——是 Python GUI 工具的稳定化关键。

**2. 跨平台的细节处理**

- Windows：启动时 `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RichQAQ.PasteMD")`，保证托盘/任务栏正确归属。
- macOS：Dock 默认隐藏，`start_server(_handle_command)` 接收「再次打开 App」的 IPC 命令唤起设置页；`install_reopen_handler` 捕获系统 Reopen 事件——解决 macOS「重复点击图标不新建进程但要唤起窗口」的怪癖。

## 六、社区口碑

- 5.3k⭐（AGPL-3.0，仓库 LICENSE 为 AGPL-3.0 文本），中文社区（公众号 / 小红书）有推广；提供 Windows / macOS 安装包（含 dmg 构建脚本 `build_dist_dmg.sh`）。
- 开源免费，定位精准（「一键粘贴 Markdown/AI 对话到 Office」）；文档含中/英/日多语言 README（`docs/md/README.en.md`、`README.ja.md`）。

## 七、竞品对比 + 核心研判

| 维度 | PasteMD | Typora/MarkText 导出 | Pandoc | 直接复制网页 |
|---|---|---|---|---|
| 一键热键粘贴到 Office | ✅ | ❌（需导出再打开） | ❌（命令行） | ⚠️ 丢格式 |
| AI 对话/代码块/表格样式还原 | ✅ 针对性优化 | 一般 | 一般 | ❌ |
| 本地隐私 | ✅ | ✅ | ✅ | ✅ |
| 跨平台桌面集成 | ✅ | ✅ | ✅（CLI） | — |

**研判**：对「把 AI 对话 / Markdown 快速整理进 Office 文档」是务实、顺手的小工具，定位精准、桌面集成到位，比 Pandoc 对普通用户友好得多。风险：依赖系统剪贴板 / Office COM，macOS 与 Windows 行为差异大（macOS 需辅助功能权限、Windows 靠剪贴板 HTML 格式）；复杂表格 / 数学公式还原有限；AGPL-3.0 对闭源 SaaS 化有传染性，二次分发需注意。整体属于「个人效率工具」而非「平台型项目」，长期价值取决于维护活跃度。

## 八、关键文件路径速查

- 仓库根：`https://github.com/RICHQAQ/PasteMD`
- 主入口：`PasteMD.py`（legacy）、`pastemd/app/app.py`（真实逻辑）
- 依赖注入：`pastemd/app/wiring.py`（`Container`）
- 核心态/单例：`pastemd/core/state.py`、`pastemd/core/singleton.py`
- 通知/配置/工具：`pastemd/service/notification/manager.py`、`pastemd/config/loader.py`、`pastemd/utils/`（dpi / system_detect / macos/{ipc,dock,reopen}）
- 国际化：`pastemd/i18n/`
- 打包：根 `build_dist_dmg.sh`、`build_macos.sh`、`assets/`
