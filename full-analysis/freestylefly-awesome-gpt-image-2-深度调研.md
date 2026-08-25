# freestylefly/awesome-gpt-image-2 深度调研

> 调研日期：2026-08-26 ｜ 星标：17,408 ⭐ ｜ 语言：JavaScript ｜ 协议：MIT ｜ 默认分支：main
> 定位：GPT-Image-2「提示词即代码（Prompt as Code）」工业级提示词引擎、532 个逆向案例库与可复用 Agent Skill 合集

## 一、项目亮点（差异化）

1. **把散文式提示词压缩成结构化协议**：核心不是「更多示例」，而是把主体 / 光照 / 材质 / 布局 / 视觉细节拆成可组合的原子字段（atomic schema），让 Agent 与自动化工作流能复用，而非堆砌孤立案例。
2. **532 个真实逆向案例**：`data/cases.json` 收录的是「真实 GPT-Image-2 生成结果 + 完整提示词」的逆向工程样本，而非臆测模板，含金量大。
3. **提炼成可安装的 Agent Skill**：`agents/skills/gpt-image-2-style-library/` 是一个符合 Agent Skills 规范的技能包（SKILL.md + references + bin），可直接进 Claude Code / Cursor。
4. **配套产品化画廊**：`gpt-image2.canghe.ai` 把案例库做成可浏览、可复制完整提示词、可按风格/场景筛选的网页产品，降低使用门槛。
5. **多语言文档 + 持续更新**：EN / 简中 / 日文三语文档，并带「100% Original AI Rewritten」质量标（强调非搬运）。

## 二、核心架构

仓库本质是「**提示词资产库 + 网页画廊 + Agent Skill**」三者合一，不是传统意义上的运行时软件：

```
awesome-gpt-image-2/
├── data/
│   ├── cases.json          # 532 个逆向工程真实案例（图 + 完整 prompt）
│   ├── style-library.json  # 「Prompt as Code」核心：原子化模板 schema
│   └── images/
├── agents/skills/
│   └── gpt-image-2-style-library/   # 可安装 Agent Skill
│       ├── SKILL.md         # 技能入口与用法
│       ├── agents/ references/ bin/ assets/ package.json
├── src/ api/ supabase/      # 网页画廊前端 + Supabase 后端（Vite SPA + vercel 部署）
├── docs/ scripts/ .claude-plugin/marketplace.json
```

`data/style-library.json` 的真实键结构是理解整个项目的钥匙：

```json
{
  "version": "...",
  "repository": "...",
  "templateDocument": "...",   // 提示词骨架模板
  "tagLabels": [...],
  "categories": [...],
  "styles": [...],             // 风格原子
  "scenes": [...],             // 场景原子
  "templates": [...]           // 20+ 套工业级模板
}
```

`templateDocument` 是「提示词骨架」，`styles` / `scenes` / `templates` 是可组合的原子块，组合起来即一条结构化、可复现的 GPT-Image-2 提示词 —— 这就是「Prompt as Code」的落地形态。

## 三、应用场景与启发

- **批量可控出图**：当需要做「同一主体、不同光照、不同材质」的一批图时，原子 schema 比散文提示词更容易程序化拼装与变量替换。
- **Agent 工作流接入**：通过 `gpt-image-2-style-library` Skill，编码 Agent 能直接调用风格库生成提示词，把「出图」变成可编排节点。
- **团队提示词资产化**：把散落社区的爆款图逆向成结构化案例 + 模板，形成可检索、可继承的内部资产。
- **对同类需求的启发**：任何「提示词工程」场景（文生图 / 文生视频 / 甚至代码生成）都可以借鉴「原子 schema + 案例库 + Skill 包」三层结构，把经验从人脑搬到可机器消费的协议层。

## 四、源码深度解读

**1. 原子化模板（`data/style-library.json`）** —— 全项目最有价值的「代码」不是运行时，而是这份 schema：它把一条好提示词拆成 `templateDocument`（骨架）+ `styles`/`scenes`/`templates`（可插拔原子）。复用价值在于「组合」而非「背诵」。

**2. 可安装技能（`agents/skills/gpt-image-2-style-library/SKILL.md`）** —— 遵循 Agent Skills 规范（与 anthropics/skills、ComposioHQ/awesome-claude-skills 同生态），让 Claude Code / Cursor 把风格库当作一等公民工具调用，是「awesome list → 可执行技能」的进化形态。

**3. 画廊产品（`src/` + `supabase/` + `vercel.json`）** —— 用 Vite 构建 SPA、Supabase 做后端、Vercel 部署，把静态案例库变成带登录（Google sign-in）、可测试生成的在线产品，是「开源资产 + SaaS 体验」的常见但有效的分发模式。

## 五、社区口碑

- Trendshift 榜单收录，三语文档 + 画廊产品带来较好的初期传播。
- ⚠️ **信任风险点**：README 头部塞入大量赞助商区块（apimart / hiapi / packyapi / pptoken，均为 AI 图像/视频 API 中转或编码 Agent API 中转，且带 `aff=` 返利参数）。对「中立资产库」的定位有一定稀释，读者需警惕其作为 API 中转导流入口的倾向。
- 整体口碑偏向「实用提示词合集」，但商业化气息较重。

## 六、竞品对比与核心研判

| 维度 | awesome-gpt-image-2 | Lexica / PromptHero | Awesome 类纯清单 | 厂商官方 Prompt 指南 |
|------|--------------------|--------------------|----------------|--------------------|
| 结构化程度 | 原子 schema（Prompt as Code） | 散文/标签检索 | 纯链接 | 散文教程 |
| 真实案例量 | 532 逆向案例 | 社区上传图 | 无 | 少量 |
| 可机器消费 | ✅ Agent Skill | ❌ | ❌ | ❌ |
| 中立性 | ⚠️ 赞助商导流重 | 中立 | 中立 | 厂商立场 |

**核心研判**：
- ✅ **值得收藏的资产**：532 真实案例 + 原子化 schema + 可安装 Skill，是 GPT-Image-2 提示词领域信息密度最高的开源资产之一，比读厂商文档能拿到更多「可复用结构」。
- ⚠️ **弱点**：README 商业化气息重（返利链接密集），作为「中立知识库」的信任度打折；本质是策展资产而非软件系统，长期价值取决于案例/模板的持续更新与去商业化。
- 🔭 **启发**：「原子 schema + 案例库 + Skill 包」三层结构可复用于任何提示词工程场景，是 awesome-list 的自然进化方向。

## 七、关键文件速查

| 文件 | 作用 |
|------|------|
| `data/style-library.json` | Prompt as Code 核心：templateDocument + styles/scenes/templates 原子 schema |
| `data/cases.json` | 532 个逆向工程真实案例（图 + 完整提示词） |
| `agents/skills/gpt-image-2-style-library/SKILL.md` | 可安装 Agent Skill 入口 |
| `src/` + `supabase/` + `vercel.json` | 网页画廊（Vite SPA + Supabase + Vercel） |
| `.claude-plugin/marketplace.json` | Claude 插件市场注册 |
