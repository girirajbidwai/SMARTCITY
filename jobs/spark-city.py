from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType
from pyspark.sql.functions import from_json, col
from pyspark.sql import DataFrame

def main():
    spark = SparkSession.builder.appName("SmartCityStreaming")\
    .config("spark.jars.packages", 
        "org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.1,"
        "org.apache.hadoop:hadoop-aws:3.3.1,"
        "com.amazonaws:aws-java-sdk:1.11.469")\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config("spark.hadoop.fs.s3a.access.key", "")\
    .config("spark.hadoop.fs.s3a.secret.key", "")\
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
        StructField("FuelType", StringType(), True),
    ])

    # GPS Schema
    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("VehicleType", StringType(), True),
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
        StructField("weatherCondition", IntegerType(), True),
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

    def streamWriter(input: DataFrame, checkpointFolder: str, output: str):
        return (input.writeStream
                .format('parquet')
                .option('checkpointLocation', checkpointFolder)
                .option('path', output)
                .outputMode('append')
                .start()
        )

    def read_kafka_topic(topic: str, schema):
        return (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', 'localhost:29092')
                .option('subscribe', topic)
                .option('startingOffsets', 'earliest')
                .load()
                .selectExpr('CAST(value AS STRING)')
                .select(from_json(col('value'), schema).alias('data'))
                .select('data.*')
                .withWatermark('timestamp', '2 minutes')
        )

    vehicleDF = read_kafka_topic('vehicle_data', vehicleSchema).alias('vehicle')
    gpsDF = read_kafka_topic('gps_data', gpsSchema).alias('gps')
    trafficDF = read_kafka_topic('traffic_data', trafficSchema).alias('traffic')
    weatherDF = read_kafka_topic('weather_data', weatherSchema).alias('weather')
    emergencyDF = read_kafka_topic('emergency_data', emergencySchema).alias('emergency')

    query1 = streamWriter(vehicleDF, 's3a://spark-streamin-data/checkpoints/vehicle_data', 's3a://spark-streamin-data/vehicle_data')
    query2 = streamWriter(gpsDF, 's3a://spark-streamin-data/checkpoints/gps_data', 's3a://spark-streamin-data/gps_data')
    query3 = streamWriter(trafficDF, 's3a://spark-streamin-data/checkpoints/traffic_data', 's3a://spark-streamin-data/traffic_data')
    query4 = streamWriter(weatherDF, 's3a://spark-streamin-data/checkpoints/weather_data', 's3a://spark-streamin-data/weather_data')
    query5 = streamWriter(emergencyDF, 's3a://spark-streamin-data/checkpoints/emergency_data', 's3a://spark-streamin-data/emergency_data')

    query5.awaitTermination()   

if __name__ == "__main__":
    main()
