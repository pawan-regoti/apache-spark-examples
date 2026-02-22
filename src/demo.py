import os
import time
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType
from pyspark.broadcast import Broadcast

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def timer(label: str):
    """Simple context manager to measure elapsed time."""
    class _Timer:
        def __enter__(self):
            self._start = time.time()
            return self
        def __exit__(self, *_):
            elapsed = time.time() - self._start
            print(f"[{label}] elapsed: {elapsed:.3f}s")
    return _Timer()


def wait_for_next_demo():
    print("\nWaiting for 120 seconds before next demo...")
    time.sleep(120) # wait a bit before next action to allow inspection in Spark UI


def run_demo():
    # ─────────────────────────────────────────────────────────────────────────────
    # 1. Session
    # ─────────────────────────────────────────────────────────────────────────────

    spark = (
        SparkSession.builder
        .appName("SparkDemo")
        .config("spark.sql.shuffle.partitions", "8")   # keep small for local demo
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    csv_path = os.path.join(data_dir, "seattle-weather.csv")

    # ─────────────────────────────────────────────────────────────────────────────
    # 2. Create a large dataset  (multiply the CSV ~20× by union)
    # ─────────────────────────────────────────────────────────────────────────────

    section("Create a large dataset")

    schema = StructType([
        StructField("date",          DateType(),   True),
        StructField("precipitation", DoubleType(), True),
        StructField("temp_max",      DoubleType(), True),
        StructField("temp_min",      DoubleType(), True),
        StructField("wind",          DoubleType(), True),
        StructField("weather",       StringType(), True),
    ])

    base = spark.read.csv(csv_path, header=True, schema=schema)

    # Replicate 20 times to produce a larger dataset (~28 k rows)
    large_df = base
    for _ in range(4):          # 2^4 = 16 doublings → ~23 k rows
        large_df = large_df.union(large_df)

    large_df = large_df.repartition(8)   # 8 balanced partitions
    spark.sparkContext.setJobDescription("[Dataset] Count total rows")
    print(f"Total rows  : {large_df.count():,}")
    print(f"Partitions  : {large_df.rdd.getNumPartitions()}")
    large_df.printSchema()

    # ─────────────────────────────────────────────────────────────────────────────
    # 3. Lazy evaluation  – nothing runs until an action is called
    # ─────────────────────────────────────────────────────────────────────────────

    section("Actions and Lazy Evaluation")

    # These are all transformations – no data is processed yet:
    filtered  = large_df.filter(F.col("weather") == "rain")
    projected = filtered.select("date", "precipitation", "temp_max")
    aggregated = projected.groupBy(F.month("date").alias("month")).agg(
        F.avg("precipitation").alias("avg_precip"),
        F.max("temp_max").alias("max_temp"),
    )

    print("Query plan (no execution yet):")
    aggregated.explain(mode="simple")

    # First ACTION – triggers the whole chain:
    print("Triggering action: show()")
    spark.sparkContext.setJobDescription("[Lazy Eval] Monthly rain aggregation")
    aggregated.orderBy("month").show()

    wait_for_next_demo()
    # ─────────────────────────────────────────────────────────────────────────────
    # 4. Narrow vs wide transformations
    # ─────────────────────────────────────────────────────────────────────────────

    section("Narrow Transformations  (no shuffle)")

    # map / filter / select  →  each partition processed independently
    narrow = (
        large_df
        .filter(F.col("temp_max") > 20)               # filter    – narrow
        .withColumn("temp_range",                       # withColumn – narrow
                    F.col("temp_max") - F.col("temp_min"))
        .select("date", "weather", "temp_range")       # select    – narrow
    )
    print("Narrow result sample:")
    spark.sparkContext.setJobDescription("[Narrow] Filter + withColumn + select")
    narrow.show(5)

    section("Wide Transformations  (require shuffle)")

    # groupBy / join / distinct  →  data must move across partitions (shuffle)
    wide = (
        large_df
        .groupBy("weather")                            # wide – triggers shuffle
        .agg(
            F.count("*").alias("count"),
            F.avg("temp_max").alias("avg_max_temp"),
            F.avg("precipitation").alias("avg_precip"),
        )
        .orderBy(F.desc("count"))                      # wide – global sort
    )
    print("Wide result (weather summary):")
    spark.sparkContext.setJobDescription("[Wide] GroupBy weather + orderBy (shuffle)")
    wide.show()

    wait_for_next_demo()

    # ─────────────────────────────────────────────────────────────────────────────
    # 5. Caching
    # ─────────────────────────────────────────────────────────────────────────────

    section("Caching")

    # Without cache – DataFrame recomputed from scratch each time
    spark.sparkContext.setJobDescription("[Cache] count without cache – pass 1")
    with timer("count WITHOUT cache (1st pass)"):
        _ = large_df.count()
    spark.sparkContext.setJobDescription("[Cache] count without cache – pass 2")
    with timer("count WITHOUT cache (2nd pass)"):
        _ = large_df.count()

    # With cache – first action materialises and stores; subsequent hits memory
    large_df.cache()
    spark.sparkContext.setJobDescription("[Cache] count WITH cache – materialise")
    with timer("count WITH cache (materialise)"):
        _ = large_df.count()
    spark.sparkContext.setJobDescription("[Cache] count WITH cache – cache hit")
    with timer("count WITH cache (cache hit)"):
        _ = large_df.count()

    print("Cached DataFrame storage level:", large_df.storageLevel)
    large_df.unpersist()

    wait_for_next_demo()

    # ─────────────────────────────────────────────────────────────────────────────
    # 6. Shuffle and partitioning
    # ─────────────────────────────────────────────────────────────────────────────

    section("Shuffle and Partitioning")

    print(f"Partitions before repartition : {large_df.rdd.getNumPartitions()}")

    # repartition  – full shuffle, round-robin or hash, can increase/decrease
    reshuffled = large_df.repartition(16)
    print(f"Partitions after repartition(16)   : {reshuffled.rdd.getNumPartitions()}")

    # coalesce    – avoids full shuffle, only decreases, merges existing partitions
    coalesced = reshuffled.coalesce(4)
    print(f"Partitions after coalesce(4)       : {coalesced.rdd.getNumPartitions()}")

    # Partition by a key column (useful before repeated joins/groupBys on same key)
    by_weather = large_df.repartition(8, "weather")
    print(f"Partitions after repartition by 'weather': {by_weather.rdd.getNumPartitions()}")

    # Show partition distribution
    print("Row counts per partition:")
    spark.sparkContext.setJobDescription("[Partitioning] Row distribution across partitions")
    by_weather.groupBy(F.spark_partition_id().alias("partition_id")).count().orderBy("partition_id").show()

    wait_for_next_demo()

    # ─────────────────────────────────────────────────────────────────────────────
    # 7. Broadcast variables
    # ─────────────────────────────────────────────────────────────────────────────

    section("Broadcast Variables")

    # A small lookup dict shipped once to every executor – avoids shuffle joins
    weather_labels: dict[str, str] = {
        "drizzle": "Light Rain",
        "rain":    "Heavy Rain",
        "sun":     "Sunny",
        "snow":    "Snow",
        "fog":     "Foggy",
    }

    broadcast_labels: Broadcast = spark.sparkContext.broadcast(weather_labels)

    # UDF that reads from the broadcast variable (no network hop per row)
    @F.udf(StringType())
    def map_label(weather_type: str) -> str:
        return broadcast_labels.value.get(weather_type, "Unknown")

    labelled = large_df.withColumn("weather_label", map_label(F.col("weather")))
    print("Broadcast join result (sample):")
    spark.sparkContext.setJobDescription("[Broadcast] UDF lookup via broadcast variable")
    labelled.select("date", "weather", "weather_label").show(8)

    wait_for_next_demo()

    # ─────────────────────────────────────────────────────────────────────────────
    # 8. Accumulators
    # ─────────────────────────────────────────────────────────────────────────────

    section("Accumulators")

    # Accumulators are write-only from executors; driver reads the total
    rainy_days   = spark.sparkContext.accumulator(0)
    extreme_heat = spark.sparkContext.accumulator(0)
    missing_data = spark.sparkContext.accumulator(0)

    def audit_row(row):
        if row["weather"] == "rain":
            rainy_days.add(1)
        if row["temp_max"] is not None and row["temp_max"] > 30:
            extreme_heat.add(1)
        if row["precipitation"] is None:
            missing_data.add(1)

    # foreach is an action – triggers execution across all executors
    spark.sparkContext.setJobDescription("[Accumulator] foreach audit – rainy/heat/missing counts")
    large_df.foreach(audit_row)

    print(f"Rainy day records        : {rainy_days.value:,}")
    print(f"Extreme heat (>30°C) rows: {extreme_heat.value:,}")
    print(f"Missing precipitation rows: {missing_data.value:,}")

    wait_for_next_demo()

    # ─────────────────────────────────────────────────────────────────────────────
    # Done
    # ─────────────────────────────────────────────────────────────────────────────

    section("All demos complete")
    spark.stop()


if __name__ == "__main__":
    run_demo()
