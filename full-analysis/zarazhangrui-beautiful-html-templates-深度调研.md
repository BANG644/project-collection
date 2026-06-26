# 📊 beautiful-html-templates 深度调研报告

> **仓库**: [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)  
> **Stars**: 2,698 | **Forks**: 246 | **语言**: HTML / JavaScript | **License**: MIT  
> **创建时间**: 2026-05-05 | **最后推送**: 2026-06-09  
> **批次**: batch_03 (#42) | **调研日期**: 2026-06-17

---

## 一、项目定位

beautiful-html-templates 是一个**面向 AI Agent 的 HTML 幻灯片模板库**。它不是给人类设计师用的，而是让 Claude Code、Cursor、OpenClaw 等编码 Agent 能根据用户的一两句需求，自动挑选最合适的模板并生成美观的 HTML 幻灯片。

### 核心创新
传统的"模板库"是为人类准备的手动编辑资源；这个库的独特之处在于 **Agent-first 设计**——模板的选择、克隆、内容填充全部由 Agent 自主完成，用户只需要说一句"帮我做一个产品发布会幻灯片"即可。

---

## 二、架构设计

### 仓库结构

```
beautiful-html-templates/
├── AGENTS.md              # Agent 操作手册——如何读取 index.json、匹配模板、克隆、适配内容
├── index.json             # 34 个模板的元数据索引（Agent 唯一需要读取的文件）
├── templates/             # 34 个模板目录，每个含 index.html + metadata.json
├── runtime/               # Agent 运行时支持
│   └── deck-stage.js     # 幻灯片舞台运行时（22KB JS）
├── screenshots/           # 每个模板 3 张截图（封面、中间、后面）
├── README.md              # 人类可读的画廊
└── LICENSE
```

### 设计决策
1. **仅一个入口文件**：Agent 只需读取 `index.json` 就能了解全部 34 个模板的元数据、视觉特征、适用场景
2. **模板不自包含执行逻辑**：统一由 `deck-stage.js` 提供运行时，保持模板 HTML 干净、可预测
3. **截图驱动选择**：人类浏览 README 画廊，Agent 读取 `index.json` 的 schema

---

## 三、34 个模板全景

模板涵盖多种视觉风格，按设计体系分类：

### 编辑风格（Editorial）
| 模板 | 视觉特征 | 适用场景 |
|------|---------|---------|
| Soft Editorial | 暖纸色 + Cormorant 衬线体 + 鼠尾绿/腮红/柠檬黄 | 品牌故事、精致报告 |
| Editorial Forest | 森林绿 + 尘土粉 + 暖奶油色 | 季度回顾、自然主题 |
| Emerald Editorial | 祖母绿 + 深蓝 + 粗体 Bodoni 展示字 | 商业报告、财报演示 |
| Editorial Tri-Tone | 尘土粉 + 芥末奶油 + 深酒红 | 创意提案、设计评审 |

### 实验/复古风格
| 模板 | 视觉特征 | 适用场景 |
|------|---------|---------|
| Pin & Paper | 黄纸 + 安全别针插画 + 手写体 | 手工作坊、创意工作坊 |
| Sakura Chroma | 复古日式磁带美学 + 彩虹缎带 | 音乐/文化/创意展示 |
| Stencil & Tablet | 骨白纸 + 镂空字 + 六色土色盘 | 考古/教育/非盈利 |
| Cobalt Grid | 电光钴蓝 + 方格纸 + 像素故障装饰 | 技术演示、数据展示 |

### 现代/极简风格
| 模板 | 视觉特征 | 适用场景 |
|------|---------|---------|
| Monochrome | 象牙账本纸 + 纯黑字体 | 学术、法律、正式报告 |
| Neo-Grid Bold | 新粗野主义 + 单一霓虹黄点缀 | 激进品牌、创投 Pitch |
| Vellum | 深蓝画布 + 暖黄衬线 | 安静、学术、高端 |
| Creative Mode | 奶油纸 + 多色（绿/粉/橙/黄） | 创意作品集、艺术展示 |

### 叙事/大胆风格
| 模板 | 视觉特征 | 适用场景 |
|------|---------|---------|
| People's Platform | 活动海报能量 + 蓝/橙/红 | 社会议题、社区动员 |
| Pink Script | 黑画布 + 热粉笔触 | 晚宴、时尚、创意活动 |
| Children's Mural | 蜡笔画 + 明亮多彩 | 教育、儿童主题 |

---

## 四、Agent 操作流程（来自 AGENTS.md）

1. **读取 `index.json`** → 获取全部模板的视觉特征标签和适用场景
2. **匹配用户需求** → 根据关键词（"专业"、"创意"、"简约"）筛选候选模板
3. **克隆模板** → 将目标模板目录复制到输出位置
4. **填充内容** → Agent 按照模板的 HTML 结构填入用户内容
5. **加载运行时** → 在页面中包含 `deck-stage.js` 获得翻页动画等交互
6. **交付** → 生成可独立打开的 HTML 文件，用户无需任何额外工具即可浏览

---

## 五、技术亮点

### 1. Agent-first Schema 设计
`index.json` 包含每个模板的：
- 颜色方案（primary, secondary, accent, background）
- 字体家族（headline, body）
- 视觉标签（"modern", "editorial", "bold", "minimal"）
- 适用场景推荐
- 结构特征（单列/双列/网格、图片有无、数据表格有无）

### 2. 无依赖运行时
`deck-stage.js` 约 22KB，零外部依赖，自动检测键盘/触控/鼠标事件。

### 3. Agent 自主决策
Agent 可以通过 `index.json` 的 schema 推理出最适合的模板，无需用户干预。

### 4. 纯 HTML 输出
生成的幻灯片是单个自包含 HTML 文件，无需服务器、无需构建工具、无需安装。

---

## 六、关键优势与不足

### 优势
- 🎨 **高质量设计**：34 个模板覆盖从商业到创意的全场景
- 🤖 **Agent-first**：不同于人类设计师模板库，整个设计围绕 Agent 自主决策
- 📦 **零依赖交付**：一个 HTML 文件就是一整份幻灯片
- 🔄 **可扩展**：新模板只需添加目录 + 更新 `index.json`

### 不足
- 📐 **仅限幻灯片**：不支持其他文档类型（报告、简历、海报等）
- 🔀 **缺乏内容推理**：Agent 需要自行决定内容布局，模板不提供"自动排布"逻辑
- 🎞️ **无动画编辑器**：用户无法在模板基础上编辑动画效果
