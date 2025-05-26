import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
from dotenv import load_dotenv

load_dotenv()

# Initialize Spark with Delta support and S3 configs
spark = SparkSession.builder \
    .appName("Kafka JSON Stream to MinIO") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_USER")) \
    .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_PASSWORD")) \
    .config("spark.hadoop.fs.s3a.endpoint", f"http://minio:{os.getenv('MINIO_USER')}") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Define schema for JSON data
json_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("content", StringType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("post_id", IntegerType(), True),
    StructField("created_at", StringType(), True),
])

# Read from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "dbserver1.public.comments") \
    .option("startingOffsets", "earliest") \
    .load()

# Extract JSON from Kafka 'value'
json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), json_schema).alias("data")) \
    .select("data.*")

# Write to MinIO in Delta format
query = json_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "s3a://delta/checkpoints/comments") \
    .start("s3a://delta/comments")

query.awaitTermination()