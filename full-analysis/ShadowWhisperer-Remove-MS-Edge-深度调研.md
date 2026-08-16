# Remove-MS-Edge 深度调研报告

> **仓库**: [ShadowWhisperer/Remove-MS-Edge](https://github.com/ShadowWhisperer/Remove-MS-Edge)  
> **Stars**: 5,419 | **Forks**: 203 | **Issues**: 8 | **语言**: Batchfile / Python  
> **许可**: CC0-1.0（公共领域 dedication）  
> **创建**: 2020-12-09 | **最后推送**: 2026-08-05  
> **Releases**: 2.3 (2025-12-11, ~559k 下载) / 2.2 / 2.1 / 2.0  
> **调研日期**: 2026-08-17（重写升级：补全源码解读 / 竞品 / 核心研判）

---

## 一、项目全景

Remove-MS-Edge 是一个帮助用户**彻底卸载 Microsoft Edge 浏览器（含 AppX 包、WebView2 残留、计划任务、服务、注册表项）**的开源工具集。它提供三种分发通道——预编译 EXE、Python 源码、批处理脚本——覆盖从"双击即用"到"可审计脚本"的全场景需求。

Edge 并非普通应用，而是深度嵌入 Windows 的"系统组件"：普通「应用和功能」卸载会被系统拒绝或自动回装。该工具的本质是**把微软自己的卸载机制（setup.exe 的隐藏参数）+ 社区手写的注册表/文件清扫组合成一条完整链路**。

### 核心数据

- **5,419⭐ / 203 Fork / 8 Open Issues**（长周期低 issue，项目稳定）
- **三通道分发**：预编译 EXE（含无终端静默版）/ Python 源码（edge.py）/ 批处理脚本（Edge.bat / Both.bat / Edge-Appx.bat）
- **CC0-1.0 许可**：公共领域奉献，无版权负担，可任意嵌入
- **v2.3 单版本 559k 下载**：Windows 去 Edge 刚需的真实规模佐证
- **WebView2 依赖感知**：明确列出哪些应用依赖 WebView，并提供"只删 Edge 保留 WebView"的模式

---

## 二、项目亮点（差异化）

1. **三通道分发，覆盖全场景**：预编译 EXE 给小白、"无终端版"给任务计划静默执行、Python 源码与批处理给想审计/改造的 Power User——同类工具通常只有一种形态。
2. **UAC 自提权 + 防炸弹（UAC bombing）保护**：Edge.bat 用 PowerShell `Start-Process -Verb RunAs` 自我提权，并检测内建管理员账户的 SID 前缀（`S-1-5-`），避免自我提权陷入无限递归；对自动化场景还提供 `-auto` 参数跳过确认。
3. **版本感知的 EdgeCore 清扫（edgecore_cleanup）**：先读注册表拿到**当前在用的 WebView2 版本号**，只删 EdgeCore 下**不匹配**该版本的子目录，**绝不误删仍在被 WebView2 依赖的运行时**——这是多数竞品会踩的坑。
4. **下载即校验**：Edge.bat 从 GitHub raw 拉取 setup.exe / SQLite.dll 时，用**硬编码 SHA-256 哈希**（如 `setup.x64.exe` = `0950336e…f636e7`）做完整性校验，防止中间人篡改。
5. **WebView2 注册表键备份/恢复**：删除前先 `reg export` 备份 `{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`（WebView2 的 EdgeUpdate GUID），删除后立刻 `reg import` 还原，把"删 Edge"与"保 WebView"精确解耦。

---

## 三、核心架构

仓库是**多分发形态共享同一套"卸载语义"**的结构，而非单一程序：

```
Remove-MS-Edge/
├── README.md                       # 主文档 + 下载链接 + WebView 依赖警告
├── LICENSE                         # CC0-1.0（7KB）
├── Batch/
│   ├── Edge.bat                    # 仅移除 Edge（含 AppX），865 行，自提权
│   ├── Both.bat                    # 移除 Edge + WebView（调用 Edge + WebView 逻辑）
│   └── Edge-Appx.bat               # 仅移除 AppX 版 Edge（保留系统 Chromium 内核）
└── _Source/
    ├── edge.py                     # Python 主逻辑（307 行），pyinstaller 打包源
    ├── setup.exe / setup.x64.exe / setup.x86.exe  # 微软官方 setup.exe
    ├── System.Data.SQLite.x64.dll  # 仅 Edge.bat 的 file_obtain 校验用
    └── icon.ico                    # EXE 图标
```

**两套独立卸载引擎**：

| 引擎 | 主力手段 | 适用分发 | 关键差异 |
|------|---------|---------|---------|
| **edge.py** | 调用微软 `setup.exe --uninstall --system-level --force-uninstall` | EXE / Python 源码 | 借微软自己之手卸载，最"官方"；AppX 残留用 PowerShell + winreg 补刀 |
| **Edge.bat** | 手动 `reg delete` + `takeown/icacls` + `rd` 逐层拆除 | 批处理脚本 | 不依赖 setup.exe 主卸载，强攻注册表/文件系统；含架构检测与 SHA 校验下载 |

二者在"收尾"上重合：都清计划任务（`schtasks`）、服务（`sc delete edgeupdate/edgeupdatem/MicrosoftEdgeElevationService`）、桌面/开始菜单快捷方式、AppX 目录（`SystemApps\Microsoft.MicrosoftEdge*`、`WindowsApps\Microsoft.MicrosoftEdge*`）。

---

## 四、应用场景与启发

**直接用**：Windows 用户想用 Chrome/Firefox 替代 Edge；系统精简/去广告 Power User；企业环境用"无终端版"静默移除 Edge（需配套 `Fix-WinUpdates` 规避更新循环）。

**对同类"清理/卸载"类工具的启发**：

- **「借官方卸载器之力」是最高效的反集成策略**：Edge 之所以难删，是因为微软把它当系统组件。edge.py 的精髓是用 `--force-uninstall --system-level` 这组合隐藏参数（微软 setup.exe 文档未公开，社区逆向得来），让官方卸载器自己把 Edge 拆干净——比纯手写删文件稳健得多。**同类启发**：任何"厂商不愿让你卸载的东西"，优先找它的官方卸载 CLI 隐藏开关。
- **「删 A 但保共享依赖 B」的版本感知清扫范式值得复刻**：`edgecore_cleanup` 先查注册表拿到 WebView2 在用版本，再只删 EdgeCore 里版本不匹配的目录。这个"读依赖版本 → 差分删除"模式可迁移到任何"需移除某组件但保留其共享运行时"的场景（如删旧版运行时、清理 SDK 但保留构建链）。
- **批处理也能工程化**：Edge.bat 用 SHA-256 校验下载物、防 UAC 递归炸弹、备份/恢复关键注册表键——证明即使是最朴素的 `.bat` 也能做出"安全可审计"的工程实践，不一定要上 PowerShell/Python。

**⚠️ 风险边界（用户必须知道）**：卸载 Edge 可能触发 Windows Update 循环失败（官方已知问题，工具建议"先装 Edge→装完所有更新→再删"）；PowerToys、Xbox App、Roblox、Windows Mail 等依赖 WebView2 的应用会受影响，需重装 WebView2 Runtime；微软后续更新可能重新注入 Edge。

---

## 五、源码深度解读

### 模块 1：`edge.py` —— 借微软 setup.exe 自卸（第 50–77 行）

Python 版的核心逻辑极简：探测 Edge 安装标志（pwahelper.exe 是否存在），存在就**直接调用微软自己的 setup.exe 带上隐藏强制卸载参数**；WebView 同理带 `--msedgewebview`；AppX 残留则交给 PowerShell + 注册表。

```python
# Edge
for p in [os.path.join(PROGRAM_FILES_X86, "Microsoft\\Edge\\Application\\pwahelper.exe"), ...]:
    if os.path.exists(p):
        print("Removing Microsoft Edge")
        cmd = [src, "--uninstall", "--system-level", "--force-uninstall"]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        os.system("timeout /t 2 >nul")
        break

# Edge / MicrosoftEdgeDevTools (Appx Packages)
user_sid = subprocess.check_output(["powershell", "...Translate(...SecurityIdentifier...).Value"]) ...
output = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    'Get-AppxPackage -AllUsers | Where-Object {$_.PackageFullName -ilike "*MicrosoftEdge*"} | Select-Object -ExpandProperty PackageFullName'])
edge_apps = [app.strip() for app in output.decode().strip().split('\r\n') if app.strip()]
base_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore"
for app in edge_apps:
    for path in [f"{base_path}\\EndOfLife\\{user_sid}\\{app}",
                 f"{base_path}\\EndOfLife\\S-1-5-18\\{app}",
                 f"{base_path}\\Deprovisioned\\{app}"]:
        winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, path, 0, access_flag)
```

要点：AppX 包不靠 `Remove-AppxPackage`，而是**在 `AppxAllUserStore` 下写入 `EndOfLife` / `Deprovisioned` 标记键**，让系统认为该包已终结——这是绕过"系统保护不让删"的注册表级技巧。提权则走 `ctypes.windll.shell32.IsUserAnAdmin()` 检测，未提权直接提示退出（不自动提权，避免静默风险）。

### 模块 2：`Edge.bat` —— UAC 自提权 + 防炸弹（第 50–79 行）

批处理版最精巧的是**自提权且不会无限递归**：

```bat
REM When 1st arg looks like valid NT_AUTHORITY SID, assume elevation by script (prevent infinite loop aka UAC bombing)
if /i "%USER_SID:~0,6%" equ "S-1-5-" (
    echo Built-in Admin account possibly corrupted & echo. & pause & exit /b %ISSUE_UAC%
)
...
REM Elevate with psl
echo Start-Process -Verb RunAs """$env:COMSpec""" "%ecm% """"%~0"" ""%EXEC_SID%"""""|powershell -noprofile - %bat_log%
...
REM For automaters: when Built-in Admin account enabled, specify "-auto" as 1st argument to bypass confirmation
if /i "%~1" equ "-auto" goto uac.done
choice /c yn /n /m "Logged as Admin? [Y,N]"
```

要点：`Start-Process -Verb RunAs` 以管理员身份重启自身；通过传入 `EXEC_SID` 并在重启后检测 SID 前缀来判定"是否由脚本自身提权"，从而打断自我提权递归（UAC bombing）。`-auto` 为任务计划等无人值守场景跳过交互确认。

### 模块 3：`edgecore_cleanup` —— 版本感知 EdgeCore 清扫（第 562–597 行）

这是整套工具里**最能体现"清理而不破坏"工程素养**的片段：

```bat
:edgecore_cleanup
if not exist "%x86ProgramsFolder%\Microsoft\EdgeCore" goto _edgecore_cleanup.end
set "webview2_ver="
for /f "tokens=2,*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-...}" /v pv ...') do set "webview2_ver=%%b"
... (依次查 native / 卸载项 作为兜底) ...
if not defined webview2_ver (
    echo webview2_ver not found - skipping EdgeCore cleanup to avoid breaking WebView2
    goto _edgecore_cleanup.end
)
for /d %%d in ("%x86ProgramsFolder%\Microsoft\EdgeCore\*") do (
    if /i not "%%~nxd" equ "%webview2_ver%" (
        rd /s /q "%%~d"
    ) else (
        echo keeping ^(in use by WebView2^): "%%~d"
    )
)
```

要点：先从注册表取出**当前在用的 WebView2 版本** `webview2_ver`；拿不到就**整体跳过**（宁可不删也不冒险）；拿到后只删 EdgeCore 下版本号不匹配的子目录，保留 WebView2 正在用的那个。配合前文的 `{F3017226-...}` GUID 键备份/恢复，实现"删 Edge 但 WebView2 毫发无伤"。

---

## 六、社区口碑

- **规模证据**：v2.3 单版本 ~559k 下载，5.4k⭐、CC0 许可——是 Windows 去 Edge 赛道里受众最广的开源方案之一，长期位居相关搜索前列。
- **稳定性**：2020 年创建、2026 仍活跃推送，Open Issues 仅 8 个，社区反馈以"好用/求增功能"为主，无明显信任危机。
- **已知共识痛点**：① Edge 卸载后 Windows Update 可能循环失败（工具已在 README 明确提示规避流程）；② 依赖 WebView2 的第三方应用（PowerToys、Xbox、Roblox 等）会受影响——这是"删 Edge"的固有代价，非工具缺陷。
- **信任底色**：CC0 + 开源可审计，相比闭源一键卸载器（如下文 EdgeRemover）更受技术用户信赖；edge.py 与 Edge.bat 均可逐行审阅，无隐藏行为。

---

## 七、竞品对比 + 核心研判

### 竞品对比

| 维度 | Remove-MS-Edge | EdgeRemover | Winget 卸载 | Win10Debloat / Win11Debloat | O&O ShutUp10 |
|------|---------------|-------------|------------|------------------------------|--------------|
| 开源 | ✅ CC0 | ❌ 闭源 | —（官方 CLI） | ✅ PowerShell 脚本 | ❌ 闭源免费 |
| 多通道（EXE/脚本/静默） | ✅ | ✅ | ❌ | ✅ 脚本 | ✅ |
| WebView 可选保留 | ✅（edgecore_cleanup 版本感知） | ❌ 全删 | ❌ | 部分 | ❌ |
| 下载 SHA-256 校验 | ✅ | ❌ | — | ❌ | — |
| UAC 自提权+防炸弹 | ✅ | ✅ | ✅（需管理员） | ✅ | ✅ |
| WebView 依赖警告 | ✅ | ❌ | ❌ | 部分 | ❌ |
| 更新失败循环修复 | ✅（Fix-WinUpdates 配套） | ❌ | ❌ | ❌ | ❌ |

### 核心研判

**优势**
1. **真正的刚需 + 最高可达性**：大量 Windows 用户想彻底移除 Edge，工具三通道 + CC0 让"会用电脑就能删"。
2. **工程素养超出体量**：SHA-256 校验、UAC 防递归炸弹、WebView2 版本感知清扫、GUID 键备份恢复——这些在"卸载小工具"里属于罕见的安全实践。
3. **双引擎互补**：edge.py 借官方 setup.exe 自卸（稳），Edge.bat 强攻注册表/文件（彻底），两种路线互补覆盖不同环境。

**风险 / 不足**
1. **功能单一且受微软反向约束**：Edge 越嵌越深，微软每次大版本都可能在更新里重新注入；工具是"追着微软打补丁"，长期是猫鼠游戏。
2. **批处理可维护性差**：Edge.bat 已达 865 行，手写注册表扫描路径（`reg_SFT_paths_scn` 等）受批处理变量 8167 字符上限约束，后续扩展笨重——不如迁 PowerShell。
3. **误用成本高**：普通用户不理解 WebView2 依赖，删 Edge 后 PowerToys/Xbox 等失灵，工具有警告但仍属"高危操作"。

**趋势判断**
- 微软持续强化 Edge 的"系统组件"定位（甚至通过 Accumulate/Update 回装），独立卸载工具的生存空间会被持续挤压，但刚需不会消失。
- 竞品里 **Win10Debloat/Win11Debloat 类 PowerShell 脚本** 因可组合、可审计、易贡献，正成为社区新主流；本仓库若把 865 行 .bat 重构为模块化 PowerShell，长期生命力更强。

**应用启发（给同类需求）**
-  uninstall 类工具的最高杠杆是"**找到官方卸载器的隐藏开关**"，而非手写删文件。
- "**删 A 保共享依赖 B**"务必做版本感知（读注册表在用版本 → 差分删除），这是避免破坏系统的关键模式。
- 即使是 .bat 也能做 SHA 校验 + 备份恢复，安全实践不依赖语言高级。

---

## 八、关键文件速查

| 文件 | 说明 | 关键行 |
|------|------|--------|
| `_Source/edge.py` | Python 主逻辑（307 行），pyinstaller 打包源 | 50–77 行：setup.exe 强制卸载 + AppX 标记键 |
| `Batch/Edge.bat` | 仅移除 Edge（含 AppX），865 行，自提权 | 50–79 行 UAC 自提权/防炸弹；562–597 行 edgecore_cleanup |
| `Batch/Both.bat` | 移除 Edge + WebView | 调用 Edge + WebView 逻辑 |
| `Batch/Edge-Appx.bat` | 仅移除 AppX 版 Edge | 保留系统 Chromium 内核 |
| `_Source/setup.x64.exe` | 微软官方 setup.exe（x64），SHA `0950336e…` | edge.py / Edge.bat 的卸载执行体 |
| `_Source/System.Data.SQLite.x64.dll` | Edge.bat `file_obtain` 校验用 | SHA `1b3742c5…` |
| `README.md` | 主文档 + 下载链接 + WebView 依赖列表 | — |
| `LICENSE` | CC0-1.0（7KB） | 公共领域奉献 |

> **本次升级说明**：旧报告（2026-06-19，4.2KB）仅覆盖功能表 + 浅竞品，缺源码解读与核心研判。本报告补全三通道架构、edge.py 的 setup.exe 隐藏参数调用、Edge.bat 的 UAC 防炸弹与 `edgecore_cleanup` 版本感知清扫等真实源码引用，并深化竞品对比（新增 Win10Debloat / O&O ShutUp10）与核心研判。星标 5,210→5,419、许可明确为 CC0-1.0（旧报告误标"未明确"）。
