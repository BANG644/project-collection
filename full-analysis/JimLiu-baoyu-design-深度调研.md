# 🔬 JimLiu/baoyu-design — 全方位深度调研

> **调研日期**: 2026-07-09 | **数据来源**: GitHub API + README + 源码树 + 中文社区评测 | **总评**: ⭐ 2,491 | 🍴 185 | 🍃 MIT

## 📌 一句话定位

**把 Claude Design（claude.ai/design）的设计引擎打包成本地可安装的 Agent Skill**——让 Cursor、Claude Code、Codex 等本地 Agent 直接产出高保真 UI 原型、交互式原型、幻灯片、线框图，输出自包含的 HTML 文件，无需依赖 Anthropic 托管的网站。

> 核心判断：2.5K ⭐ 但 GitHub Trending 常见榜上有名（2026年6月创建），说明这不仅是"工具"，而是**本地设计工作流的一种新范式**——让 Agent 替代 Figma/Sketch，直接在代码仓库里完成设计迭代。

## ⭐ 项目亮点

1. **离线可用的 Claude Design** — 脱离 `claude.ai/design` 网站，在本地 Agent 中复刻官方设计能力，且无需额外订阅
2. **Figma `.fig` 文件离线解码** — 直接导入 Figma 源文件（无需 Figma API Key），完全在本地解析视觉结构和样式
3. **PPTX 导出 Pipeline** — "渲染→捕获→转换"三阶段架构：Playwright 无头渲染 HTML 幻灯片，逐节点翻译为 PptxGenJS 对象，保留 `data-anim` 动画属性为 PowerPoint 原生动画
4. **Design System as Code** — 导入的设计系统被编译为本地"约束性视觉契约"，Agent 不会"自由发挥"出设计系统之外的色彩
5. **跨 Agent 兼容** — 通过 `references/` 目录适配 Cursor、Claude Code、Codex 三种 Agent 的工具映射，一套技能跑三个平台

## 🏗️ 项目架构全景

### 目录结构

```
skills/baoyu-design/
├── SKILL.md                    # 流程编排入口（9KB）
├── system-prompt.md            # 设计方法论与工艺标准（41KB，设计之源）
├── references/                 # 环境适配
│   ├── claude.md               # Claude Code 工具映射
│   ├── cursor.md               # Cursor 工具映射
│   └── codex.md                # Codex Agent 工具映射
├── built-in-skills/            # 35+ 专项设计能力（按需加载）
│   ├── hi-fi-design.md         # 高保真设计
│   ├── interactive-prototype.md # 交互原型
│   ├── make-a-deck.md          # 幻灯片制作（22KB，最详细）
│   ├── import-from-figma.md    # Figma 导入
│   ├── export-as-pptx-editable.md # PPTX 导出
│   └── ...
├── starter-components/         # 设计原语（设备壳/画布/动画）
└── agents/                     # 本地 CLI 工具
    ├── gen-pptx/               # PPTX 导出引擎（TypeScript, Playwright）
    ├── gen-video/              # 视频导出引擎
    ├── import-figma.mjs        # Figma 文件解析器
    └── build-preview.mjs       # 预览服务器
```

### 核心工作流

```
用户: "帮我设计一个记账应用的设置页面"
        │
        ▼
┌─────────────────────────────────────┐
│  1. SKILL.md（流程编排）              │
│  - 识别用户意图（高保真 vs 原型 vs 线框）│
│  - 加载 system-prompt.md 方法论       │
│  - 检测运行环境 → 加载对应 references │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  2. 按需加载 built-in-skill         │
│  - "高保真设计" 加载 hi-fi-design.md │
│  - "移动端原型" 加载 mobile-prototype.md│
│  - "幻灯片" 加载 make-a-deck.md      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  3. 设计执行                         │
│  - 加载 starter-components 脚手架    │
│  - 启动预览服务器（python -m http）   │
│  - 生成自包含HTML → design/<project>/ │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  4. 迭代 + 导出                      │
│  - 用户指向预览元素 → 说出修改需求    │
│  - 导出为 PPTX/PDF/MP4/独立 HTML    │
└─────────────────────────────────────┘
```

### 设计哲学：Source of Truth

