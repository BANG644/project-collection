# 🧠 zai-org/GLM-5 — 从 Vibe Coding 到 Agentic Engineering 的旗舰模型

> GitHub: [zai-org/GLM-5](https://github.com/zai-org/GLM-5)  
> ⭐ 6,746 | 🔄 430 forks（抓取日期 2026-06-19，星标已校正至 2026-07-24 实时值）  
> 协议: 开源  
> 抓取日期: 2026-06-19（核心研判补完于 2026-07-24）

---

## 一、项目概述

**GLM-5** 是智谱 AI（Zhipu AI）推出的旗舰级开源大语言模型系列，定位从" Vibe Coding"迈向"Agentic Engineering"。参数规模从 GLM-4.5 的 355B（32B 激活）扩展到 **744B 参数（40B 激活）**，预训练数据量从 23T tokens 增加到 28.5T tokens。

GLM-5 系列目前包含：
- **GLM-5**（基础版，744B-A40B）
- **GLM-5.1**（增强版，面向 agentic 任务）
- **GLM-5.2**（最新旗舰，1M tokens 上下文 + IndexShare 注意力机制）

---

## 二、核心架构创新

### 2.1 IndexShare 注意力机制
- 在每 4 个稀疏注意力层之间复用相同的索引器
- **1M 上下文长度下，每个 token 的 FLOPs 降低 2.9×**
- 论文：[IndexShare](https://arxiv.org/abs/2603.12201)

### 2.2 DeepSeek Sparse Attention (DSA)
- 降低部署成本的同时保持长上下文能力
- 从 GLM-4.5 的 32B 激活 → GLM-5 的 40B 激活

### 2.3 MTP 推测解码层增强
- GLM-5.2 改进 MTP 层，接受长度提升最多 **20%**

### 2.4 Slime RL 基础设施
- 自研异步 RL 训练框架：[THUDM/slime](https://github.com/THUDM/slime)
- 大幅提升 RL 训练吞吐和效率
- 支持更细粒度的后训练迭代

---

## 三、性能基准

### 3.1 编程能力
| 基准 | GLM-5.2 | GLM-5.1 | Claude Opus 4.8 | Gemini 3.1 Pro |
|------|---------|---------|----------------|----------------|
| Terminal-Bench 2.1 | **81.0** | 62.0 | 85.0 | ~70+ |
| SWE-bench Pro | **62.1** | 58.4 | — | — |

GLM-5.2 在编程基准上：
- 大幅超越前代 GLM-5.1（81.0 vs 62.0 on Terminal-Bench）
- 逼近闭源前沿 Claude Opus 4.8（81.0 vs 85.0）
- 领先 Gemini 3.1 Pro

### 3.2 Agentic 能力

**CC-Bench-V2**（内部评测）：
- 在前端、后端、长周期任务上显著超越 GLM-4.7
- 缩小了与 Claude Opus 4.5 的差距

**Vending Bench 2**（长期运营能力基准）：
- **开源模型排名第一**
- 全年模拟账户余额 **$4,432**，接近 Claude Opus 4.5

### 3.3 开源模型对比
GLM-5 在所有开源模型中取得 **推理、编程、Agentic 任务上的最佳性能**。

---

## 四、GLM-5.2 关键能力

1. **Solid 1M Context** — 稳定支撑长周期工作
2. **Flexible Effort 多级编程** — 不同思考力度，在性能和延迟间权衡
3. **Agent 长周期有效** — 不同于其他模型"三板斧就耗尽"，GLM-5.1/5.2 能在数百轮工具调用中持续优化

---

## 五、模型下载

| 模型 | 大小 | 精度 | 下载 |
|------|------|------|------|
| GLM-5.2 | 744B-A40B | BF16 | [HuggingFace](https://huggingface.co/zai-org/GLM-5.2) / [ModelScope](https://modelscope.cn/models/ZhipuAI/GLM-5.2) |
| GLM-5.2-FP8 | 744B-A40B | FP8 | [HuggingFace](https://huggingface.co/zai-org/GLM-5.2-FP8) |
| GLM-5.1 | — | — | [HuggingFace](https://huggingface.co/zai-org/GLM-5.1) |
| GLM-5 | 744B-A40B | BF16 | [HuggingFace](https://huggingface.co/zai-org/GLM-5) |

---

## 六、API 服务
- [Z.ai API Platform](https://docs.z.ai/guides/llm/glm-5.2)
- 线上体验：[z.ai](https://z.ai)

---

## 七、社区与生态
- 微信 / [Discord](https://discord.gg/Hc5z9bx5Xw)
- 技术博客：[GLM-5.2 发布博客](https://z.ai/blog/glm-5.2)
- 技术报告：[GLM-5 Technical Report](https://arxiv.org/abs/2602.15763)

---

## 八、竞品定位

```
                   闭源前沿（Claude Opus 4.8 / GPT-5）
                         ↑
                      GLM-5.2 ← 差距已大幅缩小
                         ↑
                      GLM-5.1 ← 开源最强
                         ↑
                       GLM-5  ← 开源第一梯队
                         ↑
                  其他开源模型（Qwen / LLaMA / DeepSeek）
```

---

## 九、关键发现

1. **开源逼近闭源** — GLM-5.2 在 Terminal-Bench 上距离 Claude Opus 4.8 仅 4 个点的差距，是当前最接近闭源前沿的开源模型之一
2. **长周期 Agentic 能力** — 这可能是 GLM-5 系列最大的差异化优势：模型在长时间交互中持续有效，而非"快速耗尽"
3. **1M 上下文 + IndexShare** — 通过架构创新而非简单堆算力来降低长上下文推理成本（2.9× FLOPs 降低）
4. **中国团队开源主力** — 智谱 AI 持续在开源大模型领域保持领先地位

---

## 十、核心研判

- **优势**：开源模型里最接近闭源前沿（Terminal-Bench 距 Claude Opus 4.8 仅 4 个点）；长周期 Agentic 能力是最大差异化——数百轮工具调用中持续优化而非"三板斧耗尽"；1M 上下文靠 IndexShare 架构创新降本（2.9× FLOPs），而非单纯堆算力。
- **风险**：744B 参数体量对自部署极不友好（需多卡+HBM），个人/小团队实际只能用 API 或 FP8 蒸馏版；与 DeepSeek/Qwen 同属中国开源阵营，海外合规与供应链接续存在外部不确定性；"开源第一梯队"的位次会被后续版本快速洗牌。
- **趋势**：旗舰模型竞争焦点已从"参数规模"转向"长上下文成本 + Agentic 持久力 + 推理/编程一体化"；IndexShare/DSA 这类稀疏注意力会成为长上下文标配。
- **启发**：给 AI 应用构建者的启示——选基座模型时，**长周期任务稳定性**比单次基准分数更关键；GLM-5 的"数百轮不耗尽"特性，适合做需要多步工具调用的 Agent 后端。

---

## 十一、竞品对比

| 维度 | GLM-5.2 | DeepSeek-V3/R1 | Qwen3-Max | Claude Opus 4.8 | GPT-5 |
|------|:--------:|:--------------:|:---------:|:---------------:|:-----:|
| 上下文 | 1M | 128K/256K | 256K | 200K | 200K+ |
| 开源 | ✅ | ✅ | ✅(部分) | ❌ | ❌ |
| 编程(Terminal-Bench) | 81.0 | ~75 | ~70 | 85.0 | ~85 |
| Agentic 长周期 | ✅ 强 | ⚠️ | ⚠️ | ✅ 强 | ✅ |
| 自部署门槛 | ❌ 极高(744B) | ⚠️ 高 | ⚠️ 高 | ❌ | ❌ |
| 中国合规 | ✅ 本土 | ✅ | ✅ | ⚠️ | ⚠️ |
