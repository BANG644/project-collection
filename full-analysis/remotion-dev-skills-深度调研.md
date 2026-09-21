# remotion-dev/skills 深度调研

> 调研日期：2026-09-22 ｜ 定位：Remotion 官方维护的 Agent Skills 集合，把"程序化视频最佳实践"做成 AI 可消费的技能包 ｜ Stars：4,679 ｜ 语言：TypeScript ｜ 许可：未声明（README 未标注 SPDX，复用前需确认）｜ 默认分支：main ｜ 最近活跃：2026-09-17

## 一、项目定位（一句话）

`remotion-dev/skills` 是 Remotion（用 React 写视频的框架）官方出品的 **Agent Skills 仓库**：把"如何写好 Remotion 代码、如何渲染、如何做字幕/地图/SaaS"等经验封装成符合 [agentskills.io](https://agentskills.io/home) 规范的 SKILL.md，供 Claude Code、Codex、Kimi Code、Cursor 等客户端 `npx skills add remotion-dev/skills` 一键安装。

## 二、项目亮点（差异化）

- **框架厂商亲自下场写 Skills**：不是社区第三方整理，而是 Remotion 团队把官方文档与最佳实践"agent 化"，权威性高、随框架版本同步（含 `/remotion-upgrade` 技能）。
- **覆盖完整创作链路**：从建项目、写 React markup、本地预览、渲染出视频，到字幕、地图动画、SaaS 化、Studio 可交互编辑、文档检索——一条龙。
- **符合开放 Skill 规范**：每个技能是 `SKILL.md` + `agents/openai.yaml` + `REFERENCE.md` + `assets/`，可被任意兼容 agentskills.io 的 harness 发现注入。
- **双入口分发**：既 `npx skills add` 单独装，也在 `bun create video` 新建 Remotion 工程时顺势推荐安装。

## 三、核心架构

```
skills/
└─ remotion-best-practices/        # 元技能（聚合所有其他技能）
    ├─ SKILL.md
    ├─ agents/openai.yaml          # 面向 OpenAI Agents 的声明
    ├─ assets/remotion-icon.svg
    ├─ remotion-create/            REFERENCE.md(tailwind/video-layout)
    ├─ remotion-markup/            写作 React markup 的最佳实践
    ├─ remotion-studio/            启动预览
    ├─ remotion-render/            渲染视频/静帧
    ├─ remotion-captions/          transcribe/import-srt/display
    ├─ remotion-maps/              Mapbox/MapLibre/CesiumJS 地图动画
    ├─ remotion-saas/              Remotion 驱动的 App 架构
    ├─ remotion-interactivity/     Studio 可编辑
    ├─ remotion-docs/              检索官方文档→Markdown
    ├─ remotion-upgrade/           升级 Remotion 与已装技能
    └─ remotion-multimedia/         Mediabunny 多媒体处理
```

- **生成机制**：README 由 `packages/skills/scripts/sync-readme.ts` 自动生成，说明该仓库与 Remotion 主仓库的文档系统联动。
- **技能形态**：`/remotion-<name>` 斜杠命令式触发，每个 SKILL.md 内部用自然语言讲"何时用、怎么用"，并带示例 prompt。

## 四、应用场景与启发

- **AI 辅助做视频**：想用自然语言生成宣传片/数据动画时，装这套技能让 agent 产出符合 Remotion 约定的代码，少踩坑。
- **"厂商发 Skill"范式样本**：这是"框架/库官方把自身知识打包成 Agent Skills"的标杆案例——对任何做开发者工具/SDK 的团队，都是"如何让 AI 更好地用我家的东西"的现成示范（对比 anthropics/skills、vercel-labs/skills 的横向模式）。

## 五、源码深度解读（关键片段）

技能以标准结构落地，例如 `skills/remotion-best-practices/remotion-captions/`：

```
remotion-captions/
├─ SKILL.md                  # 引导文案 + 示例 prompt
├─ REFERENCE.md              # transcribe-captions / import-srt-captions / display-captions 细则
├─ agents/openai.yaml        # OpenAI Agents 声明
└─ assets/remotion-icon.svg
```

`remotion-create/REFERENCE.md` 内置 `tailwind.md` 与 `video-layout.md`，把"怎么搭布局"写成 agent 可读参考；`remotion-docs` 技能则负责把远端文档抓成 Markdown 再喂给模型，避免模型凭旧记忆乱写 API。

## 六、全网口碑

- **正面**：Remotion 官方背书、随主框架更新；被 `bun create video` 与多 agent 客户端原生支持；是 agentskills.io 生态里"领域框架技能"的代表作之一。
- **注意**：仓库**未声明许可证**（README 无 SPDX），若要在自有产品/闭源场景复用其 SKILL.md 文案，需先向 Remotion 确认授权；README 偏薄（自动生成、基本是技能清单），深度在各自的 `REFERENCE.md` 里。

## 七、竞品对比与核心研判

| 维度 | remotion-dev/skills | anthropics/skills | vercel-labs/skills | addyosmani/agent-skills |
|------|---------------------|-------------------|--------------------|-------------------------|
| 范围 | Remotion 视频领域 | 通用/Claude 生态 | Vercel 前端部署 | 通用精选 |
| 维护方 | 框架官方 | 官方 | 官方 | 社区 |

**核心研判**：⭐⭐⭐⭐ — 如果你用 Remotion 做 AI 视频，这是**首选技能源**；更广义地，它是"SDK 厂商把知识 agent 化"的优质参考实现。局限在于许可未明示、内容随 Remotion 版本演进（需常 `upgrade`）。对不做视频的团队，价值在"范式借鉴"而非直接使用。

## 八、关键文件路径速查

- `skills/remotion-best-practices/SKILL.md` — 元技能入口（聚合全部）
- `skills/remotion-best-practices/<name>/` — 各子技能（SKILL.md + REFERENCE.md + agents/openai.yaml）
- `scripts/`（`sync-readme.ts` 上游生成入口）｜ `package.json` — 技能包元信息
- 安装：`npx skills add remotion-dev/skills` ｜ 文档：[remotion.dev/docs/ai/skills](https://www.remotion.dev/docs/ai/skills)
