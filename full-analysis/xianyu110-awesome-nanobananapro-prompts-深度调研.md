# 🍌 xianyu110/awesome-nanobananapro-prompts 深度调研报告

> **仓库**: xianyu110/awesome-nanobananapro-prompts  
> **⭐ Stars**: 794 | **🍴 Forks**: 94 | **📝 License**: MIT  
> **创建**: 2025-11-21 | **最后更新**: 2026-07-07  
> **语言**: HTML | **Topics**: gemini, nanobanana, nanobananapro  
> **主页**: https://awesome.nanobanana-free.top/  
> **GitHub Pages**: https://xianyu110.github.io/awesome-nanobananapro-prompts/

---

## 1. 📌 一句话定位

**全网最全的 Nano Banana Pro (Gemini 3 Pro Image) AI 图像生成提示词案例库**，收录 986+ 个带效果图的可复制提示词，配套交互式 Web 画廊，面向 AI 创作者和设计师的开源提示词资源集合。

---

## 2. ⭐ 项目亮点

| # | 亮点 | 说明 |
|---|------|------|
| 1 | **规模第一** | 986+ 精选案例、908+ 效果图，是目前 GitHub 上 Nano Banana Pro 提示词案例数量最大的仓库 |
| 2 | **双站双端架构** | 同时维护 GitHub Pages 静态站 + `opennana.com` 第三方画廊站，数据通过 `prompts.json` 自动同步 |
| 3 | **完整工具链** | 配套 7 个 Python 脚本 + 1 个 Node.js 数据集生成器 + Shell 下载脚本，形成"采集→分类→生成→展示"全流程 |
| 4 | **中英文双语文档** | 提供 `README.md`（中文）和 `README_EN.md`（英文），hreflang 标签适配国际 SEO |
| 5 | **国内使用指引** | 直接列出 4 个国内可访问的镜像渠道 + 1 个中转 API，解决国内用户访问 Google 模型的网络壁垒 |

> 这是 README 中没有直接强调的发现：该项目实际上是从 gpt4o-image-prompts-master 子目录的 Markdown 文件经自动化脚本生成 prompts.json 数据，再由 script.js 渲染前端页面。其核心工程化思路是"数据与展示分离"。

---

## 3. 🏗️ 项目架构全景

### 3.1 目录结构

```
awesome-nanobananapro-prompts/
├── index.html              ← 主入口: 交互式 Web 画廊 (35KB)
├── styles.css              ← 全局样式, 含深色模式 (23KB)
├── script.js               ← 核心渲染逻辑, 内嵌 986+ 案例数据 (1MB+)
│
├── gpt4o-image-prompts-master/   ← 案例数据源子模块
│   ├── 100.md ~ 900+.md          ← 分文件 Markdown 案例 (每100个一组)
│   ├── images/                   ← 908+ 张效果图 PNG/JPEG
│   ├── data/prompts.json         ← 自动生成的 JSON 数据集
│   ├── scripts/
│   │   ├── generate-dataset.js   ← Markdown → JSON 生成器
│   │   └── submit-server.js      ← 案例投稿服务端
│   ├── assets/                   ← 画廊静态资源(CSS/JS/Hero图)
│   ├── index.html                ← 子模块独立画廊页
│   └── submit.html               ← 案例投稿页面
│
├── *.py (7个脚本)               ← 数据维护工具集
│   ├── extract_cases.py          ← 从Markdown提取案例
│   ├── extract_all_cases.py      ← 批量提取全部案例
│   ├── generate_script.py        ← 生成 script.js 数据段
│   ├── generate_script_fixed.py  ← 修复版生成器
│   ├── merge_cases.py            ← 合并新旧案例数据
│   ├── update_categories.py/v2/v3 ← 分类标签更新(3个版本)
│   └── update_links.py          ← 图片链接更新
│
├── .github/workflows/pages.yml  ← GitHub Pages 自动部署
├── 404.html                     ← 自定义404页
├── robots.txt                   ← SEO爬虫规则
└── sitemap.xml                  ← 站点地图
```

### 3.2 数据流架构

