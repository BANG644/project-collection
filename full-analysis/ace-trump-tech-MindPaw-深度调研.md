# ace-trump-tech/MindPaw 深度调研

> 调研日期：2026-08-17　|　★ 2,392　|　Fork **2,207**　|　Open Issues 0　|　C++　|　**无 LICENSE 文件**
> 仓库：https://github.com/ace-trump-tech/MindPaw
> 创建：2026-05-26（仅 3 个月）　|　最近推送：2026-08-15　|　Topics：`esp32` `esp8266` `vla`
> 官方描述：🐕 基于 ESP8266 的桌面级四足机器狗，支持语音交互 (HLK-V20)、手势识别 (OV2640+轻量MLP)、AI 对话 (豆包大模型)、PAD 情感计算、WiFi 网页遥控。总物料成本 ≈¥50

---

## 一、项目全景

一个 **¥50 物料成本**的桌面四足机器狗：ESP12F 主控 + 4×SG90 舵机 + SSD1306 OLED 表情屏 + OV2640 摄像头 + SU-03T 离线语音 + 8Ω 喇叭，PCB / 3D 模型 / 固件全部开源，README 手把手教你用嘉立创免费券把 PCB 和外壳成本压到 ¥0。

但这个项目真正值得看的**不是硬件 BOM，而是它在 80KB RAM 的 ESP8266 上塞进了一条完整的"情感计算 → 多模态融合 → LLM"链路**——而且是有学术引用的正经实现，不是玩票。

### 项目亮点（差异化）

| # | 亮点 | 说明 |
|---|---|---|
| 1 | **真·PAD 情感状态机** | 严格按 Mehrabian (1996) PAD 三维模型实现，代码里写着论文引用，6 个离散情感的 PAD 原型坐标是文献真值（如 HAPPY = `{0.81, 0.65, 0.57}`） |
| 2 | **Big Five 人格调制情感速率** | 外倾性影响积极情感变化速率、神经质影响 arousal 衰减、宜人性影响愤怒反应——人格不是标签而是真的进了微分方程 |
| 3 | **知识蒸馏 int8 MLP 端侧推理** | 38→16→8→5 的手势 MLP，权重仅 ~1.1KB，纯 int8 定点推理，配套 306 行 PC 端蒸馏管线（引用 Hinton 2015） |
| 4 | **情感注入 LLM Prompt** | `buildAffectivePrompt()` 生成 `[情感:快乐 P=0.81 A=0.65 D=0.57][模态:语音] 用户说: 你好` —— 把情感状态显式喂给豆包，闭环回来再更新 PAD |
| 5 | **流式特征提取（不需要完整帧）** | `classifyStream(w, h, RowReader)` 用回调逐行读，ESP8266 存不下完整图像也能推理 |
| 6 | **成本工程做到偏执** | README 逐项标注"买裸模块别买开发板（贵 3 倍）"、"搜 SU-03T 比 HLK-V20 便宜，同一个东西"、"嘉立创每月 2 张免费券" |
| 7 | **10 页内置 Web 控制台** | `data/` 下 10 个 HTML 页面（含 `egg.html` 彩蛋页），从 SPIFFS 直接提供，手机连热点即用 |

---

## 二、核心架构

### 2.1 仓库结构（仅 69 个文件，2.0 MB）

