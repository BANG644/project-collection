# storytold/artcraft 深度调研

> 调研日期：2026-10-09 ｜ 来源：GitHub Trending（当日新增） ｜ Stars：7,146 ⭐ ｜ 语言：Rust ｜ 许可：NOASSERTION（实为 Fair Source 自定义许可） ｜ 默认分支：main

## 一、项目定位（一句话）

「艺术家的 IDE」——交互式 AI 图像 / 视频创作工具：在 2D 合成、3D 场景 staging 中**先把构图摆好再生成**，把「提示词」升级为可重复、可精确的 **crafting（精雕）**；Rust 单体仓库，桌面端（Win / macOS）发布。

## 二、项目亮点（差异化）

1. **62 模型聚合目录**：图像（16）/ 视频（25）/ 音乐音效（5）/ 3D 网格（11）/ 世界与高斯泼溅（5）共 62 个模型，跨 ArtCraft / Grok / Midjourney / Sora / World Labs / Kling / Veo / FLUX / Seedream / Hunyuan3D / Meshy / Rodin 等。
2. **「先构图再生成」的创作范式**：Image to Location、3D / 2D 合成、Character Posing、Scene Blocking with Kitbashing——用可视化工具在生成前摆好构图 / 机位 / 角色，追求可控、可重复的结果。
3. **Rust 工程化**：workspace（crates/）+ SQLx 编译期查询缓存（`.sqlx/`）+ Tauri 式桌面发布工作流（Windows / macOS publish workflows）+ AGENTS.md / CLAUDE.md 提供 agent 规则。
4. **Fair Source 许可**：源码可见、个人免费可改可用，但禁止商业售卖 / 做竞品 / 去除社区与付费模型链接（非 OSI）。

## 三、核心架构

- **Rust workspace**：`crates/` 下 `api_clients/artcraft/artcraft_api_defs/` 把**每个生成端点拆成独立 `.rs` 模块**（如 `generate/image/edit/gpt_image_1_edit_image.rs`），强类型请求 / 响应 + `utoipa` 自动 OpenAPI schema。
- **SQLx 编译期查询缓存**：`.sqlx/` 存 `query-*.json`（编译期校验的 SQL），保证数据库访问类型安全、零运行时 SQL 拼写错误。
- **Agent 规则文件**：根与 `crates/` 均含 `AGENTS.md` / `CLAUDE.md`，给 AI 编码助手定义 api-conventions / code-style / testing 约定。
- **桌面发布**：`.github/workflows/artcraft-{macos,windows}-publish.yml` 走打包发布；路线图明确要「去除对 ArtCraft 托管服务的依赖」。

## 四、应用场景与启发

- **给 AI 图像 / 视频创作者一个统一多供应商工作台**，避免被单一厂商锁定；「构图前置 + 多模型聚合」思路对任何 AIGC 工具都有借鉴。
- **Fair Source 许可模式**（源码可见但限制商用）是中小团队「开源引流 + 商业护城河」的折中范例，值得想兼顾社区与变现的创作者工具参考。

## 五、源码深度解读（真实片段）

**每端点一模块的强类型 API（crates/api_clients/artcraft/artcraft_api_defs/src/generate/image/edit/gpt_image_1_edit_image.rs 节选）：**

```rust
pub const GPT_IMAGE_1_EDIT_IMAGE_PATH: &str = "/v1/generate/image/edit/gpt_image_1";

#[derive(Serialize, Deserialize, ToSchema)]
pub struct GptImage1EditImageRequest {
  pub uuid_idempotency_token: String,        // 幂等 token 防重复请求
  pub prompt: Option<String>,
  pub image_media_tokens: Option<Vec<MediaFileToken>>,
  pub image_size: Option<GptImage1EditImageImageSize>,   // Square/Horizontal/Vertical
  pub num_images: Option<GptImage1EditImageNumImages>,   // One..Four
  pub image_quality: Option<GptImage1EditImageImageQuality>, // Auto/Low/Medium/High
}

#[derive(Serialize, Deserialize, ToSchema)]
pub struct GptImage1EditImageResponse {
  pub success: bool,
  pub inference_job_token: InferenceJobToken,
}
```

每个模型端点 = 一个 Rust 模块，请求 / 响应 struct + 路径常量 + `utoipa` schema + **幂等 token**——是「多供应商 API 强类型封装」的清晰范式。

**许可（LICENSE.md 节选，确为 Fair Source 而非 OSI）：**

> What you *can't do*: ① 不能商业售卖 ArtCraft 软件；② 不能用其代码做竞争业务 / 产品；③ 不能 fork 后去除 ArtCraft 社区 / 捐赠 / 付费模型链接；④ 未经许可不能用其名号 / logo 推广。承诺若公司倒闭将转 OSI 许可。

## 六、社区口碑

- 7,146 ⭐ / 950 Fork（2022 起，近期 trending 飙升），活跃 Discord / YouTube 社区。
- 口碑两极化：创作者欢迎「多模型聚合 + 构图前置」；开源纯粹派质疑其**非 OSI** 许可是否算真开源。Fair Source 模式本身是讨论焦点。
- 详细舆情「数据不可用」，但 trending 增速说明产品契合当下 AIGC 创作刚需。

## 七、竞品对比

| 维度 | ArtCraft | ComfyUI / Fooocus / InvokeAI / Krea / Firefly / Runway |
|------|---------|------------------------------------------------------|
| 定位 | 艺术家「IDE」：构图前置 + 多模型 | 节点工作流 / 单模型 Web |
| 模型覆盖 | 62 模型统一台 | 各自偏单一或少量 |
| 源码 | Fair Source（可见，限商用） | 多 OSI 开源 / 闭源 SaaS |
| 依赖 | 当前依赖 ArtCraft 托管服务 | 各异 |

差异化在 **「艺术家 IDE」的产品形态 + 62 模型聚合 + 源码可见**；短板是非 OSI 许可、生态年轻、暂未完全脱离官方托管。

## 八、核心研判

它不是模型厂，而是 **「AI 创作的操作系统层」**——用统一工作台 + 多模型聚合卡位，降低创作者被单一厂商锁死的风险。对 AIGC 工具创业者，其「构图前置 + 聚合」的产品思路与 Fair Source 许可策略都值得研究。**许可须标注为非标准（GitHub 显示 NOASSERTION），商用前务必确认条款**。

## 九、关键文件速查

- `README.md` — 功能矩阵与 62 模型目录
- `ROADMAP.md` — 产品 / 工作室 / 架构目标
- `LICENSE.md` — Fair Source 许可细则（务必读）
- `crates/api_clients/artcraft/artcraft_api_defs/` — 每端点一模块的强类型 API 定义
- `.sqlx/` — SQLx 编译期校验的 SQL 查询缓存
- `AGENTS.md` / `CLAUDE.md` — agent 编码规则
- `.github/workflows/` — 桌面端发布流水线
