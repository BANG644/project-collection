# Windhawk 深度调研报告

> 调研日期：2026-07-04 | 仓库：ramensoftware/windhawk | 语言：C++ | 许可：GPL-3.0

---

## 📌 一句话定位

**Windhawk 是一个面向 Windows 程序的开放模组市场（mod marketplace）——通过 DLL 全局注入技术，让用户以安装/卸载"模组"的方式任意修改 Windows 系统行为，而无需等待微软官方更新。**

---

## ⭐ 项目亮点（5条差异化）

| # | 亮点 | 差异化价值 |
|---|------|-----------|
| 1 | **模组市场（Mod Marketplace）架构** | 不是单一功能的"优化工具"，而是一个开放的模组平台——社区开发者可在其上自研 mod 并发布。类比于 Firefox 扩展商店之于浏览器。 |
| 2 | **VSCode 插件化 UI** | 其用户界面竟是一个 VSCode 扩展（`vscode-windhawk`），这在系统工具中极为罕见。用户通过 VSCode 的 webview 浏览/安装/管理 mod，编辑器本身提供编译、调试、符号搜索等能力。 |
| 3 | **非破坏性修改** | 所有修改都在**运行时内存**中完成（DLL 注入 + API Hook），不修改系统文件、不写注册表、不替换二进制。完全可逆——卸载 Windhawk 后系统恢复原状。 |
| 4 | **跨架构跨进程的全域注入** | 支持 x86 → x64、x64 → WOW64、ARM64 等多架构场景下的 DLL 注入；覆盖从 UWP 应用到系统服务的大多数进程。其实现方案（APC 注入、私有命名空间、MinHook 定制分支）有独立的技术参考价值。 |
| 5 | **开源可审计 + 防反作弊机制** | 核心引擎与所有 mod 均开源。内置反作弊游戏的进程排除配置，默认屏蔽主流游戏目录以减少误封风险——这是同类工具中少见的"社会责任"意识。 |

---

## 🏗️ 项目架构全景

### 总体分层架构

```
┌──────────────────────────────────────────────────┐
│                  用户交互层                        │
│  ┌─────────────────────┐  ┌───────────────────┐  │
│  │  app.exe             │  │ VSCode Extension  │  │
│  │  (托盘图标 + 服务)   │  │ (mod 浏览/安装/UI) │  │
│  └──────────┬──────────┘  └────────┬──────────┘  │
└─────────────┼──────────────────────┼─────────────┘
              │ IPC                  │ HTTP/REST
┌─────────────┼──────────────────────┼─────────────┐
│             ▼                      ▼              │
│        ┌────────────────────────────────────┐     │
│        │   windhawk.dll (引擎 DLL)           │     │
│        │  ┌──────────────────────────────┐  │     │
│        │  │  ModsManager                  │  │     │
│        │  │  ├─ 模组加载/卸载/热更新      │  │     │
│        │  │  └─ 模组 API 暴露             │  │     │
│        │  ├─ AllProcessesInjector         │  │     │
│        │  │  ├─ 新进程注入（APC/远程线程） │  │     │
│        │  │  └─ 跨架构注入（x86↔x64↔ARM64）│  │     │
│        │  ├─ MinHook 钩子引擎             │  │     │
│        │  └─ CustomizationSession         │  │     │
│        │     ├─ 符号解析（dbghelp/SymSrv）│  │     │
│        │     └─ 进程私有命名空间          │  │     │
│        └────────────────────────────────────┘     │
│                     DLL 注入层                     │
└──────────────────────────────────────────────────┘
```

### 三个子项目

| 子项目 | 语言 | 功能 | 关键文件 |
|--------|------|------|----------|
| `src/windhawk/app` | C++ | 托盘应用、Windows 服务、事件监控、更新检查 | `app.cpp`, `service.cpp`, `main_window.cpp` |
| `src/windhawk/engine` | C++ | 全局注入引擎、模组加载器、API Hook 基础设施 | `dll_inject.cpp`, `mods_manager.cpp`, `customization_session.cpp` |
| `src/vscode-windhawk` | TypeScript | VSCode 扩展——提供 mod 市场 UI、编译工具链、代码编辑器 | `package.json`, `src/extension.ts` |