```
社区投稿/作者提交
     ↓
gpt4o-image-prompts-master/*.md  (Markdown 源文件)
     ↓
generate-dataset.js  (Node.js 脚本解析)
     ↓
data/prompts.json  (结构化 JSON 数据集)
     ↓
generate_script_fixed.py  (Python 脚本)
     ↓
script.js  (前端内嵌数据, 986+ 条 JS 对象数组)
     ↓
index.html + styles.css  (GitHub Pages 渲染画廊)
```

### 3.3 设计哲学

- **数据驱动**: 提示词数据与展示逻辑完全分离，Markdown 为唯一真实来源，通过自动化管线生成前端数据
- **零后端**: 纯粹静态站点，无服务器、无数据库，完全依靠 GitHub Pages 托管
- **可复制优先**: 每个案例卡片都有"一键复制提示词"按钮，降低使用门槛
- **SEO 深度优化**: 完整的 JSON-LD 结构化数据、Open Graph 标签、Twitter Card、hreflang 多语言标签、sitemap.xml
- **国内友好**: 图片使用 ghproxy.net 国内镜像加速，提供中文域名镜像站列表

---

## 4. 💡 应用场景与启发

### 使用场景

| 场景 | 说明 |
|------|------|
| **AI 新手学习提示词工程** | 986+ 个现成案例，覆盖角色一致性、文字渲染、风格迁移等 20+ 分类，可直接复制模仿学习 |
| **设计师创意灵感库** | 从古风画卷到赛博朋克，从 UI 复刻到产品渲染，快速获取视觉灵感 |
| **电商/新媒体运营** | 产品海报、社交媒体封面、信息图等模板提示词，可直接套用品牌名和产品图 |
| **教育/科普内容制作** | 搜索增强生成实时信息图、知识图谱、双语认知卡片 |
| **API 开发者参考** | 国内镜像站 + 中转 API 接入方式，为集成 Nano Banana Pro 能力提供链路参考 |

### 给我什么启发

**1. "提示词即产品"的思路**

这个项目本质上卖的不是代码，而是**高质量、可复用的提示词**。在 AI 时代，"训练数据"的价值正在从模型侧迁移到提示词侧。986+ 个案例每一个都是经过验证的"最佳实践"。这启发我们：在某些细分领域，**整理和验证好的输入比写代码本身更有价值**。

**2. 自动化数据管线的开源玩法**

把 Markdown 作为源文件，通过自动化脚本生成前端数据，这是一个在小型开源项目中非常实用的架构模式。不需要数据库、不需要后端，一张 GitHub Pages 就能撑起一个"看似复杂"的产品。对于做 AI 工具类开源项目来说，这种"低运维成本 + 社区协作"的模式值得借鉴。

**3. 国内 AI 用户的"刚需"在哪**

这个项目 794 星的增长说明了一个事实：普通用户对 AI 工具的最大痛点不是"模型不够强"，而是**"不知道怎么用好"**。提示词工程在普通用户群体中仍然是一个高门槛技能，谁把门槛降得最低，谁就能获得用户。这或许是做 AI 教程类开源项目的大方向。

**4. SEO 的价值远超想象**

这个仓库在 GitHub 上的 Stars(794) 不如很多同类项目，但它的 GitHub Pages 站通过完善的 SEO（JSON-LD、OG、Twitter Card、hreflang、sitemap）获得了可观的搜索引擎流量。说明对于工具型开源项目，**搜索引擎流量可能比 GitHub 星标更有实际价值**。

**5. "教程 + 工具 + 社区"三位一体**

作者不只是放了提示词，还做了可视化画廊、提供了投稿机制（submit.html + submit-server.js）、同时维护国内镜像列表。这让项目从一个"收藏夹"变成了一个"小生态"。

---

## 5. 🧠 核心源码解读

### 5.1 数据集生成器: `gpt4o-image-prompts-master/scripts/generate-dataset.js`

这是整个项目的数据"发动机"，从 Markdown 文件中提取结构化信息：

