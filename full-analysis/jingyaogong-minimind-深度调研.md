jingyaogong/minimind 全方位深度调研报告调研日期：2026-06-13 | 数据来源：GitHub API + README📦 项目概览属性值仓库jingyaogong/minimindStars⭐ 51,667Forks6,638语言Python许可证Apache 2.0创建时间2024-07-27最后更新2026-06-01最新版本v2 (2025-10-21)官网jingyaogong.github.io/minimind相关项目MiniMind-V（视觉）、MiniMind-O（多模态 Omni）、MiniMind-dLM（扩散语言模型）一句话定位：从零训练 64M 参数小语言模型的完整开源教程，最低仅需 3 元成本、2 小时即可在单张 3090 上完成训练。📖 项目定位与核心理念使命宣言"用乐高自己拼出一架飞机，远比坐在头等舱里飞行更让人兴奋"MiniMind 的核心使命是降低大语言模型的学习门槛，让每个人都能从理解每一行代码开始，从零亲手训练一个极小的语言模型，而不是仅仅停留在使用 LoRA 微调现有模型的层面。核心亮点极致低成本：单卡 3090、2 小时、3 元即可从零训练一个对话模型完整链路：覆盖 Pretrain → SFT → LoRA → RLHF(DPO) → RLAIF(PPO/GRPO/CISPO) → Tool Use → Agentic RL → 蒸馏等全流程原生实现：核心算法从零使用 PyTorch 实现，不依赖第三方高层抽象文档详尽：超过 5 万字的 README，涵盖架构设计、算法原理、训练技巧🏗️ 核心架构分析模型架构minimind-3 (Dense)：参数值参数量64M词表大小6,400最大位置编码32,768RoPE theta1e6层数8隐藏维度768KV heads4Q heads8激活函数SwiGLU归一化Pre-Norm + RMSNormminimind-3-moe (MoE)：参数值参数量198M-A64M激活参数64MExperts4Top-K routingtop-1其余参数与 Dense 版本一致架构特点对齐 Qwen3/Qwen3-MoE 生态（便于转换到 transformers/llama.cpp/vllm/ollama）Dense 约 64M，MoE 约 198M-A64M移除 shared expert 设计支持 YaRN RoPE 长度外推训练链路Pretrain (预训练) → SFT (监督微调) → RLHF/RLAIF → Agentic RL阶段训练数据耗时(单卡3090)成本Pretrainpretrain_t2t_mini (1.2GB)~1.21h~1.57￥SFTsft_t2t_mini (1.6GB)~1.10h~1.43￥RLAIFrlaif.jsonl (24MB)~1.1h~1.43￥Agentic RLagent_rl.jsonl按需按需合计~2.3h~3.0￥强化学习算法对比算法策略项

### 优势

项正则项模型数DPO无显式

### 优势

项隐含在  中1 (前向2)PPO2GRPO1CISPO1📊 社区口碑与影响力积极评价教育价值极高：被认为是 LLM 入门的最佳实践项目之一代码质量高：从零实现的代码注释详尽，适合学习持续迭代：从 2024 年至今持续更新，从 v1 演进到 v3学术引用：已被多篇学术论文引用（ICML 2025、清华大学出版社教材等）生态丰富：衍生了 MiniMind-V（视觉）、MiniMind-O（多模态）等子项目客观局限性模型能力有限：64M 参数决定了其在复杂任务上的表现中文为主：英文能力较弱，中文评测优于英文知识幻觉明显：在事实性问答上存在较严重的幻觉问题RL 后训练 trade-off：Agent RL 提升 Tool Use 能力但降低通用问答稳定性评测数据（选择题基准）模型cevalcmmluarc_easypiqaopenbookqahellaswagsocial_iqaminimind-3 (64M)24.8925.3828.4950.6523.6028.2834.19minimind-3-moe (198M)25.4824.3227.7450.7126.2027.4334.03SmolLM2-135M24.4424.7158.5068.1732.8043.1539.46TinyLlama-1.1B25.7125.0354.8074.4335.6060.3843.09🔄 竞品对比特性minimindbaby-llama2-chinesechatlm-mini-chinesenanoGPTStars51.6K9K+2K+36K+参数量26M-198M0.2B0.2B不等中文支持✅ 优秀✅ 良好✅ 良好❌ 英文训练链路完整度✅ 极完整⚠️ 部分⚠️ 部分⚠️ 部分RLHF/RLAIF✅ 完整❌❌❌Agentic RL✅❌❌❌文档质量✅ 优秀✅ 良好⚠️ 一般✅ 良好第三方生态兼容✅ 广泛⚠️ 有限⚠️ 有限⚠️ 有限成本（从零训练）3元不等不等不等

## 🎯 核心研判

项目价值LLM 教育天花板：在同参数量级开源项目中，文档质量、代码清晰度和训练链路完整度均属最佳RL 算法教科书：PPO/GRPO/CISPO/DPO 等算法的完整原生实现，是理解 RL 后训练的绝佳参考低成本验证平台：3 元成本即可验证 LLM 训练全流程，适合教育和研究学术影响力：已被 ICML 2025 等顶级会议论文引用竞争力分析Stars 增长迅猛：从 0 到 51.6K 仅用约 2 年差异化

### 优势

明显：在"从零训练极小模型"这个细分赛道无直接竞品生态壁垒：衍生的 MiniMind-V/O/dLM 形成子项目矩阵潜在

### 风险

模型能力上限：64M 参数限制了实际应用场景维护负担：全链路代码维护成本高，每次框架升级都需要适配AI 教育赛道竞争：随着 AI 教育工具增多，可能面临更多竞争使用建议LLM 入门学习者：作为第一个从零训练 LLM 的实践项目RL 算法研究者：参考其原生实现的 PPO/GRPO/CISPO/DPOAI 教育者：作为教学案例，展示 LLM 训练全流程🔑 关键文件路径路径说明model/model_minimind.py模型结构定义（Dense + MoE）trainer/train_pretrain.py预训练脚本trainer/train_full_sft.py有监督微调脚本trainer/train_dpo.pyDPO 偏好优化脚本trainer/train_ppo.pyPPO 强化学习脚本trainer/train_grpo.pyGRPO 强化学习脚本trainer/train_agent.pyAgentic RL 训练脚本trainer/train_lora.pyLoRA 微调脚本trainer/train_distillation.py知识蒸馏脚本eval_llm.py模型推理评估脚本eval_toolcall.pyTool Call 能力测试脚本scripts/serve_openai_api.pyOpenAI 兼容 API 服务scripts/web_demo.pyStreamlit 聊天 WebUIscripts/convert_model.py模型格式转换脚本dataset/训练数据集目录📌 总结MiniMind 是 LLM 入门教育领域的标杆项目（51.6K Stars），以"从零训练 64M 模型仅需 3 元 2 小时"的极致低成本著称。其核心

### 优势

在于完整覆盖 Pretrain → SFT → LoRA → RLHF → RLAIF(PPO/GRPO/CISPO) → Agentic RL → 蒸馏的全流程代码和详尽文档，所有核心算法均从零原生实现。虽然模型能力受限于参数量，但在教育价值和学术影响力上远超同类项目。适合 LLM 入门学习者和 RL 算法研究者。