```
MindPaw_main/
├── platformio.ini              779 B   ← espressif8266 / nodemcuv2 / arduino
├── PIN_WIRING.md              11 KB   ← 接线圣经
├── src/                               ← 12 个模块（.cpp + .h 成对）
│   ├── main.cpp                62 KB  ⚠️ 单文件巨石
│   ├── image.cpp               58 KB  ← OLED 位图 C 数组
│   ├── emotion_engine.*        11.6 + 4.1 KB  ★ PAD 情感引擎
│   ├── motion_emotion.*        10.8 + 2.7 KB  ← 情感→步态映射
│   ├── doubao_agent.*          10.3 + 2.6 KB  ← 豆包 HTTPS 客户端
│   ├── gesture_nn.*             8.5 + 3.5 KB  ★ int8 MLP 推理
│   ├── ov2640.*                 5.8 + 1.9 KB  ← ArduCAM SPI 摄像头
│   ├── multimodal_fusion.*      5.4 + 2.3 KB  ★ 多模态归一化
│   ├── doubao_config.h          5.3 KB        ← AgentEmotion/EmotionAction 枚举
│   ├── speaker.*                5.3 + 4.0 KB  ← 10 种旋律
│   └── hlkv20.*                 4.7 + 4.0 KB  ← 离线语音串口协议
├── data/                              ← 10 个 HTML（SPIFFS）
│   ├── aichat.html 9.8K  aiconfig.html 8.8K  control.html 6.1K
│   ├── egg.html 5.1K（彩蛋）  index/home/motion/network/setting/expression
└── tools/distill_gesture.py   11.4 KB / 306 行  ★ 蒸馏管线
Docs/  8 篇（硬件/PCB/图片转换/烧录/组装/快速上手/API/产品手册）
3Dmodel/  body.stl 207K  bottom.stl 427K  foot.stl 216K
SCH&PCB/  MindPaw_SCH&PCB.epro2 806 KB（嘉立创 EDA 专业版工程）
Picture/  13 张 OLED BMP + PCtoLCD2002 转换工具（含 .exe，2.3 MB）
```

**架构观察**：`main.cpp`(62KB) + `image.cpp`(58KB) = 120KB，占全部 C++ 源码约 60%。也就是说**模块化只做在了"能力层"，主控逻辑仍是单文件巨石**。这在 Arduino 项目里很常见，但对二次开发是实质门槛。

### 2.2 PAD 情感引擎（本项目技术核心）

**状态定义与基线**：

```cpp
struct PADState { float pleasure; float arousal; float dominance; };
// pleasure [-1,1]  arousal [0,1]  dominance [0,1]

_baseline = {0.0f, 0.3f, 0.5f};   // 中性人格基线
_current  = _baseline;
_extraversion = 0.7f;             // 默认偏外向
_neuroticism  = 0.3f;             // 默认情绪稳定
```

**人格调制的 EMA 更新**（全项目最优雅的 5 行）：

```cpp
void EmotionEngine::_emaUpdate(float& current, float target, float rate, float personalityMod) {
    // Δ = rate · (target - current) · (1 + personalityMod)
    float delta = rate * (target - current) * (1.0f + personalityMod);
    current += delta;
}
```

调用侧把 Big Five 真的接进了速率项：

```cpp
float pRate = 0.3f * (1.0f + 0.5f * (_extraversion  - 0.5f));   // 外倾 → 快乐来得快
float aRate = 0.2f * (1.0f + 0.5f * (_neuroticism   - 0.5f));   // 神经质 → 唤醒度更敏感
_emaUpdate(_current.pleasure,  targetP, pRate, _agreeableness      > 0.5f ?  0.2f : -0.1f);
_emaUpdate(_current.dominance, targetD, dRate, _conscientiousness > 0.5f ?  0.1f : -0.1f);
```

**无交互时的基线回归（含神经质修正）**：

```cpp
_current.pleasure = _decayP * _current.pleasure + (1.0f - _decayP) * _baseline.pleasure;
float neuroMod = 1.0f + 0.2f * (_neuroticism - 0.5f);
_current.arousal  = (_decayA / neuroMod) * _current.arousal
                  + (1.0f - _decayA / neuroMod) * _baseline.arousal;   // ← 神经质越高，唤醒衰减越慢
```

**PAD → 离散情感：最近邻分类到文献原型**

```cpp
struct Proto { float p, a, d; DiscreteEmotion e; };
static const Proto protos[] = {
    { 0.81f, 0.65f, 0.57f, DE_HAPPY},
    {-0.63f, 0.06f, 0.28f, DE_SAD},
    {-0.51f, 0.59f, 0.25f, DE_ANGRY},
    { 0.40f, 0.67f, 0.13f, DE_SURPRISE},
    { 0.85f, 0.42f, 0.35f, DE_LOVE},
    { 0.00f, 0.30f, 0.50f, DE_NEUTRAL},
};
// 欧氏距离（省开方，比较平方即可）
float dist = dp*dp + da*da + dd*dd;
```

