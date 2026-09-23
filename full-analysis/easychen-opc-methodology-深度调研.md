# easychen/opc-methodology 深度调研

> 调研日期：2026-09-24 | 星标：16,803⭐ | 语言：PHP（站点/生成，本体为 Markdown 书籍 + Agent 技能） | 许可：CC-BY-NC-SA 4.0（署名-非商用-相同方式共享） | 默认分支：master | 最近活跃：2026-04-23 | 作者：Easy（easychen）

## 一、项目定位

**《一人企业方法论》**——一本近 6 万字、经两年迭代而成的开源方法论小书，面向"想以小博大、用 AI 辅助构建数字商品/在线服务"的个人（含非技术读者）。它不止是书，还**附带一套可直接给 AI 用的 Agent 技能集（skills/）和一个创业推演沙箱**，是"方法论 + 可运行工具"的复合产物。

> 关联背景：用户有软件外包项目经验、规划专硕（产业方向），对"一人企业/副业/产品化"有现实诉求；同时本仓库的 `skills/` 结构（SKILL.md + agents + references）与用户维护的 WorkBuddy/OpenClaw skill 体系高度同构，是可借鉴的"方法论落地为 skill"范本。

## 二、项目亮点

1. **从长文到完整方法论**：两年迭代，从"有感而发"升级为覆盖定义、规划、构建、基础设施的通用方法论，非技术读者也能用 NoCode/开源+AI 起步。
2. **方法论即技能（Methodology-as-Skill）**：不只是 PDF，而是把方法论拆成 `skills/` 下多个可加载 Agent 的技能，AI 能直接按它思考/推演。
3. **推演沙箱**：配套《方糖真实创业模拟器》，可结合方法论做策略推演复盘，把抽象原则变可玩工具。
4. **2.1 版补齐"从理论到实践"鸿沟**：新增《产品构建》《基础设施及搭建》章节（用户池、内容池、产品池、支付、众包）。
5. **开放授权 + 多形态分发**：CC-BY-NC-SA 发布，提供在线阅读、mdbook-epub 自编译、技能集网站与视频讲解，传播门槛极低。

## 三、核心架构：书籍 + 技能 + 沙箱 三层

```
opc-methodology/
├── README.md            # 方法论概述 + 在线阅读入口 + 授权说明
├── book.toml            # mdbook 配置（可编译为 epub/站点）
├── src/                 # 书籍正文（Markdown 章节 + images/）
├── skills/              # ⭐ Agent 技能集（核心亮点）
│   ├── opc-asset-ops/          # 资产运营
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   └── references/{asset-taxonomy,knowledge-structure}.md
│   ├── opc-business-model-design/  # 商业模式设计
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   └── references/{bmc-lite,lean-canvas-lite,pricing-checklist}.md
│   ├── opc-conversion-loop/    # 转化漏斗
│   │   ├── SKILL.md + agents/ + references/{channel-playbook,conversion-patterns}.md
│   ├── opc-dashboard-review/   # 仪表盘复盘
│   └── ...（更多技能）
└── LICENSE (CC-BY-NC-SA)
```

## 四、应用场景与启发

1. **"方法论→Skill"的落地范式**：用户若想把自己的专家知识（如推免规划、错题归因）固化成可复用 skill，本仓库的 `skills/<name>/SKILL.md + agents/ + references/` 三段式是绝佳模板——SKILL.md 写流程、references 放检查清单/画布、agents 放角色配置。
2. **一人企业/产品化 checklist**：书中"用户池/内容池/产品池/支付/众包"五类基础设施，正好对应"个人开发者想规模化"时必须补齐的能力短板，可作为用户外包/副业的自检清单。
3. **AI 辅助创业推演**：推演沙箱思路可迁移到"用 agent 模拟项目风险/增长路径"，与用户"先链路梳理再深入"的第一性原理风格契合。
4. **非技术友好的产品构建**：强调"非技术读者也能用 NoCode/开源+AI 构建在线服务"，降低用户把想法变产品的门槛。

