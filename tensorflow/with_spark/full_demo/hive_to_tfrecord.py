# Auther        : wangrc
# Date          : 2019-05-07
# Description   : NEED: spark-tensorflow-connector_2.11-1.11.0.jar
# Refers        : None
# Returns       : tfrecord of mnist dataset in HDFS
import argparse
from pyspark.sql import SparkSession


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default='mlg')
    args = parser.parse_args()
    return args


def main(args):
    ss = SparkSession.builder \
        .appName("hive_to_tfrecord") \
        .enableHiveSupport() \
        .getOrCreate()
    ss.sql(f'use {args.db}')

    train_df=ss.sql('select * from g_mnist_train')
    test_df=ss.sql('select * from g_mnist_test')
    tr_path='/user/wangrc/mnist.tfrecord/train'
    te_path='/user/wangrc/mnist.tfrecord/test'
    train_df.repartition(10).write.format("tfrecords").mode("overwrite").option("recordType", "Example").save(tr_path)
    test_df.repartition(10).write.format("tfrecords").mode("overwrite").option("recordType", "Example").save(te_path)

if __name__ == '__main__':
    args = parse_args()
    main(args)