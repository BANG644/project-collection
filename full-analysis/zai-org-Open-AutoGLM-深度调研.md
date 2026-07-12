# 🔬 zai-org/Open-AutoGLM — 深度调研报告

> **仓库**: [zai-org/Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)  
> **调研日期**: 2026-07-13  
> **数据**: ⭐ 25,756 | 🍴 4,009 | 🐞 261 open issues | 📅 创建 2025-12-08，活跃推送至 2026-03-06  
> **语言**: Python | **协议**: Apache-2.0  
> **出品**: 智谱 AI (Zhipu AI) | **定位**: 开源手机端智能助理（Phone Agent）框架

---

## 一、项目定位

**Open-AutoGLM 是智谱 AI 开源的"手机 Agent 框架"**——输入一句自然语言（如"打开小红书搜索美食"），它通过 ADB/HDC 控制安卓/鸿蒙手机，用视觉语言模型（VLM）理解屏幕、规划动作、循环执行，直到任务完成。本质上是一个 **GUI Agent / Computer-Use 在手机端的开源落地**。

## 二、项目亮点（差异化）

1. **开源模型 + 开源框架双开放**：不仅框架开源，核心模型 `AutoGLM-Phone-9B`（基于 GLM-4.1V-9B-Thinking）也开源，可在 Hugging Face / ModelScope 下载，或直连智谱 BigModel / ModelScope API。
2. **跨平台设备控制**：同时支持 Android（ADB）与 HarmonyOS NEXT（HDC），覆盖 50+ 主流中文 App 与 60+ 鸿蒙 App。
3. **感知-规划-执行闭环**：截图 → VLM 理解界面 → 输出结构化动作（Launch/Tap/Type/Swipe/Back）→ 设备执行 → 再截图循环，max_steps 可配（默认 100）。
4. **安全与人工接管**：内置敏感操作确认回调 + `Take_over` 人工接管（登录/验证码场景），截图黑屏自动判定敏感页。
5. **远程调试**：支持 WiFi/网络 ADB/HDC，无需 USB 即可控制设备，配套 Python `ADBConnection`/`HDCConnection` 连接管理器。

## 三、核心架构

**两段式架构**：
1. **Agent 代码（本仓库）**：跑在用户电脑，负责调模型、解析动作、控制手机。
2. **视觉模型服务**：可远程 API（BigModel/ModelScope）或本地 vLLM/SGLang 部署（约 20GB，建议 24GB+ 显存）。

**核心循环**：`截图 → VLM 推理（think + action JSON）→ 动作执行（ADB/HDC）→ 状态更新 → 循环`

**动作空间（actions）**：`Launch` / `Tap(x,y)` / `Type` / `Swipe` / `Back` / `Home` / `Long Press` / `Double Tap` / `Wait` / `Take_over`

**项目结构**：
```
phone_agent/
├── agent.py          # PhoneAgent 主类（编排循环）
├── adb/              # ADB 工具：connection / screenshot / input / device
├── actions/handler.py# 动作执行器（把 JSON action 映射到设备指令）
├── config/           # apps.py(应用映射) / prompts_zh.py / prompts_en.py
└── model/client.py   # OpenAI 兼容模型客户端
main.py               # CLI 入口
examples/             # basic_usage / 批量 / 回调示例
```

## 四、应用场景与启发

- **个人自动化**：用嘴发指令完成"打开淘宝搜耳机下单""美团搜附近火锅"等高频操作。
- **RPA / 无障碍**：为视障或行动不便者提供语音控制手机的入口。
- **Agent 研究基线**：开源手机 GUI Agent 的完整闭环（模型+框架+设备控制），是做 mobile-agent 研究的优质起点。
- **给同类需求的解法**：做 GUI/Computer-Use Agent 时，核心是**把"动作"设计成结构化 JSON（带 action 类型 + 参数）+ 让 VLM 直接输出该 JSON**，而非自由文本；再配一个轻量 `handler` 把 JSON 翻译成 ADB/HDC 原语。这种"VLM 出 schema、handler 执行"的分层，比端到端直接生成设备指令更可控、可调试。

