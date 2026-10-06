# PySpark first setup test
# File: spark_test.py

from pyspark.sql import SparkSession


# Create a SparkSession
spark = (
    SparkSession.builder
    .appName("PySparkFirstTest")
    .master("local[2]")
    .getOrCreate()
)


print("Spark started successfully!")
print("Spark version:", spark.version)


# Stop Spark when finished
spark.stop()

print("Spark stopped successfully!")
