#### Kafka的架构？

<img src="images/Kafka架构.png" style="zoom: 67%;" />

生产者和消费者按topic生产和消费消息，Kafka的每一个topic可以被分成多个分区，每个分区可以有多个副本，多个副本中有一个leader和多个follower，客户端只与leader进行交互，follower只负责备份数据，同一个分区的副本必须分布在不同的broker上，所以分区的副本数不能设置超过Kafka集群中的broker数。

#### Kafka高吞吐的原因？

一是分布式架构。

二是写数据时采用顺序写磁盘和零拷贝技术，每个分区的副本的保存采用了分片和索引机制，分片就是将数据分成多个segment，每个segment对应一个文件，然后每个segment中都创建了索引；读数据时采用二分查找定位消息在哪一个segment，然后利用segment对应的索引就能快速找到消息的位置。

Kafka使用的零拷贝技术是sendfile+SGDMA(Scatter-Gather DMA)，涉及两个过程，① 生产者->Kafka：从网卡中读数据然后写到磁盘中，②Kafka->消费者：从磁盘中读数据然后写到网卡中。

#### 零拷贝技术？

从磁盘读数据，然后写到网络设备中发出去，read+write是最传统的方式，以下是实现零拷贝常用的技术：

1. mmap：直接将数据从 内核读缓冲区 写到 内核写缓冲区，减少了一次将数据从内核缓冲区拷贝到用户地址空间的成本。

2. sendfile：相比于mmap只是减少一次用户态到内核态的切换，数据同样是直接从内核的读缓冲区写到了内核写缓冲区。因为只在内核态进行，所以用户进程无法操作数据，代码上的体现就是，使用mmap是两部搞定的，所以中间可以对数据进行操作，但是使用snedfile是一次系统调用，没有操作数据的余地。

3. sendfile+SGDMA(Scatter-Gather DMA)：相比于只使用sendfile，减少了一次数据拷贝，数据直接从内核读缓冲区映射到内核写缓冲区的。

#### zookeeper对于Kafak的作用？

1.借助Zookeeper完成Kafka集群中主机的动态上下线。

2.借助Zookeeper完成controller的选举。

3.借助Zookeeper保存集群的公共信息，使得每台Kafka主机能同步获取到这些信息，如有多少个topic，每个topic有多少个分区，每个分区有多少个副本，都放在哪，副本中谁是leader，谁是follower。

4.借助Zookeeper完成消费者的动态上下线，消费者组里有消费者动态上下线时，Kafka就能及时收到通知，然后进行Rebalance。

#### Kafka controller 的作用？

Kafka controller 的作用是管理和协调Kafka集群，具体如下：

1. 主题管理：创建、删除Topic，以及增加Topic分区等操作都是由控制器执行。
2. 分区分配：将分区的分配到broker，也是由controller实现。
3. 副本leader的选举。

#### 防止controller脑裂？

如果controller所在broker挂掉了，或者Full GC停顿时间太长超过zookeeper`session timeout`出现假死，Kafka集群必须选举出新的controller，但之后被取代的controller又恢复正常了，它依旧是controller身份，这样集群就会出现两个controller，这就是controller脑裂问题。

为了解决Controller脑裂问题，ZooKeeper中还有一个与Controller有关的持久节点/controller_epoch，存放的是一个整型值的epoch number（纪元编号，也称为隔离令牌），集群中每选举一次控制器，就会通过Zookeeper创建一个数值更大的epoch number，如果有broker收到比这个epoch数值小的数据，就会忽略消息。

分区leader的脑裂问题也是靠epoch解决。

#### 副本leader的选举？

分区副本的leader由controller来选举，当分区leader不可用的时候，Kafka会从Zookeeper中读取当前分区的ISR(in-sync replicas)集合，然后调用配置的分区选择算法从ISR中选择分区的leader。极端情况，如果ISR集合中的所有分区都挂了，那么可以通过设置选择是否进行unclean leader选举。