最值得关注的不是技术实现，而是**设计哲学**：系统明确建立了"设计系统作为约束性契约"的原则。导入 Figma 文件或创建设计系统后，Agent 会生成 `designs/<project>/_ds/<slug>/` 目录，包含所有 Token（色彩/字体/间距）。Agent 被明确禁止"超出设计系统范围自由发挥"——这在 AI 生成设计中极其罕见。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 用法 | 传统替代 |
|------|------|---------|
| **快速原型验证** | 描述功能 → 3 分钟拿到可点击 HTML 原型 | Figma 拖半小时 |
| **设计系统迁移** | 导入 Figma 设计系统 → 自动生成 Token | 人工对照 |
| **开发者设计前期** | 前端在 Cursor 中直接生成 UI 并调试 | 等设计师出稿 |
| **产品演示** | 生成可交互原型 + 导出 PPTX 动画 | Keynote 手动做 |
| **设计评审** | 生成多个变体 → 预览 → 指向修改 | 手动切图 |

### 对同类项目的启发

1. **"设计即代码"的新定义**：不是 SVG/JSX 手写 UI，而是**从自然语言直接到可预览的 HTML**。跳过 Figma/Sketch/XD 这些中间媒介
2. **局部迭代比重新生成更实用**：系统内置的"指向预览中的元素→说出修改"工作流，比每次都"从头描述一个页面"高效得多
3. **离线设计系统的价值**：Figma 离线 `.fig` 解码意味着**不依赖 Figma 的商业 API**，这对团队私有 Repo 和 CI/CD 管线是巨大的优势

## 🧠 核心源码解读

### 1. SKILL.md：入口编排器（9KB）

不是传统的"工具调用脚本"，而是一个**流程编排器**：

```markdown
# 入口流程
1. 读取 README 了解项目上下文（如果用户没有明确说明设计需求）
2. 读取 system-prompt.md 加载设计方法论
3. 识别当前环境（Cursor / Claude Code / Codex）→ 加载对应 references/ 文件
4. 根据用户需求，加载对应的 built-in-skill（多个可并行）
5. 执行设计，生成 `designs/<project>/<file>.html`
6. 启动预览服务器（python3 -m http.server 4311）
```

"先看 README 再执行"的设计意味着 Agent 不需要在 prompt 中原生携带所有上下文——它按需读取，极大降低了上下文占用。

### 2. PPTX 导出引擎（`agents/gen-pptx/`，TypeScript）

三阶段流水线，是该项目的技术皇冠：

```
Phase 1: Render（Playwright 无头渲染）
  HTML slide page → Chromium 渲染 → 实时布局和计算样式
  
Phase 2: Capture（DOM 捕获）
  window.__genpptx 模块 → 获取 DOM 树、计算样式、字体度量、图片
  
Phase 3: Transform（Node.js 转换）
  JSON 节点树 → 逐节点翻译为 PptxGenJS 对象
  data-anim 属性 → 解析为 PowerPoint <p:timing> 动画 XML
```

关键设计：**不解析 HTML 源码，而是渲染后捕获真实布局**。这意味着 HTML/CSS 中任何复杂布局（Flexbox、Grid、阴影、渐变）都能被精确捕获，因为 Playwright 已经完成了浏览器级的渲染计算。

### 3. Figma 离线导入（`import-figma.mjs`，32KB）

```javascript
// 核心：离线解码 .fig 文件（实际是 ZIP）
async function importFigma(figPath) {
    const zip = new JSZip();
    const figData = await zip.loadAsync(fs.readFileSync(figPath));
    
    // .fig 文件结构：meta.json + pages/*.bin（protobuf 编码）
    const meta = JSON.parse(await figData.file('meta.json').async('string'));
    const pages = [];
    for (const file of Object.values(figData.files)) {
        if (file.name.startsWith('pages/')) {
            const binary = await file.async('uint8array');
            pages.push(decodeProtobuf(binary));  // protobuf → JSON
        }
    }
    return extractDesignTokens(meta, pages);
}
```

`fig-materialize.mjs`（319KB）是将 Figma 的 protobuf 二进制格式解码为结构化设计 Token 的核心库——整个项目中最重的单一文件。这意味着 baoyu-design 不依赖 Figma REST API，完全可以在离线环境下工作。

## 🌐 全网口碑画像

### 好评共识

- **"不用打开 Claude Design，也能在本地 Agent 里做 UI 原型"** — 今日头条评测指出"核心价值不是'画得好看'，而是把设计流程嵌入了开发工作流"
- **"体验过就回不去 Figma 了"** — 多位前端开发者反馈，在 Cursor 中直接描述 UI、预览、修改的迭代速度远超传统设计工具（来源：CSDN、掘金评测）
- **"独木成林"** — onlythinking.com 的技术文章评价项目"把 claude.ai/design 的设计引擎拆成 Markdown 指引 + 少量 JS 工具，可读性高、可扩展"
- **"Figma 导入功能是核武器"** — 评论指出可以导入现有设计系统，避免 Agent "自由发挥"出不符合品牌规范的设计

### 差评共识 & 踩坑高发区

