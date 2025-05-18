from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, TimestampType, MapType

# ------------------ Configuration ------------------

KAFKA_BROKER = "kafka:9092"
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "admin123"
TOPICS = "Posts,dbserver1.public.posts,dbserver1.public.users,dbserver1.public.comments"

# ------------------ Spark Setup ------------------

spark = SparkSession.builder \
    .appName("DebeziumToMinIO") \
    .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ------------------ Kafka Stream ------------------

df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", TOPICS) \
    .option("startingOffsets", "latest") \
    .load()

# Convert Kafka `value` from bytes to string
df_value = df_raw.selectExpr("CAST(topic AS STRING)", "CAST(value AS STRING)")

# ------------------ JSON Parsing (Debezium format) ------------------

# Simplified schema; customize as needed
schema = StructType() \
    .add("payload", StructType()
         .add("op", StringType())  # operation: c (create), u (update), d (delete)
         .add("after", MapType(StringType(), StringType()))
         .add("before", MapType(StringType(), StringType()))
         .add("ts_ms", StringType())  # timestamp in ms
         )

df_parsed = df_value.withColumn("json", from_json(col("value"), schema)) \
    .select("topic", "json.payload.*")

# Convert timestamp to readable format if needed
from pyspark.sql.functions import from_unixtime
df_parsed = df_parsed.withColumn("ts", from_unixtime(col("ts_ms") / 1000).cast(TimestampType()))

# ------------------ Write to MinIO per topic ------------------

def write_topic_to_minio(topic_name):
    df_topic = df_parsed.filter(col("topic") == topic_name)
    return df_topic.writeStream \
        .format("parquet") \
        .option("checkpointLocation", f"/tmp/checkpoints/{topic_name}") \
        .option("path", f"s3a://wpbd-output/{topic_name}") \
        .outputMode("append") \
        .start()

# Create one streaming writer per topic
queries = [
    write_topic_to_minio("Posts"),
    write_topic_to_minio("dbserver1.public.posts"),
    write_topic_to_minio("dbserver1.public.users"),
    write_topic_to_minio("dbserver1.public.comments")
]

# ------------------ Await all queries ------------------

for query in queries:
    query.awaitTermination()