# 🔬 vim/vim - 全方位深度调研

## 📌 一句话定位
Vim 是用 C 写就、拥有 30+ 年演进史的开源文本编辑器，以「模态编辑 + 极致可移植 + 强向后兼容」为核心哲学，并通过 Vim9 script 把脚本执行速度提升了两个数量级。

## ⭐ 项目亮点
- **Undo Tree（撤销树）而非线性撤销**：`src/undo.c` 中每个 `u_header_T` 同时持有 `uh_next/uh_prev`（时间线）与 `uh_alt_next/uh_alt_prev`（分支），允许"回到旧状态后走另一条修改路径"，这是几乎所有现代编辑器只做线性 undo 时缺失的能力。
- **Vim9 script 编译器**：9.0 引入的新脚本语法把函数编译成基于栈的中间指令（每条指令 1-2 参数，操作数即 `typeval_T`），实测 for 循环场景比旧 Vim script 快 ~68×（5.0s → 0.07s，见 `README_VIM9.md` 基准表）。
- **可移植性即设计约束**：`AGENTS.md` 明确要求代码必须能在 Compaq C on OpenVMS 上构建——因此语言标准锁定在 C95 + 少量 C99 特性，且用 `char_u` 替代 `char`、`vim_free()` 替代 `free()` 等自有包装层。
- **极致工程纪律**：提交信息主题必须写"问题陈述"而非"修复动作"，强制 `Signed-off-by`（DCO），并有开发期/稳定期交替的发版策略——稳定期只收 bug/安全/文档修复。

## 🏗️ 项目架构全景
### 目录结构（来自 `AGENTS.md` + master 树）
- `src/`：C 源码，按子系统命名文件（`buffer.c`/`window.c`/`search.c`/`vim9compile.c`/`undo.c`）；`src/proto/` 是自动生成的 `.pro` 原型；`src/xdiff`、`src/libvterm` 是 vendored 上游库。
- `runtime/doc/`：Vim help 格式文档（`*.txt`，78 列、`*`tag`*` 交叉引用），修改用户可见特性必须同补文档。
- `src/version.c`：`included_patches[]` 列表，每个触及 `src/` 的 patch 需在顶端追加条目。

### 设计哲学
"稳定、健壮、渐进加新特性、尽量向后兼容"。`runtime/doc/develop.txt` 定义了 `design-policy`：一旦在 minor 版本发布，C-core 特性必须向后兼容；deprecated 特性要通过 config 可达而非硬报错。

## 💡 应用场景与启发
- **编辑器的"可逆修改树"范式**：Vim 的 undo tree 是「时间旅行 + 分支探索」的教科书实现。任何需要"尝试多种修改路径并保留历史"的工具（如 AI agent 的代码改写、文档协同）都可借鉴 `uh_alt_*` 双链表设计。
- **渐进式语言现代化**：Vim 没有推翻旧脚本，而是用 `vim9script` 新方言 + `:import`/`:export` 渐进兼容——比 Neovim 直接重写 runtime 更保守，但换来海量旧插件的零成本存活。对"老代码库如何现代化"是极佳反面/正面教材。
- **把外部工具当一等公民**：`README_VIM9.md` 明确"弱化内嵌语言接口、鼓励 job/channel 与外部进程通信"，这与当今 agent 用 JSON/stdio 调外部工具的思路一致。

## 🧠 核心源码解读
### 1. 撤销树（`src/undo.c`）
不是栈，是图。每个 undo 头同时维护两条链：
```c
typedef struct u_header {
    u_header_T *uh_next;     // 时间线：下一个（更新）状态
    u_header_T *uh_prev;     // 时间线：上一个（更旧）状态
    u_header_T *uh_alt_next; // 分支：同一父节点的"另一条路"
    u_header_T *uh_alt_prev; // 分支：回到分支起点
} u_header_T;
```
`u_check_tree()` 在每次操作后递归校验这四条指针的一致性——这是 undo 不丢历史的根。

### 2. Vim9 编译（`src/vim9compile.c` + `README_VIM9.md`）
Vim9 函数先被编译成指令序列，局部变量直接落在栈上（`def MyFunction(arg: number): number ... enddef`），不再走 `a:`/`l:` 字典。这把"调用开销 + 逐行解释"这个旧模型最大瓶颈彻底绕开。

### 3. 内存/字符串封装层
`AGENTS.md` 列出 libc→Vim 的映射：`free→vim_free`（容忍 NULL）、`memcpy→mch_memmove`（处理重叠）、`isspace→vim_isspace`（处理 >127 字节）。统一封装让同一份代码跨 OS 行为一致。

## 📐 架构决策与设计哲学
- **C95 而非现代 C**：不是保守，是"必须在 OpenVMS/老 AIX 上编译"的硬约束（见 `develop.txt` 的 `assumptions-C-compiler`）。
- **稳定期 vs 开发期**：社区在 2023 年 Bram Moolenaar 离世后转为基金会式治理，仍严守"minor 版本不破坏 C-core 兼容"。
- **`char_u` + `_T` 后缀类型**：避免与 POSIX `char`/`*_t` 冲突，全工程统一。

## 🌐 全网口碑画像
- **好评共识**：模态编辑仍是"肌肉记忆型效率"的代名词；Vim 几乎是 Unix 系默认 `vi` 兼容编辑器；Vim9 让脚本插件性能不再是短板。
- **差评共识**：学习曲线陡峭；配置/插件生态被 Neovim（2014 年 fork）在 Lua 现代化上反超；默认配置对新手不友好。
- **争议焦点**：Vim 与原生 Neovim 的"正统之争"——Vim 守兼容与可移植，Neovim 押注 Lua 与异步架构。两者 runtime 仍有代码共享。
- **维护信号**：`AGENTS.md` 是罕见的"给 AI agent 的贡献指南"，说明维护者已主动拥抱 AI 协作（注明 `Co-Authored-By` 是接受 AI 协助的合规方式）。

## ⚔️ 竞品对比
| 维度 | Vim | Neovim | Emacs |
|------|-----|--------|-------|
| 语言 | C | C + Lua | C + Emacs Lisp |
| 扩展机制 | Vim script / Vim9 | Lua（异步） | Elisp |
| 设计重心 | 可移植/兼容 | 现代/异步/API | 可扩展操作系统 |
| 生态现状 | 庞大但老化 | 增长快 | 极客向 |

## 🎯 核心研判
- **优势**：无可替代的可移植性与兼容性，undo tree 是独门能力，Vim9 补上了性能短板。
- **风险**：核心贡献者依赖度仍高；年轻开发者更倾向 Neovim；GUI/异步体验落后。
- **适用**：需要稳定、可脚本化、键盘流的场景；不适用追求开箱即用现代 UI 的用户。
- **趋势**：稳定期项目，靠基金会与 AI 辅助贡献维持，短期不会衰退但增长平缓。

## 📂 关键文件路径速查
- `src/undo.c` — 撤销树实现（`u_header_T` / `u_check_tree`）
- `src/vim9compile.c` — Vim9 编译到栈指令
- `src/version.c` — `included_patches[]` 发版清单
- `AGENTS.md` — AI 贡献指南 + 工程纪律
- `README_VIM9.md` — Vim9 设计动机与基准
- `runtime/doc/develop.txt` — 设计目标与 C 编译器假设