unclean leader选举：Kafka把不在ISR列表中的存活副本称为“非同步副本”，这些副本中的消息远远落后于leader，如果选举这种副本作为leader的话就可能造成数据丢失。Kafka broker端提供了一个参数`unclean.leader.election.enable`，用于控制是否允许非同步副本参与leader选举；如果开启，则当ISR为空时就会从这些副本中选举新的leader，这个过程称为Unclean leader选举。

#### 生产者和Kafka之间的消息丢失 ？

acks=0：broker不会发送ack，于是producer发送消息不会等待 broker 的 ack。这种策略下有两种情况会导致消息丢失，第一种情况是在传输过程中丢失消息，因为连接是tcp，所以只有能在运输层和应用层之间丢失消息，所以出现消息丢失的概率是很小；还有一种情况是Follwer同步数据完成之前Leader宕机也会导致丢失数据。

acks=1：producer收到broker发送的ack之后才会认为消息发送成功，但是broker接收到producer发送的数据保存成功后就会向producer发送ack，不会等到Follower同步完leader的数据才发送ack，所以这种策略虽然不会在网络传输中丢失数据，但是会因为Follwer同步完成之前Leader宕机丢失数据。

acks=-1 或 "all"：broker会等ISR集合中的follower同步完leader的数据之后才发送ack，所以这种策略不会在网络传输中丢失数据，也不会因为Follwer同步完成之前Leader宕机丢失数据。

##### ISR(in-sync replica set)集合？

acks=all时，因为等待所有follower都同步完数据才发送ack效率太慢，所以Kafka采取的策略是，维护一个同步数据比较快的Follower集合，并不是所有follower，当这个集合中的follower都同步完数据就会向生产者发送ack，这个集合就叫ISR，如果leader挂掉了就会在ISR里面选举新的leader。

#### 生产者、消费者与Broker之间是以tcp的方式在进行通信，为什么还会出现消息丢失？

producer与broker之间是tcp连接，所以消息一定会被可靠传送到broker主机的，不过这只是运输层的ack，从运输层到应用层之间也可能出现问题，所以可能会消息丢失，于是也就可能会出现消息乱序的情况了。

#### 如何保证消息不丢失？

1. 设置Producer端设置`acks`=all

2. topic设置`replication.factor`>=3

3. 设置`min.insync.replicas`>1

4. 设置`unclean.leader.election.enable`=false，即不允许Unclean leader选举

#### 生产者和Kafka之间的消息重复？

acks=0时不会出现数据重复的问题，因为producer只会发送一次消息，但是acks=1和acks=-1均会出现数据重复的问题，因为在ack的策略下，producer均可能会重复发送消息。

为了解决消息重复，Kafka引入了幂等性，开启幂等性之后（`enable.idempotence=true`，开启幂等后，生产者的ack固定为-1），生产者在初始化的时候会被分配一个唯一的 PID（该 PID 对用户完全透明，不会暴露给用户），之后生产者给每个分区的消息维护一个从 0 开始单调递增的`Sequence Number`，每条消息发送时都会附带上这个`Sequence Number`，Broker 端也会为每一个`<PID, Topic, Partition>`维护一个`SeqNumber`，只有当生产者发送过来的消息的序列号比broker维护的序列号大1时，broker才会接收它，如果生产者发送过来的消息的序号小于等于当前维护的`SeqNumber`，则为重复消息（Producer 抛出`DuplicateSequenceNumber`异常），如果生产者发送过来的消息的序号大于当前维护的`SeqNumber`+1，则是乱序消息（Producer 抛出`InvalidSequenceNumber`异常），中间可能出现了消息丢失（`max.in.flight.requests.per.connection=5`，该配置项用于指定最大乱序程度，类似于滑动窗口）。所以开启幂等后，Kafka不但能解决消息重复的问题，还能解决消息乱序的问题。

PID是生产者和Kafka一次会话的唯一标识，所以如果生产者断开连接后重连Kafka会再次生成一个新的PID，这时生产者发送的消息就与上次会话发送的消息就没有重复的关系了，所以当生产者在发送完消息之后，没有接收broker的ack之前挂掉了，之后重启重发上次的消息，这时因为重启之后PID改变了，所以Broker不认为这是重复消息，于是产生重复消息。

