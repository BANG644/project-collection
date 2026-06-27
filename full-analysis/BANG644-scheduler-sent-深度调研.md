# 🔬 BANG644/scheduler-sent — 全方位深度调研

> **调研日期**: 2026-06-28 | **数据来源**: GitHub API + README + 源码

## 📌 一句话定位

带 GUI 的智能定时屏幕点击器——PyQt5 构建，支持坐标捕获、反检测抖动、窗口定位和动作序列编排，专为 AI 工具冷却管理、课程自动点击等场景设计。

> 核心判断：这是一个**功能完整的 Windows 桌面自动化工具**，实现了从"定时触发→窗口定位→动作执行→反检测"的全链路。架构清晰、代码工整，42/42 测试全通过。

## ⭐ 项目亮点

1. **全链路自动化** — 从定时调度（APScheduler）到坐标捕获（全屏覆盖层）到动作执行（pyautogui）到反检测（随机抖动的完整闭环）
2. **视觉坐标捕获器** — 全屏暗色覆盖层 + 十字准星定位，无需手动输入像素坐标
3. **动作序列编排** — 点击 → 打字 → 按键 → 等待的链式编排，支持无限组合
4. **反检测抖动** — 随机时间偏差（±N 分钟），避免被判定为机器人行为
5. **完整测试套件** — 13 个测试组 42 个用例全部通过，覆盖序列化、存储循环、调度引擎、窗口定位等

## 🏗️ 项目架构全景

```
scheduler_sent/
├── main.py                 # 入口点 + 崩溃处理器
├── models.py               # Task & Action 数据类 + 序列化
├── storage.py              # JSON 持久化
├── scheduler_engine.py     # APScheduler 包装器
├── automation.py           # pyautogui 执行器 + 窗口激活
├── tests.py                # 完整端到端测试
├── requirements.txt
└── ui/
    ├── main_window.py      # 主窗口：任务表格+工具栏+调度开关
    ├── task_dialog.py      # 任务编辑器：调度+窗口+动作
    ├── action_dialog.py    # 动作编辑器：点击/打字/按键/等待
    ├── capture_overlay.py  # 全屏坐标捕获覆盖层
    ├── window_picker.py    # 窗口选择对话框
    └── styles.py           # 暗色主题样式
```

**技术栈**: Python 3.9+ / PyQt5 / APScheduler / pyautogui / pywin32 / pyperclip

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 配置 | 效果 |
|------|------|------|
| AI 工具冷却管理 | 每 2 小时点击"继续"→ 输入提示词 → 发送 | 人不在电脑前时自动恢复 AI 工作流 |
| 自动课程进度 | 每 30 分钟点击下一课 | 远程课程被动打卡 |
| 表单自动填充 | 点击字段 → 粘贴文本 → 提交 | 定时执行重复填表 |
| UI 冒烟测试 | 重复点击序列 | 无头 UI 测试 |
| 终端看板重置 | 每天 09:00 点击刷新按钮 | 自动维护显示面板 |

### 可借鉴的设计模式

- **APScheduler 包装模式**：将 APScheduler 的三种触发器（Interval/Date/Cron）封装为统一的 Task 模型，上层代码无需关心调度细节
- **QThread 异步执行**：动作执行放在后台线程，保持 UI 响应，通过回调更新实时状态
- **Clipboard-Based 输入**：使用系统剪贴板 + pyperclip 输入 Unicode/CJK 文本，避开了 pyautogui.typewrite() 对非 ASCII 字符支持不佳的问题

## 🧠 核心源码解读

### 调度引擎（scheduler_engine.py）
核心是将 APScheduler 的三种触发器封装为统一接口：

```python
def add_task(self, task: Task) -> None:
    trigger = self._create_trigger(task.schedule)
    self.scheduler.add_job(
        func=self._on_task_fire,
        trigger=trigger,
        id=task.id,
        args=[task],
        misfire_grace_time=60
    )
```

