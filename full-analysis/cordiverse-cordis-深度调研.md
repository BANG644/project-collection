# cordiverse/cordis 深度调研

> 调研日期：2026-08-17　|　★ 4,624　|　Fork 240　|　Open Issues 41　|　TypeScript　|　MIT
> 仓库：https://github.com/cordiverse/cordis
> 创建：2022-05-17　|　最近推送：2026-08-13　|　Topics：`effect` `framework` `nodejs` `plugin`
> 官方描述：*Meta-Framework of Spatiotemporal Composability*（时空可组合性元框架）

---

## 一、项目全景

Cordis 不是又一个 Node.js 应用框架，它是**一层"生命周期代数"**：把"申请资源 → 使用资源 → 释放资源"这件所有长驻程序都要做、但几乎所有框架都做得很脏的事，抽象成一个可组合、可嵌套、可回滚、可观测的原语 `ctx.effect()`。

三个关键定位信号，比 README 更能说明它是什么：

1. **它有论文。** README 只有 10 行，但第一行链接就是 [`cordiverse/paper` — *A Programming Paradigm for Spatiotemporal Composability*](https://github.com/cordiverse/paper)。作者是先想清楚范式、再写实现的路径，不是反过来。
2. **它的官方文档托管在 DeepSeek Harness 名下。** `homepage` 字段指向 `deepseek-harness.github.io/.../reference/cordis-primer` —— 也就是说 cordis 已经被当作某个 Agent Harness 系统的**底层运行时规范**在引用，而不只是一个独立 npm 包。
3. **它是 Koishi 的心脏被摘出来单独长大的。** cordis 的插件/服务/隔离模型正是 Koishi 机器人框架多年沉淀的那套东西，2022 年独立成仓，剥掉聊天机器人语义，只留下"时空组合"内核。

**一句话定位**：给"需要在运行时反复装卸、热重载、按作用域隔离的长驻 Node 服务"提供一套论文级严谨的插件 + 依赖注入 + 副作用生命周期内核。

### 项目亮点（差异化）

| # | 亮点 | 为什么别处没有 |
|---|---|---|
| 1 | **`effect()` 统一 4 种副作用形态** | 同一个 API 吞下 `Disposable`、`Promise<Disposable>`、`Iterable<Disposable>`、`AsyncIterable<Disposable>`，调用方不用关心同步/异步/批量 |
| 2 | **LIFO 逆序释放 + 失败自动回滚** | `disposables.splice(0).reverse()`，后申请先释放；`effect` 执行抛错时立即 `dispose()` 已申请的部分，不留半开资源 |
| 3 | **epoch 竞态守卫** | 异步迭代器每一轮都校验 `runner.epoch !== oldEpoch`，卸载信号一到立刻停止继续申请资源——这是热重载框架最容易漏的地方 |
| 4 | **dispose 句柄同时是函数和 thenable** | `dispose()` 同步收，`await dispose` 等待异步 effect 就绪后再收，一个返回值两种语义 |
| 5 | **副作用树可观测** | 每个 dispose 挂 `EffectMeta {label, children}`，`getEffects()` 直接吐出整棵资源树，调试"到底谁没释放" |
| 6 | **Standard Schema 而非绑定 zod** | 配置校验走 `Config['~standard'].validate()`，不锁定任何一家 schema 库 |
| 7 | **官方 HMR 包带 i18n** | `packages/hmr` 自带 `en-US.yml` / `zh-CN.yml`，热重载的错误提示是本地化的 |

---

## 二、核心架构

### 2.1 Monorepo 结构（112 文件，9 个包）

```
packages/
├── core/            ← 内核（context / fiber / registry / service / reflect / events / logger / utils）
├── loader/          ← 声明式 YAML 配置树加载器（config/{entry,group,isolate,tree,utils}.ts）
├── hmr/             ← 热模块替换插件（带 en-US/zh-CN 本地化）
├── include/         ← 配置文件 include/patch 机制
├── group/           ← 插件分组
├── isolate（在 loader/config/isolate.ts）← 服务隔离域
├── timer/           ← 定时器服务（生命周期安全的 setTimeout/setInterval）
├── logger-console/  ← 控制台日志后端（browser.ts / index.ts / shared.ts 三端）
├── create/          ← `npm create cordis` 脚手架
└── utils/
```

内核只有 9 个源文件，其中 `fiber.ts` 486 行**独占近半复杂度**——这就是全项目的重心。

### 2.2 Fiber：状态机 + 副作用容器

```ts
export const enum FiberState {
  PENDING, LOADING, ACTIVE, FAILED, DISPOSED, UNLOADING,
}
```

一个 Fiber = 一个插件实例的完整生命。它持有：

- `_disposables: DisposableList<Disposable>` —— 本 Fiber 申请的全部资源
- `_runner: EffectRunner<string>` —— 执行器（`epoch` / `execute` / `collect` / `getOuterStack`）
- `inertia: Promise<void> | undefined` —— **"惯性"**，把并发的 reload/unload 串行化
- `store: Dict<Impl>` —— 本 Fiber 向外提供的服务实现

Fiber 自身的存活也是一个 effect（**自举**）：

```ts
this.dispose = parent.fiber.effect(() => {
  const remove = runtime.fibers.push(this)
  try {
    this.config = resolveConfig(runtime, config)
    this._refresh()
  } catch (error) {
    this.ctx.logger.error(error)
    this._error = error
  }
  return async () => {                      // ← 这就是 dispose 逻辑
    this.uid = null
    this.context.emit('internal/plugin', this)
    if (this.ctx.registry.has(runtime.callback)) {
      remove()
      if (!runtime.fibers.length) this.ctx.registry.delete(runtime.callback)
    }
    this._setEpoch(INACTIVE)
    while (this.inertia) await this.inertia   // 等惯性耗尽
  }
}, 'ctx.plugin()')
```

注意 `label = 'ctx.plugin()'` —— 副作用树里插件本身也是一个有名字的节点。

### 2.3 `effect()`：全项目最值得抄的 60 行

```ts
effect(execute: () => Effect, label = 'anonymous'): any {
  this.assertActive()                         // 非 ACTIVE 直接抛 INACTIVE_EFFECT

  const disposables: Disposable[] = []
  const dispose = () => {
    let task!: void | Promise<void>
    for (const dispose of disposables.splice(0).reverse()) {   // ← LIFO
      if (task) task = task.then(dispose)                      // 异步则串行链
      else {
        const result = dispose()
        if (isObject(result) && 'then' in result) task = result as any
      }
    }
    return task
  }

  const meta: EffectMeta = { label, children: [] }
  const runner: EffectRunner<boolean> = {
    execute, epoch: true,
    collect: (dispose) => {
      disposables.push(dispose)
      this._disposables.delete(dispose)        // 从 Fiber 级转移到本 effect 级（所有权移交）
      if (dispose[symbols.effect]) meta.children.push(dispose[symbols.effect])  // 建树
    },
    getOuterStack: buildOuterStack(),          // 抓外层同步栈，供跨 await 拼接
  }

  let task: void | Promise<void>
  try { task = this._execute(runner) }
  catch (reason) { dispose(); throw reason }   // ← 失败即回滚

  task?.catch(dispose).catch((e) => this.ctx.logger.error(e))  // 防 unhandled rejection

  const wrapper = defineProperty(() => {
    if (!runner.epoch) return                  // 幂等
    runner.epoch = false
    return task ? task.then(dispose) : dispose()
  }, symbols.effect, meta) as AsyncDisposable

  wrapper.then = async (onFulfilled, onRejected) =>            // ← 双形态
    Promise.resolve(task).then(() => disposeAsync).then(onFulfilled, onRejected)

  disposables.push(this._disposables.push(wrapper))
  return wrapper
}
```

四个设计决断，每一个都对应一类真实事故：

| 决断 | 防的是什么事故 |
|---|---|
| `catch (reason) { dispose(); throw }` | 初始化到一半失败 → 前面开的 socket/文件句柄永久泄漏 |
| `task?.catch(dispose).catch(logger.error)` | 异步 effect 拒绝 → Node 进程 unhandled rejection 崩溃 |
| `if (!runner.epoch) return` | 重复调 dispose → double-free / 释放到别人的资源 |
| `this._disposables.delete(dispose)` | 资源被 Fiber 和 effect 双重持有 → 释放顺序不确定 |

### 2.4 形态归一化：`_execute()`

```ts
const effect: Effect = runner.execute.call(this)
if (typeof effect === 'function')            return runner.collect(effect)      // ① 直接返回 disposer
else if (isNullable(effect))                 { /* 无资源，合法 */ }
else if ('then' in effect)                   return effect.then(safeCollect)     // ② Promise
else if (Symbol.iterator in effect) {                                            // ③ 同步生成器
  info.error = new Error()
  const iter = effect[Symbol.iterator]()
  while (true) { const r = iter.next(); safeCollect(r.value); if (r.done) return }
} else if (Symbol.asyncIterator in effect) {                                     // ④ 异步生成器
  const iter = effect[Symbol.asyncIterator]()
  return (async () => {
    await Promise.resolve()                  // 强制生成异步栈
    info.error = new Error()
    while (true) {
      if (runner.epoch !== oldEpoch) return  // ★ epoch 守卫：卸载信号到了就不再申请
      const r = await iter.next()
      safeCollect(r.value)
      if (r.done) return
    }
  })()
} else throw new TypeError('Invalid effect')
```

**生成器形态是精髓**：一个插件可以写

```ts
ctx.effect(async function* () {
  yield await openDatabase()      // 第 1 个资源，立即被 collect
  yield await connectRedis()       // 第 2 个资源
  yield startHttpServer()          // 第 3 个
})
```

任何一步失败或中途被卸载，前面已 `yield` 的都已进入 `disposables`，会被 LIFO 逆序释放。这比 `try/finally` 手写嵌套干净一个量级。

### 2.5 跨异步边界的栈拼接

`composeError((info) => {...}, runner.getOuterStack)` + `info.error = new Error()`：在进入异步之前抓一份"外层同步栈"，异步内部再抓一份"内层栈"，出错时把两段缝起来。这解决了 Node 里 `await` 之后堆栈只剩几帧、根本看不出是哪个插件的哪一行申请了资源的经典痛点。

### 2.6 Service：既是对象也是函数

```ts
export abstract class Service<out T = never> {
  constructor(protected ctx: Context, name: string) {
    let self = this
    const tracker: Tracker = { associate: name, property: 'ctx' }
    if (self[symbols.invoke]) {
      self = createCallable(name, joinPrototype(Object.getPrototypeOf(this), Function.prototype), tracker)
    }
    self.ctx = ctx; self.name = name
    defineProperty(self, symbols.tracker, tracker)
    self.ctx.reflect.provide(name, self, this[symbols.check])
    return self                               // ← 构造函数 return 别的对象
  }

  protected [symbols.filter](ctx: Context) {  // 隔离域判定
    return ctx[symbols.isolate][this.name] === this.ctx[symbols.isolate][this.name]
  }
}
```

若子类实现了 `[symbols.invoke]`，Service 实例会被包成可调用对象——于是 `ctx.http` 既能 `ctx.http.get(...)` 也能 `ctx.http(...)`。`joinPrototype(..., Function.prototype)` 是把原型链拼到 `Function.prototype` 上的关键小技巧。

`[symbols.filter]` 用 `ctx[symbols.isolate][name]` 比较：**同名服务在不同隔离域里是不同实例**，这就是 loader 里 `isolate` 配置项的底层支撑。

`[symbols.resolveConfig]` 沿 `Context.intercept` 原型链向上收集配置并合并，实现"父上下文设默认、子上下文覆盖"的配置继承。

### 2.7 配置校验不绑架用户

```ts
export function resolveConfig(runtime: Plugin.Runtime, config: any) {
  if (!runtime.Config) return config
  const result = runtime.Config['~standard'].validate(config)   // Standard Schema V1
  if ('then' in result) throw new TypeError('Async config validation is not supported')
  if (result.issues) throw new ValidationError(result.issues)
  return result.value
}
```

走 `@standard-schema/spec`，zod / valibot / arktype 任选。`ValidationError` 额外挂 `Symbol.for('ValidationError')` 标记——跨包多副本时 `instanceof` 会失效，用全局 Symbol 兜底，这是库作者才会想到的细节。

---

## 三、测试与工程化

`packages/core/tests/` 12 个 spec，命名本身就是一份能力清单：

`associate` · `decorator` · `dispose` · `events` · `fiber` · `invoke` · `isolate` · `logger` · `plugin` · `reflect` · `service` · `shadow`

其中 `shadow.spec.ts`（服务遮蔽）和 `associate.spec.ts`（关联追踪）测的都是很难写对的语义。工具链：Vitest + nyc（`.nycrc.json`）+ yakumo（`yakumo.yml`，作者自研的 monorepo 发布工具）+ 三层 tsconfig（`base` / `test` / 各包）。

值得注意：**仓库没有一个 GitHub Release**（`releases` API 返回空）。版本完全走 npm，变更日志不在 GitHub 上体现——对使用者是个信息摩擦点。

---

## 四、应用场景与启发

### 4.1 直接可用的场景

| 场景 | cordis 提供什么 |
|---|---|
| **Multi-Agent Harness / Agent 运行时** | 每个 Agent = 一个 Fiber，工具/连接/子进程都用 `effect()` 申请；Agent 崩了自动回收全部资源，不留孤儿进程。官方 homepage 指向 DeepSeek Harness 的 cordis-primer 就是这个用法 |
| **插件化机器人 / IM 平台** | Koishi 的原生底座，适配器、中间件、数据库都是 Service |
| **长驻数据管道 / ETL 守护进程** | `hmr` 让你改一行转换逻辑就热替换，不断连接、不丢队列 |
| **多租户服务** | `isolate` 让同名服务（如 `database`）在不同租户上下文里是不同实例 |
| **需要"运行时装卸能力"的 CLI/IDE 后端** | `loader` 提供 YAML 声明式插件树 + `include` 配置分片 |

### 4.2 可以偷走的思想（哪怕不用 cordis）

1. **把资源生命周期做成组合子而不是约定。** 大多数项目靠"记得在 `onDestroy` 里关掉"，cordis 把它变成类型系统能检查的返回值。任何语言都能移植这个模式：*申请函数必须返回释放函数*。
2. **异步生成器 = 天然的资源栈。** `yield` 一次就登记一次，比嵌套 `try/finally` 可读性高得多。这是 JS 里少有的"语言特性刚好完美贴合问题"的案例。
3. **epoch 号是最轻量的取消机制。** 不需要 `AbortController`，一个自增/布尔 epoch 就能让异步循环在正确的点自愿退出。
4. **副作用要有名字。** `EffectMeta {label, children}` 让"内存泄漏排查"从玄学变成读一棵树。任何有资源池的系统都该抄。
5. **跨 await 拼栈。** 进异步前先 `new Error()` 存栈，出错时缝合。成本极低，收益是排障时间从小时降到分钟。
6. **用全局 Symbol 而非 instanceof 做跨包类型判定。** monorepo/多版本共存场景的通用解法。

---

## 五、社区口碑

Open issues 41，实际讨论热度不高但**问题质量很硬**，且**中文占比极高**：

| Issue | 状态 | 💬 | 内容 | 信号 |
|---|---|---|---|---|
| #72 | open | 2 | `isolate()` cleanup APIs unreliable — `Symbol.dispose` missing, `fiber.dispose` over-cleans parent context | ⚠️ **核心语义 bug**：隔离域清理会误伤父上下文 |
| #60 | open | 1 | 如何扩展到多节点的分布式 multi agent Agent Harness | 社区正把它当 Agent 底座用，但缺分布式方案 |
| #59 | open | 6 | 未来发新版本可否同步发布中文 paper？ | 中文用户基本盘，讨论最热的 open issue |
| #65 | open | 1 | `[plugin-include] writeTask?: NodeJS.Timeout` 在 `exactOptionalPropertyTypes` 下报错 | 严格 TS 配置兼容性 |
| #51 | open | 2 | fix(core): dispatch symbol and prototype-named events | 事件系统边界 case |
| #2 | closed | 7 | 为 cordis 增加全局错误处理接口 | 历史最热，已解决 |
| #1 | closed | 6 | 反复 `app.stop()` / `app.start()` 导致 service 不可访问 | 早期生命周期 bug，已修 |
| #6 / #5 | closed | 4/2 | 在已 dispose 的 context 上 plugin | 就是现在 `assertActive()` + `INACTIVE_EFFECT` 的来源 |

**解读**：issue 编号只到 72、四年（2022→2026）累计不到百条，说明**用户虽多但大多经由 Koishi 间接使用**，直接向 cordis 提 issue 的是少数深度用户。240 fork / 4,624 star ≈ 5.2%，这个比例（远高于 awesome-list 类项目的 1-2%）说明 fork 者是真在改代码而不是收藏。

README 自己写着一行加粗警告：**"Cordis is under active development. The API is not yet stable and may change without notice."** —— 官方主动降低预期。

---

## 六、竞品对比

| 维度 | **cordis** | NestJS | Effect-TS | InversifyJS / tsyringe | Koishi |
|---|---|---|---|---|---|
| 定位 | 生命周期 + 插件元框架 | 全栈应用框架 | 完整 FP effect 运行时 | 纯 DI 容器 | 聊天机器人框架 |
| 运行时热装卸 | ✅ 一等公民（`hmr` 包） | ❌ 需重启 | ❌ 非其目标 | ❌ | ✅（继承 cordis） |
| 副作用自动回收 | ✅ LIFO + 失败回滚 | ⚠️ `onModuleDestroy` 手写 | ✅ `Scope`/`acquireRelease` | ❌ | ✅ |
| 作用域隔离 | ✅ `isolate` 语义 | ⚠️ Request scope | ✅ | ⚠️ 容器级 | ✅ |
| 学习曲线 | 中（概念少但抽象重） | 中（装饰器+模块） | **高**（需懂 FP/HKT） | 低 | 中 |
| 体积 / 依赖 | 极轻（内核 9 文件） | 重 | 重 | 轻 | 重 |
| 配置校验 | Standard Schema（不锁定） | class-validator | 自带 Schema | 无 | Schemastery |
| 生态 | 小（+ Koishi 生态大） | **极大** | 中等增长快 | 中 | 中（中文圈强） |
| 文档 | ⚠️ 托管在第三方站点 | 极佳 | 好 | 一般 | 好（中文） |

**关键差异**：Effect-TS 是"把整个程序变成 effect"，cordis 是"只把资源生命周期变成 effect"。前者要求你重写全部业务代码，后者可以只在插件边界使用、内部照常写命令式 TS。这个**渐进采用成本**是 cordis 相对 Effect-TS 最实际的优势。

---

## 七、核心研判

### 护城河

1. **Koishi 多年生产验证。** 不是实验室玩具——热重载、服务隔离这些语义在成千上万个 Koishi 机器人实例上跑过。
2. **论文级抽象 + 极小内核。** 9 个源文件的内核，读完能完整掌握，这在框架里罕见。可审计性 = 长期信任。
3. **被当作 Agent Harness 底座。** homepage 指向 DeepSeek Harness 的 cordis-primer，issue #60 在讨论分布式 multi-agent。如果 Agent 运行时这条赛道起来，cordis 占的是"生命周期层"这个位置——Agent 最需要的恰是"工具/连接/子进程的可靠回收"。

### 风险

1. **API 自认不稳定。** README 加粗声明，`ctx.plugin()` 语义、`isolate` 清理都还在动。生产上锁死版本 + 自建回归测试是必须的。
2. **#72 是硬伤。** `fiber.dispose` 过度清理父上下文 + 缺 `Symbol.dispose` 支持，意味着"隔离域"这个卖点在边界情况下不可靠。用 isolate 前必须自测。
3. **文档主权不在自己手上。** 官方文档托管在 `deepseek-harness.github.io`，没有独立站点；`packages/hmr/README.md` 只有一行标题。文档投入明显落后于代码质量。
4. **零 GitHub Release。** 没有变更日志、没有 tag 说明，升级要读 npm diff。对企业采纳是实质阻碍。
5. **中文语境依赖。** issue 大量中文、#59 求中文 paper，国际化社区尚未真正形成，英文圈发现成本高。

### 谁应该用 / 不该用

- ✅ **该用**：正在写需要运行时装卸插件的长驻 Node 服务；正在做 Agent Harness 且被"工具资源泄漏"折磨；已在 Koishi 生态内。
- ⚠️ **谨慎**：需要长期 API 稳定性的企业级项目（等 1.0 或锁版本）；重度依赖 `isolate` 隔离语义的（先验证 #72）。
- ❌ **不该用**：只需要 DI 的（用 tsyringe 更轻）；愿意全盘 FP 重写的（Effect-TS 更彻底）；团队无人能读 486 行 fiber.ts 的（出问题无法自救）。

### 一句话研判

**cordis 是一个"抽象水平远超其星标数"的项目**——4.6k star 配得上论文级的生命周期代数设计，但配不上它的文档和 API 稳定性承诺。它最大的价值可能不是被直接依赖，而是 `fiber.ts` 那 486 行给所有做资源管理的人提供了一份可抄的正确答案。

---

## 八、关键文件路径速查

| 路径 | 行数 | 说明 |
|---|---|---|
| `packages/core/src/fiber.ts` | **486** | ⭐ 全项目核心：`Fiber` 状态机、`effect()`、`_execute()` 形态归一化、`ValidationError`、`CordisError` |
| `packages/core/src/registry.ts` | 214 | 插件注册表、`Plugin.Runtime`、`fibers` 列表管理 |
| `packages/core/src/service.ts` | 80 | `Service` 抽象基类、`createCallable`、`[symbols.filter]` 隔离判定、配置继承 |
| `packages/core/src/context.ts` | 78 | `Context` 类型与 `extend()` / `intercept` 原型链 |
| `packages/core/src/reflect.ts` | — | `provide` / `impl` 反射层（服务注册的底层） |
| `packages/core/src/utils.ts` | — | `composeError`、`buildOuterStack`、`DisposableList`、`getTraceable`、`symbols` |
| `packages/core/src/events.ts` | — | 事件系统（`internal/plugin` 等内部事件） |
| `packages/core/tests/*.spec.ts` | 12 文件 | 能力清单：associate/decorator/dispose/events/fiber/invoke/isolate/logger/plugin/reflect/service/shadow |
| `packages/loader/src/config/isolate.ts` | — | 隔离域配置解析（对应 issue #72） |
| `packages/loader/src/config/tree.ts` | — | YAML 插件树解析 |
| `packages/hmr/src/index.ts` | — | 热模块替换实现 |
| `packages/hmr/src/locales/{en-US,zh-CN}.yml` | — | HMR 错误提示本地化 |
| `packages/timer/src/index.ts` | — | 生命周期安全的定时器服务（`effect()` 的最小示例） |
| `yakumo.yml` / `.nycrc.json` / `vitest.config.ts` | — | 发布 / 覆盖率 / 测试配置 |

**外部资源**：
- 论文：https://github.com/cordiverse/paper 《A Programming Paradigm for Spatiotemporal Composability》
- 文档：https://deepseek-harness.github.io/deepseek-harness/reference/cordis-primer
