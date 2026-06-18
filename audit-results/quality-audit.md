# Project Collection 调研报告质量审计

- 扫描文件数：145
- Critical：42
- High：5
- Medium：7
- Low：91

## 判定维度

- Markdown 结构：换行、标题、表格、代码围栏
- 内容语言：英文原文占比、中文讲解是否不足
- 数据污染：乱码、抓取截断、JSON/Issue 原始 dump
- 调研完整性：核心章节是否齐全、是否模板化/过浅

## 高风险清单（按分数倒序）

| 严重级别 | 分数 | 文件 | 行数 | 最长行 | 英文占比 | 核心章节 | 原因 |
|---|---:|---|---:|---:|---:|---:|---|
| critical | 123 | `full-analysis/GLips-Figma-Context-MCP-全方位深度调研.md` | 422 | 5015 | 0.927 | 8 | 存在超长行 max_line_len=5015<br>英文占比过高 english_ratio=0.93<br>含原始抓取/JSON/截断残留 34 处<br>模板化/浅层占位句过多 7 处 |
| critical | 117 | `full-analysis/sybil-solutions-codex-shim-全方位深度调研.md` | 421 | 3208 | 0.937 | 8 | 存在超长行 max_line_len=3208<br>英文占比过高 english_ratio=0.94<br>含原始抓取/JSON/截断残留 37 处<br>模板化/浅层占位句过多 9 处 |
| critical | 113 | `full-analysis/NoopApp-noop-全方位深度调研.md` | 216 | 31147 | 0.981 | 8 | 存在超长行 max_line_len=31147<br>英文占比过高 english_ratio=0.98<br>含原始抓取/JSON/截断残留 146 处<br>模板化/浅层占位句过多 7 处 |
| critical | 113 | `full-analysis/evershopcommerce-evershop-全方位深度调研.md` | 407 | 4906 | 0.933 | 8 | 存在超长行 max_line_len=4906<br>英文占比过高 english_ratio=0.93<br>含原始抓取/JSON/截断残留 32 处<br>模板化/浅层占位句过多 7 处 |
| critical | 113 | `full-analysis/greensock-GSAP-全方位深度调研.md` | 361 | 4378 | 0.941 | 8 | 存在超长行 max_line_len=4378<br>英文占比过高 english_ratio=0.94<br>含原始抓取/JSON/截断残留 63 处<br>模板化/浅层占位句过多 7 处 |
| critical | 113 | `full-analysis/anthropics_skills - 全方位深度调研.md` | 104 | 3658 | 0.870 | 8 | 存在超长行 max_line_len=3658<br>英文占比过高 english_ratio=0.87<br>含原始抓取/JSON/截断残留 14 处<br>模板化/浅层占位句过多 7 处 |
| critical | 110 | `full-analysis/abhigyanpatwari_GitNexus - 全....md` | 142 | 10288 | 0.939 | 8 | 存在超长行 max_line_len=10288<br>英文占比过高 english_ratio=0.94<br>含原始抓取/JSON/截断残留 30 处<br>模板化/浅层占位句过多 6 处 |
| critical | 110 | `full-analysis/kageroumado-phosphene-全方位深度调研.md` | 194 | 10128 | 0.922 | 8 | 存在超长行 max_line_len=10128<br>英文占比过高 english_ratio=0.92<br>含原始抓取/JSON/截断残留 22 处<br>模板化/浅层占位句过多 6 处 |
| critical | 110 | `full-analysis/colbymchenry_codegraph - 全方位....md` | 127 | 7191 | 0.913 | 8 | 存在超长行 max_line_len=7191<br>英文占比过高 english_ratio=0.91<br>含原始抓取/JSON/截断残留 24 处<br>模板化/浅层占位句过多 6 处 |
| critical | 96 | `full-analysis/hugohe3-ppt-master-全方位深度调研.md` | 234 | 2204 | 0.856 | 8 | 英文占比过高 english_ratio=0.86<br>含原始抓取/JSON/截断残留 38 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 96 | `full-analysis/OthmanAdi-planning-with-files-全方位深度调研.md` | 354 | 2185 | 0.925 | 8 | 英文占比过高 english_ratio=0.93<br>含原始抓取/JSON/截断残留 38 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 94 | `full-analysis/withkynam-vibecode-pro-max-kit-全方位深度调研.md` | 255 | 274 | 0.855 | 8 | 英文占比过高 english_ratio=0.86<br>疑似乱码/错误转码命中 2 次<br>含原始抓取/JSON/截断残留 5 处<br>模板化/浅层占位句过多 6 处 |
| critical | 93 | `full-analysis/Michaelliv-pi-dynamic-workflows-全方位深度调研.md` | 393 | 990 | 0.881 | 8 | 英文占比过高 english_ratio=0.88<br>含原始抓取/JSON/截断残留 10 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 93 | `full-analysis/jackwener-OpenCLI-全方位深度调研.md` | 347 | 553 | 0.898 | 8 | 英文占比过高 english_ratio=0.90<br>含原始抓取/JSON/截断残留 14 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 91 | `full-analysis/CyC2018_CS-Notes - 全方位深度调研.md` | 115 | 2740 | 0.733 | 8 | 英文占比过高 english_ratio=0.73<br>疑似乱码/错误转码命中 1 次<br>含原始抓取/JSON/截断残留 24 处<br>模板化/浅层占位句过多 6 处 |
| critical | 91 | `full-analysis/wuji-labs-nopua-全方位深度调研.md` | 165 | 1467 | 0.770 | 8 | 英文占比过高 english_ratio=0.77<br>疑似乱码/错误转码命中 1 次<br>含原始抓取/JSON/截断残留 17 处<br>模板化/浅层占位句过多 6 处 |
| critical | 89 | `full-analysis/topoteretes_cognee - 全方位深度调研.md` | 63 | 14848 | 0.940 | 8 | 存在超长行 max_line_len=14848<br>英文占比过高 english_ratio=0.94<br>含原始抓取/JSON/截断残留 48 处<br>模板化/浅层占位句过多 3 处 |
| critical | 89 | `full-analysis/xming521_WeClone - 全方位深度调研.md` | 61 | 3069 | 0.748 | 8 | 存在超长行 max_line_len=3069<br>英文占比过高 english_ratio=0.75<br>含原始抓取/JSON/截断残留 19 处<br>模板化/浅层占位句过多 3 处 |
| critical | 89 | `full-analysis/VAST-AI-Research_TripoSplat ....md` | 77 | 2209 | 0.783 | 8 | 标题层级过少 headings=4<br>英文占比过高 english_ratio=0.78<br>疑似乱码/错误转码命中 1909 次<br>模板化/浅层占位句过多 3 处 |
| critical | 87 | `full-analysis/index-tts-index-tts-全方位深度调研.md` | 279 | 866 | 0.843 | 8 | 英文占比过高 english_ratio=0.84<br>含原始抓取/JSON/截断残留 21 处<br>模板化/浅层占位句过多 9 处<br>疑似直接搬运 README 英文原文 |
| critical | 87 | `full-analysis/KKKKhazix-khazix-skills-全方位深度调研.md` | 193 | 764 | 0.647 | 8 | 英文占比过高 english_ratio=0.65<br>含原始抓取/JSON/截断残留 6 处<br>模板化/浅层占位句过多 9 处<br>疑似直接搬运 README 英文原文 |
| critical | 87 | `full-analysis/larksuite-cli-全方位深度调研.md` | 373 | 350 | 0.885 | 8 | 英文占比过高 english_ratio=0.88<br>含原始抓取/JSON/截断残留 6 处<br>模板化/浅层占位句过多 9 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/jd-opensource-JoyAI-Echo-全方位深度调研.md` | 185 | 2985 | 0.825 | 8 | 英文占比过高 english_ratio=0.82<br>含原始抓取/JSON/截断残留 21 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/ClaudioDrews-memory-os-全方位深度调研.md` | 162 | 2603 | 0.903 | 8 | 英文占比过高 english_ratio=0.90<br>含原始抓取/JSON/截断残留 24 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/pewdiepie-archdaemon_odysseu....md` | 127 | 1870 | 0.873 | 8 | 英文占比过高 english_ratio=0.87<br>含原始抓取/JSON/截断残留 6 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/msitarzewski_agency-agents -....md` | 107 | 1626 | 0.805 | 8 | 英文占比过高 english_ratio=0.80<br>含原始抓取/JSON/截断残留 6 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/sapientinc-HRM-Text-全方位深度调研.md` | 178 | 563 | 0.812 | 8 | 英文占比过高 english_ratio=0.81<br>含原始抓取/JSON/截断残留 10 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 86 | `full-analysis/Sjj1024-PakePlus-全方位深度调研.md` | 271 | 410 | 0.838 | 8 | 英文占比过高 english_ratio=0.84<br>含原始抓取/JSON/截断残留 12 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| critical | 83 | `full-analysis/lynote-ai-humanize-text-全方位深度调研.md` | 275 | 2495 | 0.899 | 8 | 英文占比过高 english_ratio=0.90<br>含原始抓取/JSON/截断残留 12 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 83 | `full-analysis/AUTOMATIC1111_stable-diffusi....md` | 123 | 2378 | 0.883 | 8 | 英文占比过高 english_ratio=0.88<br>含原始抓取/JSON/截断残留 23 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 83 | `full-analysis/supermemoryai-supermemory-全方位深度调研.md` | 385 | 1602 | 0.928 | 8 | 英文占比过高 english_ratio=0.93<br>含原始抓取/JSON/截断残留 48 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 83 | `full-analysis/dreammis-social-auto-upload-全方位深度调研.md` | 388 | 959 | 0.745 | 8 | 英文占比过高 english_ratio=0.74<br>含原始抓取/JSON/截断残留 24 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 80 | `full-analysis/VoltAgent_awesome-design-md ....md` | 118 | 1162 | 0.811 | 8 | 英文占比过高 english_ratio=0.81<br>含原始抓取/JSON/截断残留 10 处<br>模板化/浅层占位句过多 6 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/GitHub 项目研究 — 元目录.md` | 13 | 3920 | 0.588 | 3 | 存在超长行 max_line_len=3920<br>标题层级过少 headings=4<br>核心章节缺失 core_section_hits=3 |
| critical | 77 | `full-analysis/📚 GitHub 项目研究 — 元目录.md` | 13 | 3920 | 0.588 | 3 | 存在超长行 max_line_len=3920<br>标题层级过少 headings=4<br>核心章节缺失 core_section_hits=3 |
| critical | 77 | `full-analysis/aaif-goose_goose - 全方位深度调研.md` | 129 | 2548 | 0.876 | 8 | 英文占比过高 english_ratio=0.88<br>含原始抓取/JSON/截断残留 6 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/clash-verge-rev_clash-verge-....md` | 143 | 2273 | 0.818 | 8 | 英文占比过高 english_ratio=0.82<br>含原始抓取/JSON/截断残留 38 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/supabase_supabase - 全方位深度调研.md` | 124 | 2264 | 0.911 | 8 | 英文占比过高 english_ratio=0.91<br>含原始抓取/JSON/截断残留 31 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/excalidraw_excalidraw - 全方位深....md` | 155 | 1797 | 0.869 | 8 | 英文占比过高 english_ratio=0.87<br>含原始抓取/JSON/截断残留 9 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/ruvnet_ruflo - 全方位深度调研.md` | 128 | 925 | 0.850 | 8 | 英文占比过高 english_ratio=0.85<br>含原始抓取/JSON/截断残留 5 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| critical | 77 | `full-analysis/MatinSenPai-SenPaiScanner-全方位深度调研.md` | 240 | 335 | 0.842 | 8 | 英文占比过高 english_ratio=0.84<br>含原始抓取/JSON/截断残留 4 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| critical | 75 | `full-analysis/tastyeffectco_sandboxd - 全方位....md` | 28 | 3365 | 0.881 | 8 | 存在超长行 max_line_len=3365<br>标题层级过少 headings=4<br>英文占比过高 english_ratio=0.88 |
| high | 63 | `full-analysis/ace-trump-tech-DeltaForce-OBS-Locker-全方位深度调研.md` | 217 | 1583 | 0.568 | 8 | 含原始抓取/JSON/截断残留 14 处<br>模板化/浅层占位句过多 7 处<br>疑似直接搬运 README 英文原文 |
| high | 62 | `full-analysis/elder-plinius-CL4R1T4S-全方位深度调研.md` | 169 | 244 | 0.772 | 8 | 英文占比过高 english_ratio=0.77<br>含原始抓取/JSON/截断残留 1 处<br>模板化/浅层占位句过多 8 处<br>疑似直接搬运 README 英文原文 |
| high | 59 | `full-analysis/microsoft_agent-lightning - ....md` | 66 | 2467 | 0.763 | 8 | 英文占比过高 english_ratio=0.76<br>含原始抓取/JSON/截断残留 11 处<br>模板化/浅层占位句过多 3 处 |
| high | 54 | `full-analysis/amap-demo_amap-sdk-skills - ....md` | 27 | 2726 | 0.667 | 8 | 标题层级过少 headings=4<br>英文占比过高 english_ratio=0.67<br>模板化/浅层占位句过多 3 处 |
| high | 53 | `full-analysis/OpenCut-app_OpenCut - 全方位深度调....md` | 114 | 1068 | 0.746 | 8 | 英文占比过高 english_ratio=0.75<br>含原始抓取/JSON/截断残留 1 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| medium | 40 | `full-analysis/microsoft_PowerToys 全方位深度调研报告.md` | 1 | 2031 | 0.576 | 4 | 整篇几乎没有换行，Markdown 会退化成超长段落 |
| medium | 39 | `full-analysis/liyue-aigc_female-portrait-d....md` | 28 | 5674 | 0.372 | 8 | 存在超长行 max_line_len=5674<br>模板化/浅层占位句过多 3 处 |
| medium | 39 | `full-analysis/521xueweihan_HelloGitHub - 全....md` | 109 | 924 | 0.582 | 8 | 含原始抓取/JSON/截断残留 2 处<br>模板化/浅层占位句过多 5 处<br>疑似直接搬运 README 英文原文 |
| medium | 37 | `full-analysis/easychen-lean-side-bussiness-全方位深度调研.md` | 190 | 240 | 0.465 | 8 | 含原始抓取/JSON/截断残留 2 处<br>模板化/浅层占位句过多 9 处 |
| medium | 37 | `full-analysis/qiuqiubuchongle-cloud-chokepoint-atlas-全方位深度调研.md` | 279 | 129 | 0.397 | 8 | 含原始抓取/JSON/截断残留 2 处<br>模板化/浅层占位句过多 9 处 |
| medium | 35 | `full-analysis/Jane-xiaoer_xiaoer-videolab ....md` | 47 | 615 | 0.571 | 8 | 疑似乱码/错误转码命中 357 次 |
| medium | 32 | `full-analysis/BANG644_scheduler-sent_全方位深度调研.md` | 33 | 2508 | 0.694 | 9 | 英文占比过高 english_ratio=0.69<br>模板化/浅层占位句过多 4 处 |

## 建议修复优先级

1. Critical：先修；通常是完全不可读/一整行/乱码/原始 dump。
2. High：再修；通常可读但英文搬运、模板化、章节缺失明显。
3. Medium：批量润色；补中文解释、修 checklist/table/code fence。
4. Low：暂不动，除非人工点名。
