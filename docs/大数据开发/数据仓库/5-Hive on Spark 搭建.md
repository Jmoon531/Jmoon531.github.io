---

Created at: 2021-10-24
Last updated at: 2022-12-16


---

# 5-Hive on Spark 搭建


**Hive on Spark 搭建**
Hive引擎包括：默认MR、tez、spark
Hive on Spark：Hive既作为存储元数据又负责SQL的解析优化，语法是HQL语法，执行引擎为Spark，Spark负责采用RDD执行。
Spark on Hive：Hive只作为存储元数据，Spark负责SQL解析优化，语法是Spark SQL语法，Spark负责采用RDD执行。

前提是把Hive搭建好，然后按照如下步骤将Hive默认的MR引擎换成Spark：
1.解压spark并更名
```
tar -zxvf spark-3.0.0-bin-hadoop3.2.tgz -C /opt/module/
```
```
mv spark-3.0.0-bin-hadoop3.2/ spark-3.0.0
```
2.配置SPARK\_HOME
```
sudo vim /etc/profile.d/my_env.sh
```
```
# SPARK_HOME
export SPARK_HOME=/opt/module/spark-3.0.0
export PATH=$PATH:$SPARK_HOME/bin
```
```
source /etc/profile.d/my_env.sh
```
3.在hive中创建spark配置文件
```
vim /opt/module/hive-3.1.2/conf/spark-defaults.conf
```
```
spark.master                 yarn
spark.yarn.queue             offline
spark.eventLog.enabled       true
spark.eventLog.dir           hdfs://hadoop102:8020/spark/spark-history
spark.executor.memory        1g
spark.driver.memory          1g
```
4.在HDFS创建路径，用于存储历史日志
```
hadoop fs -mkdir -p /spark/spark-history
```
5.向HDFS上传Spark纯净版jar包
说明1：由于Spark3.0.0非纯净版默认支持的是hive2.3.7版本，直接使用会和安装的Hive3.1.2出现兼容性问题。所以采用Spark纯净版jar包，不包含hadoop和hive相关依赖，避免冲突。
说明2：Hive任务最终由Spark来执行，Spark任务资源分配由Yarn来调度，该任务有可能被分配到集群的任何一个节点。所以需要将Spark的依赖上传到HDFS集群路径，这样集群中任何一个节点都能获取到。
5.1 解压spark-3.0.0-bin-without-hadoop.tgz
```
tar -zxvf /opt/software/spark/spark-3.0.0-bin-without-hadoop.tgz -C /opt/software/spark/
```
5.2 在HDFS创建路径
```
hadoop fs -mkdir -p /spark/spark-jars
```
5.3上传spark的jar包
```
hadoop fs -put spark-3.0.0-bin-without-hadoop/jars/* /spark/spark-jars
```
6.修改hive-site.xml文件
```
vim /opt/module/hive-3.1.2/conf/hive-site.xml
```
```
<!--Spark依赖位置（注意：端口号8020必须和namenode的端口号一致）-->
<property>
    <name>spark.yarn.jars</name>
    <value>hdfs://hadoop102:8020/spark/spark-jars/*</value>
</property>
<!--Hive执行引擎-->
<property>
    <name>hive.execution.engine</name>
    <value>spark</value>
</property>
```
7.测试
```
bin/hive
```
```
create table student(id int, name string);
```
```
insert into table student values(1,'abc');
```

Hive启动脚本：
```
#!/bin/bash

case $1 in
"start"){
    echo " --------启动 MySQL-------"
    sudo systemctl start mysqld
    echo " --------启动 hiveserver2-------"
    nohup hive --service hiveserver2 >/dev/null 2>&1 &
};;
"stop"){
    echo " --------关闭 MySQL-------"
    sudo systemctl stop mysqld
    echo " --------关闭 hiveserver2-------"
    ps -ef | grep hiveserver2 | grep -v grep | awk '{print $2}' | xargs -n1 kill -9
};;
esac
```