这 6 组坐标不是拍脑袋的——是 Mehrabian 基本情感 PAD 原型的文献值。**在一个 ¥50 玩具里看到有出处的情感坐标表，是这个项目最不寻常的地方。**

情感状态最终驱动三路输出：`recommendAction()`（步态）/ `recommendExpression()`（OLED 表情）/ `recommendMelody()`（喇叭旋律）。

### 2.3 int8 量化 MLP 推理

**特征工程**（38 维，刻意做得极便宜）：

- 32-bin 灰度强度直方图
- 6-bin 空间分布（3×2 网格平均亮度）

输入是 40×30 灰度图（仅 1200 像素），**故意压到这个尺寸就是为了让 ESP8266 存得下**。

**定点全连接层**：

```cpp
void GestureNN::_fcRelu(const int8_t* input, const int8_t* weight, const int8_t* bias,
                         uint8_t inputDim, uint8_t outputDim, int8_t* output) {
    for (uint8_t o = 0; o < outputDim; o++) {
        int32_t sum = 0;
        for (uint8_t i = 0; i < inputDim; i++)
            sum += (int32_t)input[i] * (int32_t)weight[o * inputDim + i];
        sum += (int32_t)bias[o];
        sum >>= 6;                       // 固定缩放：除以 64
        if (sum < 0)   sum = 0;          // ReLU
        if (sum > 127) sum = 127;        // 饱和
        output[o] = (int8_t)sum;
    }
}
```

`sum >>= 6` 是**全网络共用一个固定缩放因子**——比 TFLite Micro 的 per-tensor/per-channel scale 粗糙得多，但省掉了所有量化参数存储和乘法，在 80MHz 无 FPU 的 ESP8266 上是合理取舍。

**流式推理接口**（值得单独指出）：

```cpp
typedef void (*RowReader)(int y, uint8_t* rowOut, int width);
GestureNNResult classifyStream(int imageWidth, int imageHeight, RowReader rowReader);
```

不要求完整帧驻留内存，逐行回调即可累加直方图和网格亮度。这是被 RAM 逼出来的设计，但恰好也是流式视觉的正确姿势。

### 2.4 ⚠️ 关键发现：手势模型权重是**未训练的占位值**

这是 README 完全没有提、但直接决定"手势识别"这个卖点成立与否的事实。`gesture_nn.cpp` 第 8-10 行原文：

```cpp
// ==================== 模型权重 (占位) ====================
//
// 当前权重为初始化占位值，能保证分类流程但准确率未经训练
```

`gesture_nn.h` 里也写着：

```cpp
// 占位权重 — 使用前请运行蒸馏管线生成真实权重
static const int8_t _w1[FEATURE_DIM * HIDDEN1_DIM];
```

而**仓库文件树里并不存在 `gesture_weights.h`**（69 个文件全部核对过）。`tools/distill_gesture.py` 的文档字符串给出了产出路径：

```
用法: python distill_gesture.py --dataset ./gesture_data --export ../src/gesture_weights.h
依赖: pip install torch numpy scikit-learn opencv-python tqdm
参考: Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the Knowledge
      in a Neural Network. arXiv:1503.02531
流程: 加载 HaGRID/自采集数据 → 提取 38 维特征 → 训练教师(RF/小CNN)
      → 蒸馏学生 MLP → int8 量化 → 导出 C 头文件
```

**结论**：开箱状态下手势识别**跑得通但认不准**。要真正可用，使用者必须自己下载 HaGRID 数据集（约数十 GB）、装 PyTorch、跑完蒸馏管线。**README 的功能表把"手势控制"和"语音控制"并列呈现，没有任何标注说明这一差异。** 这是本次调研认为最需要被指出的一点。