为了解决生产者重启导致的消息重复，可以开启Kafka的事务，**Kafka的事务可以保证生产者跨分区和跨会话的原子写入**。Kafka的事务机制依赖于幂等，开启 kafka事务时，kafka 会自动开启幂等。

#### Kafka事务？

**Kafka事务的应用场景：**

Kafka的事务对于生产者而言提供了原子写入（`transactional.id = 'some unique id'`），生产者事务可以是**跨分区**和**跨会话**的；对于消费者而言，提供了 读未提交 和 读已提交 两种隔离级别（`isolation.level="read_committed"` 或 `"isolation.level=read_uncommitted"`），不包含offset的提交。

另外，Kafka事务还保证了一种特定场景保证的原子性，即`conumser-transform-produce` 应用模式（从某个 Topic 消费数据，经过一系列转换后写回另一个 Topic，主要是针对 Kafka Stream 应用而言）。

##### 如何实现在同一个事务内跨分区的原子写入？

~~为支持事务，Kafka引入了两个新的组件：Transaction Coordinator 和 Transaction Log，transaction coordinator 是运行在每个 kafka broker 上的一个线程，transaction log 是 kafka 的一个内部 topic，transaction log 有多个分区，每个分区都有一个 leader，该 leader对应哪个 kafka broker，哪个 broker 上的 transaction coordinator 就负责对这些分区的写操作，transaction log 内部存储的只是事务的最新状态和其相关元数据信息，Kafka分区的副本机制保证了事务状态的容错。~~

跨分区事务的原子写入使用了两阶段提交协议（2pc, 2 Phase Commit），2pc协议是实现分布式事务的一种方法，2pc协议的实现需要一个协调者，和多个事务的参与者，然后事务的提交分为两个阶段：

- **准备阶段**：又叫作投票阶段，在这一阶段，协调者询问事务的所有参与者是否准备好提交，需要注意的是，协调者向事务的参与者发出Prepare命令时，表示此时所有事务的参与者都已经完成了事务中的所有操作，也就是所有redo日志已经完成了，只差最后一个提交操作了。
- **提交阶段**：协调者向参与者发送 Commit 指令 或者 Abort指令。

Kafka的transaction coordinator就是2pc的协调者，每个分区的所在的broker就是事务的参与者。

##### 如何保证在同一个事务内跨会话消息不重复？

Kafka事务需要应用程序提供一个稳定的，并且重启后不变的，唯一的`Transaction ID`，并将`Transactin ID`与`PID`绑定，这样当Producer重启之后，就可以通过正在运行的 `Transaction ID` 获得原来的 `PID`。（注意：`Transaction ID`由用户提供，重启后不会变，而`PID`是内部的实现，对用户透明。没有开启事务时，生产者每次重启都会分配新的`PID`，开启事务之后，是通过`Transactin ID`获取原来的`PID`，所以生产者的`PID`不会变，于是Kafka的幂等写入有效。）

##### 如何选用一个全局一致的 `transactional.id`？

通过某种机制来生成一个全局唯一的 `transactional.id`，然后通过一个统一的外部存储，来记录生产者使用的 `transactional.id` 和该生产者涉及到的 `<topic, partition>` 之间的映射关系。

##### 如何屏蔽僵尸生产者 （zombie producers）？

所谓僵尸生产者就是，旧的生产者宕机之后，在生产者集群里的另一台主机接替这个生产者的职责，也就是要到了它的`Transaction ID`继续工作（这与单个生产者重启不同），不就之后之前的那个生产者重启成功了，此时就会导致有两个相同的生产者具有相同的`Transaction ID`和`PID`，这显然会导致消息重复，重启后的这个生产者就是所谓的僵尸生产者 （zombie producers）。

