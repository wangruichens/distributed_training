from tensorflow.python.keras.datasets import mnist
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.ml.linalg import Vectors
import numpy as np

def gen_data():
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    #NHWC is tensorflow default
    x_train=x_train.reshape(x_train.shape[0],28*28)
    x_test=x_test.reshape(x_test.shape[0],28*28)
    y_train=y_train.reshape(y_train.shape[0],1)
    y_test=y_test.reshape(y_test.shape[0],1)
    train_data = np.concatenate((y_train, x_train), axis=1)
    test_data = np.concatenate((y_test, x_test), axis=1)
    print(train_data.shape)
    return train_data,test_data

def df_to_hive(spark, df, table_name):
    tmp_table_name = "tmp_" + table_name
    df.registerTempTable(tmp_table_name)
    delete_sql = "drop table if exists " + table_name
    create_sql = "create table " + table_name + " as select * from " + tmp_table_name
    spark.sql(delete_sql)
    spark.sql(create_sql)

def data_to_hive(data,ss,hive_name):
    fields = [StructField("label", IntegerType()),StructField("features", ArrayType(IntegerType(), False))]
    schema = StructType(fields)
    train_df = list(map(lambda x: (int(x[0]),x[1:].tolist()), data))
    rdd = ss.sparkContext.parallelize(train_df,numSlices=10)
    df = ss.createDataFrame(rdd, schema)
    df_to_hive(ss,df,hive_name)

def main():
    ss = SparkSession.builder \
            .appName("mnist_to_hive") \
            .enableHiveSupport() \
            .getOrCreate()
    ss.sql(f'use mlg')
    train,test=gen_data()
    data_to_hive(train,ss,'g_mnist_train')
    data_to_hive(test,ss,'g_mnist_test')


if __name__ == '__main__':
    main()