### 模组（Mod）生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  编写     │───▶│  编译    │───▶│  安装    │───▶│  运行    │
│ mod 源码  │    │ (VSCode) │    │ (VSCode) │    │          │
└──────────┘    └──────────┘    └─────┬────┘    └─────┬────┘
                                      │               │
                                      ▼               ▼
                                 ┌──────────┐   ┌──────────┐
                                 │ windhawk │   │ 引擎 DLL  │
                                 │ .dll 写入 │   │ 注入并调用│
                                 │ 磁盘     │   │ mod 初始化│
                                 └──────────┘   └──────────┘
```

每个 mod 是独立的 DLL，暴露标准入口函数。引擎通过 `mods_api.h` 中定义的 `Wh_*` API 向 mod 提供：存储读写、Hook 注册、符号枚举、反汇编、URL 内容获取等能力。

### 全局注入技术栈

Windhawk 使用一套**混合注入策略**，而非单一方法：

1. **初始注入**：枚举当前运行进程 → `VirtualAllocEx` + `WriteProcessMemory` + `CreateRemoteThread`（或 `NtCreateThreadEx`）
2. **新进程拦截**：Hook `CreateProcessInternalW`（所有进程创建函数的最终汇合点），拦截后即时注入
3. **APC 注入**：对尚未开始执行的进程（初始线程还未执行第一条指令），使用 `NtQueueApcThread` 排队注入，避免崩溃
4. **跨架构注入（WOW64→x64）**：利用 `wow64ext` 库通过 `NtQueueApcThread64` / `NtCreateThreadEx64` 实现
5. **UWP 兼容**：通过 `icacls` 修改 DLL 权限 + `CreatePrivateNamespaceW` 绕过 AppContainer 沙箱

> **核心技术来源**：`dll_inject.cpp` 约 500 行 shellcode 数据 + 注入逻辑，`all_processes_injector.cpp` 实现新进程的持续监控。

---

## 💡 应用场景与启发

### 适合的 Windows 自定义场景

1. **任务栏深度改造**：调整高度/图标大小、显示文本标签、恢复右键菜单、时钟格式自定义——这些微软多年"不开放"的设置通过 mod 轻松实现。
2. **资源管理器增强**：恢复经典导航栏 Ribbon、调整上下文菜单、添加文件操作快捷键。
3. **窗口行为优化**：窗口半透明磨砂效果、禁用手势冲突、鼠标滚轮增强（浏览器标签切换、任务栏音量调节）。
4. **开始菜单改造**：默认显示"所有应用"、删除"推荐"区域、调整布局。
5. **特定应用的补丁**：为 Chrome/Edge/Firefox 添加缺少的功能——无需安装浏览器扩展。

### 对同类工具的架构启发

1. **"UI 即 VSCode 扩展"的设计**：Windhawk 使用 VSCode 扩展作为前端，直接获得了：
   - 免费的多标签编辑器
   - 内置的语法高亮和 C++ 智能提示
   - 一键编译 + 输出面板
   - 无需维护独立 GUI
   - 跨平台的前端开发体验（即使后端是 Windows 专用）
   
   **启示**：对于需要"编辑器 + 设置 + 浏览"三合一的系统工具，VSCode 扩展是一个被低估的 UI 载体。

2. **模组市场 vs. 单体内置**：Windhawk 的选择是"不决定用户需要什么，只提供安装它们的机制"。与 StartAllBack/ExplorerPatcher 等将功能写死在代码里不同，Windhawk 将"功能定义权"下放给了社区。这带来了：
   - 功能增长速度远超市面任何单体工具（2026 年已有数百个 mod）
   - 单一 mod 出问题不影响其他 mod
   - 但也带来了品控不一致的问题

3. **非破坏性运行时修改**：DLL 注入 + MinHook 钩子的模式，可作为其他需要"在不修改原程序的情况下扩展功能"的项目的模板。其 APC 延迟注入 + 互斥锁同步的方案，对进程注入类工具有直接的参考价值。

4. **安全边界的自觉确认**：Windhawk 在 README 和安装流程中多次警告"只安装信任作者的 mod"，并内置了反作弊游戏的进程排除列表——这种安全 UX 设计值得所有存在第三方生态的工具学习。

---

## 🧠 核心源码解读

### 1. 入口点：引擎 DLL 的初始化（`engine/main.cpp`）

```cpp
// engine/main.cpp - DLL 入口 + 初始化
BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            g_hDllInst = hinstDLL;
            break;
        case DLL_PROCESS_DETACH:
            if (lpvReserved) {
                NoDestructorIfTerminatingBase::SetProcessTerminating();
            }
            break;
    }
    return TRUE;
}

