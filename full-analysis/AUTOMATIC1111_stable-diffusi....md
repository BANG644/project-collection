# 🔬 AUTOMATIC1111/stable-diffusion-webui - 全方位深度调研

## 📌 一句话定位

Stable Diffusion web UI

## 🏗️ 项目全景

仓库：AUTOMATIC1111/stable-diffusion-webui
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=163585 / Forks=30370 / 默认分支=master
- **Topics**：deep-learning, diffusion, image-generation, image2image, img2img, text2image, txt2img, ai, ai-art, gradio, pytorch, stable-diffusion, torch, upscaling, web, unstable
- **Homepage**：数据不可用

## 🧠 核心架构

目录结构判断
- **顶层目录分布（递归树抽样汇总）**：modules(154), extensions-builtin(43), javascript(25), test(13), html(12), scripts(12), .github(7), configs(7), textual_inversion_templates(6), models(5)
- **关键文件候选**：
- `package.json`, 
- `pyproject.toml`, 
- `requirements.txt`, 
- `README.md`, test/init.py, test/conftest.py, test/test_extras.py, test/test_face_restorers.py, test/test_img2img.py, test/test_torch_utils.py, test/test_txt2img.py, test/test_utils.py设计亮点研判
- 存在 Node/前端或工具链入口，依赖与脚本编排主要由 
- `package.json` 驱动。
- 存在 Python 入口，通常意味着 CLI、服务端或研究型流水线由 Python 主导。
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 🔍 源码深度解读