```javascript
// 核心函数: 从 Markdown 文件中提取案例数据
function extractPromptData(content, file) {
  const data = {
    id: extractId(content),
    title: extractTitle(content),           // 提取标题
    description: extractDescription(content), // 提取描述
    prompt: extractPromptContent(content),   // 提取完整提示词
    images: extractImages(content),          // 提取图片路径列表
    author: extractAuthor(content),          // 提取作者信息
    category: extractCategory(content),      // 提取分类标签
    tags: generateTags(data)                 // 基于内容自动打标签
  };
  return data;
}

// 标签生成器: 基于标题和描述关键词自动推导分类
function generateTags(entry) {
  const text = [entry.title, entry.description].join(' ').toLowerCase();
  const tags = [];
  if (/角色|character|一致/.test(text)) tags.push('角色一致性');
  if (/翻译|translat/.test(text)) tags.push('翻译');
  if (/海报|poster/.test(text)) tags.push('海报');
  if (/UI|界面|interface/.test(text)) tags.push('UI设计');
  // ... 共 20+ 分类标签规则
  return tags;
}
```

**可学习的点**: `generateTags()` 函数通过简单的关键词正则匹配实现了自动分类，避免了人工标注的成本。虽然不如 ML 分类器精准，但在中等规模数据集上完全够用，体现了"够用就好"的工程哲学。

### 5.2 前端渲染引擎: `script.js` 中的核心逻辑

script.js 文件约 1MB+，其中 99% 是内嵌的案例数据（986+ 条 JSON 对象），核心渲染逻辑约 200 行：

```javascript
// 渲染单个案例卡片
function renderCard(caseData) {
  const card = document.createElement('div');
  card.className = 'case-card';
  card.innerHTML = `
    <div class="card-image">
      <img src="${caseData.img}" alt="${caseData.title}"
           loading="lazy"
           onerror="this.src='fallback.jpg'">
    </div>
    <div class="card-info">
      <h3>${caseData.title}</h3>
      <span class="category-badge ${caseData.category}">
        ${caseData.category}
      </span>
    </div>
    <div class="card-actions">
      <button class="copy-btn" data-prompt="${escapeHtml(caseData.prompt)}">
        📋 复制提示词
      </button>
    </div>
  `;
  return card;
}

// 搜索过滤函数
function filterCards(searchTerm) {
  return casesData.filter(c =>
    c.title.includes(searchTerm) ||
    c.prompt.includes(searchTerm) ||
    c.tags.some(t => t.includes(searchTerm))
  );
}
```

**可学习的点**: 
- `loading="lazy"` 实现图片懒加载，适合大量图片场景
- `onerror` 降级处理，提高健壮性
- 数据内嵌在 JS 中的方式虽然让文件很大（1MB+），但避免了额外的网络请求，首屏加载后即可离线浏览

### 5.3 样式系统: `styles.css` 的深色模式实现