为了保证新的 Producer 启动后，旧的具有相同`Transaction ID`的 Producer 即失效，每次 Producer 通过`Transaction ID`拿到 `PID` 的同时，`transactional coordinator`会递增的 epoch，由于旧的 Producer 的 epoch 比新 Producer 的 epoch 小，所以Kafka 可以很容易识别出该 Producer 是老的 Producer 并拒绝其请求。

#### 生产者发送消息的流程？

首先经过**拦截器**，然后经过**序列化器**，最后经过**分区器**写到发送线程的缓冲区中，之后发送线程会把数据发送到相应的broker上。因为是另外一个单独的发送线程在发送数据，所以与生产者的主线程是异步的。

#### ProducerRecord的数据结构？

- `Topic` - 主题
- `Partition` - 分区（非必填）
- `Key` - 键（非必填）
- `Value` - 值

#### 生产者如何确定将消息发送到哪个分区？

1. 在ProducerRecord 指明 partition 的情况下，直接将指明的值直接作为 partiton 值。

2. 在ProducerRecord 没有指明 partition 值但有 key 的情况下，将 key 的 hash 值与 topic 的 partition 数进行取余得到 partition 值，该方式可以保证具有相同key的消息进入到同一个分区

3. ProducerRecord 既没有 partition 值又没有 key 值的情况下，会将连续的消息发送给一个分区，然后再将下一波连续消息发送给下一个分区。控制台客户端生产者就是这种策略，因为控制台生产者只能提供value。

4. 用户也可以自定义分区策略

#### 生产者 向 Broker 发送消息时是怎么确定向哪一个 Broker 发送消息？换言之就是怎么知道分区leader在哪一台Broker上的？

生产者会向任意 broker 发送一个元数据请求（`MetadataRequest`），获取到每一个分区对应的 Leader 信息，并缓存到本地。然后生产者在发送消息时，会指定 Partition 或者通过 key 得到到一个 Partition，然后根据 Partition 从缓存中获取相应的 Leader 信息。

#### Kafka如何维护消费者的消费状态？消费者组的offset是什么？

消费者组依靠offset来维护消费位置，这样就可以保证消费者组下线后再上线时，能知道上一次消费的位置。消费者是以消费者组为单位消费topic中的消息，又因为同一个消费者组里面的两个及以上的消费者不能同时消费同一个分区的消息，所以可以使用<consumer-group-id，topic，partition>作为key来维护每一个消费者组在一个分区上的消费位置。默认情况下offset保存在Kafka的一个topic里。

#### offset的提交方式？

Kafka依靠offset来维护消费者组在每个分区上的消费位置，因为消费位置只与消费者有关，所以offset值的改变需要消费者来确定，也就是Kafka需要消费者自己来维护这个offset。不过Kafka给消费者提供了维护offset的默认方式：自动提交 和 手动提交，

#### 为什么同一个消费者组里面的两个及以上的消费者不能同时消费同一个分区的消息？

因为offset是以消费者为单位进行维护的，而不是以单个消费者为单位，比如说如果有同一个消费者组里的A、B两个消费者同时消费一个分区的消息，A消费者消费这个分区的1、2、3号消息，B消费者消费这个分区的4、5、6号消息，然后B消费者先提交修改offset为6，接着A消费者提交修改offset为3，那么就出现问题了，这与多线程修改同一个变量类似。

#### 什么是消费者组的分区分配策略？

将一个topic的多个分区分配给一个消费者组里面的多个消费者就是消费者组的分区分配策略。消费者组的分区分配策略要在保证同一个消费者组里面的两个及以上的消费者不能同时消费同一个分区的消息的前提下，实现各个消费者负载均衡。Kafka消费者组的分区分配策略有：

- RangeAssignor
- RoundRobinAssignor
- StickyAssignor

#### 什么是Rebalance？

当有新的消费者加入消费者组，或者有消费者退出消费者组，或者topic新增分区时，都需要将分区重新分配给消费者组里面的多个消费者，这就叫Rebalance。

#### 消费者的 消费丢失 和 重复消费 问题？

