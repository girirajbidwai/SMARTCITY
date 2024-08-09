from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType
from pyspark.sql.functions import from_json, col

def main():
    spark = SparkSession.builder.appName("SmartCityStreaming")\
    .config("spark.jars.packages", 
        "org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.1,"
        "org.apache.hadoop:hadoop-aws:3.3.1,"
        "com.amazonaws:aws-java-sdk:1.11.469")\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config("spark.hadoop.fs.s3a.access.key", "<YOUR_AWS_ACCESS_KEY>")\
    .config("spark.hadoop.fs.s3a.secret.key", "<YOUR_AWS_SECRET_KEY>")\
    .config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')\
    .getOrCreate()

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel('WARN')

    # Vehicle Schema
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True),
    ])

    # GPS Schema
    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicleType", StringType(), True),
    ])

    # Traffic Schema
    trafficSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("cameraId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("snapshot", StringType(), True),
    ])

    # Weather Schema
    weatherSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("airQualityIndex", DoubleType(), True),
    ])

    # Emergency Schema
    emergencySchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("incidentId", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True),
    ])

    # Read data from Kafka topics
    vehicleStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .option("subscribe", "vehicle_data")\
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(from_json("value", vehicleSchema).alias("data"))\
        .select("data.*")

    gpsStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .option("subscribe", "gps_data")\
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(from_json("value", gpsSchema).alias("data"))\
        .select("data.*")

    trafficStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .option("subscribe", "traffic_data")\
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(from_json("value", trafficSchema).alias("data"))\
        .select("data.*")

    weatherStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .option("subscribe", "weather_data")\
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(from_json("value", weatherSchema).alias("data"))\
        .select("data.*")

    emergencyStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .option("subscribe", "emergency_data")\
        .load()\
        .selectExpr("CAST(value AS STRING) as value")\
        .select(from_json("value", emergencySchema).alias("data"))\
        .select("data.*")

    # Write streams to console for debugging
    vehicleStream.writeStream.outputMode("append").format("console").start()
    gpsStream.writeStream.outputMode("append").format("console").start()
    trafficStream.writeStream.outputMode("append").format("console").start()
    weatherStream.writeStream.outputMode("append").format("console").start()
    emergencyStream.writeStream.outputMode("append").format("console").start()

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
