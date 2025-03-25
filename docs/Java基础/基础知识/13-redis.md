#### **redis服务器启动命令**

```
以默认配置启动：redis-server
指定配置文件启动：redis-server /path/to/redis.conf
```

#### **redis客户端连接命令**

```
redis-cli -h <ip> -p <port> 省略-h参数默认连接127.0.0.1，省略-p参数默认6379端口
也可以只执行一条命令而不进入客户端：redis-cli <命令>，如:
查看redis服务器信息：redis-cl info server
关闭redis服务器信息：redis-cl shutdown
```

#### **redis容器**

redis的docker容器没有默认的配置文件，所以需要在redis的官方github仓库下载redis.conf，然后再编辑，在启动redis服务器容器时挂载，注意，挂载文件需要修改文件的权限为777，容器才能同步文件的修改。

```
docker run -d -v /root/redis/redis.conf:/data/redis.conf -v /root/redis/data:/data -p 6379:6379 --name myredis redis redis-server /usr/local/etc/redis/redis.conf
```

#### **redis配置文件**

```
################################ 常规配置 ################################
#后台启动redis
daemonize yes
#绑定到本机的某个网络接口上，127.0.0.1是ipv4的环回接口，::1是ipv6的环回接口，-表示当redis检测到本机网络接口并没有该ip地址时启动不会失败，注释掉bind，redis会默认绑定本机所有的网络接口
#bind 127.0.0.1 -::1
#设置端口
port 6379
#设置客户端无操作的超时时间
timeout 0
#每300s检测一次客户端的心跳
tcp-keepalive 300
#设置redis的数据库个数
databases 16
#设置密码
#requirepass foobared
#开启保护模式会使得只能通过本机环回接口连接redis
protected-mode no
#在指定日志文件的名称，若为空串则打印到标准输出上，若为空串且是以守护进程的方式启动，则将日志输出到/dev/null
logfile ""

################################ SNAPSHOTTING RDB持久化配置 ################################
#关闭RDB持久化
# save ""
#rdb持久化的文件名，默认dump.rdb
dbfilename dump.rdb
#文件保存的位置
dir /data
#保存策略
save 3600 1
save 300 100
save 60 10000
#bgsave出错时停止写
stop-writes-on-bgsave-error yes
#开启压缩存储
rdbcompression yes
#存储时生成校验和，恢复时检查校验和
rdbchecksum yes

################################ APPEND ONLY MODE AOF持久化配置 ################################
#开启AOF，AOF和RDB同时开启，系统默认取AOF的数据
appendonly yes
#AOF文件名，默认appendonly.aof，且与dump.rdb放在同一目录下
appendfilename "appendonly.aof"
#AOF同步频率
#始终同步，每次Redis的写入都会立刻记入日志；性能较差但数据完整性比较好
# appendfsync always
#每秒同步，每秒记入日志一次，如果宕机，本秒的数据可能丢失
appendfsync everysec
#redis不主动进行同步，把同步时机交给操作系统
# appendfsync no
# 不是很清楚这个配置的含义，大致意思是有子线程在bgsave或者bgrewriteaof时不进行文件AOF文件同步。官方建议为no，即要进行文件同步，不会丢失数据，但会造成阻塞；设置为yes表示不进行文件同步，而是写进缓冲区，待子线程下次保存时再同步AOF文件，也就是可能会数据丢失。
no-appendfsync-on-rewrite no
#重写触发的时机
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
#忽略AOF文件结尾不完整的情况继续加载恢复数据
aof-load-truncated yes
#重写时把rdb文件数据放在在新的AOF文件的头部作为已有的历史数据，替换掉原来的流水账操作
aof-use-rdb-preamble yes

############## REPLICATION 主从复制 ##################
#设置从机的master主机
# replicaof <masterip> <masterport>
#设置主机挂掉了从机还可以读，单词stale是陈旧的意思，表示主机挂掉了，在从机上读到的可能是一些旧数据
replica-serve-stale-data yes
#设置从机只读，设置为no可能产生一些问题
replica-read-only yes
#backlog用于从机增量式更新
# repl-backlog-size 1mb
#设置当主机没有从机时，主机backlog过期删除时间，0表示永不删除，注意，从机本来就永不删除backlog
# repl-backlog-ttl 3600
#哨兵选举时，从机的优先级，越小优先级越高，为0表示永不当master
replica-priority 100

################################ REDIS CLUSTER  ###############################
#开启集群模式
cluster-enabled yes
#集群模式下，节点自动生成的配置文件的名字，该文件不要手动去修改
cluster-config-file nodes-6379.conf
#节点判定为不可达的超时时间（毫秒）
cluster-node-timeout 15000
#如果设置为yes，当某一段插槽的主从都挂掉了，那么整个集群也就挂掉了；设置为no，当某一段插槽的主从都挂掉了，那么整个集群不会挂掉，只是该段插槽不可用
cluster-require-full-coverage yes
```