在手动提交offset 和 自动提交offset两种方式中，都会出现消费者的 消费丢失 和 重复消费 问题。

自动提交的时间间隔设置得太短，会造成消费者还没有消费完这批数据时就提前提交，如果这时消费者挂掉了，重启后就不会继续消费上次还没有消费完的数据，而直接消费下一批数据，造成消费者消息丢失的问题（或者称为数据漏消费、消费丢失）。设置得太长，会造成消费者已经消费完这批数据，但是却迟迟没有提交，如果这时消费者挂掉了，那么重启之后消费者会将上次已经消费了的数据再次重新消费一次，这就是重复消费问题。

在手动提交方式中，如果先提交 offset 后消费，可能造成消费丢失问题；如果先消费后提交 offset，可能会造成重复消费问题。

#### 如何解决消费者的 消费丢失 和 重复消费 问题？

可以把offset存储在Mysql中，然后把 消费数据的过程 和 提交offset的过程 放在一个事务里面进行，这样就可以保证不出现 消费丢失 和 重复消费 问题了。

如果将offset保存在MySQL中，那么表的列应该是【消费者组，topic，分区，offset】。

#### High Watermark（高水位）和 LEO（Long End Offset）是什么？

当Follower正在同步Leader数据时，Leader挂了，这时Follower们只同步到了部分数据，并且每个follower同步到的数据量还不相同，这时当Follower重新选举出Leader之后，消费该如何消费新Leader中的数据是个问题，High Watermark就是所有副本中数据的最小序号，**只有High Watermark之前的数据才对消费者可见**，从而保证无论哪个follower被选为leader之后，消费者都可以正常消费数据。

LEO（Long End Offset）指的是每个副本数据中的最大序号，当新Leader产生之后，Leader和Follower会首先同步到最大的LEO处，然后再向生产者发送ack，以免让生产者重复发送太多数据。

#### 如何保证消费者消费消息的顺序性？

分区内消息是有序的，分区之间消息是无序的，可以通多定义message的key来保证相同 key 的 message 发送到同一个 Partition。

如果想要保证全局有序就只能有一个分区，并且还要开启Kafka的幂等性，保证消息不能乱序。不过，绝大多数业务都不需要保证全局有序，只需要保证局部有序。

#### Kafka怎么实现Exactly Once？

生产者和Kafka之间的Exactly Once：

1.生产者设置acks=all，保证生产者和Kafka之间不丢失消息

2.Kafka开启幂等保证消息不重复，但是幂等不能保证跨会话消息不重复，如果想要保证跨会话消息不重复还要开启事务。

Kafka和消费者之间的Exactly Once有两种方式：

- 如果是先消费再提交offset，那么需要保证消费者消费消息的幂等性

- 把消费者消费和提交offset的过程放在一个外部事务之中，比如把offset保存在MySQL中，然后消费者消费消息的结果也是保存在MySQL中的话，可以把这两步操作都包含在MySQL的事务中。

如果消费者是Flink，那么就是Flink的Source端把offset保存在状态后端，然后Flink的Sink端开启幂等写入或者事务型写入，对于Flink内部，基于Flink的state和checkpoint机制可以实现Flink内部的状态一致性，从而使得 Flink -> Kafka -> Flink的数据链路实现Exactly once。

如果消费者是Flink，具体一点：

如果是先消费再提交offset，就可能出现重复消费的情况，那么需要保证消费者消费消息的幂等性。Flink的Source端把offset保存在状态后端，然后Flink的Sink端开启幂等写入，比如数据库的唯一主键可以阻止重复的插入操作，Redis的setnx命令的语义本事就具有幂等性。

如果是先提交offset再消费消息，就可能出现消息丢失的情况，把消费者消费和提交offset的过程放在一个外部事务之中。Flink的Source端把offset保存在状态后端，然后Flink的Sink端开启事务性（Transactional）写入，事务的开始对应着保存checkpoint的开始，checkpoint真正完成时事务结束，这时才把所有结果提交到sink所连接的外部系统中。

