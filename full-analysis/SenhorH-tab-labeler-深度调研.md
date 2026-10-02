# tab-labeler（Browser Tab Renamer）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树），抓取日期 2026-10-03。许可：MIT。语言：TypeScript（Manifest V3 浏览器扩展）。

## 一、项目定位（一句话）
轻量 **Manifest V3** 浏览器扩展：给混乱的标签页**本地重命名**、加 emoji 前缀、重置、查看已命名标签——纯本地、无后端、隐私优先。

## 二、项目亮点（差异化）
1. **本地重命名**：从弹窗重命名当前标签、重置标题。
2. **跨刷新持久**：标签保持打开期间标签名持续生效。
3. **emoji 前缀 + 快捷预设**：✅ Done / 🔥 Important / 📌 Read later / 🐛 Bug / 🧪 Testing。
4. **SPA 友好**：content script 更新 `document.title`，并应对单页应用的标题变化重应用本地标签。
5. **隐私优先**：无后端、无分析、无遥测、无远程同步，标签仅存 `browser.storage.local`。

## 三、核心架构（Manifest V3）
- **manifest**：`public/manifest.json`（MV3 元数据）。
- **popup**：`src/popup/` — 弹窗 UI 与标签操作。
- **content**：`src/content/` — 页面 `document.title` 更新（含 SPA 重应用）。
- **background**：`src/background/` — service worker + content-script 标签查找。
- **lib**：`src/lib/` — 共享标签存储与消息工具。
- **权限最小化**：`storage` + `tabs` + `http(s)` content script 访问；明确不碰 `chrome://` 内部页（弹窗会提示限制而非静默失败）。

## 四、应用场景与启发
- 「最小可用、隐私优先扩展」的范本：权限收口、local-first、处理 SPA 标题重应用等细节。
- 对任何做**浏览器效率插件**的同学是干净的参考；也体现 MV3 service worker 架构下的状态管理范式（storage.local + content script 回写）。
- 与 EverythingToolbar / ExplorerTabUtility 等同属「本地优先的效率小工具」，但落在浏览器域。

## 五、源码深度解读
仓库结构清晰（README 给出完整结构），核心分工：
- `src/lib/` 封装标签存储（local）与消息工具，作为 popup / background / content 的共享层。
- `src/content/` 负责 `document.title` 更新，并监听 SPA 标题变化以重应用本地标签（这是「持久化」不丢失的关键）。
- `src/background/` 作为 service worker 做标签查找与中转。
- ⚠️ 本次未抓取具体源文件全文，代码结构依据 README「Project Structure」章节；如需逐行引用建议后续拉取 `src/lib` 与 `src/content`。

## 六、全网口碑
约 **165 ⭐**，小而美；工程规范完整（`npm run lint / test / build` + `docs/manual-testing.md` 手动 QA 清单），MIT。⚠️ 本次无人值守巡检未单独爬取深度舆情；项目体量小、维护规范清晰。

## 七、竞品对比
| 维度 | tab-labeler | Toby / Workona | OneTab | 传统 Tab Renamer |
|------|------------|----------------|--------|-----------------|
| 核心能力 | 本地重命名标签 | 标签管理/收藏（偏云端同步） | 标签收纳 | 改名 |
| 后端/同步 | ❌ 纯本地 | ✅ 云端 | ❌ | ❌ |
| 隐私 | 优先 | 中 | 中 | 中 |

差异化：极简、本地优先、隐私优先、无同步。
- **风险**：功能单一；依赖浏览器标签 API；MV3 对常驻后台能力有约束。

## 八、核心研判
典型的「小而美、本地优先」工具，工程规范完整（测试/lint/QA），适合学习 **Manifest V3 扩展开发范式**。
- **适合**：作为「最小可用浏览器扩展」模板参考，或需要本地标签治理的场景。
- **局限**：作为生产力工具功能较窄、无跨设备同步；roadmap 提到 Firefox 适配 / 导入导出 / 按窗口分组等，仍处早期。

## 关键文件路径速查
- `public/manifest.json` — MV3 扩展元数据与权限声明
- `src/popup/` — 弹窗 UI 与标签操作
- `src/content/` — 页面标题更新（含 SPA 重应用）
- `src/background/` — service worker + 标签查找
- `src/lib/` — 共享标签存储与消息工具
- `docs/manual-testing.md` — 手动浏览器 QA 清单