------

#### **redis常用命令**

动态设置redis的运行配置

```
config set <directive> <value>
redis运行期间设置密码，重启失效：config set requirepass 123456
设置密码之后，客户端需要认证：auth <password>
```

获取redis的配置信息

```
config get <pattern>
```

把redis运行时的配置信息重写到文件

```
config rewrite
```

切换数据库，默认16个数据库0~15

```
select <dbid>
```

查看当前库的key

```
keys <pattern>
<pattern>是正则表达式，如查看当前库的所有key：keys *
```

判断某个key是否存在

```
exists <key>
```

查看key对应的value是什么数据类型，redis的5大常用数据结构：字符串 (string)、列表 (list)、集合 (set)、哈希 (hash)、有序集合 (zset)

```
type <key>
```

删除key-value

```
del <key>
```

非阻塞异步地删除key-value

```
unlink <key>
```

设置过期时间

```
expire <key> <seconds>
```

查看剩余多少时间过期，ttl (time to live)

```
ttl <key>
```

清空当前库

```
flushdb
```

清空全部库

```
flushall
```

------

#### **字符串 (string) 常用操作**

String类型是Redis最基本的数据类型，一个Redis中字符串value最多可以是512M，

添加键值对

```
set <key> <value>  
set <key> <value> [ex <seconds> | px <miliseconds>] [nx | xx]
同时设置key的过期时间 ex 秒 px 毫秒
nx不存在时才设置，等同于setnx <key> <value> 当key不存在时添加，xx存在时才设置
```

查询键对应的值

```
get <key>
```

把 value 追加到原值的末尾

```
append <key> <value>
```

查询值的长度

```
strlen <key>
```

增加value中数字的值，字符串里必须全是数字，这是一个原子性操作

```
incr <key> 加1
incrby <key> <step> 加step
```

减少value中数字的值，字符串里必须全是数字，这是一个原子性操作

```
decr <key> 减1
decr <key> <step> 减step
```

同时设置一个或多个 key-value对

```
mset <key> <value> [<key> <value> ....]
```

同时获取一个或多个 value 

```
mget <key> [<key> ....]
```


同时设置一个或多个 key-value 对，当且仅当所有给定 key 都不存在，有一个存在则会导致所有设置失败

```
msetnx <key> <value> [<key> <value> ....]
```

获取值的子串，类似java中的substring，**前闭，后闭**，-1表示最后一个位置

```
getrange <key> <起始位置> <结束位置>
```

从起始位置开始覆盖原值

```
setrange <key> <起始位置> <value>
```

设置新值的同时获得旧值

```
getset <key> <value>
```

------

#### **列表 (list) 常用操作**

向列表中插入值

```
lpush <key> <element> [<element> ...] 从左边插入值
rpush <key> <element> [<element> ...] 从右边插入值
```

从左到右在列表中取值

```
lrange <key> <start> <stop> 
```

弹出列表中的值

```
lpop <key> [count] 从左边弹
rpop <key> [count] 从右边弹
```

从 key1 列表右边弹出一个值，插到 key2列表左边

```
rpoplpush <key1> <key2>
```

取索引在 index处的值（从左到右）

```
lindex <key> <index>
```

获得列表长度

```
llen <key>
```

在 value 的 前面/后面 插入 newvalue 

```
linsert <key> before/after <pivot> <element>
```

从左到右删除n个 value

```
lrem <key> <n> <value>
```

将列表下标为index的值替换成value

```
lset <key> <index> <value>
```