## 五、源码深度解读

**1) PhoneAgent 主循环（phone_agent/agent.py 抽象）**

```python
agent = PhoneAgent(model_config=ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b"))
result = agent.run("打开淘宝搜索无线耳机")
```
Agent 内部不断：截图 → 调 VLM（prompt 见 `config/prompts_zh.py`）→ 解析 `{"_metadata":"do","action":"Tap","element":[500,100]}` → 交 `actions/handler.py` 执行 → 直到模型输出任务完成或达 `max_steps`。

**2) 设备抽象（adb/ 与 hdc/）**

```python
from phone_agent.adb import ADBConnection, list_devices
conn = ADBConnection()
conn.connect("192.168.1.100:5555")   # WiFi 远程
devices = list_devices()
```
`adb/connection.py` 管本地/远程连接，`screenshot.py` 截图，`input.py` 经 ADB Keyboard 输入中文，`device.py` 执行点击/滑动。鸿蒙侧 `hdc/` 镜像同构，仅 transport 不同——**设备差异被收敛到 connection 层**，Agent 逻辑与设备无关。

**3) 中英文双 prompt 与敏感操作护栏**

`config/prompts_zh.py` / `prompts_en.py` 两套系统提示词，`--lang` 切换；`confirmation_callback` / `takeover_callback` 让用户对敏感操作（支付、登录）二次确认或人工接管，是 GUI Agent 上生产的必备安全层。

## 六、全网口碑

- GitHub 25.7k⭐、4k fork，是中文社区最活跃的手机 GUI Agent 开源项目之一。
- 开发者普遍认可"开源 9B 模型 + 完整框架"的诚意，相比仅开放 API 的竞品更受研究者欢迎。
- 痛点：本地部署门槛高（需 24GB+ 显存 + vLLM/SGLang 调参）；Android 中文输入依赖 ADB Keyboard 易踩坑；261 open issues 多围绕设备兼容与部署。
- 智谱配套"实战派"开发者激励活动（现金奖池），社区运营力度大。

## 七、竞品对比 + 核心研判

| 维度 | Open-AutoGLM | UI-TARS (字节) | OS-Atlas / Aguvis | Anthropic Computer Use |
|------|--------------|----------------|-------------------|------------------------|
| 开源模型 | ✅ 9B 开源 | 部分 | 部分 | ❌(闭源API) |
| 设备 | Android+鸿蒙 | Android(iOS实验) | 跨平台 | 桌面为主 |
| 框架开源 | ✅ | 部分 | ✅ | ❌ |
| 中文App覆盖 | 强(50+) | 中 | 中 | 弱 |

**核心研判**：
- ✅ **稀缺的"双开源"组合**：模型+框架都开放，在手机 GUI Agent 赛道差异化明显，研究者与二次开发者首选。
- ⚠️ **部署门槛是采用瓶颈**：9B 模型本地跑需高端 GPU，普通用户只能走 API（又回到"依赖智谱"）。
- 💡 **鸿蒙支持是差异化护城河**：国产手机生态下，HDC 适配让它在中文市场独特。
- 🔧 **风险**：手机 GUI Agent 商业价值尚在验证期；若大厂（Google/Apple）把原生手机 Agent 做进系统，第三方框架长尾需求或被吸收。

## 关键文件路径速查

- `phone_agent/agent.py` — PhoneAgent 主类（推理-执行循环）
- `phone_agent/adb/` — ADB 连接/截图/输入/设备控制
- `phone_agent/hdc/` — 鸿蒙 HDC 适配（同构于 adb）
- `phone_agent/actions/handler.py` — 动作执行器
- `phone_agent/config/` — apps.py / prompts_zh.py / prompts_en.py
- `phone_agent/model/client.py` — OpenAI 兼容模型客户端
- `main.py` — CLI 入口
- `examples/` — 基础/批量/回调示例
- `README_coding_agent.md` — 面向 AI 助手的自动化部署指南
