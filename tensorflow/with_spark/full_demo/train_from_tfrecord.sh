#!/bin/bash
source /etc/profile
export HADOOP_HOME=/tmp/hadoop-2.7.3
export CLASSPATH=$(${HADOOP_HOME}/bin/hadoop classpath --glob)
spark-submit \
--master yarn \
--conf spark.network.timeout=600 \
--conf spark.sql.shuffle.partitions=10 \
--conf spark.executor.memoryOverhead=2048 \
--conf spark.driver.memoryOverhead=2048 \
--executor-cores 1 \
--num-executors 1 \
--executor-memory 4g \
--driver-memory 10g \
train_from_tfrecord.py