-----

#### **集合 (set) 常用操作**

将一个或多个 member 加入到集合 key 中，自动去重

```
sadd <key> <value1> [<member>]
```

取出集合中的所有值

```
smembers <key>
```

判断集合是否为含有 member，有1，没有0

```
sismember <key> <member>
```

集合的元素个数

```
scard <key>
```

删除集合中的某个元素

```
srem <key> <member> [<member> ...]
```

从集合中随机弹出一个值

```
spop <key>
```

随机从该集合中取出n个值，不会从集合中删除

```
srandmember <key> <n>
```

把集合中一个值从一个集合移动到另一个集合

```
smove <source> <destination> <value>
```

得到集合的交集

```
sinter <key1> [<key2>...]
```

得到集合的并集

```
sunion <key1> [<key2>...]
```

得到 key1 - key2 - ... 的差集，即key1中有但是key2....没有的元素

```
sdiff <key1> [<key2>...]
```

------

#### **哈希 (hash) 常用操作**

设置 field value 

```
hset <key> <field> <value> [<field> <value> ...]
```

从取出 field 的 value 

```
hget <key> <field>
```

检查 field 是否存在

```
hexists <key> <field>
```

列出所有field

```
hkeys <key>
```

列出所有value

```
hvals <key>
```

将 field 的值value增加 increment

```
hincrby <key> <field> <increment>
```

设置 field 的值为 value ，当且仅当域 field 不存在 

```
hsetnx <key> <field> <value>
```

------------

#### **有序集合 (zset) 常用操作**

将一个或多个 member 元素及其 score 值加入到有序集 key 当中

```
zadd <key> <score> <member> [<score> <member>...]
```

返回有序集合中下标在<start><stop>之间包括下标的元素（从小到大），加withscores表示把score也带上

```
zrange <key> <start> <stop> [WITHSCORES]
```

返回 score 值介于 min 和 max 之间（包括min，max)的元素（从小到大）

```
zrangebyscore key min max [withscores] [limit offset count]
```

同上，改为从大到小排列

```
zrevrangebyscore key max min [withscores] [limit offset count]
```

value 的 score 加上 increment

```
zincrby <key> <increment> <value>
```

删除该集合下，指定值的元素

```
zrem <key> <value>
```

统计该集合，分数区间内的元素个数 

```
zcount <key> <min> <max>
```

返回该值在集合中的排名，从0开始

```
zrank <key> <value>
```

-------

#### **发布和订阅**

**订阅**

```
subscribe channel [channel...]
psubscribe <pattern> [<pattern>...]
```

**发布**

```
publish channel message
```

查看活跃的频道数

```
pubsub channels [<pattern>]
```

查看频道订阅数

```
pubsub numsub [<channel>...]
```

查看模式订阅数

```
pubsub numpat
```


------

####  **Bitmaps**

设置值

```
setbit <key> <offset> <value>
```

获取值

```
getbit <key> <offset>
```

指定范围为1的个数

```
bitcount [start] [end]
```

Bitmaps之间的运算

```
bitop <and|or|not|xor> <destkey> <key> [<key>...]
```

获取第一个值为bit的偏移量

```
bitpos <key> <bit> [start] [end]
```

------

#### **HyperLogLog**

添加元素

```
pfadd <key> <element> [<element>]
```

计算一个或多个HyperLogLog的独立总数

```
pfcount <key> [<key>...]
```

合并多个HyperLogLog到destkey

```
pfmerge <destkey> <sourcekey> [<sourcekey>]
```

------

#### **redis事务**

redis里面的单个命令都是原子操作，但当某个需求需要执行多条命令时就不是一个原子操作了，redis事务就是将多条命令打包在一起执行，防止其它命令插队。

multi命令表示开始组队，输入的每条命令都不会执行，只是先把命令组合在一起

```
multi
```

discard命令表示 放弃执行队列 并 结束组队

```
discard
```

**exec命令表示 结束组队 并  执行队列，执行过程中不会被插队**。执行过程指令不被插队有三种情况，一是单线程执行，只有一个线程，没有其它线程，自然不会被打断；二是多线程并发，但是只有一个线程在执行，其它线程阻塞，于是不会被打断；~~三是多线程并行，并行时各自执行各自的，没有锁，不会被阻塞，所有线程都能同时执行，也没有被打断，（但其实在一条时间线上看，好像指令的执行还是有先后，也就是还是被插队了~~。**redis在执行exec命令时采用的是单线程执行。**

