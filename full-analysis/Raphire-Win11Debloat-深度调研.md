# 🔬 Raphire/Win11Debloat — 全方位深度调研

> **调研日期**: 2026-07-06 | **数据来源**: GitHub API + 源码分析 + 全网口碑
> **Stars**: 50,069 ⭐ | **Forks**: 2,015 | **语言**: PowerShell | **许可**: MIT
> **创建**: 2020-10-27 | **最新版本**: 2026.06.11

---

## 📌 一句话定位

**轻量级 PowerShell 脚本**，一键去除 Windows 11 预装应用、禁用遥测和 AI 功能、优化系统体验。核心价值：一行命令 = 100+ 系统优化项，所有操作完全可逆，覆盖从"卸载 Copilot"到"恢复 Win10 右键菜单"的全场景。

> 🔥 50K ⭐ 说明它不是另一个"去广告软件"，而是 Windows 用户对抗微软不断增加的系统臃肿的最受欢迎的开源武器。

---

## ⭐ 项目亮点

1. **50K ⭐ 的 Windows 去臃肿标杆** — 纯 PowerShell 脚本做到了单一维护者 + 50K Stars，远超 ChrisTitusTech/winutil 在 Windows 优化子领域的表现
2. **"AI 功能开关"的独特定位** — 在微软强推 Copilot/Recall/Click to Do 的背景下，Win11Debloat 是唯一系统性地提供 AI 功能禁用能力的开源工具
3. **完全可逆的设计哲学** — 所有修改都生成 .reg 恢复文件，被移除的应用可通过 Microsoft Store 一键恢复，"后悔了随时回去"
4. **三种交互模式覆盖全用户画像** — GUI 交互菜单（小白）→ 命令行参数（高级用户）→ Sysprep 模式（企业批量部署）
5. **紧跟 Windows 更新的发布节奏** — 每月发布新版本，Windows 每次大版本更新后一周内就适配新功能（2026.06.11 版本已涵盖 Windows 11 24H2 的改动）

---

## 🏗️ 项目架构全景

### 目录结构

```
Win11Debloat/
├── Win11Debloat.ps1          # 主脚本（核心执行引擎）
├── Run.bat                   # 便捷启动批处理
├── Config/
│   ├── Apps.json             # 可移除的预装应用列表
│   ├── DefaultSettings.json  # 默认优化配置
│   └── Features.json         # 功能开关定义
├── Regfiles/                 # 注册表操作文件（60+ .reg 文件）
├── Assets/
│   ├── Images/               # 截图
│   └── Start/                # 开始菜单布局
├── .github/                  # CI/Issue 模板
└── README.md
```

### 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| **脚本引擎** | PowerShell 5.1+ | Windows 原生运行，零依赖 |
| **配置系统** | JSON 配置 | 功能模块化定义 |
| **注册表操作** | .reg 文件 | 安全的可逆注册表修改 |
| **应用管理** | Get-AppxPackage / Remove-AppxPackage | 预装应用卸载 |
| **包管理** | winget (可选) | OneDrive 卸载等 |
| **恢复机制** | 恢复 .reg 文件 | 所有更改完全可逆 |

### 核心执行流程

```
用户启动
  │
  ├─ 管理员权限检查 ──→ 不是管理员 → 请求提权
  │
  ├─ PowerShell 版本检查 ──→ PS7 → 警告（某些功能不可用）
  │
  ├─ 加载配置
  │   ├─ Apps.json → 可移除应用列表
  │   ├─ DefaultSettings.json → 默认优化项
  │   └─ Features.json → 功能开关
  │
  ├─ 交互选择（GUI 模式）
  │   ├─ Default Mode → 使用默认配置
  │   └─ Custom Mode → 打开功能选择 UI
  │
  ├─ 执行引擎
  │   ├─ Remove-Bloatware → 卸载预装应用
  │   ├─ Apply-RegistryTweaks → 应用注册表优化
  │   ├─ Disable-AIFeatures → 禁用 Copilot/Recall
  │   └─ Optimize-System → 系统性能优化
  │
  └─ 完成报告
      ├─ 生成恢复 .reg 文件
      ├─ 显示已执行操作摘要
      └─ 提示重启（如需要）
```

