# morluto/rea — 深度调研

> 调研日期：2026-10-08 ｜ 来源：GitHub Trending（当日新增，未入库）

## 1. 项目定位（一句话）
REA（Reverse Engineer Anything）是一个**为 AI Agent 设计的逆向工程 MCP/CLI 工具**——把二进制、应用运行行为与桌面端观测能力统一封装成 Agent 可调用的"证据契约（Evidence）"，让智能体从"猜"变成"查"。

## 2. 项目亮点（差异化，开篇呈现）
- **Agent-native 而非 GUI 套壳**：同一套 investigation workflows 与 evidence contracts 同时服务终端 CLI 与 MCP Server，会话内可保留活动目标与证据账本。
- **Provider 抽象 + 确定性路由**：Hopper / Ghidra / IDA / 原生 macOS / Artifact Graph / Browser CDP / Android(JADX) / Firmware(Binwalk·Unblob) / Process Capture 多 provider，由 deep-provider registry 按目标确定性选择，失败绝不静默切换。
- **125+ 工具分层编目**：native inspection(41) / investigation workflows(14) / macOS utilities(7) / artifact graph(5) / managed PE·CLI(7) / firmware(2) / Android APK(5) / browser(11) / Electron(5) / JS runtime(2) / application workflows(13) / workspace&observation(21)。
- **本地优先、可解释**：分析在本地受支持主机跑，不上传 App；每一步给出"如何得出结论"的证据，明确声明"不声称恢复原源代码、不自动克隆应用"。
- **Decompile→Understand→Recreate 三段式调查模型**：最终把学到的行为改写成适配你自己技术栈的特性（与 AnyPS5 这类"重建"路线互补）。

## 3. 核心架构
CLI/MCP 同一应用层 → **Target-bound session router** → **Deep-provider registry（确定性选择）** → 各 provider runtime（Hopper/Ghidra/IDA 各自 owned runtime，带 deadline + bounded diagnostics + cleanup）→ Target software。同时 Browser CDP / Android static / Firmware / Process capture 平行挂载到 session。

```
Agent ─▶ REA(CLI+MCP) ─▶ Session(target-bound router)
                            ├─ Registry ─▶ Hopper / Ghidra / IDA provider (owned runtime)
                            ├─ Native macOS provider
                            ├─ Artifact graph provider
                            ├─ Browser CDP provider
                            ├─ Android static (JADX adapter)
                            ├─ Firmware (Binwalk/Unblob)
                            └─ Process capture provider ─▶ Target
```

关键设计：provider 声明"支持的能力"与"这些能力可能产生的副作用"；终端命令短生命周期，MCP 会话可长期持有目标与 evidence ledger。

## 4. 应用场景与启发
- **给同类需求的解法思路**：任何"想让 Agent 操作重型 GUI/二进制分析器"的场景，都该学 REA 的 **provider 能力声明 + 副作用契约 + 证据信封** 模式——把脆弱的"让 LLM 点按钮"换成"LLM 调确定性工具拿结构化证据"。
- 应用：解释无源码功能如何工作、重建认证/存储/更新/网络流、从字符串或符号追到实现代码、把行为改写成产品特性/测试/迁移笔记/可互操作替代品。
- DX-Ball 重建案例：用 Ghidra provider 追函数→游戏状态→依赖，再用 original-x86 differential tests 校验，复现 3,205 个原始 x86 case、63 个编译函数字节全部一致。

## 5. 源码深度解读
**① provider 注册与路由（src/ 顶层 + server/）**
`src/` 直接以领域分目录：`hopper/ ghidra/ ida/ native/ browser/ android/ firmware/ dotnet/ process/ application/ artifacts/`，每个 provider 一个包；`server/` 与 `cli.ts` 共用 `contracts/` 下的证据信封定义。这种"目录即 provider"的扁平结构让新增分析器零样板。

**② 证据契约与 CLI（src/cli*.ts + contracts/）**
CLI 是 MCP 的薄封装，二者返回同一 Evidence envelope：
```bash
npx -y rea-agents@latest analyze /Applications/Notes.app
npx -y rea-agents@latest trace  /Applications/Notes.app "offline"
npx -y rea-agents@latest compare left-evidence.json right-evidence.json
```
`cliEvidenceCommands.ts` / `cliReferenceSourceImportStatus.ts` 等文件表明证据可被序列化、比较、跨会话复用——这是"Keeps context"卖点的工程落地。

**③ 调查工作流编排（src/application + src/composition）**
`application/` 定义"app overviews / function dossiers / feature traces / call graphs"等 14 类 investigation workflows；`composition/` 负责把多个 provider 的结果拼成一条 feature trace。一次 `trace` 调用背后是 open_binary→search_strings→find_xrefs→get_call_graph→procedure_pseudo_code 的工具链编排。

## 6. 社区口碑
- 当日 Trending 榜首级曝光（13.7k⭐，1.4k forks，2026-04 创建、10-07 仍在高频推送），README 含 8 语种、DX-Ball 完整重建 showcase，专业度明显高于普通 viral 仓库。
- 定位清晰："不声称恢复原码/不自动克隆"，规避了"AI 逆向 = 抄袭"的伦理雷区，社区接受度高。
- 仍在快速迭代（Roadmap 分 Now/Next/Later，正在扩展 Hopper/Ghidra 的架构与间接调用覆盖）。

## 7. 竞品对比 + 核心研判
| 维度 | REA | Ghidra/IDA 原生 | Binary Ninja | radare2 |
|------|-----|----------------|--------------|---------|
| Agent 接口 | MCP+CLI 一等公民 | 需自接脚本 | 有 API | 有 r2pipe |
| 多 provider 编排 | 内置 registry | 无 | 无 | 无 |
| 证据可复用 | Evidence envelope | 无 | 部分 | 无 |
| 学习曲线 | 自然语言提问 | 高 | 中 | 高 |

**研判**：REA 的价值不在"反编译引擎"（它依赖 Hopper/Ghidra/IDA），而在**把异构分析器统一成 Agent 可消费的确定性工具层**——这是 AI-native RE 的正确抽象。风险：深度分析强绑定商业工具（Hopper/IDA），纯开源用户只能走 Ghidra；provider 越多维护面越广。长期看，若能把"Recreate"阶段接到用户代码库生成器，会从"分析器"升级为"移植/互操作平台"。

## 8. 关键文件路径速查
- 入口与契约：`src/main.ts`、`src/cli.ts`、`src/contracts/`、`src/server/`
- Provider 实现：`src/hopper/`、`src/ghidra/`、`src/ida/`、`src/native/`、`src/browser/`、`src/android/`、`src/firmware/`、`src/process/`
- 工作流编排：`src/application/`、`src/composition/`、`src/domain/`
- Agent Skill：`skills/reverse-engineer-anything/`
- 配置与治理：`src/config.ts`、`src/mcpStartupPolicy.ts`、`src/mcpDoctor.ts`、`AGENTS.md`
- 说明文档：`docs/native-investigation.md`、`docs/dev/`（架构/构建）
