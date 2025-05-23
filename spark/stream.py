from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StringType, StructType, StructField, IntegerType

# Initialize Spark
spark = SparkSession.builder \
    .appName("Kafka JSON Stream") \
    .getOrCreate()

# Define schema for the JSON value (adjust according to your actual payload)
json_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("content", StringType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("post_id", IntegerType(), True),
    StructField("created_at", StringType(), True),  # timestamps often come as strings
])

# Read from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "dbserver1.public.comments") \
    .option("startingOffsets", "earliest") \
    .load()

# Extract JSON from value field
json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), json_schema).alias("data")) \
    .select("data.*")

query = json_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()