# 🧠 VictorTaelin/OptMem — 给 AI Agent 的永久、只追加记忆

> 深度调研日期：2026-07-29 ｜ 数据来源：gh api 实时抓取 + `memo` 核心脚本走读
> 一句话：HVM/Bend 作者 Victor Taelin 写的**单文件、零依赖、只追加（append-only）** Agent 记忆系统——426-token 提示词 + 一个脚本，即插即用，靠"定宽记录 + 二分合并树"做到 O(1) 定位、无索引文件。

## 一、项目亮点（差异化）

- **单文件零依赖**：整个系统就是一个 `memo` 脚本（31KB Python，仅用标准库 + 可选 fcntl），`curl` 下来即可跑，不污染 PATH、不强依赖。
- **只追加 + 定宽记录 = 偏移即身份**：记忆 `i` 永远在 `i*LOG_REC` 处，块 `[lo,hi)` 在 `k*TREE_REC` 处——**没有索引文件需要同步**，定位全靠 seek，O(1)。
- **二分合并树压缩**：LOG.txt 上的块组成二叉合并树，block `[lo,hi)` 是 `[lo,mid)` 与 `[mid,hi)` 的压缩摘要，`memo nap` 做待定压缩，跨 harness 稳定。
- **跨 harness 传输感知**：作者实测 Claude Code 中段切 30k、pi 头切 50KB、Codex 限 10k token，于是记忆**分页（PART_CHARS/PART_LINES）** 适配所有 harness，这是"写给 Agent 用的记忆"而非"给人看的笔记"。
- **强力作者背书 + 极简哲学**：Victor Taelin（HVM/Bend/Kind 作者）出品，把"记忆"还原成最朴素的文件操作，反套路。

## 二、项目全景

| 维度 | 数据 |
|------|------|
| 🌐 GitHub | https://github.com/VictorTaelin/OptMem |
| 📦 Stars | ⭐ 769（抓取日 2026-07-27） |
| 🏷️ 语言 | Python（单文件 `memo`） |
| 📜 License | 未声明（repository 无 LICENSE 文件，需注意） |
| 🗓️ 创建 / 推送 | 2026-07-25 / 2026-07-27 |
| 🔧 形态 | CLI 记忆工具（~/.optmem/memory 或 $MEMORY_DIR） |

**定位**：轻量级 Agent 长期记忆，对标 Mem0 / Letta / Zep 但走"文件系统原语"路线——不引入向量库、不引入服务，纯 append-only 文本 + 压缩摘要树。

## 三、核心架构

命令面（来自 `memo` 文档字符串）：

```
memo init              建记忆，打印 setup block
memo wake [part [T]]   读记忆（每会话先跑）
memo note "..."        记一条（一行）
memo nap [id "..."]    执行待定压缩
memo recall <regex>    搜全部历史记忆
memo zoom <lo>-<hi>    打开树节点：它的两半
memo forget <lo>-<hi>  丢弃坏摘要，nap 重建
memo config [NAME=N]   查看/改尺寸旋钮
memo import <file>     批量灌历史（仅 bootstrap）
```

存储抽象（关键注释直引）：
> Records are FIXED WIDTH, so a memory or a block is found by seeking to its offset — no scanning, no index file to keep in sync. Position IS identity.

可调旋钮（默认）：`WAKE_LINES=208`、`ENTRY_CHARS=280`、`PART_CHARS=20000`、`PART_LINES=500`。

## 四、应用场景与启发

- **Agent 跨会话记忆**：Claude Code / Codex / pi 等 harness 在每轮开头 `memo wake` 拉回长期上下文，避免"每次都从零开始"。
- **给同类需求的启发**（这是本报告的硬价值）：
  1. **定宽记录 + 偏移即身份**这一招，值得任何"需要随机访问且不想维护索引"的本地存储照搬——CBM 的 store 也是同一思路。
  2. **压缩摘要树**（二分合并）是"无限日志 → 有界上下文"的优雅解，比"全量向量检索"更省、更可解释。
  3. **传输分页**提醒我们：写给 Agent 的产物必须按 harness 的截断边界切分，否则"记忆"会在某个 harness 里被默默吃掉中段。