### 2.5 多模态融合 → Affective Prompt

```cpp
enum InputModality : uint8_t { MOD_TEXT = 0, MOD_VOICE = 1, MOD_GESTURE = 2 };

struct MultimodalContext {
    InputModality modality;
    String userText;             // 三种模态统一归一化成文本
    int8_t gestureClass;  float gestureConfidence;
    int8_t voiceCmd;
    String emotionDescription;   // 当前 PAD 状态描述
};

// 输出格式: "[情感:快乐 P=0.81 A=0.65 D=0.57][模态:语音] 用户说: 你好"
String buildAffectivePrompt(const MultimodalContext& ctx);
```

设计上很干净：**语音命令和手势都先翻译成自然语言**（`_voiceCmdToText` / `_gestureToText`），再统一走文本通道进 LLM。好处是 LLM 侧不需要任何多模态能力；代价是手势的连续置信度信息在翻译时被离散化丢失。

闭环链路：`模态输入 → MultimodalFusion → PAD 更新 + Affective Prompt → 豆包 → response.emotion → updateFromLLMResponse() → PAD 再更新 → 动作/表情/旋律`。

一个小细节暴露了开发历史：`multimodal_fusion.h` 注释写的是 `MOD_VOICE = 1, // 语音命令 (LD3320)`，但实际用的是 HLK-V20/SU-03T——**语音方案中途换过，注释没跟上**。

### 2.6 豆包 Agent 客户端：嵌入式 HTTP 的正确写法

```cpp
private:
    ConversationEntry _history[AGENT_MAX_HISTORY];   // 定长循环缓冲
    uint8_t _historyCount;   uint8_t _historyIndex;  // 覆盖式写入

    // 复用静态缓冲区 (避免 String 堆碎片)
    char _requestBuf[AGENT_REQ_BUF_SIZE];
    char _responseBuf[AGENT_RESP_BUF_SIZE];
```

三个正确决策：定长循环历史（不会 OOM）、静态收发缓冲（避免 `String` 在 ESP8266 上臭名昭著的堆碎片）、`getFallbackResponse()` 断网降级。

**但有一个硬伤，作者自己在注释里承认了**：

```cpp
// ---------- 核心 API 调用 (阻塞 2-8 秒，在 loop 中调用) ----------
bool ask(const String& userText, AgentResponse& response);
```

阻塞 2-8 秒且在 `loop()` 里调用 → **AI 对话期间舵机控制、语音接收、Web 服务全部停摆**。ESP8266 单核无 RTOS 抢占的必然结果。这也解释了 topics 里为什么标 `esp32`——ESP32 双核才是这个架构该待的地方。

---

## 三、应用场景与启发

### 3.1 直接适用

| 场景 | 为什么合适 |
|---|---|
| **嵌入式 AI / HRI 教学** | ¥50 成本 + 8 篇分步文档 + PCB/3D 全套，一个班 30 人的实验课材料费 ¥1500 |
| **情感计算（Affective Computing）课程实验** | PAD + Big Five 的完整可跑实现，学生能直接改人格参数看行为差异 |
| **端侧量化推理入门** | 38→16→8→5 是能手算验证的规模，比啃 TFLite Micro 源码友好得多 |
| **创客竞赛 / 毕设底座** | 硬件已验证，可专注改上层（换 LLM、加传感器、改步态） |
| **AI 玩具产品原型验证** | 完整的"情感状态 + 云端 LLM + 本体表达"链路可直接搬到 ESP32-S3 量产方案 |

### 3.2 可以偷走的思想