```
exec
```

需要注意的是，组队过程中某条命令出现了语法等错误，那么整个队列都会被取消；执行过程中某条命令出现了语法等错误，那么该命令不会执行，但其它命令依然会正常执行，这正是redis事务不同于关系型数据库事务的地方，redis事务不会回滚，没有原子性。

因为redis事务在组队过程中命令没有执行，而在执行过程也不会被其它命令插队，所以redis事务的执行是串行化的，隔离性就是串行化，没有mysql的隔离级别。

虽然redis事务是串行化执行的，但由于其对数据库的操作是打包执行，导致其串行化与mysql的串行化十分不同，因为打包执行意味着redis事务执行过程中不可能穿插其它java代码的逻辑，但mysql的事务就不一样，mysql的事务是并发执行的长事务，每个命令都是立即执行可以拿到结果的，事务执行期间可以根据结果执行其它java代码逻辑，从而进行读写操作，然后通过锁来保证串行化，也即保证了事务执行后数据库数据的一致性，这个一致性包括了java代码的逻辑。但redis事务串行化带来的一致性并不包括java代码的逻辑。

一致性是一个逻辑上的概念，指的是满足特定逻辑的状态，在秒杀案例中库存不能小于0就是一个逻辑，保证数据库的一致性指数据库从一种一致性状态转移到另一种一致性状态。mysql的串行化事务是一个长过程，事务期间可以加入各种java代码的逻辑判断来保证一致性，但redis不能，那如何在redis事务的一致性中加入java代码的逻辑呢？

答案就是**乐观锁**。mysql的串行化事务采用是悲观锁，如读锁、写锁；redis则采用乐观锁；这都是各自执行特点所决定。

redis乐观锁命令watch需要在multi命令之前执行，具体的执行位置要看业务代码的逻辑，因为它就是用来确保一致性中有业务逻辑的。

```
watch <key>
```

秒杀案例，注意watch的位置：

```
public String doSecKill(String phone, String prodId) {
        if (phone == null || prodId == null || phone.length() == 0 || prodId.length() == 0) {
            log.info("系统错误！");
            return "系统错误！";
        }

        //商品的库存
        String stock = "sk:" + prodId + ":stock";
        //秒杀成功的用户的手机号
        String user = "sk:" + prodId + ":phone";

        try (Jedis jedis = jedisPool.getResource()) {

            if (jedis.get(stock) == null) {
                log.info("秒杀还没开始！！");
                return "秒杀还没开始！";
            }
            if (jedis.sismember(user, phone)) {
                log.info("您已成功秒杀到商品，不可重复秒杀！");
                return "您已成功秒杀到商品，不可重复秒杀！";
            }
/*watch必须放在这里或之前，当有两个或多个线程执行到这还没watch时，如果其中一个watch并执行了后面所有的代码，那么其它线程watch的将会是0，然后挂在下面的if判断；如果多个线程都watch的是1，通过了下面的if判断，则悲观锁只会让其中一个线程执行成功，其它均失败。*/
            jedis.watch(stock);
            //下面的jedis.get(stock)并不属于redis事务中的操作
            if (Integer.parseInt(jedis.get(stock)) <= 0) {
                log.info("秒杀已经结束！");
                return "秒杀已经结束！";
            }

/*如果把watch放在这里，可能出现，在stock=1时，有两个请求同时到这里，一个没有执行watch，一个已经watch并执行了剩下所有，于是没有watch的线程此时watch的就是0，然后还能正常执行下面的代码，于是库存就变成-1了*/
            //jedis.watch(stock);
            Transaction multi = jedis.multi();
            multi.decr(stock);
/*由于这里并没有真正执行sadd，前面的if判断只能是在真正add之后有效，所以可能出现一个用户的多次请求都执行到这里，但没有执行下面的exec，最后的效果是一个用户成功抢到多次，库存归零了，但由于是set集合，所以只有保留用户的一条信息，于是成功抢到的用户数少于库存数*/
            multi.sadd(user, phone);
            List<Object> results;
            /*//验证取不到值，确实取不到
            if (multi.get(stock) != null) {
                System.out.println(multi.get(stock));
            }*/
            results = multi.exec();
            if (results == null || results.size() == 0) {
                log.info("很遗憾您未能抢到商品！");
                return "很遗憾您未能抢到商品！";
            }
            log.info("秒杀成功");
            return "秒杀成功！";
        }
    }
```

