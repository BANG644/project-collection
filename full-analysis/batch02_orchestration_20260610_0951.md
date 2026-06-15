# batch02_orchestration_20260610_0951

## objective
并行完成 batch_02.txt 中 16 个 GitHub 仓库的深度调研工作流。当前阶段先做任务拆分与编排，后续汇总子代理产出的本地报告，再统一执行 IMA 上传与元目录更新，避免并发写冲突。

## key reasoning
- 任务量大，适合拆成 4 个子批次并行处理。
- 元目录更新属于共享写操作，必须由当前会话串行完成，避免覆盖冲突。
- 子代理只负责：解析 owner/repo、完成仓库调研、生成本地 Markdown 报告、写结构化结果文件。
- 主编排代理负责：收集结果、调用 IMA API 上传、更新元目录、写 batch_02_done.txt。

## conclusions
已读取关键规则文件：qclaw-rules、github-repo-deep-dive、AGENTS.md、TOOLS.md，并确认 batch_02.txt 的 16 个仓库条目。下一步已准备启动 4 个并行子代理处理子批次。
