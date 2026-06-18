# 🔬 JimLiu/baoyu-design - 全方位深度调研

## 📌 一句话定位

baoyu-design 把 Claude Design 的设计流程包装成可安装的 Agent Skill，让 Cursor、Claude Code、Codex 等本地编码代理直接生成高保真 UI、原型、线框、Deck 与自包含 HTML 设计资产。🏗️ 项目架构全景GitHub: https://github.com/JimLiu/baoyu-designStars: 516（采集时）主语言: JavaScript/Markdown 技能包。License: MIT。目录：skills/baoyu-design/SKILL.md 为入口，system-prompt.md 是设计方法论，references/{claude,cursor,codex}.md 适配不同代理，built-in-skills/ 包含 24 个专项设计能力，starter-components/ 提供设备壳、画布、Deck、动画等 HTML/JS 脚手架。🧠 核心源码/内容解读1. skills/baoyu-design/SKILL.md入口不是“工具调用脚本”，而是流程编排器：先读 system-prompt.md，识别 harness，再按任务加载 built-in skill。这个设计使它能跨 Claude Code/Cursor/Codex，而不是绑定单一 CLI。2. system-prompt.md虽然本次采集只截取到 README 与内置技能片段，但 README 明确它是“methodology & craft standards source of truth”。这说明项目将设计质量标准中心化，避免各子技能发散。3. built-in-skills/hi-fi-design.md / interactive-prototype.md默认任务会加载高保真设计与交互原型两类技能，体现“默认不是静态图，而是可预览/可迭代 HTML”的产品哲学。4. built-in-skills/export-as-pptx-editable.md内置 PPTX 导出说明显示项目不止生成 HTML，还考虑交付物进入 PowerPoint、PDF、Figma、Canva 等实际设计/汇报链路。5. starter-components/README 提到 iOS/Android/macOS/browser frames、pan-zoom canvas、deck stage、timeline animation engine、tweaks panel、fillable image slot；这是“给 Agent 的设计原语库”，降低模型从零写 UI 框架的随机性。📐 架构决策与设计哲学Skill as product：不是做网页 SaaS，而是把设计系统能力下沉到本地代理。Harness adapter pattern：核心方法论与环境工具引用拆开，减少跨 Agent 迁移成本。HTML-first deliverable：输出自包含 HTML，天然可版本管理、可本地预览、可由 Agent 继续修改。强模型偏好：README 明确 “Best with Opus 4.8”，承认该 Skill 是长上下文高要求设计 brief，模型能力直接影响成品。

## 🌐 全网口碑画像

GitHub/社区信号Issue #3 显示已被 CodeGuilds 收录为 Claude Code 生态包，说明它进入了技能/代理生态目录。ProSearch 最近 7 天结果中，yousou.net GitHub 当日趋势将 JimLiu/baoyu-design 列为当日趋势第 1，并摘录其定位。负面/争议信号当前 GitHub Issue 很少，缺少真实用户长周期踩坑反馈。README 的 “Claude Design engine behind claude.ai/design” 表述可能带来能力边界/授权联想

### 风险

；本报告不判断法律结论，仅提示传播表述需谨慎。

## ⚔️ 竞品对比

项目/产品定位

### 优势

局限Claude Design 网页官方网页设计体验官方体验完整需要离开编辑器，产物/流程不一定落在 repo 中v0 / Lovableprompt-to-UI/Web app生态成熟、云端预览更偏 SaaS/应用生成，不是本地 Agent Skill 方法论Figma AI设计工具内 AI与专业设计流程贴合依赖 Figma 工作台，不是代码代理本地流程baoyu-design本地 Agent Skill跨 Cursor/Claude/Codex，HTML 可版本化质量依赖模型与浏览器验证能力，缺少长期用户反馈

## 🎯 核心研判

### 优势

切中 2026 Agent Skill 生态：把设计方法论变成可安装资产。交付物 HTML-first，便于 Agent 二次编辑和本地版本控制。内置 skill 粒度细，覆盖 Deck、PPTX、Figma/Canva、移动端、动效等实际设计链路。

### 风险

容易被用户误解为“复刻 Claude Design 官网完整能力”，但本质仍取决于本地 Agent 和模型。真实口碑样本不足，当前更多是趋势热度而非生产验证。设计质量门槛高，弱模型或无视觉验证工具时成品会明显下降。

### 适用场景

产品经理/开发者在 Cursor/Claude Code 中快速产出 UI 方案、原型、Deck。希望设计资产直接落到 repo、可迭代、可导出的团队。不

### 适用场景

严格品牌设计系统或专业 Figma 协同流程。需要官方 Claude Design 完整网页体验与服务保证的用户。趋势判断早期上升期，受 Agent Skill/Claude Code 生态增长推动；需要更多真实案例和失败样本来证明稳定性。

## 📂 关键文件路径速查

skills/baoyu-design/SKILL.mdskills/baoyu-design/system-prompt.mdskills/baoyu-design/references/claude.mdskills/baoyu-design/references/cursor.mdskills/baoyu-design/references/codex.mdskills/baoyu-design/built-in-skills/export-as-pptx-editable.md✅ 质量门禁源码/内容：入口、方法论、引用适配、内置技能、组件脚手架均已分析。Issue/口碑：Issue 很少，外部搜索有限，已标注数据不足。竞品：Claude Design、v0/Lovable、Figma AI。