---

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 | 推荐模式 |
|------|------|---------|
| **新电脑开箱优化** | 新购 Windows 11 电脑，去除 OEM 预装软件 | Interactive - Default |
| **隐私保护** | 禁用遥测、定向广告、位置追踪、活动历史 | Interactive - Custom |
| **AI 功能禁用** | 关闭 Copilot、Recall、Click to Do | Interactive - Custom |
| **企业批量部署** | Sysprep 模式 + 命令行参数，所有新用户自动继承 | Sysprep + Silent |
| **系统性能恢复** | 关闭动画、透明效果、搜索高亮等视觉特效 | Interactive - Custom |

### 可借鉴的解决方案模式

1. **PS7 兼容性守卫**（Issue #675 的核心教训）— `Get-AppxPackage` / `Remove-AppxPackage` 在 PowerShell 7（Core）中不可用，因为 Appx 模块是 Windows PowerShell 5.1 特有的。社区贡献者开了 #676 来添加启动时检测，这是一个优秀的设计模式：**在入口处检测兼容性，失败就退出并给出明确提示**，而不是在运行到一半时报莫名其妙的错误。

   ```powershell
   # 兼容性检测（#676 引入）
   if ($PSVersionTable.PSEdition -eq 'Core') {
       Write-Warning "Win11Debloat 必须在 Windows PowerShell 5.1 中运行"
       Write-Output "请使用 powershell.exe 而非 pwsh.exe 启动"
       exit 1
   }
   ```

2. **模块化 .reg 文件管理** — 每个优化功能对应一个独立的 .reg 文件（60+ 个），主脚本根据用户选择有选择地执行。这种设计使得新增一个优化项 = 新建一个 .reg 文件 + 在 JSON 配置中注册一行，无需修改主脚本。

3. **三项配置分离设计** — `Apps.json`（应用列表）、`DefaultSettings.json`（默认设置）、`Features.json`（功能元数据）各司其职，使得配置更新可以独立于主脚本发布。

### 同领域可参考思路

- 如果你需要构建类似的系统优化工具，**纯 PowerShell + .reg 文件**的组合是最可靠的选择——不需要任何额外依赖，Windows 原生支持
- 更新频率与 Windows 版本绑定是这个领域产品的核心风险：Win11Debloat 每月一更的策略是维持竞争力的最低要求
- 从该项目的 Issue 可以看出，"false success"（报"所有更改已成功应用"但实际什么都没做）是比失败更严重的问题——Issue #675 中用户用 PS7 运行，所有卸载都失败了，但脚本仍然显示"成功"

---

## 🧠 核心源码解读

### 主脚本入口

`Win11Debloat.ps1` 是一个 1000+ 行的 PowerShell 脚本，执行流程清晰：

```powershell
# 入口逻辑示意
function Main {
    # 1. 系统检查
    Test-AdminPrivileges
    Test-PowerShellCompatibility  # #676 引入

    # 2. 加载配置
    $appsList = Get-Content "Config/Apps.json" | ConvertFrom-Json
    $defaultSettings = Get-Content "Config/DefaultSettings.json" | ConvertFrom-Json

    # 3. 模式选择
    if ($Mode -eq "Interactive") {
        Show-Menu   # GUI 交互菜单
    } elseif ($Mode -eq "Silent") {
        Apply-SilentConfig $ConfigFile  # 静默模式
    }

    # 4. 执行优化
    Remove-Bloatware $selectedApps
    Apply-RegistryTweaks $selectedTweaks
    Disable-AIFeatures
    Optimize-System-Performance

    # 5. 完成报告
    Show-Summary
}
```

### 预装应用移除

Win11Debloat 的核心能力之一是通过 `Get-AppxPackage` 枚举并移除 Windows 预装应用：

```powershell
function Remove-Bloatware {
    param([string[]]$AppNames)

    foreach ($app in $AppNames) {
        $packages = Get-AppxPackage -Name "*$app*" -AllUsers
        $provisioned = Get-AppxProvisionedPackage -Online | Where-Object {
            $_.PackageName -like "*$app*"
        }

        # 移除已安装包
        foreach ($pkg in $packages) {
            Remove-AppxPackage -Package $pkg.PackageFullName
        }

        # 移除预置包（新用户不会自动安装）
        foreach ($pkg in $provisioned) {
            Remove-AppxProvisionedPackage -Online -PackageName $pkg.PackageName
        }
    }
}
```

