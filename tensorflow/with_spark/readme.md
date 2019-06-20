* 介绍如何根据利用spark生成tfrecord 
* 从tensorflow读取hdfs上的tfrecord文件 
* ooize 调用 tensorflow 训练
![image](https://github.com/wangruichens/samples/blob/master/distribute/tf/spark_tfrecord/done.png)

# 1. 利用spark生成tfrecord
参考：
https://github.com/tensorflow/ecosystem/tree/master/spark/spark-tensorflow-connector

```sh
# Build TensorFlow Hadoop
cd ../../hadoop
mvn versions:set -DnewVersion=1.13.1
mvn clean install

# Build Spark TensorFlow connector
cd ../spark/spark-tensorflow-connector
mvn versions:set -DnewVersion=1.13.1
mvn clean install

mvn clean install -Dmaven.test.skip=true -DnewVersion=1.13.0 -Dspark.version=2.3.0
```

测试用例可能有一些跑不通。 可以跳过： mvn clean install -Dmaven.test.skip=true

将打好的jar包附在命令后面，测试是否成功 pyspark --jars target/spark-tensorflow-connector_2.11-1.11.0.jar
最后将jar包拷到目标环境上就可以了。
/usr/hdp/2.6.5.0-292/spark2/jars/spark-tensorflow-connector_2.11-1.11.0.jar

# 2. 从tensorflow读取hdfs上的tfrecord文件
参考TensorFlow on Hadoop：
https://github.com/tensorflow/examples/blob/master/community/en/docs/deploy/hadoop.md

问题一： libhdfs.so 没有的话，需要下载hadoop源码进行编译。 cmake -> make
/hadoop-2.7.1-src/hadoop-hdfs-project/hadoop-hdfs/src
成功之后，会在目录下生成Makefile文件，接下来就可以执行make编译生成libhdfs.so和libhdfs.a了 (target目录)。

生成之后拷到server目录下。
```sh
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JAVA_HOME}/jre/lib/amd64/server
```

问题二： 报错loadFileSystems error:
(unable to get stack trace for java.lang.NoClassDefFoundError exception: ExceptionUtils::getStackTrace error.)

原因是CLASSPATH 没有设置。 需要包含hadoop相关的所有jar包。

```sh
export HADOOP_HOME=/home/wangrc/hadoop-2.7.3
export CLASSPATH=$(${HADOOP_HOME}/bin/hadoop classpath --glob)
```
然后 tensorflow 就能够从集群的tfrecord上读取数据了

* 一个坑：

写在shell脚本里的 $(${HADOOP_HOME}/bin/hadoop classpath --glob)。
glob命令在terminal交互的情况下是可以生效的，但是写在shell脚本里是不生效的。在测试环境中，echo $CLASSPATH 仍然为空。

解决：权限问题，yarn服务不能访问之前设置的hadoop home, 也就是/home/wangrc目录

* 线上环境 第一个坑

tensorflow现在默认安装 gpu版本。 如果机器上没有nvidia显卡，就会报错libcuda.so.1找不到。
需要conda重新安装 ，指定cpu版本
conda search tensorflow

升级tensorflow, 可以指定 cpu 或者 gpu 版本
```sh
conda install 'tensorflow=1.13*=mkl*'
conda install 'tensorflow=1.13*=gpu*'
```

* 线上环境 第二个坑

线上需要找到相关的class path，这个是通过线上spark2通过打包生成的。
在主节点的本地目录添加jar包以后，还需要重启spark2服务。
确认打包重新生成，新加入的jar包被添加进去。




-------------------------------------------------------------------------------------------
# 总结：
-------------------------------------------------------------------------------------------
### 添加jar包

/usr/hdp/2.6.5.0-292/spark2/jars/spark-tensorflow-connector_2.11-1.11.0.jar
需要export 三个变量 ：
```sh
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JAVA_HOME}/jre/lib/amd64/server
export HADOOP_HOME=/opt/data/hadoop-2.7.3
export CLASSPATH=$(${HADOOP_HOME}/bin/hadoop classpath --glob)
```

#### 1.放置jar包spark-tensorflow-connector_2.11-1.11.0.jar到找定目录位置
```sh 
本地位置: /usr/hdp/2.6.5.0-292/spark2/jars/spark-tensorflow-connector_2.11-1.11.0.jar
ooize集群： /user/oozie/share/lib/lib_20180712144755/spark2
```
#### 2.拷贝libhdfs.so，放在${JAVA_HOME}/jre/lib/amd64/server目录下， 在/etc/profile文件末尾添加环境变量

```sh
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JAVA_HOME}/jre/lib/amd64/server\
source /etc/profile
```

#### 3.将hadoop-2.7.3 文件夹放在/opt/data目录下，所有人可读可写
```sh
sudo chmod -R 777 /opt/data/hadoop-2.7.3
```

-------------------------------------------------------------------------------------------
sever A无需密码ssh sever B:
```sh
scp .ssh/id_rsa.pub wangrc@192.168.1.1:/home/wangrc/id_rsa.pub
cat id_rsa.pub >> .ssh/authorized_keys
sudo chmod 600 .ssh/authorized_keys
'''