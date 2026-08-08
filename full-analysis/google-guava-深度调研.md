# 🔍 Google Guava 深度调研报告

> 调研日期：2026-08-09 ｜ 仓库：`google/guava` ｜ 星标：51,829 ⭐（2026-08-09，当日 Trending +93）｜ 协议：Apache-2.0 ｜ 语言：Java ｜ 创建：2014-05 ｜ 主题：guava, java

## 一、项目定位（一句话）

Google 核心 Java 工具库——补充 JDK 缺失的通用基础设施（集合/缓存/并发/IO/哈希/字符串/图论等），是 Java 服务端生态的事实标准基础依赖。

## 二、项目亮点（差异化，开篇呈现）

1. **事实标准**：51k★，Google 长期维护，几乎所有 Java/Kotlin/Android 服务端项目都直接或间接依赖。
2. **模块化清晰且克制**：`guava/src/com/google/common/` 下 18+ 独立包，各自职责单一。
3. **开创性 API 后被 JDK 借鉴**：`Optional`、`ImmutableList/Map/Set`、`Joiner/Splitter`、`Preconditions`、varargs 等范式被 JDK 逐步吸收，证明设计前瞻。
4. **多形态分发**：`guava`（核心）、`guava-gwt`（GWT 兼容）、`futures`、`android`、`guava-testlib`、`guava-bom`（依赖管理）。
5. **强兼容性纪律**：`@Beta` 显式契约 + 跨版本移除需 2 个 release 周期的迁移指南，是大型公共库版本治理的范本。

## 三、核心架构

```
guava/src/com/google/common/
├── base/        # Optional, Preconditions, Joiner, Splitter, Objects, Strings
├── collect/     # 不可变集合 + Multimap, BiMap, Table, RangeSet, Range
├── cache/       # 本地缓存：CacheBuilder, LoadingCache, RemovalListener
├── concurrent/  # ListenableFuture, Service, Monitor（future 语义）
├── eventbus/    # 发布-订阅：@Subscribe / @AllowConcurrentEvents
├── graph/       # 图论：Graph, ValueGraph, Network
├── hash/        # Hashing（一致性哈希、指纹）
├── io/          # Files, ByteSource, CharSource, CharSink
├── net/         # InetAddresses, HttpHeaders
├── primitives/  # UnsignedInteger, UnsignedLong
├── reflect/     # TypeToken, Invokable, Reflection
├── math/ escape/ xml/ util/ annotations/ ...
```

- **构建**：Maven（`pom.xml` + `mvnw`），`overview.html` 是总文档入口。
- **Android 分支**：`android/` 提供兼容旧 Android 的 jar，避免 JDK 8+ API 在旧运行时缺失。

## 四、源码深度解读

- **缓存是 Guava 最常被单独引用的模块**。`CacheBuilder` 用 Builder 模式链式配置：

```java
LoadingCache<Key, Graph> graphs = CacheBuilder.newBuilder()
    .maximumSize(1000)
    .expireAfterWrite(10, TimeUnit.MINUTES)
    .refreshAfterWrite(1, TimeUnit.MINUTES)
    .softValues()
    .build(new CacheLoader<Key, Graph>() {
        public Graph load(Key key) { return createExpensiveGraph(key); }
    });
```

  TTL/引用/权重/刷新/移除监听全套齐备，是本地缓存的事实标准实现。

- **EventBus 解耦组件**：`@Subscribe` 标注方法 + `eventBus.register(obj)` + `eventBus.post(event)`，同步 `EventBus` 与 `AsyncEventBus(Executor)` 两档，把组件间调用关系转换为发布-订阅。

- **不可变集合通过 Builder + 防御性拷贝**保证线程安全：`ImmutableList.copyOf(...)` 返回真正不可变实例，避免外部后续修改穿透。

- **`@Beta` 生命周期管理**：标注为 `@Beta` 的 API 可在 2 个 release 后被移除/改签名，给调用方明确迁移窗口——这是大型库"既要演进又不停用户"的关键契约。

## 五、应用场景与启发

- **适用**：任何 Java/Kotlin/Android 服务端或客户端项目的基础工具层——集合增强、本地缓存、事件解耦、字符串/IO 处理。
- **启发**：
  1. 先做"小而稳"的工具抽象再沉淀为标准（`Optional`/`Joiner` 先出现后被 JDK 吸收）。
  2. `@Beta` 显式契约是公共库版本治理的范本，值得所有长期维护的库学习。
  3. 不可变集合 / Optional 范式证明：好的抽象会被语言标准吸收，库的价值在于"先于标准定义正确抽象"。

## 六、社区口碑

- **广泛好评**：可靠性高、文档完整、Google 背书，是 Java 生态"必备依赖"；大量框架（Spring、Hadoop 生态等）内部依赖。
- **批评**：
  1. **jar 体积大**：全量 guava 约 2.7MB+，轻量场景引入成本高。
  2. **版本碎片**：Android 侧用旧 jar 易踩坑，升级需谨慎对齐。
  3. **破坏性变更阵痛**：移除 `@Beta` API 常引发上游升级痛。
  4. **被 JDK 逐步蚕食**：随着 JDK 吸收 Optional、`String.join`、varargs 等，部分 Guava API 显得冗余（尤其 Kotlin 项目可直接用语言特性替代）。

## 七、竞品对比

| 库 | 定位 | 与 Guava 关系 |
|----|------|--------------|
| Apache Commons (Lang/Collections/IO) | 更早的通用工具 | API 风格旧、碎片化；Guava 更现代统一 |
| JDK 标准库 | 语言内置 | Guava 补 JDK 短板，部分被 JDK 吸收 |
| Eclipse Collections | 高性能函数式集合 | 更小众，性能取向 |
| Vavr / Cactoos | 函数式不可变 | 范式不同，受众窄 |
| Kotlin stdlib | 语言级工具 | Kotlin 项目可替代部分 Guava |

## 八、核心研判

- **优势**：事实标准、超稳、Google 长期维护、设计前瞻（多个 API 被 JDK 吸收）、模块边界清晰。
- **风险**：体积/碎片、被 JDK 逐步蚕食导致"冗余感"、API 移除阵痛。
- **趋势**：随 JDK 吸收其基础 API，Guava 重心转向 JDK 未覆盖区（缓存、图论、丰富集合类型 Multimap/Table）；Android 侧仍是刚需。
- **启发**：基础设施库的生命周期管理（`@Beta` 契约 + 迁移窗口）是所有公共库应学的治理方法论；"先于标准定义正确抽象"是工具库的最高价值。

## 九、关键文件路径速查

- `guava/src/com/google/common/collect/` — 集合（不可变 + Multimap/Table/RangeSet）
- `guava/src/com/google/common/cache/` — 缓存（CacheBuilder / LoadingCache）
- `guava/src/com/google/common/eventbus/` — 事件总线
- `guava/src/com/google/common/graph/` — 图论（Graph / ValueGraph / Network）
- `guava/src/com/google/common/base/` — 基础（Optional / Preconditions / Joiner / Splitter）
- `pom.xml` / `overview.html` — Maven 构建与总文档
- `android/` / `guava-gwt/` — Android / GWT 兼容分发