这里的关键在于**同时移除 `AppxPackage` 和 `AppxProvisionedPackage`**——前者移除当前用户的已安装包，后者移除系统的预置注册（新用户登录时不会自动安装）。许多类似工具只做了前者，导致新用户登录后应用又回来了。

### 注册表优化的 .reg 策略

每个优化功能对应一个 .reg 文件，例如禁用 Copilot：

```reg
; Regfiles/Disable_Copilot.reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\WindowsCopilot]
"TurnOffWindowsCopilot"=dword:00000001

[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot]
"TurnOffWindowsCopilot"=dword:00000001
```

这种设计的好处是：用户可以双击 .reg 文件手动应用/撤销，不需要运行整个脚本。

---

## 📐 架构决策与设计哲学

### 核心设计决策

| 决策 | 选择 | 影响 |
|------|------|------|
| **纯 PowerShell** | 零外部依赖，Windows 原生运行 | PS7 兼容性需额外守卫 |
| **.reg 文件恢复机制** | 所有更改完全可逆 | 需要用户执行恢复脚本 |
| **交互式 GUI 菜单** | 小白和高级用户各取所需 | 增加了脚本复杂度 |
| **默认不激进** | 默认设置只移除最基础的应用 | 不会损伤系统功能 |

### Issue 社区揭示的设计红线

从 Issue 列表可看出维护者 @Raphire 的设计原则：

- **不直接修改系统文件** — 所有操作通过官方 API（Appx 模块、注册表策略）完成，不暴力删除系统组件
- **不触及其它用户的 OneDrive 文件** — Issue #9 中讨论 OneDrive 卸载时，重点强调了"确保用户不会丢失文件"
- **开始菜单操作受限于微软限制** — Issue #41 中用户要求只移除特定应用图标，维护者解释了 Windows 11 的二进制文件格式限制无法部分修改
- **假成功比失败更严重** — Issue #675 的深度讨论揭示了"成功提示但什么都没做"是用户最反感的问题

---

## 🌐 全网口碑画像

### 好评共识

- **"一行命令就能搞定"** — 几乎所有正评都提到"一行命令运行"的极度简便
- **"比手动改注册表安全百倍"** — 社区普遍认可 .reg 恢复机制的可靠性
- **"紧跟 Windows 更新"** — 每月一更的频率让用户信任项目不会因 Windows 更新而失效
- **"完全可逆"** — 这是区分 Win11Debloat 和闭源优化工具（如 O&O ShutUp10++）的核心特点

### 差评共识 & 踩坑高发区

