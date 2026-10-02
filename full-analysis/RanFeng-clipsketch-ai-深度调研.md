# ClipSketch AI（剪辑·素描）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树），抓取日期 2026-10-03。许可：MIT。语言：TypeScript（React 19 单页应用）。

## 一、项目定位（一句话）
把 Bilibili / 小红书视频链接解析 → 帧级标记精彩瞬间 → 用 Google Gemini 一键生成**手绘风格故事板 + 多风格社媒文案**的 AI 内容创作工作台。

## 二、项目亮点（差异化）
1. **多源导入**：解析 B 站/小红书分享链接（支持短链 + 混合文案）。
2. **帧级标记系统**：毫秒级记录、`T` 键打点，导出 TXT 时间轴或 ZIP 图片包。
3. **AI 艺术工作室（Gemini 驱动）**：整合多标记帧成连贯手绘故事板（`gemini-3-pro-image-preview`）；基于视觉内容生成 3 种文案风格（情感故事/干货教程/短小精悍）；角色融合、封面生成、批量精修（支持 Batch API 省成本）。
4. **全平台适配**：响应式（PC/iPad/手机竖屏切换上下布局）。
5. **本地持久化 + 一键部署**：IndexedDB 存状态，Docker（`earisty/clipsketch-ai:latest`，端口 3000）。

## 三、核心架构
- **前端单仓**：React 19 + TypeScript + Tailwind + Lucide React；`App.tsx`（约 37KB）为整合入口。
- **AI SDK**：`@google/genai`（`@google/genai`）直连 Gemini；Canvas 截图、JSZip 打包下载。
- **无后端**：纯前端直连 Gemini API，Key 走 `.env.local` 或运行时输入；`referrerPolicy="no-referrer"` + 特定代理策略解决外部视频跨域播放/截图。
- **数据**：IndexedDB 本地状态持久化。

## 四、应用场景与启发
- 「视频 → 故事板 → 文案」流水线非常适合二创/种草场景；给「前端直连多模态大模型」的轻量架构样本（无后端、IndexedDB 状态）。
- **启发**：帧级标记 + AI 重绘的组合可复用到任何「素材 → 成品」工具；处理第三方视频跨域是此类工具必须攻克的工程点（README 专门点出代理策略）。
- 与 RedInk 互补：RedInk 从「一句话」生成图文，ClipSketch 从「已有视频」反推故事板/文案。

## 五、源码深度解读
仓库以前端单仓为主，未见独立后端目录（README 与目录树均指向 `App.tsx` + `src/` 组件）。关键技术约束在跨域视频处理：
- 为支持外部视频链接播放与截图，使用了特定代理策略 + `referrerPolicy="no-referrer"`（README「注意事项」明确）。
- AI 调用集中于 `@google/genai` 封装；故事板生成依赖 `gemini-3-pro-image-preview`、文案依赖 `gemini-3-pro-preview`。
- ⚠️ 本次未抓取 `App.tsx` 全文（37KB），具体实现细节以 README 描述为准；如需源码级引用建议后续拉取 `App.tsx` 与 `src/` 组件。

## 六、全网口碑
约 **1.9k ⭐**，多语言 README（中/英/日/韩），Docker Hub 有镜像。⚠️ 本次无人值守巡检未单独爬取深度舆情；星标与多语言文档反映国际化接受度尚可。

## 七、竞品对比
| 维度 | ClipSketch AI | RedInk | NarratoAI | 剪映/必剪 |
|------|--------------|--------|-----------|-----------|
| 输入 | 视频链接 | 一句话 | 视频 | 视频 |
| 输出 | 手绘故事板+文案 | 社媒图文 | 解说文案+剪辑 | 成片 |
| 后端 | 无（纯前端） | Flask | FastAPI | 闭源 |
| 许可 | MIT | CC BY-NC-SA | MIT | 闭源 |

差异化：聚焦「手绘故事板 + 种草文案」且纯前端轻量。
- **风险**：强依赖 Gemini 图像模型（403 权限门槛）；第三方视频链接解析易被平台反爬/失效。

## 八、核心研判
轻量、定位鲜明的前端 AI 创作工具，适合快速二次开发；但无后端意味着无多用户/无云端队列，且深度绑定 Gemini、依赖外部视频解析稳定性。
- **适合**：作为「纯前端 + 多模态大模型」范式参考、二创/种草工具原型的起点。
- **建议**：生产化需补足后端（配额/队列/缓存）与多模型兜底，降低对单一厂商与第三方链接解析的依赖。

## 关键文件路径速查
- `App.tsx` — 主入口（整合导入/标记/AI 工作室流程）
- `Dockerfile` — 单容器部署（端口 3000）
- `.env.local`（`GEMINI_API_KEY`）— API Key 配置
- `img/` — 文档与预览图
- `README.en.md` / `README.ja.md` / `README.ko.md` — 多语言文档
- ⚠️ 未见独立后端目录（纯前端架构）
