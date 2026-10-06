# Task 203 - Define a manual StructType schema for customer_churn.csv
# File: CP5/spark_pipeline.py

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)


# Create SparkSession
spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("CustomerChurnDE5")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)


# Define the schema manually
schema = StructType([

    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),

    # IMPORTANT:
    # TotalCharges is initially StringType.
    # We will clean and convert it to DoubleType in Task 205.
    StructField("TotalCharges", StringType(), True),

    StructField("Churn", StringType(), True)
])


# Print the schema we created
schema.simpleString()


print("Manual schema created successfully!")

# Task 204 - Read customer_churn.csv using the manual schema and compare Spark schema with pandas
# File: CP5/spark_pipeline.py


# Path to the raw CSV file
csv_path = r"data\landing\customer_churn.csv"


# Read CSV using our manually defined schema
df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv(csv_path)
)


# Print Spark DataFrame schema
print("\n===== SPARK SCHEMA =====")
df.printSchema()


# Print number of rows
print("\n===== ROW COUNT =====")
print("Rows:", df.count())


# Show first 5 rows
print("\n===== FIRST 5 ROWS =====")
df.show(5, truncate=False)

# Task 205 - Replace blank TotalCharges values and cast TotalCharges to DoubleType
# File: CP5/spark_pipeline.py

from pyspark.sql import functions as F


# Replace blank/whitespace values with NULL
df = df.withColumn(
    "TotalCharges",
    F.regexp_replace(
        F.col("TotalCharges"),
        r"^\s*$",
        ""
    )
)


# Convert empty strings to NULL and cast to double
df = df.withColumn(
    "TotalCharges",
    F.when(
        F.trim(F.col("TotalCharges")) == "",
        None
    ).otherwise(
        F.col("TotalCharges").cast("double")
    )
)


print("\n===== TOTALCHARGES AFTER CLEANING =====")

df.select(
    "customerID",
    "TotalCharges"
).show(15)


print("\n===== TOTALCHARGES DATA TYPE =====")

df.printSchema()

# Task 206 - Encode Churn: Yes = 1, No = 0
# File: CP5/spark_pipeline.py


df = df.withColumn(
    "churn_encoded",
    F.when(
        F.col("Churn") == "Yes",
        1
    ).otherwise(0)
)


print("\n===== CHURN ENCODING =====")

df.select(
    "customerID",
    "Churn",
    "churn_encoded"
).show(10)

# Task 207 - Group by Contract and calculate customer count and churn rate
# File: CP5/spark_pipeline.py


contract_summary = (
    df
    .groupBy("Contract")
    .agg(
        F.count("*").alias("customer_count"),
        F.avg("churn_encoded").alias("churn_rate")
    )
)


print("\n===== CONTRACT CHURN SUMMARY =====")

contract_summary.show()

# Activity 208 - GroupBy InternetService and calculate average charges and churn rate
# File: spark_test.py

internet_summary = (
    df.groupBy("InternetService")
      .agg(
          F.avg("MonthlyCharges").alias("avg_monthly_charges"),
          F.avg("churn_encoded").alias("churn_rate")
      )
      .orderBy("InternetService")
)

print("\n===== INTERNET SERVICE SUMMARY =====")
internet_summary.show()

# Activity 209 - Cross-validate Spark churn rates against CP3 pandas results
# File: spark_test.py

# Expected churn rates from CP3 pandas analysis
cp3_contract_churn = {
    "Month-to-month": 0.4270967741935484,
    "One year": 0.11269517990495587,
    "Two year": 0.02831858407079646
}

# Collect Spark results into Python
spark_contract_results = {
    row["Contract"]: row["churn_rate"]
    for row in contract_summary.collect()
}

print("\n===== CP3 vs SPARK CROSS-VALIDATION =====")

for contract, expected_rate in cp3_contract_churn.items():

    spark_rate = spark_contract_results.get(contract)

    # Compare with a very small floating-point tolerance
    if abs(spark_rate - expected_rate) < 1e-10:
        print(
            f"PASS - {contract}: "
            f"CP3={expected_rate}, Spark={spark_rate}"
        )
    else:
        print(
            f"FAIL - {contract}: "
            f"CP3={expected_rate}, Spark={spark_rate}"
        )


# Activity 210 - Write contract summary as partitioned Parquet
# File: spark_test.py

output_path = "data/spark_output/contract_summary"

(
    contract_summary
    .write
    .mode("overwrite")
    .partitionBy("Contract")
    .parquet(output_path)
)

print("\n===== PARQUET WRITE =====")
print(f"Contract summary written to: {output_path}")

# Activity 211 - Read Parquet back and verify round-trip
# File: spark_pipeline.py

parquet_df = spark.read.parquet(output_path)

print("\n===== PARQUET ROUND-TRIP SCHEMA =====")
parquet_df.printSchema()

print("\n===== PARQUET ROUND-TRIP COUNT =====")
parquet_count = parquet_df.count()

print(f"Rows read from Parquet: {parquet_count}")

# Expected 3 rows because contract_summary has 3 contract types
assert parquet_count == 3, (
    f"FAIL - Expected 3 rows, but found {parquet_count}"
)

print("PASS - Parquet round-trip row count: 3")

print("\n===== PARQUET ROUND-TRIP DATA =====")
parquet_df.orderBy("Contract").show()

# Stop Spark
spark.stop()