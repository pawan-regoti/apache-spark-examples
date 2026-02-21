import os
from pyspark.sql import SparkSession

def get_weather_data(spark: SparkSession, file_path: str):
    print(f"Reading weather data from: {file_path}")
    return spark.read.csv(file_path, header=True, inferSchema=True)

if __name__ == "__main__":
    weather_file_path = os.path.join(os.path.dirname(__file__), "data", "seattle-weather.csv")
    print(f"Reading weather data from: {weather_file_path}")

    spark = SparkSession.builder.appName("WeatherData").getOrCreate()
    weather_data = get_weather_data(spark, weather_file_path)

    """
    Spark also supports pulling data sets into a cluster-wide in-memory cache.
    This is very useful when data is accessed repeatedly,
    such as when querying a small “hot” dataset or when running an iterative algorithm like PageRank.
    """
    weather_data_cache = weather_data.cache()

    print("First 5 rows of the weather data:")
    weather_data.show(5)
    weather_data_cache.show(5)

    print("Total number of records in the weather data:")
    print(weather_data.count())
    print(weather_data_cache.count())

    print("Schema of the weather data:")
    weather_data.printSchema()
    weather_data_cache.printSchema()

    print("Summary statistics of the weather data:")
    weather_data.describe().show()
    weather_data_cache.describe().show()

    print("Average max temperature:")
    weather_data.groupBy().avg("temp_max").show()
    weather_data_cache.groupBy().avg("temp_max").show()

    weather_data_cache.unpersist()
    print("Cache cleared.")

    spark.stop()
