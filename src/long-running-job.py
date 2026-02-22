import os
from pyspark.sql import SparkSession

if __name__ == "__main__":
    weather_file_path = os.path.join(os.path.dirname(__file__), "data", "seattle-weather.csv")
    print(f"Reading weather data from: {weather_file_path}")

    spark = SparkSession.builder.appName("WeatherData").getOrCreate()
    weather_data = spark.read.csv(weather_file_path, header=True, inferSchema=True)

    print("First 5 rows of the weather data:")
    weather_data.show(5)

    print("Total number of records in the weather data:")
    print(weather_data.count())

    print("Schema of the weather data:")
    weather_data.printSchema()

    print("Summary statistics of the weather data:")
    weather_data.describe().show()

    print("Average max temperature:")
    weather_data.groupBy().avg("temp_max").show()

    sleep(300)  # Simulate a long-running job by sleeping for 300 seconds

    spark.stop()
