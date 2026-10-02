# mem0-chrome-extension（跨 LLM 记忆浏览器扩展）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / 源码），抓取日期 2026-10-03。许可：MIT。语言：TypeScript（Manifest V3 浏览器扩展）。状态：**已归档（archived）**。

## 一、项目定位（一句话）
为 ChatGPT / Claude / Perplexity 等 AI 助手加一层「跨会话、跨产品」的**长期记忆**，由 Mem0 云端 API 支撑——让不同 AI 之间的上下文可以共享、复用。

## 二、项目亮点（差异化）
1. **通用记忆层**：在 ChatGPT、Claude、Perplexity 等多个 AI 助手间共享上下文。
2. **智能上下文捕获**：自动从对话中提取相关信息写入记忆。
3. **智能记忆检索**：在合适时机把相关记忆浮现到当前对话。
4. **一键同步**：可与 ChatGPT 已有记忆做一次同步。
5. **记忆仪表盘**：集中管理所有记忆；完全免费、无广告、MIT、可 fork 继续维护。
> ⚠️ 最大反差：仓库顶部明确标注 **archived**——不再积极维护，但 600+ stargazers / 97 forkers。

## 三、核心架构（Manifest V3）
- `manifest.json`：MV3 扩展元数据。
- `src/background.ts`：service worker，消息中枢（安装初始化、面板/设置消息路由、右键菜单与直链追踪）。
- **每个 AI 站点一个 content script**：`src/chatgpt/`、`src/claude/`、`src/gemini/`、`src/deepseek/`、`src/grok/`、`src/perplexity/`、`src/mem0/`——分别注入对应站点捕获/浮现记忆。
- `src/popup.html` / `src/popup.ts`：记忆仪表盘 UI。
- `src/context-menu-memory.ts`、`src/direct-url-tracker.ts`：右键菜单记忆、直链追踪。
- **后端**：Mem0 云端 API（`app.mem0.ai`），扩展本身只是客户端。

## 四、应用场景与启发
- 把「记忆」做成 LLM 应用之上的**可插拔层**，是 AI 助手增强方向的早期实践。
- 对做「跨产品上下文管理 / 个人 AI 记忆」的产品有参考意义。
- 但**已归档**说明「纯客户端 + 云端 API」的扩展模式可持续性存疑（依赖 Mem0 商业服务、无自建后端）。

## 五、源码深度解读
**`src/background.ts`（消息中枢）**：service worker 注册 `onInstalled`（设置 `memory_enabled: true`）、两类 `onMessage` 监听（`OPEN_DASHBOARD` 打开仪表盘、`SIDEBAR_SETTINGS` 转发给 content script），并在末尾初始化右键菜单与直链追踪：
```ts
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({ memory_enabled: true }, () => { ... });
});
chrome.runtime.onMessage.addListener((request) => {
  if (request.action === SidebarAction.OPEN_DASHBOARD && request.url)
    chrome.tabs.create({ url: request.url });
  return undefined;
});
initContextMenuMemory();
initDirectUrlTracking();
```

**`src/mem0/content.ts`（鉴权）**：在向 `https://app.mem0.ai/api/auth/session` 取会话后，把 `access_token` 写入 `chrome.storage.sync`，并设置 `userLoggedIn`：
```ts
fetch('https://app.mem0.ai/api/auth/session')
  .then(r => r.json())
  .then(data => {
    if (data?.access_token) {
      chrome.storage.sync.set({ access_token: data.access_token });
      chrome.storage.sync.set({ userLoggedIn: true });
    }
  });
```
> 结构判断：每个 AI 站点的 content script 负责「读页面对话 → 调 Mem0 API 存/取记忆」，background 负责跨标签消息与生命周期——典型 MV3「content + service worker」分工。

## 六、全网口碑
600+ ⭐、97 fork、明确归档；README 致谢社区但未单独爬取深度舆情。体量小、结构清晰，是「跨 LLM 记忆」的早期代表实现。

## 七、竞品对比
| 维度 | mem0-chrome-extension | ChatGPT 原生记忆 | 各站「memory」扩展 | Mem0 官方其他产品 |
|------|----------------------|----------------|-------------------|-------------------|
| 跨产品共享 | ✅ 多助手 | ❌ 仅 ChatGPT | 多为单站 | ✅（API/平台） |
| 后端 | Mem0 云端 | OpenAI 云端 | 各异 | Mem0 云端 |
| 维护状态 | ❌ 已归档 | ✅ 官方 | 各异 | ✅ 活跃 |

差异化：跨 LLM 共享 + 开源可 fork。**风险**：强依赖 Mem0 商业 API、已停维护、无自建后端。

## 八、核心研判
作为「跨 LLM 记忆」的早期开源实现有学习价值（MV3 多 content-script 架构清晰），但 **archived 状态是最大短板**——不适合直接用于生产，更适合当作「记忆层插件」的设计参考或 fork 起点。

## 关键文件路径速查
- `manifest.json` — MV3 扩展元数据与权限
- `src/background.ts` — service worker 消息中枢
- `src/mem0/content.ts` — Mem0 云端鉴权与会话
- `src/{chatgpt,claude,gemini,deepseek,grok,perplexity}/content.ts` — 各 AI 站点注入脚本
- `src/popup.ts` — 记忆仪表盘 UI
- `src/context-menu-memory.ts` / `src/direct-url-tracker.ts` — 右键菜单 / 直链追踪