apache benchmark 安装

```
yum install httpd-tools
```

压测命令

```
ab -n 2000 -c 400 -p ~/postfile -T application/x-www-form-urlencoded http://192.168.37.1:8080/secKill
```



------

#### **主从复制**

主从复制模式下，slave从机只能读不能写，master可读可写，所以master的角色主要是写，slave的角色主要是读。

设置成为谁的slave，如果在客户端中执行，则重启会失效，在配置文件中配置，重启有效

```
replicaof <host> <port>
```

设置不成为slave，而是master

```
replicaof no one
```

查看主从复制的信息

```
info replication
role
```

**哨兵模式**配置流程：

哨兵模式正确打开方式是为每个redis主机都运行一个哨兵，这样master主机挂掉了，剩下的slave主机的哨兵根据配置文件中的replica-priority值选举产生新的master，原来的master重新上线后会变成现在master的slave。

1.编辑启动哨兵的配置文件sentinel.conf。由于redis的docker容器中没有启动哨兵的配置文件，所以需要到redis的官方github仓库上下载sentinel.conf文件，然后基于此文件进行编辑，编辑完再复制到容器内。

```
# 绑定网络接口
# bind 127.0.0.1 192.168.1.1
# 关闭保护模式，不然只能本机访问
protected-mode yes
# 端口号
port 26379
# 是否以守护进程的方式启动
daemonize no
# 若以守护进程的方式启动，指定pid存放的位置
pidfile /var/run/redis-sentinel.pid
#在指定日志文件的名称，若为空串则打印到标准输出上，若为空串且是以守护进程的方式启动，则将日志输出到/dev/null
logfile ""
#工作目录
dir /tmp

# 最重要的配置，<master-name>是为master起的别名，<ip> <redis-port>是哨兵启动时master的IP和端口，哨兵会通过info
# replication 命令获取到master主机所有slave从机的ip和端口号，<quorum>表示判定master不可达至少需要quorum个哨兵同意。
# quorum一般设置为(sentinels/2 + 10)，例如：sentinel monitor mymaster 172.17.0.4 6379 2
sentinel monitor <master-name> <ip> <redis-port> <quorum>

# 如果被监控的master主机配置了密码，那么需要以下配置进行认证
# sentinel auth-pass <master-name> <password>

# 每个哨兵节点通过ping命令来判断数据节点和其它哨兵节点是否可达，如果在下面配置的时间没有收到回复，则判定为不可达，默认30秒
# sentinel down-after-milliseconds <master-name> <milliseconds>
sentinel down-after-milliseconds mymaster 30000

# 故障转移时，设置多少个从节点并行发起复制的请求
# sentinel parallel-syncs <master-name> <numreplicas>
sentinel parallel-syncs mymaster 1

# 故障转移超时时间，默认3分钟
# sentinel failover-timeout <master-name> <milliseconds>
sentinel failover-timeout mymaster 180000
```

2.启动哨兵

```
redis-sentinel sentinel.conf
```

可以连接哨兵查看哨兵监控的相关信息

```
redis-cli -h <sentinel-ip> -p 26379
info sentinel
```



------

#### **集群**

数据分区是分布式存储的核心，分布式数据库首要解决的问题是把整个数据集按照分区规则映射到多个节点上，即把数据集划分到多个节点上，每个节点只负责整个数据集的一个子集。

**手动配置集群流程：**

1.修改配置文件，主要是开启集群模式

2.启动6个redis容器，redis01、redis02 ...

```
docker run -d -v /root/redis/redis.conf:/data/redis.conf --name redis01 redis redis-server /data/redis.conf
...
```

3.任意进入一个redis实例的客户端，然后与其它5个节点握手，加入集群中的节点会自动进行协商，所以无需在每一个节点做与其它5个节点握手的动作。

