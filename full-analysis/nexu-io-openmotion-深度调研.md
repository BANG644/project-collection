# OpenMotion 深度调研报告

> 仓库：`nexu-io/openmotion` · TypeScript · Apache-2.0 · ⭐ 9,515（2026-11-11，README 徽标 2026-11-09 记 9.5k）· Fork 904 · Open Issues 86 · 创建 2026-05-11 · 更新 2026-11-11 · 主页 open-design.ai/motion

## 1. 📌 一句话定位

OpenMotion 是面向 **Opus 5.5 / 本地 Agent** 的开源全栈视频工作台：上传任意参考视频，让本地 Agent「逆向」拆解其镜头、动效与节奏，用 **HTML/CSS/JS 重建可编辑工程**，再在同一 Studio 里补素材、剪辑、渲染成 MP4。本质是 **Codex/Claude Code 的插件（包名 `codex-motion-plugin` v0.6.3）**，把 HeyGen 的 Hyperframes（HTML→视频引擎，锁定 0.9.7）包装成「用代码拍视频」的创作闭环，奉行 BYOA（自带 Agent）+ BYOK（自带 Key）+ Local-first。

## 2. ⭐ 项目亮点

1. **「逆向工程任意视频」是差异化核心**（README.REVERSE-ENGINEERING.md:37）：不是文生视频，而是把别人的片子拆成「钩子/镜头/运镜/节奏/声音」五元组，用你的素材换壳重生，并沉淀为可复用的 Motion Design Skill 包。
2. **Motion.md 创作规范格式**（docs/motion.md）：把「品牌包 + 故事板 + 时间轴 + 运动语言 + 审片规则」写进一份 Markdown，作为 Agent 可读取的显式上下文，让「风格克隆」可分享、可 fork。
3. **11 个公开 MCP 工具 + 22 个本地 Agent 适配**（README:636、README:43）：Claude Code、Codex、Cursor、Gemini CLI、Trae 等都能通过 stdio MCP 接管工程，而非绑定单一 IDE。
4. **内置 7 模型 Model Gateway（BYOK）**（README:531-534）：Codex Image / Nano Banana 2 / Seedance 2.0 / Wan 2.2 / Suno v4 / Kokoro / fal.ai，生成结果落盘进时间轴继续手改——生成与编辑同一条管线。
5. **本地优先、零按次收费**：本地工作流不收订阅/渲染费（README:409），只付你自己的模型 Key 与算力。

## 3. 🏗️ 项目架构全景

**目录结构（根运行时不依赖 OD 主应用，docs/product/architecture.md）**：
```
openmotion/
├── mcp.ts                 # MCP 服务器（11 工具、phase1 配置档）
├── browser.ts             # Puppeteer-Core + CDP 无头 Chrome 运行时
├── workspace.ts           # 工程/版本/资源 revision 存储
├── server.ts              # 预览与渲染服务（FFmpeg/FFprobe）
├── studio/  web/          # React19+Vite 前端（CodeMirror、dockview、zustand、gsap）
├── docs/                  # 架构、Model Gateway、Motion.md、MCP 契约
├── library/skills/        # 5 个核心 Skill + Motion Design Remix / Presenter Story
├── scripts/               # verify-export、motion-scan、adapter 生成
└── .github/workflows/     # CI、发布校验、gitleaks 扫描
```

**设计哲学**：「Motion as code, not as a project file」——动画活在网页里、可被查询/回滚/编程，不是导出管线末端的文件。Agent 推理与工具编排交给用户的 MCP 客户端，本地网页只负责存稿、接收写回、续编。**渲染链路**：选中版本 → HTML 引擎 + Chromium 截帧 → FFmpeg 合成 MP4，并对文件规格做校验（scripts/verify-export.ts）。

**技术栈关键配置**：Node ≥22.18（package.json engines，但 README:553 某处写 26.11.1，版本口径不一致）；依赖 `@hyperframes/*@0.9.7`、`puppeteer-core@25`、`gsap@3.15`、`react@19`、`zustand@5`；`node --experimental-strip-types` 直接跑 TS。

## 4. 💡 应用场景与启发

- **典型场景**：产品发布片（Stripe 翻卡→胶片帧对照案例）、口播改造（Dan Martell 重制）、UGC 复刻、AI recut（百天照片日记）、品牌 teaser（Kimi K3 / ElevenLabs Reception）。
- **可复用方案模式**：
  - **「参考→拆镜→换料→审片→沉淀 Skill」** 五步法（docs/motion.md 流程图）——把爆款片子的「运动语法」变成可 transfer 的设计知识单元。
  - **乐观并发的工程版本控制**（见 §5 workspace.ts）——多端（Agent 与 Studio）编辑同一工程时避免互相覆盖，值得任何协作式代码编辑器借鉴。
  - **本地 Codex 仅作生图适配器、云 Key 带验证态**（docs/model-gateway.md）——把「能力探测 / 鉴权 / 可用 / 已验证 / 已拒绝」显式建模，比偷偷自动降级更诚实。