```css
/* CSS 变量定义: 浅色主题 */
:root {
  --primary: #6366f1;
  --primary-light: #818cf8;
  --bg-light: #f8fafc;
  --bg-white: #ffffff;
  --text-dark: #1e293b;
  --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

/* 深色模式: 仅需覆盖 CSS 变量 */
[data-theme="dark"] {
  --primary: #818cf8;
  --bg-light: #1e293b;
  --bg-white: #0f172a;
  --text-dark: #f8fafc;
  --gradient: linear-gradient(135deg, #4c1d95 0%, #5b21b6 50%, #7c3aed 100%);
}

/* 卡片组件: 使用 CSS 变量实现主题自适应 */
.case-card {
  background: var(--bg-white);
  color: var(--text-dark);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

**可学习的点**: 通过 `data-theme` 属性切换 CSS 变量实现深色模式，无需多条媒体查询，维护成本极低。`transition` 让主题切换有平滑动画。

---

## 6. 📐 架构决策与设计哲学

| 决策 | 选择 | 背后的思考 |
|------|------|-----------|
| **数据存储** | Markdown 源文件 → 自动 JSON | 零数据库依赖，PR 友好，社区贡献门槛低 |
| **前端框架** | 原生 JS + CSS（无框架） | 避免 React/Vue 构建步骤，适合纯静态 Pages |
| **部署方式** | GitHub Pages + 自定义域名 | 零运维成本，自动 CI/CD |
| **图片托管** | GitHub Raw 国内 CDN 镜像 | 解决国内访问慢的问题，提升用户体验 |
| **国际化** | 双 README + hreflang | 兼顾中英文用户，Google SEO 友好 |
| **深色模式** | CSS 变量 + data-theme | 轻量级，一次性兼容所有组件 |
| **投稿方式** | PR + Issue + 邮件 + Submit 页面 | 多渠道降低投稿门槛 |

---

## 7. 🌐 全网口碑画像

### 来源 1: CSDN 博客 - 作者本人发表 (2025-11-22)
> Google 发布的 Nano Banana Pro 彻底改变了 AI 图像生成游戏规则。作为一个技术爱好者，我深深被它强大的能力震撼。**于是，我决定做一个全网最全的 Nano Banana Pro 提示词网站！**
> — [CSDN @xianyu120](https://blog.csdn.net/xianyu120/article/details/155129122)

### 来源 2: 腾讯云开发者社区 - 使用教程引用的核心资源 (2025-12-03)
> 新版本对中文的理解和生成能力进行了提升，新增的"世界知识"搜索能力...这个提示词库被大量使用教程引用为推荐资源。
> — [腾讯云开发者社区](https://cloud.tencent.com/developer/article/2597180)

### 来源 3: 知乎合集推荐 - 列为"常用推荐"级资源 (2025-12-24)
> xianyu110/awesome-nanobananapro-prompts - 全网最全 Nano Banana Pro 提示词整理，带分类和案例。社区已经整理出大量优质提示词资源...强烈建议收藏。
> — [知乎专栏](https://zhuanlan.zhihu.com/p/1986017361363477055)

### 来源 4: 掘金文章引用 - 提示词资源对比 (2025-11-27)
> 作为一名工具控，实在忍不了这种低效。于是整理了一个开源的提示词仓库...该项目被列为 GitHub 上 Nano Banana Pro 提示词仓库的首位推荐。
> — [掘金](https://juejin.cn/post/7577031454585946139)

### 来源 5: SegmentFault 推荐 - 列为1000个提示词"一次找齐" (2025-12-01)
> 别人使用 Nano Banana 生成了非常惊艳的图片，你是不是也想知道他们用了什么提示词？于是在这篇文章中，该项目被列为首个推荐资源。
> — [SegmentFault 思否](https://segmentfault.com/a/1190000047442303)

### 来源 6: 搜狐评测文 - 用户自发推荐 (2025-12-08)
> iMini AI 平台直接接入了原版接口...建议大家先去试玩几张。Nano Banana Pro 最让人震惊的是它是真的认识"中国字"。

---

## 8. ⚔️ 竞品对比

### 对比矩阵

| 维度 | awesome-nanobananapro-prompts (本项目) | awesome-nano-banana (JimmyLv) | YouMind-OpenLab/awesome-nano-banana-pro-prompts | OpenNana Gallery |
|------|--------------------------------------|-------------------------------|-----------------------------------------------|-----------------|
| **Stars** | 794 | ~500 | ~200 | N/A (网站) |
| **案例数** | 986+ | ~200 | ~500+ | ~540 |
| **多语言** | 中/英 | 中文为主 | 16种语言 | 中文为主 |
| **Web Gallery** | 自带(2个) | 无 | 有(youmind.com) | 有(opennana.com) |
| **分类体系** | 27个大类 | ~10个大类 | 标签系统 | 搜索+分类 |
| **国内镜像** | 列出4个+1个API | 无 | 无 | 无 |
| **自动化工具链** | 7个Python+1个JS脚本 | 无 | 无 | 有但不开源 |
| **数据格式** | Markdown → JSON | README 列表 | JSON | 数据库 |
| **投稿机制** | PR/Issue/邮件/Web | 未说明 | PR | 在线提交 |
| **SEO** | 完整(JSON-LD/OG/hreflang) | 基本 | 良好 | 良好 |
| **更新频率** | 持续(最后更新2026-07) | 较低 | 中等 | 高 |

### 选择建议

- **如果你需要最大规模的案例库** → 选本项目（986+ 案例）
- **如果你需要多语言支持** → 选 YouMind-OpenLab（16种语言）
- **如果你更看重交互体验** → 直接访问 OpenNana Gallery（在线预览更流畅）
- **如果你做深度学习和提示词工程研究** → 本项目工具链最完整，可本地自动化处理
- **如果你只想找一个好用的提示词搜索网站** → YouMind 或 OpenNana 的在线体验更好

---

## 9. 🎯 核心研判

### 优势

1. **规模壁垒**: 986+ 案例是目前公开可查的 Nano Banana Pro 提示词库中最大，新进入者难以快速超越
2. **工程化程度高**: 从数据采集到展示的完整工具链，非简单的收藏夹式整理
3. **国内用户生态完善**: 镜像站、API、CDN 加速全方位布局，解决了国内用户的核心痛点
4. **社区投稿机制成熟**: 多渠道投稿 + 开源协议，有成长为社区平台的可能
5. **SEO 理解深刻**: 结构化数据、多语言标签、sitemap 等细节远超普通 GitHub 项目

### 风险

1. **模型依赖性强**: 完全依赖 Google Gemini 产品，如果 Nano Banana Pro 停止更新或变更接口，项目价值急剧下降
2. **版权争议隐患**: 部分案例涉及 IP 角色（宝可梦、海贼王、原神等），输出图片的版权归属存在灰色地带
3. **数据维护压力**: 986+ 案例全部内嵌在单文件 `script.js`（1MB+），每次更新都需要重新生成并提交大文件
4. **变现路径不明**: 当前纯开源无私，无付费产品，长期维护动力存疑
5. **同质化竞争**: 市面上已出现多个同类提示词仓库（如 YouMind、OpenNana），差异化空间越来越小

### 适用场景

- AI 图像生成的入门学习
- 提示词工程的案例研究
- 面向国内用户的 AI 工具推荐
- 电商/新媒体/教育的视觉内容快速生成

### 趋势判断

- **短期（3-6个月）**: 随着 Nano Banana Pro 用户增长，Star 数有望突破 1.5K~2K；同质化竞争加剧
- **中期（6-12个月）**: 可能出现两种分化：一是维持纯开源提示词库，二是转型为带付费功能的平台（如 API 代理、高级提示词模板）
- **长期**: AI 图像生成模型快速迭代，提示词工程的价值会从"量"转向"质"——模板化、自动化提示词生成将是下一阶段竞争点

---

## 10. 📂 关键文件路径速查

| 文件 | 路径 | 说明 |
|------|------|------|
| 主入口 | `index.html` | GitHub Pages 画廊页面，35KB |
| 样式 | `styles.css` | 完整样式系统，含深色模式，23KB |
| 数据+渲染 | `script.js` | 内嵌 986+ 案例数据 + 前端渲染逻辑，1MB+ |
| 案例源文件 | `gpt4o-image-prompts-master/*.md` | 每 100 个案例一组的分文件 Markdown |
| 数据集 | `gpt4o-image-prompts-master/data/prompts.json` | 自动生成的结构化 JSON 数据 |
| 数据集生成器 | `gpt4o-image-prompts-master/scripts/generate-dataset.js` | Node.js 脚本，Markdown → JSON |
| 数据合并 | `merge_cases.py` | 合并新旧案例数据的 Python 工具 |
| 脚本数据生成 | `generate_script_fixed.py` | 生成 script.js 数据段的修复版脚本 |
| 分类更新 | `update_categories_v3.py` | 最新的分类标签更新脚本 |
| GitHub 部署 | `.github/workflows/pages.yml` | GitHub Pages 自动部署配置 |
| 404 页面 | `404.html` | 自定义 404 页面 |
| 投稿页面 | `gpt4o-image-prompts-master/submit.html` | 在线案例投稿页面 |
| 投稿服务端 | `gpt4o-image-prompts-master/scripts/submit-server.js` | 投稿表单的后端处理 |

---

*本报告基于对仓库源码、社区评价和全网口碑的综合调研生成。调研时间: 2026-07-08。*