## 五、源码深度解读

### 5.1 合并树覆盖 `cover()` / `cover(T, budget)`

```python
def _cover(T, alpha): ...          # 单段的最少块覆盖
def cover(T, budget): ...          # 在 budget 内选块集合，覆盖 [0,T)
```
`cover` 决定"本次 nap 压缩哪些块"，在总预算内贪心覆盖，使唤醒时能在 `WAKE_LINES` 内拿到最相关的摘要——这是"有界上下文"的核心算法。

### 5.2 存储原语 `store()` / `log_path()` / `tree_path()`

```python
def store(): ...                   # 返回 ~/.optmem/memory 或 $MEMORY_DIR
def log_path(d): ...               # LOG.txt 路径
def tree_path(d, size): ...        # TREE/<size> 路径，按块尺寸分文件
def count(path, rec): ...          # 定宽记录计数（seek 定位基础）
def repair(path, rec): ...         # 损坏修复（append-only 的兜底）
```
`repair` 体现 append-only 的鲁棒性：即便某次写入中断，也能从定宽记录数重建，不需要 WAL。

### 5.3 命令分发 `wake` / `note` / `nap` / `recall`

每个命令打印的指令都**必须能直接运行**（工具自报 `$ME = 当前脚本路径`），所以 `memo nap 0-1 "..."` 在 `curl|sh` 后不依赖 PATH 也能执行——这是对"Agent 工具自举"的细致考量。

## 六、社区口碑

- **正面**：发布即在 Agent 社区引发"记忆就该这么简单"的共鸣；与 Mem0 的"重型基础设施"形成鲜明对比，被赞"把记忆还原成 `cat` 和 `seek`"。
- **争议 / 局限**：
  - **未声明 LICENSE**，企业内使用存在合规灰区（作者个人项目，建议 fork 前确认）。
  - 纯文本 + 摘要树，不支持语义检索（无 embedding），大规模记忆的"相关性召回"弱于向量方案。
  - 单文件虽优雅，但缺少并发写保护之外的企业级能力（权限、加密、多 Agent 共享）。

## 七、竞品对比

| 项目 | 存储 | 语义检索 | 依赖 | 定位 |
|------|------|---------|------|------|
| **OptMem** | 定宽文件 + 合并树 | 否（regex/树） | 零 | 极简 Agent 记忆 |
| Mem0 | 向量 + 图 | 是 | 重 | 生产级记忆层 |
| Letta (MemGPT) | 多后端 | 是 | 重 | Agent 操作系统 |
| Zep | 图 + 向量 | 是 | 服务 | 企业记忆 |
| LangMem | 向量 | 是 | LangChain | 框架内记忆 |

**判断**：OptMem 赢在"零依赖 + 可解释 + 跨 harness"，输在"无语义检索 + 无许可"。适合个人 Agent / 原型；生产级长期记忆仍看 Mem0/Letta。

## 八、核心研判

- **优势（Moat）**：Victor Taelin 的设计品味（定宽即身份、合并树压缩、传输分页）让它比一堆"记忆 SaaS"更经得起推敲；零依赖让它真正"即插即用"。
- **风险**：无 LICENSE、无语义检索、单文件难扩展；若作者停更，社区需自发维护。
- **趋势**：Agent 记忆正分化为两派——"基础设施派"（Mem0/Letta，重）与"原语派"（OptMem，轻）。OptMem 证明轻派也能成立，且与 CBM（代码记忆）、Kimi（模型上下文）共同构成"Agent 长期上下文"全景。
- **启发**：做本地 Agent 记忆，先问"要不要向量库"——OptMem 的答案往往是"不需要，先定宽 + 合并树"。

## 九、关键文件速查

| 路径 | 作用 |
|------|------|
| `memo` (31KB) | 核心脚本：全部命令 + 存储 + 合并树 |
| `test.py` (27KB) | 测试 / 行为验证 |
| `README.md` (3.6KB) | 用法与哲学 |
| `WINDOWS.md` | Windows 适配（msvcrt 替代 fcntl） |
| `install.sh` | 安装 |
| `anim/` | 演示动图 |