1. **把情感状态显式注入 Prompt，再把 LLM 返回的情感码收回来更新状态。** 这个 `[情感:快乐 P=0.81 A=0.65 D=0.57]` 的做法极其廉价却有效——任何 Agent 系统想做"有性格的持续对话"都能抄，不需要微调模型，不需要向量库。
2. **人格 = 情感变化速率的调制系数，而非静态标签。** 大多数"AI 人格"实现只是往 system prompt 里塞一段人设描述。MindPaw 让人格进入 `Δ = rate · (target - current) · (1 + personalityMod)` 这个微分式——**同一件事，外向的狗高兴得更快，神经质的狗冷静得更慢**。这个思路对做 AI 陪伴产品的人价值远超一个玩具狗。
3. **无交互时向基线回归。** 情感必须会自己衰减，否则一次刺激后就永久停留。`decay` + `baseline` 两行代码解决"AI 情绪不会消退"这个陪伴产品通病。
4. **流式特征提取绕过内存墙。** `RowReader` 回调模式：当资源装不下完整数据时，把"取数据"反转成回调交给上层。这是嵌入式之外也通用的模式（大文件处理、流式解析）。
5. **成本工程也是工程。** "买裸模块别买开发板"、"SU-03T 和 HLK-V20 是同一个东西但更便宜"、"嘉立创每月 2 张免费券"——这些不写在代码里的知识，往往是复刻成败的真正关键。开源硬件项目应该把它当一等文档。
6. **PC 端训练 → 导出 C 头文件 → 编译进固件。** `distill_gesture.py --export ../src/gesture_weights.h` 这条管线不需要任何推理框架、不需要文件系统、不需要模型加载器。资源极限场景下，"把权重变成 const 数组"仍是最优解。

---

## 四、社区口碑

**这个项目的社交数据非常反常，必须谨慎解读：**

| 指标 | 数值 | 解读 |
|---|---|---|
| Stars | 2,392 | 3 个月涨到 2.4k，速度很快 |
| **Forks** | **2,207** | ⚠️ **fork/star = 92.3%** |
| Open Issues | **0** | ⚠️ 2.4k star 项目零 issue |
| 仓库年龄 | 3 个月（2026-05-26 创建） | 很新 |
| Releases | 无 | 无版本发布 |
| LICENSE | **null（无许可证文件）** | ⚠️ README 称"全开源"但法律上不是 |

**fork/star 比 92%** 意味着什么？正常开源项目这个比值在 5-20%；教学模板类可到 50-100%，但那类项目通常有明确的"点 Use this template"引导。MindPaw 是普通仓库，不是 template。这种比例通常来自三种情形之一：

1. **推广活动要求 fork**（国内硬件/掘金/CSDN 类活动常见"star + fork 领资料"）
2. **社群集中复刻**（每个复刻者 fork 一份改自己的接线）
3. **数据不自然增长**

结合 **0 open issue**：如果有 2,207 个人真的在动手复刻一个需要焊接 ESP12F、配置 SU-03T、跑 PyTorch 蒸馏的项目，issue 区不可能是空的——单是"手势识别为什么不准"就该有一堆（毕竟权重是占位的）。**因此"2.2k fork"更可能反映传播行为而非复刻行为。**

**没有 LICENSE 是实质问题**：README 明确写"代码/PCB/3D打印全开源"，但仓库无 LICENSE 文件 → 默认保留全部版权 → 严格说任何人无权复制、修改、分发。对想拿它做课程材料或商业原型的人，这是必须先联系作者解决的法律障碍。

**文档质量是加分项**：8 篇 Docs（硬件指南 / PCB 打样 / 图片转换 / 固件烧录 / 组装 / 快速上手 / API / 产品手册）+ 11KB 的 `PIN_WIRING.md`，覆盖度远超同类爱好者项目。这部分是真功夫。

---

## 五、竞品对比

