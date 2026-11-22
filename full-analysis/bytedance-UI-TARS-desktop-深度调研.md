# 🖥️ bytedance/UI-TARS-desktop 深度调研

> 调研日期：2026-11-23（全文重写，原稿为 2026-05 的架构图+勾选表水报告） | 星标：39,601⭐（原稿 38,024） | Forks：4,058 | 语言：TypeScript + Python + Rust | 许可：Apache-2.0 | 默认分支：main | 最近推送：2026-10-09 | Open Issues：509

## 一句话定位

字节跳动开源的**多模态 GUI Agent 全栈**：让模型像人一样「看屏幕截图 → 理解界面 → 输出鼠标/键盘坐标操作」，纯视觉路线不依赖 DOM/API，能操作任意有屏幕的软件；包含面向用户的 UI-TARS Desktop（Electron 桌面应用）与面向开发者的 Agent TARS（CLI + Web UI）两条产品线。

## 项目亮点（差异化，先看这 5 条）

1. **纯视觉 grounding，不读 DOM**：只吃截图、输出坐标与按键，网站改版按钮移位仍能找到——传统 RPA/选择器脚本改版即失效的痛点被绕开，能覆盖 20 年老客户端到现代 Web 的任意 GUI。
2. **基准实测领先闭源对手**：UI-TARS-2 报 OSWorld 47.5 / AndroidWorld 73.3 / Online-Mind2Web 88.2 / WindowsAgentArena 50.6，对比 Claude Computer Use 的 OSWorld 22.0；OSWorld-Verified 上 UI-TARS-2-2509 达 53.1%。跨桌面/移动/Web 三域通吃是官方主打的结构性差异。
3. **开源可自托管 + 零 API 费**：Apache-2.0，本地跑或接任意模型后端；对比 Operator $200/月、Claude API 按量付费，高频海量步骤场景成本曲线截然不同。
4. **双产品线 + MCP 集成**：Desktop（终端用户可视化）与 Agent TARS（开发者库/CLI/Web）共享 VLM 底座；AIO Sandbox 隔离浏览器 + Remote Operator 远程控制 + 原生 MCP Server 构成「可远程、可集成」的操作栈。
5. **持续高频迭代**：509 open issue 的另一面是社区活跃；0.3.x beta 快速推进 Remote Operator、混合浏览器策略（CDP + Playwright 备选）。

## 核心架构

pnpm monorepo，`apps/ui-tars` 是 Electron 桌面应用，`agent-tars` 是 Agent 引擎；底层是 Tarko 框架的三层抽象：

```
omni-tars（全能层）   文本/图像/音频/截图统一多模态输入
      ↓
agent-tars（Agent 层） VLM 推理 + CoT + 任务分解 + 动作规划
      ↓
gui-agent（GUI 层）    屏幕捕获 + 坐标计算 + 鼠标键盘模拟（NutJS 执行）
```

主进程关键目录：`src/main/agent/`（operator + prompts）、`src/main/ipcRoutes/`（agent/browser/permission/screen/window 等 IPC 路由）、`src/main/remote/`（远程 operator / auth / proxy）、`src/main/services/`（runAgent / settings / utio 遥测）、`src/main/store/`。执行链路：`用户指令 → 截图 → VLM 分析 → 生成动作(parsedPrediction) → 执行 → 再截图验证 → 循环`。

## 应用场景与启发（重点）

- **「视觉优先」替代「DOM 优先」的适用边界**：凡是没有稳定 DOM/API 的场景（老旧客户端、ERP、桌面原生应用、验证码前后），纯视觉 GUI Agent 是唯一可行路线；反过来 Web 页面有 DOM 时 Midscene/Playwright 更精准——选型看「有没有结构化句柄」。
- **成本敏感的高频自动化**：每天跑成千上万步的浏览器 Agent，按步计费的商业 API 会迅速失控；本地开源方案 + 廉价模型后端是这条成本曲线的答案（也是社区「operator 叛逃」信号的根源）。
- **合规/隐私敏感场景**：截图与识别全本地，适合财务系统、内部 OA 等禁止数据出网的场景（UTIO 遥测默认关闭）。
- **模型 ≠ 应用的解耦启示**：Desktop 只是「壳」，真正能力在可插拔 VLM（本地 7B / 火山引擎 Doubao / 任意 OpenAI 兼容 API）。做 Agent 应用要把「大脑」抽象成可替换后端，别绑死单一模型。
- **别高估开箱即用**：单显示器限制、需 16GB 显存本地模型、跨应用长任务易走错路——上生产前要有「人在环」兜底。

## 源码解读（3 个核心模块，精炼骨架）

### 1. GUI 执行器：NutJSElectronOperator（`apps/ui-tars/src/main/agent/operator.ts`）

Electron 平台执行器继承通用 NutJS Operator，只重写平台相关的截图与 Windows 输入特例——是「跨平台 Agent 如何抽象」的教科书：

```ts
export class NutJSElectronOperator extends NutJSOperator {
  public async screenshot(): Promise<ScreenshotOutput> {
    const primarySource = /* 找主显示器 source */;
    if (!primarySource) return await super.screenshot(); // 找不到就回退通用实现
    const screenshot = primarySource.thumbnail;
    const resized = screenshot.resize({ /* 按 VLM 输入尺寸缩放 */ });
    return /* ... */;
  }
  async execute(params: ExecuteParams): Promise<ExecuteOutput> {
    const { action_type, action_inputs } = params.parsedPrediction; // VLM 解析出的动作
    if (action_type === 'type' && env.isWindows && action_inputs?.content) {
      // Windows 下 type 动作的特殊处理（编码/输入法兼容）
    }
    return await super.execute(params);
  }
}
```

