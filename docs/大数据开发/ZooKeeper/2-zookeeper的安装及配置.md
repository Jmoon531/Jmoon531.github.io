---

Created at: 2021-08-30
Last updated at: 2021-10-23


---

# 2-zookeeper的安装及配置


下载地址： https://zookeeper.apache.org/

**本地模式安装**
1.安装 JDK
2.拷贝 apache-zookeeper-3.5.7-bin.tar.gz 安装包到 Linux 系统下
3.解压
    tar -zxvf apache-zookeeper-3.5.7-bin.tar.gz -C /opt/module/
4.修改目录的名字
    mv apache-zookeeper-3.5.7-bin zookeeper-3.5.7
5\. 将/opt/module/zookeeper-3.5.7/conf 这个路径下的 zoo\_sample.cfg 修改为 zoo.cfg
     mv zoo\_sample.cfg zoo.cfg
6.修改zoo.cfg 中的 dataDir=/opt/module/zookeeper-3.5.7/zkData
7.创建zkData这个目录  mkdir zkData
8.启动zookeeper
     bin/zkServer.sh start
9.查看zookeeper运行状态
     bin/zkServer.sh status
10\. 启动客户端
     bin/zkCli.sh
11\. 退出客户端
     quit
12\. 停止 Zookeeper
     bin/zkServer.sh stop

Zookeeper中的配置文件zoo.cfg中参数含义解读如下：

1. tickTime = 2000：通信心跳时间， Zookeeper服务器与客户端心跳时间，单位毫秒
2. initLimit = 10：Leader和Follower初始通信时限
3. syncLimit = 5：Leader和Follower同步通信时限

        Leader和Follower之间通信时间如果超过syncLimit \* tickTime，Leader认为Follwer死掉，从服务器列表中删除Follwer。

4. dataDir：保存Zookeeper中的数据

        注意： 默认的tmp目录，容易被Linux系统定期删除，所以一般不用默认的tmp目录

5. clientPort = 2181：客户端连接端口，通常不做修改。

**集群安装**，保留本地模式的配置，额外还需要进行如下的配置：
1. 在/opt/module/zookeeper-3.5.7/zkData 目录下创建一个 myid 的文件，文件名必须叫myid，这个是硬编码在代码里的
    vim myid
    在文件中添加本台机器zookeeper的编号（注意：上下不要有空行，左右不要有空格）如：2，这个编号在zookeeper集群选举时用。
2.在/opt/module/zookeeper-3.5.7/conf/zoo.cfg 末尾添加一下内容：
```
##########cluster############
server.2=hadoop102:2888:3888
server.3=hadoop103:2888:3888
server.4=hadoop104:2888:3888
```
    配置参数解读 server.A=B:C:D
    A 是一个数字，表示这个是第几号服务器，这个值就是myid文件里面配置的值
    B 是这个服务器的地址；
    C 是这个服务器 Follower 与集群中的 Leader 服务器交换信息的端口；
    D 是万一集群中的 Leader 服务器挂了，需要一个端口来重新进行选举，选出一个新的Leader，而这个端口就是用来执行选举时服务器相互通信的端口。
3.分发配置好的 zookeeper 到其他机器上
    xsync zookeeper-3.5.7
4\. 分别在 hadoop103、 hadoop104 上修改 myid 文件中内容为 3、4
5\. 在 hadoop102 的/home/jmoon/bin 目录下创建脚本 zk.sh，添加可执行权限chmod +x ~/bin/zk.sh后分发到其它机器上
```
#!/bin/bash

case $1 in
"start"){
    for i in hadoop102 hadoop103 hadoop104
    do
        echo ---------- zookeeper $i 启动 ------------
        ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh start"
    done
};;
"stop"){
    for i in hadoop102 hadoop103 hadoop104
    do
        echo ---------- zookeeper $i 停止 ------------
        ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh stop"
    done
};;
"status"){
    for i in hadoop102 hadoop103 hadoop104
    do
        echo ---------- zookeeper $i 状态 ------------
        ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh status"
    done
};;
esac
```

6.用脚本启动zookeeper集群 zk.sh start

