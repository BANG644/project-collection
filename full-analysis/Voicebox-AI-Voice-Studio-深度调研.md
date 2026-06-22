# 🎤 Voicebox — Open-Source AI Voice Studio

> **仓库**: [jamiepine/voicebox](https://github.com/jamiepine/voicebox)
> **Stars**: 32,132⭐ | **今日新增**: 508⭐
> **语言**: TypeScript (Tauri/Rust) | **许可证**: AGPL-3.0
> **官网**: [voicebox.sh](https://voicebox.sh) | **文档**: [docs.voicebox.sh](https://docs.voicebox.sh)

## 项目概述

Voicebox 是一款**本地优先的 AI 语音工作室**——相当于 ElevenLabs（语音生成）和 WisprFlow（语音输入）的开源合体版。它可以在你的本地机器上完成从**声音克隆**、**语音生成**、**语音听写**到**AI Agent 语音 I/O** 的完整语音工作流。

核心价值：**本地运行，数据零泄露**。模型、语音数据和录音从不离开你的电脑。

## 核心能力

### 七大 TTS 引擎

Voicebox 集成了 7 个 TTS 引擎，支持每个生成动态切换：

| 引擎 | 语言 | 特点 |
|------|------|------|
| **Qwen3-TTS** (0.6B/1.7B) | 10 | 高质量多语言克隆，自然语言交付指令（"说慢点"、"耳语"） |
| **Qwen CustomVoice** | 10 | 9 种预设声音，自然语言控制，无需参考音频 |
| **LuxTTS** | English | 轻量快速，适合实时场景 |
| **Chatterbox Multilingual** | 多语言 | 多语言支持，含变体标签 [laugh][sigh][gasp] |
| **Chatterbox Turbo** | 多语言 | 高性能版，表达性语音控制 |
| **HumeAI TADA** | English | 情感智能 TTS，情绪感知 |
| **Kokoro** | 50+ | 50+ 预设声音库，多语言覆盖最广 |

### 功能矩阵

| 功能 | 描述 | 实现方式 |
|------|------|---------|
| **声音克隆** | 数秒音频零样本克隆 | Qwen3-TTS / Kokoro |
| **语音生成** | 23 语言，不限长度 | 自动分块 + 交叉淡入 |
| **语音听写** | 全局快捷键录入任何文本域 | Whisper STT，全局热键 |
| **Agent 语音输出** | AI Agent 通过 MCP 说话 | voicebox.speak 工具调用 |
| **语音个性** | 为声音配置个性描述 + LLM 后处理 | 内置本地 LLM |
| **后期处理** | 音调/混响/延迟/合唱/压缩/滤波器 | 内置音频 DSP |
| **故事编辑器** | 多轨时间线编辑 | 对话/播客/叙事场景 |
| **API 优先** | REST API + MCP Server | 集成自有应用和 Agent |

### 架构设计

```
┌─────────────────────────────────────┐
│        Voicebox Desktop (Tauri)      │
├──────────────┬──────────────────────┤
│  Voice Input │  Voice Output         │
│  (Whisper)   │  (7 TTS Engines)      │
├──────────────┴──────────────────────┤
│  Local LLM (降噪/改写/个性)          │
├─────────────────────────────────────┤
│  MCP Server │ REST API │ CLI         │
├─────────────────────────────────────┤
│  Audio DSP (后处理效果链)            │
├─────────────────────────────────────┤
│  Storage: 本地文件系统 (语音数据)      │
└─────────────────────────────────────┘
```

### 技术栈

- **前端/桌面**: Tauri (Rust) —— 比 Electron 更轻量、更快速
- **TTS 引擎**: 7 种开源模型（Qwen, Kokoro, HumeAI 等）
- **STT 引擎**: Whisper（本地运行）
- **Agent 集成**: MCP 协议（Model Context Protocol）
- **后处理**: 内置音频 DSP 效果链
- **平台支持**: macOS (Apple Silicon/Intel), Windows (CUDA), Linux (AMD ROCm/Intel Arc), Docker

## 竞品对比

| 特性 | Voicebox | ElevenLabs | WisprFlow | Coqui TTS |
|------|---------|-----------|-----------|----------|
| 开源 | ✅ | ❌ | ❌ | ✅ (已归档) |
| 本地运行 | ✅ | ❌ | ❌ | ✅ |
| 声音克隆 | ✅ | ✅ (收费) | ❌ | ✅ |
| 语音听写 | ✅ | ❌ | ✅ (55$/月) | ❌ |
| Agent 语音输出 | ✅ (MCP) | ✅ (API) | ❌ | ❌ |
| 多引擎 | 7 个 | 1 个 | 1 个 | 1 个 |
| 隐私保护 | ✅ 完全本地 | ❌ 云端 | ❌ 云端 | ✅ |
| 平台 | 跨平台 | Web | macOS | Linux |
| 价格 | 免费 | 订阅 | 订阅 | 免费 |

## 独特优势：Agent Voice I/O

Voicebox 最大的创新在于**将语音 I/O 集成到 AI Agent 生态**：

- **Agent 说话能力**: 一条 `voicebox.speak` 让任何 MCP 感知 Agent 用克隆声音说话
- **Agent 个性**: 为声音配置自由格式个性描述，Agent 通过 Compose/Rewrite/Respond 模式个性化输出
- **本地 LLM 后处理**: 内置本地 LLM 对语音输出进行改写、润色和响应式调整

这意味着你可以和 Claude Code / Cursor 用自己喜欢的声音对话，而不是冷冰冰的合成音。

## 使用场景

1. **内容创作者**: 批量生成多语言配音，播客制作
2. **AI 开发者**: 为 Agent 系统添加语音交互层
3. **无障碍场景**: 语音听写替代键盘输入
4. **教育**: 多语言语言学习，带情感的朗读
5. **游戏/VR**: 动态角色配音生成

## 平台支持

| 平台 | 状态 | 下载 |
|------|------|------|
| macOS Apple Silicon | ✅ | voicebox.sh |
| macOS Intel | ✅ | voicebox.sh |
| Windows (CUDA) | ✅ | MSI 安装包 |
| Linux (AMD/Intel) | 源码构建 | voicebox.sh/linux-install |
| Docker | ✅ | `docker compose up` |

## 更新动态

Voicebox 近期势头凶猛，32K Stars 且以每天 500+ Stars 高速增长中。社区活跃度高，TTS 引擎和技术栈持续更新。

## 结论

Voicebox 填补了一个重要的空白：**将 ElevenLabs 和 WisprFlow 的语音 I/O 闭环开源化并本地化**。7 个 TTS 引擎 + MCP Agent 集成是差异化亮点，适合既需要语音能力又注重隐私的 AI 开发者。Tauri 框架保证了比 Electron 更流畅的体验，跨平台支持也到位。