README / 说明文档要点Stable Diffusion web UIA web interface for Stable Diffusion, implemented using Gradio library.FeaturesDetailed feature showcase with images:Original txt2img and img2img modesOne click install and run script (but you still must install python and git)OutpaintingInpaintingColor SketchPrompt MatrixStable Diffusion UpscaleAttention, specify parts of text that the model should pay more attention toa man in a ((tuxedo)) - will pay more attention to tuxedoa man in a (tuxedo:1.21) - alternative syntaxselect text and press Ctrl+Up or Ctrl+Down (or Command+Up or Command+Down if you're on a MacOS) to automatically adjust attention to selected text (code contributed by anonymous user)Loopback, run img2img processing multiple timesX/Y/Z plot, a way to draw a 3 dimensional plot of images with different parametersTextual Inversionhave as many embeddings as you want and use any names you like for themuse multiple embeddings with different numbers of vectors per tokenworks with half precision floating point numberstrain embeddings on 8GB (also reports of 6GB working)Extras tab with:GFPGAN, neural network that fixes facesCodeFormer, face restoration tool as an alternative to GFPGANRealESRGAN, neural network upscalerESRGAN, neural network upscaler with a lot of third party modelsSwinIR and Swin2SR (see here), neural network upscalersLDSR, Latent diffusion super resolution upscalingResizing aspect ratio optionsSampling method selectionAdjust sampler eta values (noise multiplier)More advanced noise setting optionsInterrupt processing at any time4GB video card support (also reports of 2GB working)Correct seeds for batchesLive prompt token length validationGeneration parametersparameters you used to generate images are saved with that imagein PNG chunks for PNG, in EXIF for JPEGc...[truncated]

### 关键文件精读

package.json{  "name": "stable-diffusion-webui",  "version": "0.0.0",  "devDependencies": {    "eslint": "^8.40.0"  },  "scripts": {    "lint": "eslint .",    "fix": "eslint --fix ."  }}
- `pyproject.toml`[tool.ruff]target-version = "py39"[tool.ruff.lint]extend-select = [  "B",  "C",  "I",  "W",]exclude = [	"extensions",	"extensions-disabled",]ignore = [	"E501", # Line too long	"E721", # Do not compare types, use `isinstance`	"E731", # Do not assign a `lambda` expression, use a `def`		"I001", # Import block is un-sorted or un-formatted	"C901", # Function is too complex	"C408", # Rewrite as a literal	"W605", # invalid escape sequence, messes with some docstrings][tool.ruff.lint.per-file-ignores]"webui.py" = ["E402"]  # Module level import not at top of file[tool.ruff.lint.flake8-bugbear]# Allow default arguments like, e.g., `data: List[str] = fastapi.Query(None)`.extend-immutable-calls = ["fastapi.Depends", "fastapi.security.HTTPBasic"][tool.pytest.ini_options]base_url = "http://127.0.0.1:7860"
- `requirements.txt`GitPythonPillowaccelerateblendmodesclean-fiddiskcacheeinopsfacexlibfastapi>=0.90.1gradio==3.41.2inflectionjsonmergekornialarknumpyomegaconfopen-clip-torchpiexifprotobuf==3.20.0psutilpytorch_lightningrequestsresize-rightsafetensorsscikit-image>=0.19tomesdtorchtorchdiffeqtorchsdetransformers==4.30.2pillow-avif-plugin==1.4.3
- `README.md`# Stable Diffusion web UIA web interface for Stable Diffusion, implemented using Gradio library.![](screenshot.png)## Features[Detailed feature showcase with images](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features):- Original txt2img and img2img modes- One click install and run script (but you still must install python and git)- Outpainting- Inpainting- Color Sketch- Prompt Matrix- Stable Diffusion Upscale- Attention, specify parts of text that the model should pay more attention to    - a man in a `((tuxedo))` - will pay more attention to tuxedo    - a man in a `(tuxedo:1.21)` - alternative syntax    - select text and press `Ctrl+Up` or `Ctrl+Down` (or `Command+Up` or `Command+Down` if you're on a MacOS) to automatically adjust attention to selected text (code contributed by anonymous user)- Loopback, run img2img processing multi...[truncated]test/conftest.pyimport base64import osimport pytesttest_files_path = os.path.dirname(__file__) + "/test_files"test_outputs_path = os.path.dirname(__file__) + "/test_outputs"def pytest_configure(config):    # We don't want to fail on Py.test command line arguments being    # parsed by webui:    os.environ.setdefault("IGNORE_CMD_ARGS_ERRORS", "1")def file_to_base64(filename):    with open(filename, "rb") as file:        data = file.read()    base64_str = str(base64.b64encode(data), "utf-8")    return "data:image/png;base64," + base64_str@pytest.fixture(scope="session")  # session so we don't read this over and overdef img2img_basic_image_base64() -> str:    return file_to_base64(os.path.join(test_files_path, "img2img_basic.png"))@pytest.fixture(scope="session")  # session so we don't read this over and overdef mask_basic_image_base64() -> str:    return file_to_base64(os.path...[truncated]

### 关键逻辑总结

从关键文件组合看，项目更像是围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 🌐 社区口碑

### GitHub Issues 抽样

#17417 [OPEN] [Bug]: pkg_resources eror（comments=[{'id': 'IC_kwDOH3JoL88AAAABFg5OXg', 'author': {'login': 'Creeeeger'}, 'authorAssociation': 'NONE', 'body': 'cd ~/Schreibtisch/stable-diffusion-webui\nsource venv/bin/activate\n\npython -m pip uninstall -y clip openai-clip\n\npython -m pip install --upgrade "pip<26" "setuptools<81" wheel packaging\n\npython -m pip install --no-build-isolation \\n  "https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip" \\n  --prefer-binary\n\ndeactivate\nbash webui.sh', 'createdAt': '2026-06-09T23:25:50Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17417#issuecomment-4665003614', 'viewerDidAuthor': False}] labels=bug-report）
- #17416 [OPEN] [Feature Request]:  vídeo sensual（comments=[] labels=enhancement）
- #17411 [OPEN] [Bug]: Unauthenticated /sdapi/v1/cmd-flags Endpoint Exposes Gradio Auth Credentials（comments=[] labels=bug-report）
- #17410 [CLOSED] [Bug]: RuntimeError: Couldn't install clip.（comments=[{'id': 'IC_kwDOH3JoL88AAAABDz-G_w', 'author': {'login': 'meetcodz'}, 'authorAssociation': 'NONE', 'body': '/assign', 'createdAt': '2026-05-27T02:47:04Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17410#issuecomment-4550788863', 'viewerDidAuthor': False}, {'id': 'IC_kwDOH3JoL88AAAABEtoFtw', 'author': {'login': 'mrbit-dev'}, 'authorAssociation': 'NONE', 'body': 'me too. how can fix this ??', 'createdAt': '2026-06-03T10:11:17Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17410#issuecomment-4611245495', 'viewerDidAuthor': False}, {'id': 'IC_kwDOH3JoL88AAAABE467PA', 'author': {'login': 'kjhf'}, 'authorAssociation': 'NONE', 'body': "workaround: \n\n1. clone CLIP yourself\n> git clone https://github.com/openai/CLIP.git\n\n2. using the venv's pip, install CLIP from the cloned directory\n> ./stable-diffusion-webui/venv/bin/pip install ./CLIP\n\n3. run the script again: it'll skip installing CLIP because it's already installed", 'createdAt': '2026-06-04T14:28:16Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17410#issuecomment-4623088444', 'viewerDidAuthor': False}, {'id': 'IC_kwDOH3JoL88AAAABE5ov9A', 'author': {'login': 'ghazel'}, 'authorAssociation': 'NONE', 'body': "It's only the tip of the iceberg. A1111 does not run on macOS at all.", 'createdAt': '2026-06-04T15:52:38Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17410#issuecomment-4623839220', 'viewerDidAuthor': False}, {'id': 'IC_kwDOH3JoL88AAAABE6O0pQ', 'author': {'login': 'mrbit-dev'}, 'authorAssociation': 'NONE', 'body': 'I fixed it. Done. Thanks', 'createdAt': '2026-06-04T17:11:01Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/17410#issuecomment-4624463013', 'viewerDidAuthor': False}] labels=bug-report）
- #17407 [OPEN] > Have a second worksheet in each spreadsheet file that contains some options for the generated page...（comments=[] labels=无）
- #17404 [CLOSED] [Bug]: Error code: 1（comments=[] labels=bug-report）

### Pull Requests 抽样

PR 
- #17418 [OPEN] docs: fix changelog typosPR 
- #17412 [CLOSED] Fix indentation in modules/launch_utils.py: align startup_timer.recor…PR 
- #17403 [CLOSED] docs: add Code of ConductPR 
- #17399 [CLOSED] Molten Hub Code: 100% Unit Test CoveragePR 
- #17393 [CLOSED] chore: update stable diffusion repository URL to nlile fork

### Releases 抽样

v1.10.1（published=2025-02-09T08:00:10Z latest=True）
- v1.10.0（published=2024-07-27T03:55:24Z latest=False）
- v1.10.0-RC（published=2024-07-06T08:28:39Z latest=False）
- v1.9.4（published=2024-05-28T18:21:30Z latest=False）
- v1.9.3（published=2024-04-22T15:03:02Z latest=False）

### 真实反馈与维护信号研判

抽样 issue 中 open/closed 约为 6/2，可作为维护者响应速度的弱信号。近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。存在 release 记录，说明作者有版本化交付意识。若外部搜索链路不可用，本报告明确以 GitHub issue/PR/release 作为一手社区反馈源，不用二手转载冒充口碑数据。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## ⚔️ 竞品对比

维度stable-diffusion-webui竞品/替代定位面向仓库作者设定的具体场景，通常更垂直CapCut / DaVinci Resolve / Shotcut 往往更通用或生态更大学习曲线依赖其内部脚本/配置约定通用方案学习成本更高，但生态更成熟差异化仓库通常以“快上手、场景专用、意见化实现”为卖点通用方案强调可扩展、稳定性、跨场景能力

### 风险

作者驱动、文档深度可能不足、接口稳定性不确定大项目更稳定，但改造成本更高

## 🎯 核心研判

### 优势

对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。如果核心文件少而清晰，二次阅读和定制成本较低。GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险

若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景

需要快速验证该仓库所解决的问题是否值得投入。团队愿意接受一定的作者意见化设计，以换取更快交付。适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。不

### 适用场景

对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。需要极高社区冗余、插件生态或企业级支持的场景。

## 📂 关键文件路径速查

package.json
- `pyproject.toml`
- `requirements.txt`
- `README.md`test/__init__.pytest/conftest.pytest/test_extras.pytest/test_face_restorers.pytest/test_img2img.pytest/test_torch_utils.pytest/test_txt2img.pytest/test_utils.py

## ⭐ 三条关键发现

代码入口/骨架集中在：
- `package.json`, 
- `pyproject.toml`, 
- `requirements.txt`, 
- `README.md`, test/init.py近期开源反馈以 issue 为主，典型议题包括：[Bug]: pkg_resources eror；[Feature Request]:  vídeo sensual发布节奏可从最新 release 观察：v1.10.1

## 🧪 研究方法与数据来源

GitHub Repo API / README / 默认分支递归文件树关键源码文件抽样精读Issues / PRs / Releases 社区活动抽样说明：
- 若外部搜索数据不可用，则明确标注并不伪造口碑结论
