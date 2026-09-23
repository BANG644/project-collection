# GoogleChrome/chrome-extensions-samples 深度调研

> 调研日期：2026-09-24 | 星标：17,778⭐ | 语言：JavaScript（含少量 TS/其他） | 许可：Apache-2.0 | 默认分支：main | 最近活跃：2026-09-22 | 官方维护：Google Chrome 团队

## 一、项目定位

**Chrome 扩展（Chrome Extensions）与已废弃 Chrome Apps 平台的官方示例代码库**。由 Google 官方维护，是学习、对照、二次开发浏览器扩展的"标准参照系"——每个示例聚焦单个 API 包或跨多个 API 的完整功能扩展，可用 `Load Unpacked` 直接加载运行。

> 关联背景：用户在做浏览器自动化相关 agent/MCP 能力（如 Windows-MCP、各类 browser 自动化），理解 Chrome 扩展 API 体系有助于"用扩展补足 agent 在浏览器内的细粒度操作能力"。

## 二、项目亮点

1. **官方权威、零歧义**：Google 亲维护，示例即 API 用法的事实标准，规避第三方教程的版本漂移。
2. **体量庞大且结构化**：仅 `_archive/apps` 1,977 个文件、`_archive/mv2` 1,162 个，活跃示例按 API 包与功能分两大目录。
3. **双组织维度**：`api-samples/`（单 API 包聚焦）与 `functional-samples/`（跨多 API 完整功能），满足"学单点"与"看集成"两种需求。
4. **紧跟新特性**：已含 Gemini on-device / in-the-cloud / audio-scribe 等 AI 相关示例，反映扩展与端侧 AI 的结合趋势。
5. **可发现性强**：配套官方 Samples 页面，可按类型/权限/API 检索，降低"找不到对应示例"的摩擦。

## 三、核心架构：目录即分类

```
chrome-extensions-samples/
├── api-samples/          # 聚焦单一 API 包的示例
│   ├── action/  tabs/  downloads/  fontSettings/  history/
│   ├── sandbox/  richNotification/  power/  omnibox/
│   ├── nativeMessaging/  declarativeNetRequest/  contextMenus/  ...
├── functional-samples/   # 跨多 API 的完整功能扩展
│   ├── sample.co2meter/  ai.gemini-on-device/  ai.gemini-on-device-audio-scribe/
│   ├── tutorial.terminate-sw/  libraries-xhr-in-sw/  cookbook.wasm-helloworld/ ...
├── _archive/apps/        # 已废弃 Chrome Apps 平台（不推荐新用）
└── _archive/mv2/         # Manifest V2 资源（MV3 迁移参考）
```

目录规模（tree 统计，递归计数）：
- `_archive/apps`：1,977 文件
- `_archive/mv2`：1,162 文件
- `api-samples/fontSettings`：45、`action`：38、`downloads`：32、`tabs`：29、`sandbox`：26（单包示例量）
- `functional-samples/` 含 `ai.gemini-on-device-summarization`(19)、`tutorial.terminate-sw`(18)、`ai.gemini-on-device`(18)、`sample.text-replacer`(15) 等

## 四、应用场景与启发

1. **agent 浏览器自动化的"能力补给站"**：当 MCP/browser 自动化在页面内遇到"原生 API 才能做的细活"（如 contextMenus 右键、declarativeNetRequest 请求改写、nativeMessaging 与本机程序通信），来这里找最小可运行范例，远比从零查文档快。
2. **MV3 迁移教科书**：`_archive/mv2` 与活跃示例对照，是旧扩展升级 Manifest V3 的现成 diff 来源。
3. **端侧 AI 扩展范式**：`ai.gemini-on-device*` 系列展示"扩展内调用端侧大模型做摘要/转写"，对"把 AI 能力嵌进浏览器"的产品思路有直接参考。
4. **WASM/Service Worker 工程样板**：`cookbook.wasm-helloworld`、`libraries-xhr-in-sw` 给出扩展内跑 WASM、在 SW 里做 XHR 的现代写法。

## 五、源码/内容深度解读

### 1. 双目录组织哲学
```text
api-samples/   →  "我想学某个具体 API 怎么用"（单点，易读）
functional-samples/ → "我想看一个能跑的完整扩展"（集成，贴近真实）
```
> 这种"单点 + 集成"双层示例结构是官方文档工程的成熟范式，值得任何 SDK 示例库借鉴。

### 2. 代表性示例
- **nativeMessaging**：扩展 ↔ 本机程序双向通信，是"浏览器内 agent 调用本地工具/CLI"的关键桥梁范式。
- **declarativeNetRequest**：声明式网络请求拦截/改写（MV3 替代旧 webRequest 阻塞版），广告拦截/请求改造类扩展核心。
- **contextMenus / omnibox**：右键菜单与地址栏命令，agent 触发式交互的 UI 入口。
- **ai.gemini-on-device / -audio-scribe**：端侧 Gemini 做摘要与音频转写，展示"隐私友好型 AI 扩展"实现。

### 3. 安装与验证契约
```bash
git clone <repo>
# Chrome → 扩展程序 → 开发者模式 → 加载已解压的扩展程序 → 选对应示例目录
```
配套检索页：`https://developer.chrome.com/docs/extensions/samples/`（按类型/权限/API 发现）。

## 六、全网口碑

- 作为 Google 官方示例库，是 Chrome 扩展开发者的"圣经级"参考资料，17.8k⭐ 且长期活跃。
- 被几乎所有扩展开发教程、StackOverflow 高赞回答引用为权威代码来源。
- 局限：示例数量多但分散，新手需要一定"知道自己在找什么"的先验；`_archive/` 内旧代码易误用，需注意 MV3 现行规范。

## 七、竞品对比与核心研判

| 维度 | chrome-extensions-samples | MDN / developer.chrome.com 文档 | 第三方教程/脚手架 |
|---|---|---|---|
| 维护 | Google 官方 | Google 官方 | 社区 |
| 形式 | 可运行代码 | 文字+片段 | 文章/模板 |
| 实时性 | 高（紧跟新 API） | 高 | 参差 |
| 适合 | 对照实现 | 查概念 | 入门引导 |

**核心研判**：
- ✅ 任何"要在浏览器内做精细操作"的 agent/自动化项目，都应把它列为首选代码参照——尤其 nativeMessaging、declarativeNetRequest、contextMenus 三类，正好补足纯浏览器自动化的能力边界。
- ⚠️ 仅示例、非框架；若要快速搭扩展骨架，需另配脚手架（如 Plasmo/crxjs），本库负责"标准用法兜底"。
- 📌 建议用户：在 browser 自动化 skill 中引用本库的具体示例路径作为"官方用法基准"，避免自造非标准扩展写法。

## 八、关键文件路径速查

- 仓库根：`https://github.com/GoogleChrome/chrome-extensions-samples`
- 官方检索页：`https://developer.chrome.com/docs/extensions/samples/`
- 单 API 示例：`api-samples/<api-package>/`
- 完整功能示例：`functional-samples/<name>/`
- 迁移参考：`_archive/mv2/`（MV2）、`_archive/apps/`（已废弃）
- 开发基础：`https://developer.chrome.com/docs/extensions/mv3/getstarted/development-basics`

> 数据来源：gh API 仓库元数据 + README + 递归 tree 统计（目录文件计数）。超出 README 部分为架构抽象、竞品研判与应用启发。
