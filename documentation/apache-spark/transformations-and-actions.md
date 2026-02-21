# Transformations and Actions

Apache Spark functions are broadly categorised into two things, **Transformations** and **Actions**.

## Transformations

**Definition:**  
Transformations are operations on an existing RDD/DataFrame/Dataset that define a new logical dataset from the existing one.  
They are **lazily evaluated** – i.e. Spark does not execute them immediately, but instead builds up a logical plan (lineage).  
The plan is only executed when an **action** is called.

Examples of common transformations:

* `map`, `flatMap`
* `filter`, `where`
* `select`, `withColumn`
* `groupBy`, `groupByKey`
* `join`
* `repartition`, `coalesce`
* `distinct`
* `union`, `intersect`, `subtract`

Spark transformations are typically divided into **narrow** and **wide** transformations, based on how data is shuffled between partitions.

### Narrow Transformations

**Definition:**  
A narrow transformation is one where each output partition depends on **data from a single input partition** (or a small, fixed set of partitions with no shuffle).  
There is **no data shuffle** across the cluster.

**Characteristics:**

* No shuffle stage introduced
* One-to-one or few-to-one partition dependency
* Can be pipelined in the same stage

**Common examples:**

* `map` – apply a function to each element.
* `flatMap` – similar to `map` but can return 0 or more elements for each input.
* `filter` / `where` – keep only rows matching a predicate.
* `mapPartitions` – transform data within a partition.
* `sample` (without replacement, no shuffle).
* Simple `withColumn` / `select` that don’t require aggregations or joins.
* `coalesce` (when reducing partitions without shuffle).

**Example (DataFrame API):**

```scala
val df2 = df
  .filter($"country" === "DK")  // narrow
  .withColumn("amount_eur", $"amount" * 7.45) // narrow
```

All of the above can be executed in a single stage without shuffle.

### Wide Transformations

**Definition:**  
A wide transformation is one where the output partitions depend on **data from multiple input partitions**.  
This requires a **shuffle** – Spark redistributes data across the cluster (e.g. by key or partitioning logic).

**Characteristics:**

* Introduces a shuffle stage boundary
* Many-to-many dependency between partitions
* More expensive: involves network I/O, disk I/O, and often sorting
* Strong impact on performance and scalability

**Common examples:**

* `groupBy`, `groupByKey`, `agg` (by key/column)
* `reduceByKey`, `aggregateByKey`, `foldByKey`
* `join` (e.g. inner, left, right, full joins)
* `distinct`
* `repartition` (when increasing partitions / full shuffle). It is used to balance skewed data, increase parallelism, or optimize output file sizes
* `sortBy`, `orderBy` (global or partition-level with shuffle)
* `cogroup`, `byKey` type operations

**Example (DataFrame API):**

```scala
val revenueByCountry = df
  .groupBy($"country")    // wide (shuffle)
  .agg(sum($"amount").as("total_amount"))
```

The `groupBy` triggers a shuffle because all rows with the same `country` key must be brought together, potentially from many different initial partitions.

## Actions

**Definition:**  
Actions are operations that **trigger the execution** of the transformations that have been defined on an RDD/DataFrame/Dataset and **return a result** to the driver or **write data** to external storage.

When you call an action, Spark:

1. Analyzes the logical plan (all previous transformations).
2. Optimizes it (Catalyst optimizer for DataFrames/Datasets).
3. Breaks it into stages separated by shuffles.
4. Schedules tasks to executors and executes them.

Actions are **eager** – they cause Spark to actually run the computations.

**Common examples (RDD API):**

* `collect()` – return all elements to the driver.
* `count()` – return the number of elements.
* `take(n)` – return the first `n` elements.
* `first()` – return the first element.
* `reduce(func)` – aggregate elements using a function.
* `foreach(func)` – run a function for each element (on the executors).
* `saveAsTextFile(path)` – write data to storage.

**Common examples (DataFrame/Dataset API):**

* `show()` – display rows in the console (triggers a job).
* `collect()` / `collectAsList()` – bring all data to driver.
* `count()` – count rows.
* `head()`, `first()`, `take(n)` – retrieve a small number of rows.
* `foreach()`, `foreachPartition()` – apply a function (side effects).
* `write` / `writeStream` operations, e.g.:
  * `df.write.parquet(path)`
  * `df.write.mode("overwrite").save(path)`
  * `df.write.jdbc(...)`
  * `df.write.saveAsTable("table_name")`

**Example (DataFrame API):**

```scala
val highValueOrders = df
  .filter($"amount" > 1000)  // transformation
  .select($"order_id", $"amount") // transformation
// Action: triggers the actual job
highValueOrders.show(20)
```

Here:

* `filter` and `select` are transformations (lazy).
* `show` is an action that causes Spark to run the query and materialize results.