- **值得学什么**：把「AI 视频」重新定义为「可编辑的确定性 HTML 工程」而非黑盒生成，使精确修改、可重复渲染、版本审计成为可能——这是相对生成式视频模型的结构性优势。

## 5. 🧠 核心源码解读

**① 浏览器运行时的安全隔离（browser.ts:44-58）—— 未公开的设计点**
```ts
await page.setRequestInterception(true);
page.on('request', r => {
  const url = r.url();
  if (r.isNavigationRequest() && !/^(https?:|about:blank)/i.test(url))
    void r.abort(); else void r.continue();   // 阻断非 http(s) 导航
});
cdp.on('Page.screencastFrame', e => { tab.frame = e.data;
  tab.publish('frame', { data: e.data }); });  // CDP 截帧流式回传
```
**为什么**：Agent 生成的 HTML 是「不可信内容」，OpenMotion 把它放进独立浏览器上下文、拦截本地文件/伪协议导航，并用 CDP screencast 而非整页截图取帧——既防本地文件泄露，又让预览实时流式。**非显而易见**：文档未强调这套「不可信页面沙箱」，这是它能安全渲染用户/Agent 任意 HTML 的关键。

**② 工程版本的乐观并发守卫（workspace.ts:47-50、35）**
```ts
export class Conflict extends Error {
  constructor(){ super('工程已被 Studio 或 Agent 更新，请重新读取 revision 后再修改。'); }
}
export function projectPath(name:string){ /* 严格白名单：长度<240、禁 \\ : 控制符、禁 . 开头与 node_modules/renders 等 */ }
```
**为什么**：Studio 与 Agent 共享同一 HTML 工程，`filePath` 强制白名单 + 每次写操作带 `expectedRevision`，旧请求改新稿直接抛 `Conflict`。这是协作编辑的「版本即契约」思路，README 没展开。**非显而易见**：`projectPath` 同时是防目录穿越的安全边界。

**③ MCP 的 phase1 配置档与运行重载守卫（mcp.ts:31、65）**
```ts
if (registry.profile !== 'phase1' || !toolNames.includes(name)) return invokeRpc(...);
// 插件目录被替换/删除时强制重载，避免操作落到错误工程：
if (!current || current.dev !== runtimeDirectory.dev || current.ino !== runtimeDirectory.ino)
  throw Object.assign(new Error('Motion 插件目录被替换，请重载 MCP 连接'), {code:'MCP_RUNTIME_RELOAD_REQUIRED'});
```
**为什么**：用文件 inode 检测「插件目录是否被动过」来强制重连，是对热更新/重装场景的务实兜底；phase1 档把工具集与资源访问分级开放。**非显而易见**：MCP 埋点里有 `replayed` 字段与 `mcp_tool_finished` 的 outcome 统计，暗示存在**请求幂等/重放检测**机制，对外未说明。

## 6. 🌐 全网口碑画像

- 🟢 **Product Hunt 首秀 #9（85 upvotes）**（kongchang.com）：「OpenMotion is a free macOS motion design studio… describe a scene in one sentence, attach screenshots, AI generates an editable motion graphics video.」——肯定其「生成后仍保留完整编辑控制」。
- 🟢 **生态博文（blog.mean.ceo, Motion Design News 2026-11）**：「It critiques its own work before you see it」——盛赞 Opus 5.5 工作流的自我审片循环，是 OpenMotion 所依赖的创作范式。
- 🟢 **youmind.com（Raphael Aubry）**：「the prompt is maybe 10% of the video. The other 90% is the harness around it.」——印证 OpenMotion 把「harness」工程化的价值。
- 🟡 **新浪/网易科技（2026-11-11）**：「ClaudeVideo 已收录 1276 段作品、X 累计观看 7890 万次」——这是 Opus 5.5 代码生视频大趋势，OpenMotion 是其中最系统的开源封装，但也说明「风口红利」成分高。
- 🔴 **命名撞车争议**：GitHub 上存在 **straygizmo/open-motion（Remotion 替代品）** 与 **Yuan-ManX/open-motion（motion runtime）** 两个同名/近似名仓库，搜索「OpenMotion」极易混淆，对品牌与 SEO 是实打实风险。
- 🔴 **隐性成本批评**：BYOK 看似免费，但图片/视频/音乐生成强依赖 Atlas Cloud、fal.ai、Suno 等**付费云 Key**，本地真正「零成本」只限于纯 HTML 动效；且 README 内部 Node 版本口径（22.18 vs 26.11.1）不一致，新手易踩坑。