| 维度 | **MindPaw** | Petoi Bittle | ESP32-Robot-Dog 类 | XiaoZhi AI 语音机器人 | Boston Dynamics Spot |
|---|---|---|---|---|---|
| 成本 | **≈¥50** | ¥2,000+ | ¥150-400 | ¥100-300 | ¥50万+ |
| 主控 | ESP8266 (ESP12F) | ATmega328P + 树莓派可选 | ESP32 | ESP32-S3 | 工业级 |
| 自由度 | 4（每腿 1 舵机） | 8-9 | 8-12 | 无腿 | 12 |
| 步态能力 | 极简（表情式动作） | 真实爬行/翻身 | 中等 | — | 顶级 |
| **情感模型** | ✅ **PAD + Big Five（有文献）** | ⚠️ 预设行为脚本 | ❌ | ⚠️ 情绪标签 | ❌ |
| 端侧 ML | ✅ int8 MLP（**权重需自训**） | 可选（树莓派） | 部分有 | 唤醒词 | 全栈 |
| 云端 LLM | ✅ 豆包 | 第三方 | 部分 | ✅ 多家 | — |
| 离线语音 | ✅ SU-03T | ✅ | 部分 | ✅ | — |
| PCB/3D 开源 | ✅ 全套 | 部分 | 参差 | ✅ 多方案 | ❌ |
| 文档完整度 | ✅ 8 篇分步 | ✅ 商业级 | 参差 | ✅ 社区强 | — |
| LICENSE | ❌ **缺失** | GPL/商业双轨 | 多为 MIT | 多为 MIT | 闭源 |

**定位判断**：MindPaw 不和 Bittle 抢"能真的走路的机器狗"，也不和 XiaoZhi 抢"AI 语音助手"。它抢的是**"最便宜的情感交互实验平台"**这个位置——4 个舵机做不出真实步态，但足够表达"开心地晃 / 沮丧地低头"，而这恰好是 HRI 研究关心的部分。

---

## 六、核心研判

### 真实价值

1. **情感引擎是可以独立拿走用的资产。** `emotion_engine.{h,cpp}` 加起来 15.7KB，无外部依赖（只依赖 `Arduino.h` 和一个枚举头），可以直接移植到 ESP32 / STM32 / 甚至纯 PC 程序。**如果你在做任何"有情绪的 AI"，这个文件值得单独读一遍。**
2. **成本工程 + 文档是真实门槛降低。** ¥50 / 8 篇文档 / 免费 PCB 打样路径，把"造一个会动会说话的机器人"从周末项目变成一节课能启动的事。
3. **Affective Prompt 模式可复用。** 不改模型、不加检索，仅靠状态注入 + 情感码回收就做出了持续人格。这是 2026 年做 AI 陪伴最务实的路子。

### 风险与保留

| 风险 | 严重度 | 说明 |
|---|---|---|
| **手势模型权重未训练** | 🔴 高 | README 宣传的核心功能开箱不可用，需自备 HaGRID + PyTorch 跑蒸馏；且 README 未标注 |
| **无 LICENSE** | 🔴 高 | 宣称"全开源"但法律上保留全部权利，教学/商用前必须联系作者 |
| **社交数据可疑** | 🟠 中 | fork/star 92% + 0 issue，star 数不能作为质量或活跃度证据 |
| **LLM 调用阻塞 loop** | 🟠 中 | 2-8 秒全机停摆（作者已注明），ESP8266 单核无解，需迁 ESP32 |
| **main.cpp 62KB 巨石** | 🟠 中 | 二次开发要在单文件里找逻辑 |
| **仓库仅 3 个月** | 🟡 低 | 无 release、无长期维护记录，可持续性未验证 |
| **注释与实现脱节** | 🟡 低 | `LD3320` vs 实际 `HLK-V20/SU-03T`，暗示改动未同步文档 |
| **topics 含 `vla`** | 🟡 低 | 项目里没有 VLA（Vision-Language-Action）模型，只有 38 维 MLP + 云端 LLM，标签属营销性表述 |

### 谁该用 / 不该用

- ✅ **该用**：教嵌入式 AI / 情感计算的老师；想低成本试 HRI 的学生；做 AI 陪伴产品想抄情感状态机的开发者；只想要 `emotion_engine.*` 这两个文件的人。
- ⚠️ **谨慎**：指望开箱就有手势识别的（要先跑蒸馏）；要做商业产品的（先解决 LICENSE）；期待机器狗真能爬行的（4 DOF 做不到）。
- ❌ **不该用**：把 star 数当质量背书来做技术选型的；需要实时响应不能容忍 2-8 秒卡顿的；需要长期上游维护承诺的。