// 由 shellcode 在目标进程中调用的导出函数
BOOL InjectInit(const DllInject::LOAD_LIBRARY_REMOTE_DATA* pInjData) {
    if (!LazyInitialize()) return FALSE;
    if (WaitForSingleObject(pInjData->hSessionManagerProcess, 0) == WAIT_OBJECT_0)
        return FALSE;  // 宿主进程已退出
    CustomizationSession::Start(/*...*/);
    return TRUE;
}
```

`InjectInit` 是注入后第一个执行的 C++ 函数。它检查宿主进程是否还活着，然后开始一个"定制会话（CustomizationSession）"——这个会话会加载所有启用的 mod。

### 2. 注入核心：Shellcode + 跨架构处理（`engine/dll_inject.cpp`）

```cpp
// dll_inject.cpp - 确定注入架构并执行
void DllInject(HANDLE hProcess, HANDLE hThreadForAPC, /*...*/) {
    USHORT targetProcessArch = GetProcessArch(hProcess);
    switch (targetProcessArch) {
        case IMAGE_FILE_MACHINE_I386:
            shellcode = x32Shellcode;       // 32-bit shellcode
            break;
        case IMAGE_FILE_MACHINE_AMD64:
            shellcode = x64Shellcode;       // 64-bit shellcode
            break;
        case IMAGE_FILE_MACHINE_ARM64:
            shellcode = arm64Shellcode;     // ARM64 shellcode
            break;
    }

    // 在目标进程中分配内存，写入 shellcode + 数据
    void* pRemoteCode = VirtualAllocEx(hProcess, nullptr,
        shellcodeSizeAligned + shellcodeDataSize,
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    WriteProcessMemory(hProcess, pRemoteCode, shellcode, shellcodeSize, nullptr);

    if (hThreadForAPC) {
        // APC 注入——对于尚未开始执行的进程
        MyQueueUserAPC(pRemoteAPCAddress, hThreadForAPC, pRemoteData, targetProcessArch);
    } else {
        // 远程线程注入
        MyCreateRemoteThread(hProcess, pRemoteThreadAddress, pRemoteData, createThreadFlags);
    }
}
```

这段代码体现了 Windhawk 最核心的技术价值：**支持所有主流 Windows 架构的交叉注入**。代码中硬编码了 x86 和 x64 的 shellcode 字节码（编译时生成），并在运行时根据目标进程架构选择对应的 shellcode 版本。

### 3. 模组 API：mod 开发者接口（`engine/mods_api.h`）

```cpp
// mods_api.h - 模组开发者的 API 入口
// mod 只需要 #define WH_MOD 然后包含此头文件

// Hook 函数——mod 的核心能力
BOOL Wh_SetFunctionHook(void* targetFunction,
                        void* hookFunction,
                        void** originalFunction);

// 符号枚举——在目标模块中按名称搜索符号
HANDLE Wh_FindFirstSymbol(HMODULE hModule,
                          PCWSTR symbolServer,
                          WH_FIND_SYMBOL* findData);

// 批量 Hook 符号——最强大的功能
BOOL Wh_HookSymbols(HMODULE module,
                    const WH_SYMBOL_HOOK* symbolHooks,
                    size_t symbolHooksCount,
                    const WH_HOOK_SYMBOLS_OPTIONS* options);

// 设置/获取存储
int  Wh_GetIntValue(PCWSTR valueName, int defaultValue);
BOOL Wh_SetIntValue(PCWSTR valueName, int value);
```

`Wh_HookSymbols` 是最具威力的 API：它通过符号服务器（SymSrv）自动下载目标模块的 PDB，解析出所有符号地址，然后批量安装 MinHook 钩子。mod 开发者只需提供函数名 + 钩子函数的配对表，引擎代劳符号解析和 Hook 注册。

### 4. 模组管理器：生命周期管理（`engine/mods_manager.cpp` / `engine/mod.h`）

```cpp
// mod.h - Mod 和 LoadedMod 类
class Mod {
public:
    bool Load(bool loadedOnStartup);     // 加载 mod DLL
    void AfterInit();                    // 所有 mod 加载后的二次初始化
    void Uninitialize();                 // 卸载
    bool ApplyChangedSettings(bool* reload);  // 热更新设置
};

class LoadedMod {
public:
    bool Initialize();                   // 调用 mod 的 Wh_ModInit
    BOOL SetFunctionHook(...);          // 委托给 MinHook
    BOOL HookSymbols(...);              // PDB 符号解析 + 批量 Hook
};
```

`LoadedMod` 是实际持有 `HMODULE`（mod DLL 句柄）的类，所有对 mod 的 API 调用都通过其内部指针转发。`Mod` 类则负责管理 mod 的文件配置、状态文件、设置变更时间等——两者形成一个"配置层 + 运行时层"的双层结构。

---

## 🌐 全网口碑画像

### 来源 1：少数派 sspai.com（2023）⭐⭐⭐⭐
> "Windhawk 通过这种**近乎无损的方式**来增强系统功能，对于不想当 Windows 新版本试验田的用户还是相当友好的，也可以让新系统用户继续延续之前的 Windows 使用习惯。"
> 
> 重点推荐模组：任务栏时钟定制、滚轮音量调节、浏览器标签页切换、资源管理器导航栏恢复。

### 来源 2：XDA Developers（2025）⭐⭐⭐⭐
> "Windhawk is the better choice for most people... Its mod ecosystem provides near-limitless possibilities. Mod-specific bugs are easier to accept than ExplorerPatcher's system-integrated bugs."
> 
> 判定：通用场景下 Windhawk 优于 ExplorerPatcher。

### 来源 3：Windows ReadMe / windowsread.me（2026）⭐⭐⭐½
> "It's a mixed bag — a complicated picture. I can't exactly recommend you run this. I can't tell you not to run it, either... Windhawk may cause serious problems with PC games that use anti-cheat software."
> 
> 从记者视角谨慎中立：功能强大但安全边际存疑。

### 来源 4：腾讯云开发者社区（2024）⭐⭐⭐⭐
> "Windhawk 是款**免费开源**的 Windows 定制工具，界面友好。能定制任务栏、窗口、开始菜单等，还有资源管理器增强等功能。"
> 
> 中文社区的正面评价，强调"免费+开源"的透明性优势。

### 来源 5：知乎专栏（2023）⭐⭐⭐⭐
> "就像很多游戏通过模组扩展玩法和内容一样，你可以在 Windhawk 上找到大量开发者提供的系统增强模组，下载应用后即可实现系统组件不能实现的新功能。"
> 
> 类比游戏 Mod 帮助读者快速理解概念，获广泛赞同。

### 来源 6：CSDN / GitCode 中文博客圈（2025-2026）⭐⭐⭐½
> "Windhawk 是一个革命性的 Windows 程序定制工具，让每个人都能成为自己系统的设计师。"
> 
> 中文技术写作号大量跟进，但内容深度不足，多为 README 复述；不过侧面印证其在国内有一定传播度。

### 来源 7：Windows Forum（2025）⭐⭐⭐⭐
> "Windhawk's open-source ecosystem means that you can contribute mods, customize them, and even fork projects. This collaborative spirit fosters rapid innovation, though at the cost of consistency."
> 
> 认可开放生态带来的创新速度，同时指出"一致性不足"的问题。

### 来源 8：80aj.com 技术博客（2026）⭐⭐⭐⭐
> 深入解读 Windhawk 与微软"基线安全模式"之间的矛盾："该工具通过 DLL 注入技术允许用户突破系统限制，但也带来了系统不稳定、触发游戏反作弊机制及第三方模块安全审计等风险。"
> 
> 从安全博弈视角的分析，在中文互联网中质量较高。

---

## ⚔️ 竞品对比

| 对比维度 | Windhawk | StartAllBack | ExplorerPatcher | OldNewExplorer |
|---------|----------|-------------|----------------|----------------|
| **定位** | 开放式模组市场 | 一键界面还原 | 经典体验恢复 | 资源管理器经典化 |
| **商业模式** | 完全免费 + 开源 | 付费（$5.99） | 免费 + 开源 | 免费 + 开源 |
| **扩展性** | 极高（社区 mod 无限扩展） | 有限（固定功能集） | 低（预设功能） | 低（单一功能） |
| **修改方式** | DLL 注入（无文件修改） | 系统文件替换 + DLL 注入 | 系统文件替换 | 注册表 + DLL 替换 |
| **Windows 11 兼容** | 持续更新 | 曾遭微软限制（24H2） | 曾遭微软限制（24H2） | 部分兼容 |
| **风险等级** | 中（mod 质量不一） | 低（商业付费产品） | 中-高（工具本身有 bug） | 低 |
| **学习成本** | 中（需要选 mod） | 低（开箱即用） | 低 | 低 |
| **适合人群** | 爱折腾的高级用户 | 追求稳定的普通用户 | 怀旧/轻度定制用户 | 仅需还原资源管理器 |
| **启动项** | 安装量约 1GB 级 | 较小 | 较小 | 极小 |

### 关键差异分析

**StartAllBack** 是 Windhawk 最直接的"功能对手"——但它选择将功能包在 $5.99 的付费墙后，用钱换来了"稳定可靠"的声誉。Windhawk 免费但要求用户自己评估每个 mod 的可靠性。

**ExplorerPatcher** 选择最窄的路线（恢复 Windows 10 风格），但因其"替换系统文件"的做法多次被微软更新兼容性问题攻击。Windhawk 通过 DLL 注入 + 运行时 Hook 避免了此类直接冲突。

**OldNewExplorer** 功能最专一但也最局限，仅修改文件资源管理器。

> **一句话结论**：Windhawk 的模组市场模式在功能的广度上碾压所有对手，但需要用户承担更多的选择和风险评估义务。StartAllBack 在"买个省心"场景下仍不可替代。

---

## 🎯 核心研判

1. **模组市场模式是代际优势**：Windhawk 选择的不是做另一个"系统优化工具"，而是做一个**平台**。这个战略选择使其在功能增长速度上超越了所有单体工具。随着社区成熟，生态优势将持续扩大。

2. **VSCode 作为 UI 载体是一个被低估的架构创新**：省去了维护独立 GUI 的成本，直接获得了 VS Code 的编辑器、调试器、Git 集成和市场。这个模式如果成功，可能被更多系统工具效仿。

3. **安全问题是其最大软肋**：DLL 全局注入 + 第三方 mod = 信任链断裂。微软正在推行的"基线安全模式"（Baseline Security Mode）如果普及，Windhawk 的运行空间将显著收缩。反作弊游戏误封问题也是一个持续的隐患。

4. **Windows 11 24H2 更新对竞品的打击利好 Windhawk**：微软在 24H2 中限制 StartAllBack 和 ExplorerPatcher，因其使用了受系统保护的 API。而 Windhawk 通过 MinHook 在运行时挂钩技术栈的底层函数（`CreateProcessInternalW`），技术路径不同，受影响的概率更低。

5. **国际化社区建设仍需加强**：相比 StartAllBack 的商业化运营，Windhawk 的社区建设（mod 文档、开发指南、QA 流程）仍较简陋。mod 的发现和评价机制单一，未能形成有效的质量信号。

6. **从 GitHub 的 issue/discussion 活跃度来看**（8.2k stars, 211 forks），这是一个**高质量的个人/小团队项目**，而非大型组织维护。代码质量和设计能力突出，但运营和生态管理的力量有限。

---

## 📂 关键文件路径速查

### 引擎核心
| 文件 | 说明 |
|------|------|
| `src/windhawk/engine/main.cpp` | DLL 入口点、`InjectInit` 导出函数 |
| `src/windhawk/engine/dll_inject.cpp` | 全局注入核心——shellcode、架构判断、APC/远程线程 |
| `src/windhawk/engine/dll_inject.h` | 注入数据结构和 LoadLibraryRemoteData |
| `src/windhawk/engine/all_processes_injector.cpp` | 枚举/监控所有进程并持续注入 |
| `src/windhawk/engine/new_process_injector.cpp` | 通过 Hook CreateProcessInternalW 拦截新进程 |
| `src/windhawk/engine/mods_manager.cpp` | Mod 管理——加载/卸载/热更新 |
| `src/windhawk/engine/mods_manager.h` | ModsManager 接口 |
| `src/windhawk/engine/mod.h` | Mod 和 LoadedMod 类定义 |
| `src/windhawk/engine/mods_api.h` | mod 开发者 API 头文件 |
| `src/windhawk/engine/mods_api_internal.h` | API 内部实现（非 mod 可见） |
| `src/windhawk/engine/customization_session.cpp` | 定制会话管理（一个进程加载多个 mod） |
| `src/windhawk/engine/symbol_enum.cpp` | 符号枚举——PDB 下载与解析 |
| `src/windhawk/engine/session_private_namespace.cpp` | UWP 兼容——跨 AppContainer 的命名空间 |

### 应用层
| 文件 | 说明 |
|------|------|
| `src/windhawk/app/service.cpp` | 后台服务——控制注入引擎 |
| `src/windhawk/app/main_window.cpp` | 设置窗口 |
| `src/windhawk/app/engine_control.cpp` | 与引擎 DLL 的通信 |
| `src/windhawk/app/update_checker.cpp` | 版本更新检查 |
| `src/windhawk/app/task_manager_dlg.cpp` | 任务管理器集成 |
| `src/windhawk/app/toolkit_dlg.cpp` | 工具集窗口 |

### VSCode 扩展
| 文件 | 说明 |
|------|------|
| `src/vscode-windhawk/package.json` | 扩展配置——命令、视图、快捷键绑定 |
| `src/vscode-windhawk-ui/` | Webview UI 源码（React/VSCode Webview） |

### 共享
| 文件 | 说明 |
|------|------|
| `src/windhawk/shared/version.h` | 版本号定义 |
| `src/windhawk/shared/portable_settings.cpp` | 便携模式设置 |
| `src/windhawk/shared/logger_base.cpp` | 日志基础设施 |

### 构建与参考
| 文件/仓库 | 说明 |
|-----------|------|
| `src/windhawk/build.bat` | 构建脚本 |
| `src/windhawk/windhawk.sln` | Visual Studio 解决方案 |
| `https://github.com/m417z/global-inject-demo` | 全局注入技术独立演示项目 |
| `https://m417z.com/Implementing-Global-Injection-and-Hooking-in-Windows/` | 注入技术详解博客 |
| `https://github.com/ramensoftware/windhawk-mods` | 社区 mod 源码仓库 |

---

*本报告基于开源仓库 ramensoftware/windhawk（GPL-3.0）及公开可用信息编译，部分信息来自社区文章和博客，仅供参考。*