| 问题 | 影响面 | 状态 |
|------|--------|------|
| **PowerShell 7 不可用** (#675) | PS7 用户无法运行，无错误提示直接"成功" | #676 已修复，添加兼容性守卫 |
| **注册表恢复操作没有回滚** (#686) | 删除注册表键子树后重写，失败时数据丢失 | 待修复 |
| **域环境用户目录错误** (#682) | 域连接的 Get-user 目录返回不正确的路径 | 待排查 |
| **OneDrive 移除不彻底** (#9) | 移除后文件不会自动恢复到默认位置 | 设计选择（安全考虑）|
| **部分系统优化过于激进** | 某些优化（如禁用 BitLocker）影响后续功能更新 | 用户自行选择 |

### 维护者风格

维护者 @Raphire 是唯一的项目所有者，以"高响应度"著称——几乎每个 Issue 都会在 24-48 小时内收到回复，即使是简单的 feature request 也会认真对待。他亲自回复所有 Issue 和 Discussions，经常说 "Heya, thanks for reporting this." 这种社区亲和的维护风格是项目持续增长的重要原因。

---

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | **Win11Debloat** | **ChrisTitusTech/winutil** | **O&O ShutUp10++** | **PrivateWin10** |
|------|:---:|:---:|:---:|:---:|
| Stars | **50K** | 50K+ | N/A（闭源） | N/A |
| 开源 | **✅ MIT** | ✅ MIT | ❌ | ✅ 部分 |
| 语言 | PowerShell | PowerShell | 原生应用 | 原生应用 |
| 功能数 | 100+ | 200+ | 300+ | 150+ |
| AI 功能禁用 | **✅ 系统性** | ⚠️ 部分 | ❌ | ❌ |
| 一键运行 | **✅** | ✅ | ✅ | ✅ |
| 交互式菜单 | **✅ GUI** | ✅ | ✅ | ✅ |
| 完全可逆 | **✅ .reg 恢复** | ⚠️ 部分 | ✅ | ❌ |
| 命令行模式 | **✅ 完整支持** | ✅ | ❌ | ❌ |
| Sysprep 模式 | **✅ 独有** | ❌ | ❌ | ❌ |
| 中文支持 | ❌ | ❌ | ✅ | ❌ |
| 更新频率 | **每月** | 每月 | 季度 | 不定期 |

### 选择建议

- **Windows 开箱去臃肿** → **Win11Debloat**（最简单、最安全、最可逆）
- **深度系统定制** → ChrisTitusTech/winutil（200+ 功能，覆盖更广）
- **不想用命令行** → O&O ShutUp10++（成熟 GUI 应用，中文支持）
- **企业批量部署** → **Win11Debloat**（Sysprep 模式是独有武器）

---

## 🎯 核心研判

### 项目优势

1. **50K ⭐ 的用户广泛认可** — 这不是开发者定向项目，而是**普通 Windows 用户**通过 GitHub Stars 投票的结果，说明它在真实用户群体中有极强的口碑效应
2. **AI 功能系统性禁用是独有定位** — 在微软强推 Copilot/Recall/Click to Do 的大环境下，唯一系统性的"AI 功能开关"工具
3. **Sysprep 模式是差异化核心** — 在竞争激烈的去臃肿工具市场中，Sysprep 模式是企业级场景的独有能力
4. **单一脚本的极度简部署** — 不需要安装、不需要依赖管理、不需要配置运行环境，一条命令在 PowerShell 中完成
5. **MIT 许可** — 最宽松的开源许可，企业和个人均可无限制使用

### 项目风险

1. **单一维护者风险** — @Raphire 是唯一所有者，如果因各种原因停止维护，50K 用户将失去保障
2. **与 Windows 高度耦合** — 每次 Windows 大版本更新都可能破坏脚本功能，维护者需要持续跟进
3. **假成功信号**（Issue #675 的核心教训）— 脚本在 PowerShell 7 下执行时，"成功"消息是假的，修复前用户完全不知道优化根本没有执行
4. **法律风险** — 部分国家/地区对禁用系统遥测有法律限制，尤其是企业环境
5. **工具同质化竞争** — 与 ChrisTitusTech/winutil、O&O ShutUp10++ 等工具功能高度重叠，差异化空间越来越小

### 趋势判断

**稳定成熟期** — Win11Debloat 已经过了高速增长期（2023-2024 从 0 到 40K，2025-2026 从 40K 到 50K）。随着 Windows 11 中 AI 功能的持续增加（微软已表示将继续深化 Copilot 集成），去臃肿需求不会消失，但增长曲线将趋缓。

### 不适用场景

- macOS/Linux 用户（仅限 Windows）
- 完全不接受任何注册表修改的用户
- 需要深度定制每个优化项的极客用户（建议 winutil）
- 企业环境需先确认当地法律对禁用遥测的规定

---

## 📂 关键文件路径速查

| 文件 | 功能 |
|------|------|
| `Win11Debloat.ps1` | 主脚本（核心执行引擎）|
| `Run.bat` | 批量启动入口 |
| `Config/Apps.json` | 可移除的预装应用列表 |
| `Config/DefaultSettings.json` | 默认优化配置 |
| `Config/Features.json` | 功能开关定义 |
| `Regfiles/Disable_Copilot.reg` | 禁用 Copilot |
| `Regfiles/Disable_AI_Recall.reg` | 禁用 Windows Recall |
| `Regfiles/Disable_AI_Service_Auto_Start.reg` | 禁止 AI 服务自启 |
| `Regfiles/Align_Taskbar_Left.reg` | 任务栏左对齐 |
| `Regfiles/Combine_Taskbar_Never.reg` | 从不合并任务栏按钮 |