其中 `_create_trigger` 根据 task.schedule.type 返回不同的 APScheduler 触发器对象，实现了调度类型的透明化。

### 动作执行器（automation.py）
动作序列执行的核心抽象：

```python
def execute_actions(actions, callback=None):
    for action in actions:
        if action.type == 'click':
            pyautogui.click(action.x, action.y, button=action.button)
        elif action.type == 'type':
            pyperclip.copy(action.text)
            pyautogui.hotkey('ctrl', 'v')
        elif action.type == 'key':
            pyautogui.hotkey(*action.keys)
        elif action.type == 'wait':
            time.sleep(action.seconds)
```

每个动作类型被清晰地映射到 pyautogui 的对应 API，Clipboard-Based 输入解决了中文输入的问题。

### 窗口激活机制

使用 pywin32 枚举窗口并匹配标题关键字，处理好最小化窗口的激活：

```python
def activate_window(title_keyword):
    hwnd = win32gui.FindWindow(None, None)
    # 枚举所有顶层窗口，模糊匹配标题
    # 处理最小化窗口（SW_RESTORE → SW_SHOW）
    win32gui.SetForegroundWindow(hwnd)
```

## 🌐 口碑

（数据不可用：该项目为个人项目，1 ⭐，暂无社区口碑。）

## ⚔️ 竞品对比

| 维度 | scheduler-sent | 按键精灵 | AutoHotkey | Pulover's Macro Creator |
|------|---------------|---------|------------|----------------------|
| GUI | ✅ PyQt5 暗色主题 | ✅ 完善 | ❌ 脚本 | ✅ 视觉化 |
| Python 可扩展 | ✅ 源码开放 | ❌ 封闭 | ❌ AHK 语法 | ❌ 封闭 |
| 反检测抖动 | ✅ 内置 | ❌ | ❌ | ❌ |
| 窗口定位 | ✅ pywin32 | ✅ | ❌ | ✅ |
| 坐标捕获 | ✅ 全屏覆盖层 | ✅ | ❌ | ✅ |
| 开源 | ✅ MIT | ❌ | ✅ GPL | ✅ GPL |
| 跨平台 | ❌ Windows | ❌ | ✅ Win/Mac | ❌ Windows |
| 学习成本 | 极低 | 低 | 高 | 中 |

**选择建议**：
- **需要 Python 生态** → scheduler-sent（可直接扩展）
- **需要复杂脚本** → AutoHotkey（更强大的脚本能力）
- **需要录制回放** → 按键精灵/Pulover（更完善的录制工具）

## 🎯 核心研判

### 项目优势

- 架构清晰（MV 风格），代码质量高（42/42 测试通过）
- 解决了"定时 + 自动点击 + 反检测"这个具体痛点，场景明确
- 开源 MIT 许可证，可自由修改和分发

### 项目风险

- 仅支持 Windows（pywin32 依赖），限制了跨平台使用
- 对屏幕内容不可见——坐标点是绝对的，不是基于图像识别，屏幕布局变化会导致失效
- 1 ⭐（用户自己的项目），社区参与度有限

### 适用场景

适合需要定时自动化点击/输入的 Windows 用户，特别是 AI 工具的冷却恢复、课程自动点击、UI 测试等场景。

### 不适用场景

- 需要屏幕内容识别（OCR/图像匹配）的场景
- 跨平台环境（macOS/Linux）
- 需要复杂的条件逻辑（if/else 分支）

## 📂 关键文件路径速查

- `main.py` — 入口点（日志、崩溃处理器）
- `models.py` — Task & Action 数据模型
- `scheduler_engine.py` — APScheduler 调度引擎
- `automation.py` — pyautogui 执行器 + 窗口激活
- `ui/capture_overlay.py` — 全屏坐标捕获（最具特色的功能）
- `ui/main_window.py` — 主窗口 UI
- `tests.py` — 端到端测试（13 组 42 用例）