### 一句话研判

**MindPaw 的硬件是噱头，情感引擎才是本体。** ¥50 的四足壳子让它在社交媒体上跑得飞快，但真正稀缺的是那 15.7KB 有文献出处的 PAD + Big Five 实现——它证明了"给 AI 一个会衰减、被人格调制的情绪状态"这件事，在 80KB RAM 里就能做完，不需要大模型微调。**代价是你必须自己读代码才能知道手势识别的权重是空的，README 不会告诉你。**

---

## 七、关键文件路径速查

| 路径 | 大小 | 说明 |
|---|---|---|
| `MindPaw_main/src/emotion_engine.h` | 4.1 KB | ⭐ **最值得读**：PAD 结构、Big Five 参数、6 种离散情感、三路推荐接口 |
| `MindPaw_main/src/emotion_engine.cpp` | 11.6 KB | ⭐ `_emaUpdate()` 人格调制、`_padToDiscrete()` 文献原型最近邻、`update()` 基线回归 |
| `MindPaw_main/src/gesture_nn.h` | 3.5 KB | int8 MLP 结构定义（38/16/8/5）、`classifyStream` 流式接口、**占位权重声明** |
| `MindPaw_main/src/gesture_nn.cpp` | 8.5 KB | ⚠️ 第 8-10 行说明权重未训练；`_fcRelu` 定点推理（`sum >>= 6`）；直方图/空间特征提取 |
| `MindPaw_main/tools/distill_gesture.py` | 11.4 KB / 306 行 | ⭐ PC 端蒸馏管线：HaGRID → 教师 → 学生 MLP → int8 → C 头文件（引用 Hinton 2015） |
| `MindPaw_main/src/multimodal_fusion.h` | 2.3 KB | 三模态归一化、`buildAffectivePrompt()` 格式定义 |
| `MindPaw_main/src/doubao_agent.h` | 2.6 KB | HTTPS 客户端、定长循环历史、静态缓冲、**阻塞 2-8 秒注释** |
| `MindPaw_main/src/doubao_config.h` | 5.3 KB | `AgentEmotion` / `EmotionAction` 枚举、缓冲区尺寸常量 |
| `MindPaw_main/src/motion_emotion.cpp` | 10.8 KB | 情感 → 步态/动作映射 |
| `MindPaw_main/src/main.cpp` | **62 KB** | ⚠️ 主循环巨石：Web 路由、状态机、任务调度全在这 |
| `MindPaw_main/src/image.cpp` | 58 KB | OLED 位图 C 数组（由 `Picture/PCtoLCD2002` 生成） |
| `MindPaw_main/platformio.ini` | 779 B | `espressif8266` / `nodemcuv2`；依赖 ESPAsyncWebServer-esphome、U8g2、ArduinoJson 7、NTPClient、ArduCAM |
| `MindPaw_main/PIN_WIRING.md` | 11 KB | 完整接线表（复刻必读） |
| `MindPaw_main/data/*.html` | 10 文件 | Web 控制台：`aichat` / `aiconfig` / `control` / `motion` / `expression` / `network` / `setting` / `home` / `index` / **`egg`（彩蛋）** |
| `Docs/01`~`08_*.md` | 8 篇 | 硬件 → PCB → 图片转换 → 烧录 → 组装 → 快速上手 → API → 产品手册 |
| `3Dmodel/{body,bottom,foot}.stl` | 850 KB | 3D 打印件（嘉立创免费券可打） |
| `SCH&PCB/MindPaw_SCH&PCB.epro2` | 806 KB | 嘉立创 EDA 专业版工程（需导出 Gerber） |

**复刻最短路径**（据 README）：烧固件（PlatformIO）→ 连热点 `MindPaw` → 浏览器 `192.168.4.1` → 先在网页上把逻辑跑通，再打 PCB / 3D 打印 / 焊接。API Key 配置页在 `192.168.4.1/aiconfig.html`。
