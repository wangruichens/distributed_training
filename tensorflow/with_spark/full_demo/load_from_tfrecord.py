# Auther        : wangrc
# Date          : 2019-05-07
# Description   :
# Refers        :
# Returns       :
import argparse
from pyspark.sql import SparkSession
import tensorflow as tf
tf.enable_eager_execution()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default='mlg')
    args = parser.parse_args()
    return args


def df_to_hive(spark, df, table_name):
    tmp_table_name = "tmp_" + table_name
    df.registerTempTable(tmp_table_name)
    delete_sql = "drop table if exists " + table_name
    create_sql = "create table " + table_name + " as select * from " + tmp_table_name
    spark.sql(delete_sql)
    spark.sql(create_sql)


def main(args):

    path = 'hdfs://cluster/user/mlg/test.tfrecord/part-r-00000'
    record_iterator = tf.python_io.tf_record_iterator(path=path)

    print ('################################ TEST BEGIN ################################')
    for string_record in record_iterator:
        example = tf.train.Example()
        example.ParseFromString(string_record)
        print(example)
    print ('################################ TEST END ################################')
    raw_dataset = tf.data.TFRecordDataset(path)

    def _parse_function(example_proto):
        feature_description = {
            'id': tf.FixedLenFeature([], tf.int64, default_value=0),
            'IntegerCol': tf.FixedLenFeature([], tf.int64, default_value=0),
            'LongCol': tf.FixedLenFeature([], tf.int64, default_value=0),
            'FloatCol': tf.FixedLenFeature([], tf.float32, default_value=0.0),
            'DoubleCol': tf.FixedLenFeature([], tf.float32, default_value=0.0),
            'VectorCol': tf.FixedLenFeature((2), tf.float32, default_value=[0, 0]),
            'StringCol': tf.FixedLenFeature([], tf.string, default_value=''),
        }
        return tf.parse_single_example(example_proto, feature_description)

    dataset = raw_dataset.map(_parse_function)
    print ('################################ TEST BEGIN ################################')
    for p in dataset.take(2):
        print(repr(p))
    print ('################################ TEST END ################################')

if __name__ == '__main__':
    args = parse_args()
    main(args)