```
cluster meet 172.17.0.2 6379
...
```

4.分别连接节点然后分配slot。节点握手后集群还不能正常工作，因为slot还没有分配，此时集群仍处于下线状态，不能进行数据的读写。

```
redis-cli -h 172.17.0.2 cluster addslots {0...5461}
redis-cli -h 172.17.0.3 cluster addslots {5462...10922}
redis-cli -h 172.17.0.4 cluster addslots {10922...16383}
```

5.连接到剩下3台redis主机，让其成为前面3台主机的从机

```
redis-cli -h 172.17.0.5 cluster replicate {nodeId}
redis-cli -h 172.17.0.6 cluster replicate {nodeId}
redis-cli -h 172.17.0.7 cluster replicate {nodeId}
```

**自动配置集群流程：**

1.修改配置文件，主要是开启集群模式

2.启动6个redis容器，redis01、redis02 ...

```
docker run -d -v /root/redis/redis.conf:/data/redis.conf --name redis01 redis redis-server /data/redis.conf
...
```

3.自动配置集群

```
docker exec -it redis01 redis-cli --cluster create --cluster-replicas 1 172.17.0.2:6379 172.17.0.3:6379 172.17.0.4:6379 172.17.0.5:6379 172.17.0.6:6379 172.17.0.7:6379
```

**常用命令：**

使用redis-cli客户端连接到redis集群，加 -c 选项表示以集群的方式连接，也就是在设置和读取值时可以根据slot重定向连接到不同的redis服务器上，不加 -c 的话不能重定向，只能设置和读取连接的redis服务器上的slot。

```
docker exec -it redis01 redis-cli -c
```

查看集群节点之间的关系

```
cluster nodes
```

查询键所对应的slot

```
cluster keyslot <key>
```

查询slot中有多少键，要与slot所在的服务器连接才能查询到

```
cluster countkeysinslot <slot>
```

查询slot中的前count个键

```
cluster getkeysinslot <slot> <count>
```



------

**缓存穿透**

问题描述：恶意用户**高并发访问数据库中不存在的数据**，这时redis中肯定没有也没有这些数据，于是将所有请求都直接交给数据库，造成数据库宕机。

解决方案：

1.布隆过滤器

**布隆过滤器可以确定某条数据一定不存在，或者某条数据可能存在。**具体做法是，将数据库中所有数据的键映射到布隆过滤器中，请求过来，首先检查布隆过滤器，如果返回为0，则可以断定数据库中一定没有这条记录，如果返回为1，虽然不能百分之百肯定数据库中一定有这条记录，但也有百分之八九十的概率可能有，于是放行，首先查redis，再查数据库，不保证一定能查到数据。比如数据库键的取值范围是40亿，数据库里有这40亿中的10亿条数据，将这10亿条数据映射到布隆过滤器之后，如果请求的数据是这10亿条数据中的一条，布隆过滤器并不能百分之百确定这条数据一定在数据库中，于是返回1，而对于剩下30亿数据的请求，其中百分之九十数据的请求，布隆过滤器会返回0，即肯定的告诉你数据库中没有这条数据，而对于剩下百分之十数据的请求，布隆过滤器拿不准，会返回1，所以布隆过滤器能拦下30亿*90%的恶意请求。

2.拦截ip

3.缓存空值

**缓存击穿**

问题描述：**热点key突然过期失效**，所有并发请求直接打到数据库上，造成数据宕机

解决方案：这里主要是因为过期之后，所有并发请求直接打到数据库上，所以可以采用加锁的办法，只让一个请求去访问数据库，访问完之后将结果缓存到redis中，接着其它请求从redis中取数据。如果是单体应用，直接加互斥锁即可，分布式集群应用就需要加分布式锁。

**缓存雪崩**

问题描述：**大面积key同时失效**，也是所有请求直接打数据库上，造成数据库宕机

解决方案：随机设置key的失效时间，防止同时失效

**分布式锁**

所谓分布式锁，其实就是让多台应用服务器互斥的访问同一个数据，这个数据是所有应用服务器都能访问到的。

三种主流的分布式锁：
1.基于数据库
2.基于缓存（redis）等
3.基于zookeeper

