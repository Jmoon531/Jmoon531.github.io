---

Created at: 2021-09-07
Last updated at: 2022-06-25


---

# 2-Kafka安装


1.官网下载Kafka
2.解压 tar -zxvf /opt/software/kafka\_2.13-2.8.0.tgz -C /opt/module/
3.配置文件 config/server.properties 中的以下内容需要修改
```
vim config/server.properties
```
```
#broker 的全局唯一编号，不能重复
broker.id=0
#topic数据存放的位置
log.dirs=/opt/module/kafka_2.13-2.8.0/data
#zookeeper集群的连接地址
zookeeper.connect=hadoop102:2181,hadoop103:2181,hadoop104:2181/kafka
```
4.配置环境变量，方便直接使用kafka的命令
```
vim /etc/profile.d/my_env.sh
```
```
#KAFKA_HOME
export KAFKA_HOME=/opt/module/kafka_2.13-2.8.0
export PATH=$PATH:$KAFKA_HOME/bin
```
```
source /etc/profile
```
5.分发
```
xsync kafka_2.13-2.8.0/
```
6.在Hadoop103和Hadoop104上修改环境变量，因为 /etc/profile.d/my\_env.sh 属于root用户，当前jmoon用户没有权限分发
7.修改Hadoop103和Hadoop104 的 配置文件 config/server.properties 中的 broker.id， broker.id 不得重复，如 broker.id=1、 broker.id=2
8.在/home/jmoon/bin目录下编写群起Kafka的脚本 kafka.sh
```
#!/bin/bash

case $1 in
"start"){
    for i in hadoop102 hadoop103 hadoop104
    do
        echo ---------- kafka $i 启动 ------------
        ssh $i "/opt/module/kafka_2.13-2.8.0/bin/kafka-server-start.sh -daemon /opt/module/kafka_2.13-2.8.0/config/server.properties"
    done
};;
"stop"){
    for i in hadoop102 hadoop103 hadoop104
    do
        echo ---------- kafka $i 停止 ------------
        ssh $i "/opt/module/kafka_2.13-2.8.0/bin/kafka-server-stop.sh stop"
    done
};;
esac
```
增加可执行权限
```
chmod +x kafka.sh
```
分发，以便在每台机器上都可以群起kafka
```
xsync kafka.sh
```
9.启动zookeeper集群，zk.sh start
10.启动kafka集群，kafka.sh start

**zookeeper对于Kafka的作用**
1.借助Zookeeper完成Kafka集群中主机的动态上下线
搭建Hadoop和Zookeeper的集群时均需要在配置文件中配置其它主机的信息，Hadoop是将其它Hadoop主机的ip地址配置在etc/hadoop/workers文件中，Zookeeper是在conf/zoo.cfg文件中配置其它Zookeeper主机的ip、通信端口号以及选举端口号。但从以上步骤中可以看到搭建Kafka集群并不需要配置其它Kafka主机的信息，而是只需要给Kafka主机指定一个在集群中唯一的id即可，这是因为每台Kafka启动之后都将自己的信息注册到zookeeper中（在/brokers/ids下创建一个临时节点，名字就是在配置文件中指定的id，该节点里面保存着Kafka主机地址等信息），所以当有新的Kafka注册到zookeeper时，其它Kafka主机能够感知到（zookeeper的通知机制）。也就是说只要Kafka配置文件里配置连接的zookeeper集群是同一个，那么这些Kafka实例就属于同一集群。原本在集群中的主机的动态上下线 与 往正在运行的集群中新增主机 是不一样的（比如zookeeper在3.5以后才支持往正在运行的集群中新增一台全新的zookeeper节点），但是由于zookeeper的存在，使得Kafka集群无论是哪一种动态的扩展都变得非常简单。

2.借助Zookeeper完成controller的选择
Kafka集群需要一个controller来主事完成一些工作，比如，将分区分配在集群的主机上、分区副本之间Leader的选举等。Kafka集群的controller的选举也需要依赖zookeeper，选举的方式就是所有Kafka主机争抢地创建临时节点/controller，并往这个节点里面写入信息，因为只有一个Kafka会创建成功，所以也就可以完成选举。

3.借助Zookeeper保存集群的公共信息，使得每台Kafka主机能同步获取到这些信息
Kafka不光把自己的注册信息存到zookeeper，还会把topic的信息存到zookeeper，比如有多少个topic，每个topic有多少个分区，每个分区有多少个副本，都放在哪，副本中谁是leader，谁是follower。因为每个Kafka主机读取到的topic信息必须相同，并且每个Kafka主机对topic信息的修改必须是立刻生效的，不存在修改导致Kafka主机读取数据不一致的情况，针对这种需求，当然可以将这些信息存放在redis里面，但zookeeper也能做到这一点，并且zookeeper是分布式存储，对于保存像topic元数据这种少量数据并且对数据可靠性和可用性要求高的需求就再适合不过了（zookeeper提供的存取数据的服务）。

4.借助Zookeeper完成消费者的动态上下线
还有一点就是消费者组的信息也是保存在zookeeper里面的，比如消费者组里的每一个消费者都创建一个临时节点，这样当消费者组里有消费者动态上下线时，Kafka就能及时收到通知，然后进行Rebalance。

当然不止上面所说的这些，还有其它很多信息都是保存在zookeeper里面的，总的来说就是，zookeeper的数据存储服务和通知机制对于协调Kafka集群起到了重要的作用。

zookeeper和Kafka都是是分布式的，整个集群对于外部来说是一个整体，用户无论连接的是集群中的哪一台机器，使用的都是这个整体向外提供的服务，用户并不需要关心读到的数据到底是哪一台主机返回的，也即不用关心整个集群内部是如何协调一起工作的。