| 痛点 | 具体表现 |
|------|---------|
| **模型依赖** | 明确要求 Claude Opus 4.8，其他模型效果大幅退化 |
| **PPTX 导出需本地编译** | `npm install && npx playwright install chromium` 过程耗时且容易出错 |
| **入门门槛** | 需要熟练使用 Cursor/Claude Code，新手有学习曲线 |
| **非设计人员使用** | 描述设计需求的能力本身就需要一定的设计素养 |

### 争议焦点

- **"这到底是谁的工具？"**：前端开发者认为它让设计师边缘化；设计师认为它模仿不了真实的设计判断力。双方观点都有道理——它的定位是**开发者在代码中完成设计**，而非取代设计师
- **"Skill 还是框架？"**：35 个 built-in skills + 4 个 Agent 工具 + 300KB+ Figma 解析库，已远超"Skill"的范畴

## ⚔️ 竞品对比

| 维度 | baoyu-design | Claude Design (原站) | Figma | v0.dev / Lovable |
|------|-------------|---------------------|-------|-----------------|
| **运行环境** | 本地 Agent（离线） | 云端网站 | 云端/桌面 | 云端 |
| **输入方式** | 自然语言 | 自然语言 | 手动拖拽 | 自然语言 |
| **输出格式** | HTML/PPTX/PDF/MP4 | HTML | FIG/导出 | React/Vue 代码 |
| **Figma 导入** | ✅ 离线 protobuf 解码 | ❌ | ✅ 原生 | ❌ |
| **设计系统约束** | ✅ 强约束 | ❌ | ✅ 原生 | ❌ |
| **模型要求** | Opus 4.8 最佳 | 任何 Claude | N/A | 任何 |
| **费用** | 免费（需自有 API Key） | 订阅 | 收费 | 按量付费 |

**选择建议**：
- **在代码仓库中做设计的前端开发者** → baoyu-design（工作流最顺滑）
- **非技术设计师** → Figma（工具成熟、协作完善）
- **快速原型验证** → v0.dev（输出即为标准 React 代码）

## 🎯 核心研判

### 不可替代的价值

baoyu-design 真正独特的不是"AI 生成 UI"——这谁都能做。独特的是**它对设计质量的控制能力**：Figma 导入作为约束性视觉契约、system-prompt.md 的设计方法论作为工艺标准、35 个 built-in skills 各自专注单一设计任务。这让它的输出质量远高于"随便给个大模型 prompt 出图"。

### 风险

1. **模型单点依赖**：最佳效果绑定 Claude Opus 4.8，这是一个双刃剑——Opus 4.8 可用则体验极佳，如果 Anthropic 的价格/可用性政策变化则受影响
2. **Agent 生态风险**：Cursor/Claude Code 改变了 Agent Skill 的加载机制，整个项目需要重构
3. **"杀手"还是"玩具"的争议**：2.5K ⭐ 虽然增长快，但尚未达到"主流"水平。设计工具领域的历史经验是"流量越大越有生命力"——需要观察是否达到 10K ⭐ 这个临界点
4. **维护复杂性**：35 个 built-in skills + 4 个 Agent CLI 工具 + Figma protobuf 解析库，单体维护成本高

### 趋势判断

**成长期**。2026 年 6 月创建，两个月达到 2.5K ⭐，增长曲线健康。如果 Agent 驱动的设计工作流成为主流（而不是设计师驱动的 Figma 工作流），baoyu-design 有望成为该方向的代表项目。

## 📂 关键文件路径速查

| 文件 | 大小 | 说明 |
|------|------|------|
| `skills/baoyu-design/SKILL.md` | 9KB | 入口编排器 |
| `skills/baoyu-design/system-prompt.md` | 41KB | 设计方法论（真理之源） |
| `skills/baoyu-design/built-in-skills/make-a-deck.md` | 22KB | 幻灯片制作（最详细的 built-in skill） |
| `skills/baoyu-design/built-in-skills/export-as-pptx-editable.md` | 10KB | PPTX 导出流程 |
| `skills/baoyu-design/built-in-skills/use-design-system.md` | 18KB | 设计系统使用指南 |
| `skills/baoyu-design/agents/gen-pptx/` | — | PPTX 导出引擎（TypeScript） |
| `skills/baoyu-design/agents/import-figma.mjs` | 32KB | Figma 文件离线解码 |
| `skills/baoyu-design/agents/vendor/fig-materialize.mjs` | 319KB | Figma protobuf 解码库 |
| `skills/baoyu-design/agents/build-preview.mjs` | 68KB | 预览构建器 |
| `skills/baoyu-design/starter-components/deck-stage.js` | 127KB | 幻灯片舞台（最大 starter component） |
