# Spark Executor Container

Spark has 3 main memory regions in an executor container:

* **On-heap Memory**
* **Off-heap Memory**
* **Overhead Memory**

Each region is controlled by different Spark configuration parameters and is used for different purposes during execution.

![spark executor container memory allocation](./apache-spark.executor-container-memory.drawio.svg)
---

## On-heap Memory

### Definition

On-heap memory is the portion of the executor memory that is managed by the **JVM heap**. Objects here are subject to **JVM garbage collection (GC)**.

Configured by:

```text
spark.executor.memory
```

This is the main chunk of memory an executor gets, and within it Spark further divides memory into:

* Execution Memory
* Storage Memory
* User Memory
* Reserved Memory

Conceptually:

```text
spark.executor.memory
 ├─ Execution Memory       (~60% of unified memory region)
 ├─ Storage Memory         (~40% of unified memory region, but can borrow from Execution)
 ├─ User Memory            (fixed fraction for user code)
 └─ Reserved Memory        (fixed 300 MB per executor JVM)
```

> Note: Exact usable sizes are influenced by `spark.memory.fraction` and `spark.memory.storageFraction`.

If `spark.executor.memory = 10 GB`, then:

* Unified Memory (`spark.memory.fraction = 0.6`) = `10 × 0.6 = 6 GB`
* Storage Memory (`spark.memory.storageFraction = 0.4`) = `6 × 0.4 = 2.4 GB`
* Execution Memory = `6 − 2.4 = 3.6 GB`
* Reserved Memory = `300 MB`
* User Memory = `spark.executor.memory − Unified Memory − Reserved Memory`  
  = `10 GB − 6 GB − 300 MB = 2.7 GB`

---

### Execution Memory

#### Purpose

Execution memory is used for **runtime data structures** required during the execution of transformations and actions, such as:

* Joins
* Shuffles
* Sorting
* Aggregations (e.g., `groupBy`, `reduceByKey`)
* Window functions
* Any operation that builds in-memory hash tables, sort buffers, or aggregation buffers

Configured by:

```text
spark.memory.fraction = 0.6
```

* By default, Spark uses `spark.memory.fraction` (commonly `0.6`) of the heap (minus reserved memory) as the **Unified Memory Region** (for both Execution + Storage).
* Within this unified region, Storage typically gets up to `spark.memory.storageFraction` of that region (see below), while Execution can expand to use Storage space when needed.

#### Behavior

* If Execution memory is insufficient, Spark may spill intermediate data to disk (temporary shuffle/spill files).
* Excessive spilling often indicates that `spark.executor.memory` is too low or the data is heavily skewed.

---

### Storage Memory

#### Purpose

Storage memory is used to **cache and persist data** and to hold broadcast variables:

* Cached / persisted **RDDs**
* Cached / persisted **DataFrames / Datasets**
* **Broadcast variables** used for broadcast joins or shared lookup tables

Configured by:

```text
spark.memory.storageFraction = 0.4
```

* `spark.memory.storageFraction` applies within the **unified memory region** defined by `spark.memory.fraction`.
* Conceptually, if `spark.memory.fraction = 0.6` and `spark.memory.storageFraction = 0.4`, then:
  * 60% of heap (minus reserved) is unified memory.
  * Of that unified memory, up to 40% is reserved for Storage (but it is elastic).

#### Behavior

* Storage memory is **elastic**:
  * If Storage is not using its portion, Execution can borrow it.
  * If Execution needs more, it can evict cached blocks (using LRU) from Storage.
* When Storage is full and new data needs to be cached, Spark will **evict** older cached blocks.

---

### User Memory

#### Purpose

User memory is the part of the heap **outside** Spark’s unified memory manager, reserved for **application / user code**:

* User-defined variables and collections
* Data structures created in driver-defined functions
* Objects created inside `map` / `flatMap` / UDFs that are **not** tracked by Spark’s memory manager
* Libraries used within the executor (e.g., JSON parsers, custom aggregation buffers not registered with Spark)

This region is **not directly controlled** by `spark.memory.fraction` or `spark.memory.storageFraction`. It is simply the remainder of heap after:

* Reserved Memory
* Unified Memory (Execution + Storage)

#### Considerations

* Excessive use of User Memory can still cause **GC pressure** or **OutOfMemoryError**, even if Execution/Storage memory appears fine.
* Large collections or heavy UDF logic should be used carefully to avoid blowing up User Memory.

---

### Reserved Memory

#### Purpose

Reserved memory is a **fixed portion** of executor heap set aside for Spark internals, metadata, and safety margins. It is meant to avoid full-heap usage by user/engine data and reduce risk of OOMs.

Typical value:

```text
300 MB
```

This reserved memory is:

* Not available for Execution or Storage
* Not available for User Memory
* Used for Spark’s internal bookkeeping and overhead structures

---

## Off-heap Memory

### Definition

Off-heap memory is memory **outside the JVM heap**, allocated directly from the operating system (native memory). Spark can use this to reduce **GC overhead** and improve performance in memory-intensive workloads.

Configured by:

```text
spark.memory.offHeap.enabled = true
spark.memory.offHeap.size   = <size in bytes>
```

### Usage

* Used by Spark’s internal **off-heap storage** mechanisms (e.g., Tungsten, off-heap caches).
* Can store serialized data, shuffle buffers, and some execution data structures off the JVM heap.
* Helps:
  * Reduce GC pauses
  * Improve predictability when working with very large datasets

### Considerations

* Off-heap memory still counts against the **container / pod’s memory limit** at the OS level.
* Must be sized carefully in addition to `spark.executor.memory` to avoid container OOM-kills.
* Requires native memory support and may slightly complicate debugging memory issues.

---

## Overhead Memory

### Definition

Overhead memory (often called **container overhead**) covers **non-heap** and miscellaneous memory usage of the executor JVM process:

* JVM metadata & native overhead
* Thread stacks
* Internal/native libraries
* Off-heap allocations not included in `spark.memory.offHeap.size`
* Other native memory used by the process (e.g., compression libraries, network buffers)

Configured by:

```text
spark.executor.memoryOverhead
```

If not explicitly set, Spark uses:

```text
max(384 MB, 10% of spark.executor.memory)
```

### Examples

* If `spark.executor.memory = 4g`:
  * 10% of 4g = 0.4g (~409 MB)
  * overhead = `max(384 MB, 409 MB) = 409 MB`
* If `spark.executor.memory = 2g`:
  * 10% of 2g = 0.2g (~205 MB)
  * overhead = `max(384 MB, 205 MB) = 384 MB`

### Container / Pod Sizing

The **total memory per executor container** is approximately:

```text
Total Executor Container Memory ≈ spark.executor.memory
                                + spark.executor.memoryOverhead
                                + spark.memory.offHeap.size (if off-heap enabled)
```

If this total exceeds the container’s memory limit (e.g., in Kubernetes), the container can be killed due to OOM at the cluster manager level, even if JVM heap seems fine.
