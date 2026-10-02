# 肉包 Roubao 深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / skills/SkillManager.kt），抓取日期 2026-10-03。许可：MIT。语言：Kotlin（原生 Android）。

## 一、项目定位（一句话）
首款**无需电脑**、原生 Android（Kotlin）运行的 VLM 手机自动化助手；受 Claude Code 启发的 **Tools + Skills 双层 Agent**，借 Shizuku 取得系统级权限，让手机本地完成「截图→规划→执行→反思」的自动化循环。

## 二、项目亮点（差异化）
1. **纯 Kotlin 重写 MobileAgent-v3**：摆脱传统方案对电脑 / ADB / Python 的依赖，截图、分析、执行全在手机本地完成。
2. **双层 Agent 架构**：Tools（原子能力）+ Skills（用户意图）分层，类 Claude Code。
3. **双执行模式**：Delegation（高置信度直接 DeepLink 跳有 AI 能力的 App，如小美/豆包/即梦）与 GUI 自动化（截图-分析-操作循环）。
4. **安全护栏**：API Key AES-256-GCM 加密存储；检测到支付/密码等敏感页面自动停止；任务全程悬浮窗可视、可随时停止。
5. **多 VLM + 好 UI**：通义千问 / GPT-4V / Claude，Material 3 双语界面。

## 三、核心架构
```
Compose UI → Skills 层(SkillManager/SkillRegistry/skills.json)
           → Tools 层(ToolManager + 原子 Tool)
           → Agent 层(MobileAgent: Manager/Executor/ActionReflector/Notetaker/InfoPool)
           → VLMClient → Shizuku(系统级控制: screencap/input tap/input swipe/am start)
```
- **Tools 层**：`search_apps / open_app / deep_link / clipboard / shell / http / screenshot / tap / swipe / type`。
- **Agent 层**：移植自 MobileAgent-v3 的四角色（规划/执行/反思/记录）+ 状态池 InfoPool。
- **工作流**：Shizuku 截图 → Manager 用 VLM 规划 → Executor 决策 → 执行动作 → Reflector 反思 → 循环至完成或安全限制。

## 四、应用场景与启发
- 把「电脑端 Agent」搬到手机本地的范式样本；双层 Skills/Tools 结构可借鉴到任何端侧 Agent。
- **Shizuku 无 Root 取权限**方案（无线调试或一次 ADB 启动后常驻）对移动自动化极具参考价值。
- v2 规划 AccessibilityService 混合模式（元素索引点击 + UI 树感知）减少纯视觉误判——是端侧 Agent 提升稳定性的关键方向。

## 五、源码深度解读
`app/.../skills/SkillManager.kt` 是 Skills 层统一入口（单例）：
```kotlin
fun initialize() {
    val loadedCount = registry.loadFromAssets("skills.json")   // 从 assets 加载技能
}
suspend fun matchIntentWithLLM(query: String): LLMIntentMatch? {
    val client = vlmClient ?: return null
    // 仅展示「已安装相关 App」的技能，构造 skills 描述
    val prompt = """你是一个意图识别助手... 返回 JSON {skill_id, confidence, reasoning}..."""
    val result = client.predict(prompt)
    return result.getOrNull()?.let { parseIntentResponse(it) }   // 解析 JSON（去 ```）
}
```
要点：① 技能配置存 `assets/skills.json`，运行时 `SkillRegistry.loadFromAssets` 加载；② 意图匹配把「已安装 App」过滤进 prompt，降低 LLM 误匹配；③ 用置信度阈值（`getBestAvailableApp(minScore=0.3)` / `matchAvailableApps(minScore=0.2)`）区分 delegation 与标准 Agent 路径。

## 六、全网口碑
约 **2.4k ⭐**，中文社区关注度高（直接对标字节「豆包手机助手」工程机），MIT 开源、路线图清晰。⚠️ 本次无人值守巡检未单独爬取深度舆情，星标与文档完整度反映接受度良好。

## 七、竞品对比
| 维度 | 肉包 Roubao | MobileAgent（阿里 X-PLUG） | 豆包手机助手 | 其他 ADB 开源方案 |
|------|------------|----------------------------|--------------|------------------|
| 是否需要电脑 | ❌ | ✅（Python+ADB） | ❌（硬件） | ✅ |
| 原生实现 | Kotlin | Python | 原生 | Python |
| Skills/Tools 架构 | ✅ | ❌ | ❓ | ❌ |
| 开源 | MIT | 开源 | 闭源 | 开源 |

差异化：原生 Android、无需电脑/Root、开源、双层架构。
- **风险**：依赖 Shizuku 无线调试（需 WiFi）；VLM 调用成本与延迟；MIUI/ColorOS/HarmonyOS 定制系统适配。

## 八、核心研判
概念验证完整、架构清晰的端侧 Agent 样本，工程价值高（尤其「Kotlin 重写 MobileAgent 摆脱 Python 依赖」的决策）。隐私/安全已有护栏。
- **适合**：研究「移动端 Agent 框架」、端侧 Skills/Tools 设计、Shizuku 权限方案。
- **生产化卡点**：权限引导（Shizuku 首次启动）、多设备/定制 ROM 适配、运行期 VLM 成本。
- v2 的 AccessibilityService 混合模式是提升操作成功率的关键演进，值得跟踪。

## 关键文件路径速查
- `app/src/main/java/com/roubao/autopilot/agent/MobileAgent.kt` — Agent 主循环
- `app/src/main/java/com/roubao/autopilot/skills/SkillManager.kt` — 意图识别/技能调度
- `app/src/main/java/com/roubao/autopilot/tools/ToolManager.kt` — 原子能力管理
- `app/src/main/java/com/roubao/autopilot/controller/DeviceController.kt` — Shizuku 控制
- `app/src/main/java/com/roubao/autopilot/vlm/VLMClient.kt` — VLM 封装
- `app/src/main/assets/skills.json` — 技能配置
- `roubao2.0+AccessibilityService` 分支 — v2 混合模式开发中