## 7. ⚔️ 竞品对比

| 维度 | **OpenMotion** | **Remotion** | **Runway / Kling** | **ComfyUI** |
|---|---|---|---|---|
| 范式 | 代码→视频 + Agent 逆向重建 | 代码（React）→视频 | 文/图生视频（扩散模型） | 节点式生图/视频管线 |
| 可编辑性 | 高（HTML 工程可续编） | 高（组件化） | 低（黑盒重生成） | 中（节点重跑） |
| 可控精度 | 像素/帧确定性 | 帧确定 | 低 | 中 |
| 本地优先 | 是（渲染本地） | 是 | 否（云） | 是 |
| 学习曲线 | 中（需懂 HTML+Agent） | 中（需 React） | 低 | 高 |
| 谁适合 | 想把爆款「拆了重做」的创作者/团队 | 程序员做数据可视化视频 | 要写实人物/自然运动 | 折腾扩散模型的极客 |

**选型建议**：要「精确复刻+可改」选 OpenMotion/Remotion；要「写实人物、复杂自然运动」仍选 Runway/Kling 等生成模型；OpenMotion 的优势区是**动态图形、信息可视化、产品展示、技术科普、风格化 3D**——恰好是 Remotion 的 Agent 增强版，而非 Runway 的替代品。注意它的上游是 **Hyperframes（HeyGen）**，严格说 OpenMotion 是「Agent 编排层 + Studio 壳」，渲染内核外购。

## 8. 🎯 核心研判

- **优势**：把「AI 视频」从黑盒生成重定义为「可编辑、可审计、可复用的确定性 HTML 工程」；MCP 多 Agent 适配 + 7 模型 Gateway + 版本并发守卫，工程完成度高；Apache-2.0 本地零订阅费。
- **风险**：① 命名撞车导致认知混乱；② 媒体生成强依赖付费云 Key，「免费」有边界；③ 新鲜度高（创建仅半年）、issue 86 个、版本 0.6.x，仍处早期，API/契约可能变；④ 本质重度依赖 Hyperframes 与浏览器/FFmpeg 本地环境，Mac 优先、跨平台与性能待验证。
- **适用**：产品发布片、口播改造、UGC 复刻、风格化动态图形、需要反复精修的视频。
- **不适用**：高写实人物/连续影视镜头（仍逊于生成模型）、无本地 Chrome/FFmpeg 的纯云端 Agent、不愿配模型 Key 的纯小白。
- **趋势判断：上升期（rising）**。踩中 Opus 5.5「代码生视频」风口（ClaudeVideo 近 1300 作品、7900 万观看），又是该范式里最完整的开源封装；但需警惕「风口红利」退潮后与生成模型的定位收敛。

## 📂 关键文件路径速查

1. `README.REVERSE-ENGINEERING.md` — 主说明（逆向工程定位、11 MCP 工具、7 模型墙）
2. `package.json` — 依赖与脚本（`codex-motion-plugin` v0.6.3，Node≥22.18，Hyperframes 0.9.7）
3. `mcp.ts` — MCP 服务器入口（phase1 配置档、RPC、inode 重载守卫、埋点）
4. `browser.ts` — Puppeteer-Core + CDP 无头 Chrome 运行时（不可信页面沙箱、截帧）
5. `workspace.ts` — 工程/资源/revision 存储（`Conflict` 并发守卫、`projectPath` 白名单）
6. `server.ts` — 预览与渲染服务（Chromium + FFmpeg/FFprobe 出片）
7. `docs/product/architecture.md` — 产品架构与职责分层（根运行时不依赖 OD 主应用）
8. `docs/model-gateway.md` — Model Router 能力状态机（Agent installed→available→verified）
9. `docs/motion-md.md` — Motion.md 创作规范（v0.1 提案，Skill 包契约）
10. `docs/mcp-phase1-tools.md` — 11 个 MCP 工具契约
11. `scripts/verify-export.ts` — 导出校验（画质/声音/时间轴证据）
12. `scripts/motion-scan.mjs` — 发布期 gitleaks 二进制（sha256 钉死）供应链加固
13. `library/skills/` — 5 核心 Skill + Motion Design Remix / Presenter Story
14. `web/` 与 `studio/` — React19+Vite 前端（设计系统、模板画廊、播放器）
15. `.github/workflows/` — CI、发布校验、安装检查流水线
