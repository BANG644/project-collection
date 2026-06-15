# batch06_rebuild_failure_summary_20260610_1005

## Objective
尝试对 `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\batch_06.txt` 中 16 个 GitHub 仓库执行“重建调研报告 → 上传 IMA → 更新元目录 → 写 done 文件”的全流程。

## What I did
1. 读取并遵循了 `qclaw-rules`、`github-repo-deep-dive`、workspace 中的 IMA/GitHub 规则。
2. 检查并复用了现有脚本：
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\upload_to_ima.py`
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\tmp_ima_fetch.py`
3. 验证了：
   - `gh` 已登录，可正常访问 GitHub。
   - 旧 `media_id` 无法通过 notes API 完整取回正文，返回 `GetNoteContent not author`。
4. 编写并运行自动化脚本：
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\batch06_rebuild.py`
5. 脚本生成了部分本地报告草稿，并输出失败明细：
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06_results.json`
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\batch_06_done.txt`
   - `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\*.md`

## Key findings
### A. 旧报告正文无法直接取回
使用 IMA notes API 按 `media_id`/`doc_id` 读取旧报告时，返回：
- `code: 210005`
- `msg: GetNoteContent not author`

这意味着不能靠“从旧 media_id 拉回全文再重传”的路线完成恢复。

### B. 当前脚本的上传参数不对
`import_doc` 可成功创建 note，但 `add_knowledge` 使用：
- `media_type: 11`
- `note_info: { content_id: doc_id }`

IMA 实际返回：
- `code: 220004`
- `msg: missing required field: note_info`

说明当前 `add_knowledge` 的 note 关联参数格式不正确，导致即使本地报告生成成功，也无法入库。

### C. 文件名解析 owner/repo 的规则不可靠
批次文件里若直接按 “第一个连字符前是 owner，其余是 repo” 解析，会错误得到：
- `vercel/labs-agent-browser`（应为 `vercel-labs/agent-browser`）
- `1Panel/dev-1Panel`（应为 `1Panel-dev/1Panel`）
- `multica/ai-multica`（应为 `multica-ai/multica`）
- `langbot/app-LangBot`（应为 `langbot-app/LangBot`）
- `Skyvern/AI-skyvern`（应为 `Skyvern-AI/skyvern`）

因此多条 `gh repo view` 直接 404 失败。

### D. 已生成的本地草稿
已落盘 5 篇本地报告：
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\searxng-searxng-全方位深度调研.md`
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\ShareX-ShareX-全方位深度调研.md`
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\microsoft-agent-lightning-全方位深度调研.md`
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\topoteretes-cognee-全方位深度调研.md`
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06\xming521-WeClone-全方位深度调研.md`

但它们尚未成功上传到 IMA。

## Final status
本次**未完成** 16/16 全流程重建。

结果文件显示：
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\batch_06_done.txt` → `DONE: 0/16`
- `C:\Users\Lenovo\.qclaw\workspace-agent-5750a030\reports\batch_06_results.json` 记录了每条失败原因。

## Recommended next steps for main agent
1. 先修正 filename → owner/repo 的映射规则，不能用简单 split 第一个 `-`。
2. 单独验证 IMA `add_knowledge` 对 note 类型的正确 payload。
3. 先用 1 个仓库（如 `searxng/searxng`）打通：
   - 报告生成
   - `import_doc`
   - `add_knowledge`
   - 元目录增量更新
4. 打通后再批量补跑 16 个仓库。
