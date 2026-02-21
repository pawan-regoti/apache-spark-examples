# Resource Utilization

## Cores

### How to calculate number of cores required

In Spark, the core requirement is primarily driven by the number of concurrent tasks you want to run (i.e., the level of parallelism).

**Key ideas:**

- Each Spark *task* runs in **one core**.
- At any moment, the **maximum number of parallel tasks** per executor = `number of cores per executor`.
- Total cluster parallelism = **sum of cores across all executors**.

**Typical approach:**

1. **Decide the desired parallelism** (often 2–4 × total cores in the cluster, but at minimum equal to the number of HDFS blocks / partitions).
2. **Set the number of partitions** ≈ desired parallelism (or slightly higher).
3. **Number of cores to request** (for a job) should be enough to:
   - Keep all partitions actively processed,
   - Without overwhelming the cluster.

If:

- `P` = number of partitions  
- `C` = total cores allocated to the application  

Then, at any time, Spark can run up to `C` tasks in parallel, and it will process the `P` partitions in `ceil(P / C)` waves.

---

## Memory

### How to calculate amount of memory required

Memory requirement is driven by:

- Size of the dataset,
- Size of each partition,
- Overhead for deserialization, shuffle, caching, and data skew.

Spark tasks **do not** hold the entire dataset in memory at once; they usually process one partition at a time. So the **per-executor** memory must be sufficient for:

- At least 1–2 partitions in memory (input + intermediate),
- Overhead for objects / metadata / shuffle.

**Rule-of-thumb approach:**

1. **Choose partition size:** Typically 128 MB or 256 MB per partition.
2. **Estimate memory per task:**
   - Raw partition size × overhead factor (e.g., 2–3× to account for object expansion, shuffle, etc.).
3. **Estimate maximum concurrent tasks per executor** (usually = number of cores per executor).
4. **Memory per executor** should be at least:

   ```text
   memory_per_executor ≈ concurrent_tasks_per_executor × memory_per_task
   ```

5. Add an additional safety margin (20–30%).

---

## Example

If a dataset is of size **5 GB**

- Typical size of a partition = **128 MB**
- While 128 MB (matching the default HDFS block size) is often cited as the default, keeping partitions within the 100–200 MB range allows for optimized performance and helps avoid common memory issues (OOM) in executors.

### Number of Partitions

Total data size = 5 GB (`5 × 1024 MB = 5120 MB`)

```plaintext
number_of_partitions = total_data_size_MB / partition_size_MB
                     = 5120 MB / 128 MB
                     = 40 partitions
```

**Number of Partitions:** **40**

---

### Number of Cores

This depends on your cluster and SLA, but a reasonable approach is:

- Keep at least as many partitions as total cores (to fully utilize them),
- Often `number_of_partitions ≥ 2 × total_cores` so that there are always tasks waiting to run.

If you decide you want to process the data in about **2 waves**, then:

```text
waves = 2
number_of_cores ≈ number_of_partitions / waves = 40 / 2 = 20 cores
```

So, examples:

- If you can allocate **20 cores**:
  - 40 partitions / 20 cores = 2 waves of tasks.
- If you can allocate **10 cores**:
  - 40 partitions / 10 cores = 4 waves of tasks.

You can write it generically:

- **Number of Cores (for ~2 waves):** ≈ `40 / 2 = 20 cores`

(Adjust this based on your actual cluster capacity and cost constraints.)

---

### Amount of Memory

Assume:

- Partition size: 128 MB
- Overhead factor (deserialization, shuffle, etc.): ~3×
- Cores per executor: e.g., 5 cores per executor (any more can cause degradation in throughput and performance)
- So, concurrent tasks per executor = 5

**Per-task memory need:**

```text
memory_per_task ≈ 128 MB × 3 = 384 MB
```

**Per-executor memory:**

```text
memory_per_executor ≈ concurrent_tasks_per_executor × memory_per_task
                     ≈ 5 × 384 MB
                     ≈ 1920 MB ≈ 2 GB
```

Add ~30% safety margin:

```text
2 GB × 1.3 ≈ 2.6 GB  ⇒ round to 3 GB per executor
```

If total required cores = 20 and cores per executor = 5:

- Number of executors = `20 / 5 = 4`
- Total executor memory:

```text
total_executor_memory ≈ 4 executors × 3 GB
                      ≈ 12 GB
```

---

## Amount of Resources Required

- Cores per executor: **5**
- Executors: **4**
- Memory per executor: **~3 GB**
- **Total executor memory:** **~12 GB** for the 5 GB dataset
