---

Created at: 2021-09-12
Last updated at: 2021-11-02


---

# 1-HBase安装配置


1.启动HDFS和zookeeper
```
start-dfs.sh
zk.sh start
```
2.下载并解压HBase
```
tar -zxvf hbase-1.4.13-bin.tar.gz -C /opt/module/
```
3.修改配置文件
3.1 在 /opt/module/hbase-1.4.13/conf/regionservers 里添加regionserver的主机地址，这样就可以在某一台主机上群起regionservers
```
hadoop102
hadoop103
hadoop104
```
3.2 可选：HMaster高可用配置
第一种方式：直接在其它主机启动HMaster
第二种方式：在/opt/module/hbase-1.4.13/conf/目录下新建一个 backup-masters文件，然后填入备份HMaster的主机地址
```
hadoop103
hadoop104
```
3.3 修改/opt/module/hbase-1.4.13/conf/hbase-env.sh 里的 HBASE\_MANAGES\_ZK=false，不然HBase就会使用自己集成的zookeeper，还有JAVA\_HOME ，其它配置注释掉。
```
export JAVA_HOME=/opt/module/jdk1.8.0_301
export HBASE_MANAGES_ZK=false
```
3.4 修改 /opt/module/hbase-1.4.13/conf/hbase-site.xml
```
<configuration> 

  <!-- 开启分布式集群模式 -->
  <property>
    <name>hbase.cluster.distributed</name>
    <value>true</value>
  </property>

  <!-- HBase在HDFS上的数据存储目录 -->
  <property>
    <name>hbase.rootdir</name>
    <value>hdfs://hadoop102:8020/HBase</value>
  </property>

  <!-- Mater的服务通信端口 -->
  <property>
    <name>hbase.master.port</name>
    <value>16000</value>
  </property>

  <!-- Master的WebUI端口，设置为-1就是不运行WebUI实例 -->
  <property>
    <name>hbase.master.info.port</name>
    <value>16010</value>
  </property>

  <!-- zookeeper集群的地址 -->
  <property>
    <name>hbase.zookeeper.quorum</name>
    <value>hadoop102,hadoop103,hadoop104</value>
  </property>

  <!-- zookeeper数据存放的目录 -->
  <property>
    <name>hbase.zookeeper.property.dataDir</name>
    <value>/opt/module/zookeeper-3.5.7/zkData</value>
  </property>

</configuration>
```

4\. 软连接 hadoop 配置文件到 HBase（如果配置好了HADOOP\_HOME本步骤可以跳过）
```
ln -s /opt/module/hadoop-3.3.1/etc/hadoop/core-site.xml /opt/module/hbase-1.4.13/conf/core-site.xml
ln -s /opt/module/hadoop-3.3.1/etc/hadoop/hdfs-site.xml /opt/module/hbase-1.4.13/conf/hdfs-site.xml
```

5.启动
单节点启动/停止命令：
```
bin/hbase-daemon.sh start master
bin/hbase-daemon.sh stop master
bin/hbase-daemon.sh start regionserver
bin/hbase-daemon.sh stop regionserver
```
群起/群关命令（输入群起命令的主机就是Master）：
```
bin/start-hbase.sh
bin/stop-hbase.sh
```
master的WebUI地址
```
http://hadoop102:16010
```

