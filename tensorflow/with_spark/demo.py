#生成tfrecord
from pyspark.sql.types import *
path = "test1.tfrecord"
fields = [StructField("id", IntegerType()), StructField("IntegerCol", IntegerType()),
          StructField("LongCol", LongType()), StructField("FloatCol", FloatType()),
          StructField("DoubleCol", DoubleType()), StructField("VectorCol", ArrayType(DoubleType(), True)),
          StructField("StringCol", StringType())]
schema = StructType(fields)
test_rows = [[11, 1, 23, 10.0, 14.0, [1.0, 2.0], "r1"], [21, 2, 24, 12.0, 15.0, [2.0, 2.0], "r2"]]
rdd = spark.sparkContext.parallelize(test_rows)
df = spark.createDataFrame(rdd, schema)
df.repartition(10).write.format("tfrecords").option("recordType", "Example").save(path)
df = spark.read.format("tfrecords").option("recordType", "Example").load(path)
df.show()



#tensorflow 读取tfrecord
import tensorflow as tf
tf.enable_eager_execution()
raw_dataset = tf.data.TFRecordDataset(['hdfs://cluster/user/wangrc/test1.tfrecord/part-r-00000'])
for raw_record in raw_dataset.take(2):
    print(repr(raw_record))


import tensorflow as tf
record_iterator = tf.python_io.tf_record_iterator(path='hdfs://cluster/user/wangrc/test1.tfrecord/part-r-00000')
for string_record in record_iterator:
    example = tf.train.Example()
    example.ParseFromString(string_record)
    print(example)