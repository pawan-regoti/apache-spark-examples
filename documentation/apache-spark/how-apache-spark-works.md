# How Apache Spark Works

![How Apache Spark works](./how-apache-spark-works.drawio.svg)

Once the code is ready to be run, the following things happen:

1. **Syntax is validated and an Unresolved Logical Plan is created.**

2. **Analysis Phase** starts, which verifies the table schema and data types against Spark’s internal catalog and a *Logical Plan* is created. For example:
   1. `SELECT site_code, pool_code FROM geography`  
      will check if columns `site_code` and `pool_code` exist in the `geography` table.
   2. `df.where("from_date > to_date")`  
      will check if `from_date` and `to_date` columns are of the same type.

3. After that, the **Optimization Phase** starts, where various optimizations are applied, like:

   1. **Predicate Pushdown**  
      Predicate pushdown is an optimization technique where filter conditions (predicates) are pushed down to the data source level, meaning that the filtering is done as close to the data source as possible, rather than loading all the data into Spark and then filtering it. This reduces the amount of data that needs to be read and processed by Spark, improving performance.

      ```python
      # Applying a filter
      filtered_df = df.filter(df['total_stock'] > 1000)

      # With predicate pushdown,
      # Spark will only read the data that meets the condition from the Parquet file
      ```

   2. **Projection Pushdown**  
      Projection pushdown involves pushing down column projections to the data source. This means that only the columns required for a query are read from storage, rather than reading all columns and then selecting the necessary ones in memory. This reduces the amount of data read from disk and processed, thereby improving query performance.

      ```python
      # We need sound and damaged stock of particular container_types
      requested_stock_df = (
          stock_df.select("sound", "damaged")
                  .join(search_df, "container_type")
      )

      # With projection pushdown,
      # Spark will only get container_type from search_df 
      # since requested_stock_df doesn't ask for any other column from search_df
      ```

   3. **Partition Pruning**  
      Partition pruning is a technique used to optimize queries on partitioned tables. When data is partitioned (e.g., by date or region), queries that include filter conditions on the partition column can benefit from partition pruning. Partition pruning means Spark will scan only the relevant partitions of the data rather than the entire dataset.

      ```python
      # Sample data
      stock_df = spark.read.parquet("path/to/stock")

      # Suppose the data is partitioned by 'year' and 'month'
      # e.g., partitions: /year=2025/month=01/, /year=2025/month=02/, ...

      # Apply a filter on the partition column
      filtered_stock_df = stock_df.filter(
          (stock_df['year'] == 2025) & (stock_df['month'] == 1)
      )

      # With partition pruning,
      # Spark will only read data from the /year=2025/month=01/ partition
      ```

4. This leads to the creation of an **Optimized Logical Plan**.

5. Various **Physical Plans** are created based on the given Optimized Logical Plan.

6. A **Cost Model** evaluates each of the physical plans and selects the most reasonable physical plan.

7. Once a physical plan is selected, the **DAG Scheduler** kicks in, creates the corresponding RDD code, and the **job is executed**.