启发：把「通用算法」放基类、把「平台差异（截图源、输入编码）」放子类 override，是 GUI Agent 跨平台的干净切法。

### 2. 权限路由（`src/main/ipcRoutes/permission.ts`）

独立 IPC 权限路由 + 测试文件（`permission.test.ts`），说明桌面 Agent 把「哪些操作需要用户授权」当成一等公民——这是本地 GUI Agent 相对云端 API 的安全补课点。

### 3. 遥测开关（`src/main/services/utio.ts`）

UTIO（使用上报）以独立 service 存在且**默认关闭**，是「隐私敏感场景可本地全自动」承诺的代码级兑现。

## 全网口碑（真实外链 + 争议）

**正面**
- [ToolBrain 评测](https://toolbrain.net/blog/2026-08-19-tool-review-ui-tars-desktop) 给 7.8/10：唯一完全开源（Apache-2.0）的原生桌面 GUI Agent，基准 wins 真实，本地/隐私/零费用三项突出。
- [AgentConn 评测](https://agentconn.com/blog/bytedance-ui-tars-desktop-review)：少数有可信公开 benchmark 的开源视觉 Agent，跨三域覆盖是结构性优势；适合「开源、自托管、不受美国依赖」的运营者。
- [什么值得买 / 今日头条](https://post.smzdm.com/p/az8xzdmr)：中文社区肯定「纯视觉不读 DOM、本地处理隐私好」，36K 星热度真实。

**争议 / 局限（独家，原稿完全缺失）**
- **最强模型不开源**：跑出 SOTA 的 UI-TARS-2 未开放权重；开源最好的 UI-TARS-1.5-7B（Apache-2.0）OSWorld 仅 **27.5 分**——「benchmark 领先」与「你能用到的模型」是两回事（ToolBrain 点破）。
- **单显示器限制**：官方明确多屏配置可能导致任务失败；无官方 Linux 桌面应用；手机控制是模型能力而非 App 功能。
- **稳定性与部署门槛**：本地 7B 需 16GB 显存；[Git Picks](https://gitpicks.dev/featured/bytedance-ui-tars-desktop-open-source-gui-automation) 列真实 bug——Windows pnpm/TS 编译失败、高 DPI 点击漂移、macOS Chrome 偶发崩溃；0.3.0-beta 的「beta」不是装饰。
- **幻觉风险**：官方自述模型在不熟悉环境会误识别 UI 元素、走错动作；复杂跨应用任务建议人在环。文档密度低于 Anthropic，工具生态更年轻。

## 竞品对比 + 核心研判

| 维度 | UI-TARS-desktop | Claude Computer Use | OpenAI Operator | OmniParser | Midscene.js |
|------|-----------------|---------------------|-----------------|------------|-------------|
| 开源/许可 | ✅ Apache-2.0 | 部分（API） | ❌ 闭源 SaaS | ✅ | ✅ |
| 本地运行 | ✅ | ❌ | ❌ | 部分 | 部分 |
| 覆盖域 | 桌面+Web+移动 | 强 Web，移动弱 | 强在线任务 | 仅解析层 | 仅 Web |
| OSWorld | 47.5（2代）/27.5（开源7B） | 22.0 | 38.1 | — | — |
| 费用 | 免费（自担算力） | API 按量 | $200/月 | 免费 | 免费 |
| 定位 | 可自托管 GUI Agent 栈 | 模型能力 | 托管产品 | 解析组件 | Web E2E 组件 |

**研判**：UI-TARS-desktop 的差异化 = 「开源 + 纯视觉 + 三域覆盖 + MCP/沙箱/远程」的组合，是想要「拿得到、改得了、自己跑」的团队目前最完整的开源 GUI Agent 栈。但需清醒：(1) 宣传基准由未开源的 2 代模型跑出，可用开源模型分数大打折扣；(2) 单显示器 + 幻觉 + beta 稳定性是上线前真实门槛。适合技术型团队在合规/成本敏感场景落地并保留人在环；追求开箱即用与生态成熟度的用户仍应选闭源方案。

## 关键文件路径速查

- `apps/ui-tars/src/main/agent/operator.ts` — NutJSElectronOperator：截图/Windows 输入 override
- `apps/ui-tars/src/main/ipcRoutes/permission.ts` — 操作授权路由（含单测）
- `apps/ui-tars/src/main/services/runAgent.ts` — Agent 运行编排
- `apps/ui-tars/src/main/remote/operators.ts` — Remote Operator 远程控制
- `apps/ui-tars/src/main/services/utio.ts` — UTIO 遥测（默认关闭）
- README / quick-start — 单显示器限制、模型后端配置、权限授予步骤

> 本报告由 GitHub 深度调研员于 2026-11-23 全文重写：原稿（2026-05）为「目录树 + 功能勾选表 + 后补竞品尾巴」，无真实源码、无外部口碑。本次基于当日 API 元数据、真实源码与 5 篇第三方评测重建，修正星标 38,024→39,601，补齐亮点/启发/源码/口碑四项铁律内容。🔍🐙
