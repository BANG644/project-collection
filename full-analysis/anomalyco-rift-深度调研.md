# rift（面向编码 Agent 的即时写时复制工作区）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / 源码），抓取日期 2026-10-03。许可：MIT。语言：Rust（crates: core / cli / ffi）。状态：branch `dev`（早期软件，接口可能变）。

## 一、项目定位（一句话）
为**编码 Agent 与并行工作**提供「即时写时复制（copy-on-write）工作区」——把当前工程状态秒级快照成隔离副本，让每个 Agent 拿到真实工作态的独立副本，而非共享 checkout 或从干净 commit 起步。

## 二、项目亮点（差异化）
1. **原生 COW**：Linux 用 btrfs 子卷 / XFS reflink(`FICLONE`)，macOS 用 APFS `clonefile`，零拷贝创建。
2. **过滤拷贝**：自动忽略 `node_modules`/`target`/venv/`dist`/`build`，保留 manifest 与 lockfile；`--copy-all` 可全量。
3. **生命周期钩子**：`.rift.toml` 在 create/remove 前后跑命令（如 `docker compose up/down`）。
4. **SQLite registry**：记录路径、父子关系、回收站；移除先进 `.trash`，`gc` 才真删。
5. **多形态入口**：CLI + JS API（Bun/Node FFI，Node 26.1+ 实验 FFI）+ 可作为 OpenCode V2 的 worktree 后端。
6. **并发安全**：并发 create 互不删除对方目标，移除为回收站操作直到 `gc`。

## 三、核心架构
- `crates/core`：`Manager`（组合 `Registry` + `Strategy`）与 `Strategy` trait（apfs/btrfs/linux/reflink 四个后端）。
- `crates/cli`：命令行。
- `crates/ffi`：Bun/Node FFI 绑定（条件导出）。
- 默认存储：源根相邻 `.rifts/<root>/<name>/`，回收 `.trash/`。
- `plugins/opencode`：OpenCode V2 插件（把 rift 当 worktree 后端）。

## 四、应用场景与启发
- 给「多 Agent 并行试验」提供**廉价隔离层**：比 git worktree 更轻（COW 不复制内容）、比容器更快。
- 钩子机制让快照自带运行环境（`compose up`），是「Agent 工作流基础设施」的精致设计。
- 过滤拷贝（忽略可再生产物、保留 lockfile）体现了对真实工程目录的深刻理解。

## 五、源码深度解读
**`crates/core/src/lib.rs`（`Manager::create`）**：核心创建流程——校验 source、Git 安全检查、生成 ID、计算目标目录、过滤拷贝、写 marker、git detach、注册、跑钩子：
```rust
pub fn create_with_options(&mut self, input: Create, options: CreateOptions) -> Result<PathBuf> {
    let source = self.workspace_from(&existing_directory(&input.from)?)?;
    let git = git::check_source(&from)?;          // 拒绝 merge/rebase/cherry-pick 中
    let id = RiftId::new();
    let destination_parent = input.into.unwrap_or_else(|| default_storage(&root.path)?); // .rifts/<root>/
    hook::run("precreate", config.precreate(), &from, &from, &destination, &id, &source.id)?;
    self.strategy.copy_directory(&from, &destination, options.copy_mode)?;  // 过滤/全量
    marker::write(&destination, &id)?;
    if git.is_repository() { git::hide_marker(&destination)?; git::detach_destination(&destination)?; }
    self.registry.insert_child(&id, &source.id, &destination)?;
    hook::run("postcreate", config.postcreate(), &destination, ...)?;
    Ok(destination)
}
```

**`crates/core/src/registry.rs`**：SQLite registry 管理 `Record`/`PathRecord`/`MovedRecord`，区分 active 与 trashed 路径；`trash_rows` 在 rename 失败时回滚已移动项，保证原子性。

**`crates/core/src/strategy/`**：`mod.rs` 按平台选择后端（`apfs`/`btrfs`/`linux`/`reflink`），统一 `copy_directory`/`remove_directory`/`initialize_directory` 接口。

## 六、全网口碑
**1320 ⭐**，README 明确标注「Early software，接口/存储细节可能变」，开发活跃（`cargo test --workspace`、基准 `cargo bench`）。社区定位清晰：Agent/并行工作的隔离层。

## 七、竞品对比
| 维度 | rift | git worktree | git stash/branch | Docker 容器 | overlayfs |
|------|------|--------------|-----------------|-------------|-----------|
| 创建速度 | ⚡ COW | 中 | 快 | 慢 | 快 |
| 隔离粒度 | 工作区副本 | 分支 | 提交 | 镜像 | 挂载 |
| Agent 友好 | ✅ API+钩子 | 中 | 弱 | 中 | 弱 |
| 跨平台 | Linux/macOS | 全 | 全 | 全 | Linux |

差异化：原生 COW + 过滤拷贝 + Agent 友好 API + 生命周期钩子。**风险**：Windows 仅发布包不支持创建；dev 分支接口不稳；依赖特定文件系统特性（btrfs/APFS/reflink）。

## 八、核心研判
精准命中「多 Agent 并行工作」痛点，架构干净（策略模式 + registry + FFI 多入口）；虽处早期、平台覆盖有限，但方向清晰，适合关注 **Agent 基础设施 / 工作流隔离** 的开发者跟踪与借鉴。

## 关键文件路径速查
- `crates/core/src/lib.rs` — `Manager`（create/init/remove/gc 核心编排）
- `crates/core/src/registry.rs` — SQLite registry 与回收站管理
- `crates/core/src/strategy/{mod,apfs,btrfs,linux,reflink}.rs` — 平台 COW 后端
- `crates/core/src/hook.rs` / `config.rs` — 生命周期钩子与 `.rift.toml` 解析
- `crates/cli/src/main.rs` — CLI 入口
- `crates/ffi/src/lib.rs` — Bun/Node FFI 绑定
- `plugins/opencode` — OpenCode V2 worktree 后端插件