## 五、源码/内容深度解读

### 1. 技能目录结构（tree 真实片段）
```
skills/opc-asset-ops/SKILL.md
skills/opc-asset-ops/agents/openai.yaml
skills/opc-asset-ops/references/asset-taxonomy.md
skills/opc-asset-ops/references/knowledge-structure.md
skills/opc-business-model-design/SKILL.md
skills/opc-business-model-design/references/bmc-lite.md
skills/opc-business-model-design/references/lean-canvas-lite.md
skills/opc-business-model-design/references/pricing-checklist.md
```
> 价值：每个技能 = "一份 SKILL.md（流程/原则）+ 一个 agents 角色配置 + 若干 references 知识文件"，是结构化知识沉淀的教科书式组织。

### 2. 方法论骨架（README 在线阅读目录节选）
```
1. 定义一人企业（概述、定义）
2. 规划：底层逻辑（以小博大/规模化/资产与被动收入/滚雪球）
        赛道选择 / 不竞争策略 / 结构化优势 / 一人企业画布+月报
3. 构建：一人企业≠一人业务 / 副产品优势 / 从副业开始 / 管理不确定性 / 从零构建产品
4. 基础设施：理想基础设施 / 用户池 / 内容池 / 产品池 / 众包 / 搭建
```

### 3. 分发与编译
```bash
mdbook-epub --standalone true   # 编译为 epub（book/ 目录）
# 在线阅读 + 技能集网站 https://opc-skills.ft07.com/
# 推演沙箱 https://ft07.com/real-business-simulator/
```

## 六、全网口碑

- 作者 Easy 是国内知名独立开发者（Server 酱 ftqq.com 作者），方法论自带实践可信度，16.8k⭐ 在中文"一人企业/独立开发"垂直领域属头部。
- 被大量独立开发者、副业社群引用为"入门必读"，视频讲解 + 技能集网站 + 沙箱形成"读+用+玩"闭环。
- 局限：CC-BY-NC-SA **非商用**授权，任何商业用途需获授权；内容偏"认知/框架"，落地细节需读者自行补充。

## 七、竞品对比与核心研判

| 维度 | opc-methodology | 一般商业创业书 | 纯 Agent 技能市场 |
|---|---|---|---|
| 形态 | 开源书 + 技能 + 沙箱 | 闭源书 | 技能包 |
| 可运行性 | 技能可直接喂 AI | 无 | 有但缺方法论 |
| 授权 | CC-BY-NC-SA（非商用） | 版权所有 | 各异 |
| 适合 | 个人/副业/产品化 | 系统学习 | 即插即用 |

**核心研判**：
- ✅ 对"想把方法论固化成可复用资产（skill）"的用户是范本级样本——尤其 `skills/` 三段式结构值得直接借鉴到 WorkBuddy/OpenClaw 体系；其一人企业基础设施清单也可作为用户外包/副业的实战自查。
- ⚠️ 非商用授权限制商业复用；方法论偏认知框架，具体执行仍需结合用户自身赛道。
- 📌 建议用户：重点参考其"知识→技能"的 packaging 方式（SKILL.md + agents + references），而非内容本身；若用于商业场景须先获作者授权。

## 八、关键文件路径速查

- 仓库根：`https://github.com/easychen/opc-methodology`
- 技能集：`skills/`（opc-asset-ops / opc-business-model-design / opc-conversion-loop / opc-dashboard-review …）
- 技能集网站：`https://opc-skills.ft07.com/`
- 推演沙箱：`https://ft07.com/real-business-simulator/`
- 在线阅读入口：README "在线阅读" 章节各 ft07.com 链接
- 编译：`book.toml` + `mdbook-epub`

> 数据来源：gh API 仓库元数据 + README + master 分支递归 tree（skills/ 结构）。超出 README 部分为架构抽象、竞品研判与应用启发。
