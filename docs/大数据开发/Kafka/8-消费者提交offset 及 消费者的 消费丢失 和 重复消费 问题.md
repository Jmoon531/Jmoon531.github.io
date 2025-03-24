---

Created at: 2021-09-08
Last updated at: 2025-03-05


---

# 8-消费者提交offset 及 消费者的 消费丢失 和 重复消费 问题


同一个消费者组里只能有一个消费者消费一个分区，不能有多个消费者消费一个分区，所以broker是以<消费者组id， topic，partition>作为key来记录每一个消费者组在此分区上的消费位置offset的，这能保证整个消费者组下线再上线后能接着继续消费。既然offset记录的是消费者消费的位置，那么offset值应该是由消费者来修改，broker只负责保存offset的值，等到下次消费者组再次上线时，由消费者读取offset值，接着继续上次的位置消费。
消费者组上线时先读取offset的值，以后每成功消费一条消费就将本地内存维护的offset加1，然后隔段时间提交offset值给broker，由broker来持久化地保存offset值。那到底何时提交offset给broker，隔段时间到底隔的是多久呢？Kafka提供好几种可供选择的策略。

1.自动提交offset
为了使我们能够专注于自己的业务逻辑， Kafka 提供了自动提交 offset 的功能。自动提交 offset 的相关参数：

* enable.auto.commit： 是否开启自动提交 offset 功能
* auto.commit.interval.ms： 自动提交 offset 的时间间隔

```
public class AutoCommitTest {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "Hadoop102:9092,Hadoop103:9092,Hadoop104:9092");
        //设置消费者组
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "AAA");
        //开启自动提交
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        //设置自动提交的时间间隔
        props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "1000");
        //指明反序列化key的类
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        //指明反序列化value的类
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        Consumer<String, String> consumer = new KafkaConsumer<>(props);
        //订阅主题
        consumer.subscribe(List.of("test-group"));
        while (true) {
            //拉取消息，参数是每次拉取消息的时间间隔
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records)
                System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
        }
    }
}
```
如果关闭自动提交，并且不使用手动提交，那么消费者就不会提交offset，于是每次重启上面这个消费者都会重新读取一次之前已经消费过的消息。

2\. 手动提交 offset

**消费者的 消费丢失 和 重复消费 问题**
自动提交的时间间隔设置的太短和太长都会有问题。设置得太短，会造成消费者还没有消费完这批数据时就提前提交，如果这时消费者挂掉了，重启后就不会继续消费上次还没有消费完的数据，而直接消费下一批数据，造成消费者消息丢失的问题（或者称为数据漏消费、消费丢失）。设置得太长，会造成消费者已经消费完这批数据，但是却迟迟没有提交，如果这时消费者挂掉了，那么重启之后消费者会将上次已经消费了的数据再次重新消费一次，这就是重复消费问题。
所以自动提交的时间间隔并不好把握，于是Kafka消费者客户端还提供了手动提交offset的方式，手动提交分为同步提交和异步提交两种方式。同步提交会阻塞当前线程，直到这批数据的offset提交成功之后，才会拉取下一批数据；异步提交新启动一个线程去提交offset，主线程并不会被阻塞，而是直接再进行下一次数据的拉取。也并不是说手动提交的两种方式不会出现消费丢失和重复消费两个问题。只是手动提交方式比起自动提交方式更加可控。 在手动提交方式中，如果先提交 offset 后消费，可能造成消费丢失问题；如果先消费后提交 offset，可能会造成重复消费问题。

2.1 同步提交
手动提交之前需要关闭自动提交
```
public class SyncCommit {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "Hadoop102:9092,Hadoop103:9092,Hadoop104:9092");
        //设置消费者组
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "AAA");
        `//关闭自动提交`
 `props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);`
        //指明序列化key的类
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        //指明序列化value的类
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        Consumer<String, String> consumer = new KafkaConsumer<>(props);
        //订阅主题
        consumer.subscribe(List.of("test-group"));
        while (true) {
            //拉取消息，参数是每次拉取消息的时间间隔
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records){
                System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
            }
           `//同步提交`
 `consumer.commitSync();`
        }
    }
}
```

2.2异步提交
同步提交会阻塞主线程，异步提交会新启动一个线程去提交，所以不会阻塞主线程，故而异步提交的吞吐量要高于图同步提交方式。
```
public class AsyncCommit {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "Hadoop102:9092,Hadoop103:9092,Hadoop104:9092");
        //设置消费者组
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "AAA");
        `//关闭自动提交`
 `props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);`
        //指明序列化key的类
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        //指明序列化value的类
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        Consumer<String, String> consumer = new KafkaConsumer<>(props);
        //订阅主题
        consumer.subscribe(List.of("test-group"));
        while (true) {
            //拉取消息，参数是每次拉取消息的时间间隔
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records){
                System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
            }
            `//异步提交`
 `consumer.commitAsync((offsets, exception) -> {`
 `if (exception != null) {`
 `System.out.println("提价失败");`
 `exception.printStackTrace();`
 `}`
 `});`
        }
    }
}
```
~~和JS以及其它所有的异步编程方式一样，~~启动一个新的线程去干活，并且提供一个回调函数，这个回调函数在收到服务器失败或者成功消息之后才会调用，并且这个回调应该是在这个新的干活的线程里被调用执行。

3\. 自定义存储 offset
以上的提交方式都是把offset存到Kafka中，其实在 Kafka 0.9 版本之前， offset 是存储在 zookeeper中的，也就是说offset存储位置并不是一定非得存储在Kafka里面，Kafka也可以让用户自定义offset的存储方式，比如将offset存储在Mysql中，这样消费数据的过程和提交offset的过程就能放在一个事务里面进行了，从而保证不出现消费丢失 和 重复消费问题。
但是自定义存储offset需要自己写读取和提交offset的代码，需要自己实现读取offset的代码是因为在消费者组分区分配时（Rebalance），消费者组里的消费者会重新分配新的分区，那么此时每个消费者就需要重新读取消费者组在该分区的消费位置，又因为自定义的存储方式，所以读取数据的过程就必须自己实现，如果不自定义，那么Kafka已经实现了这个过程，即从Kafka那里读取offset；需要自己实现提交offset的代码是因为存储方式是自定义的，所以将offset写入过程必须由用户自己实现。
因为读取offset是发生在Rebalance时，而Rebalance的过程是由Kafka控制的，所以当Rebalance完成时应该由Kafka来通知消费者重新读取offset，并且在通知时附带上分配得到的分区，这样就可以通过<消费者组，topic，分区>这个唯一标识去指定存储介质里面取offset的值了。比如将offset保存在MySQL中，那么表的列应该是【消费者组，topic，分区，offset】。
```
public class CustomCommit {
    //在本地维护的offset
    private static Map<TopicPartition, Long> currentOffset = new HashMap<>();

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "Hadoop102:9092,Hadoop103:9092,Hadoop104:9092");
        //设置消费者组
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "AAA");
        //关闭自动提交
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        //指明序列化key的类
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        //指明序列化value的类
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        Consumer<String, String> consumer = new KafkaConsumer<>(props);
        //订阅主题，自定义RebalanceListener，该监听器的方法会在Rebalance之后执行
        consumer.subscribe(List.of("test-group"), new ConsumerRebalanceListener() {
            /**
             * 该方法会在发生Rebalance，并在Rebalance开始之前那个时间点执行，
             * 也就是会在consumer关闭（消费者退出消费者组）时，或者是消费者组里面有消费者取消订阅主题时被调用，
             * 所以这个方法里面应该放提交offset到自定义存储介质的代码，以免发生重复消费的问题。
             */
            @Override
            public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
                commitOffset(currentOffset);
            }

            /**
             * 这个方法会在会在Rebalance完成时执行，所以这里面应该放从自定义存储介质里面读取offset的代码
             */
            @Override
            public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
                //第一步，先清空本地维护的offset
                currentOffset.clear();
                for (TopicPartition partition : partitions) {
                    //第二步，getOffset()获取该消费者分配得到的每个分区的offset，然后告诉这个消费者
                    consumer.seek(partition, getOffset(partition));
                }
            }
        });
        while (true) {
            //拉取消息，参数是每次拉取消息的时间间隔
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records){
                System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
                //消费者每消费完一条数据就更新一下本地维护的offset的值
                currentOffset.put(new TopicPartition(record.topic(), record.partition()), record.offset());
            }
            //消费完这一批数据后就可以提交一次offset，当然你也可以每消费完一条数据后就提交，但是那样效率有点低
            commitOffset(currentOffset);
        }
    }
    //从自定义存储介质里面读取某个分区的offset并保存到本地维护的offset中
    private static long getOffset(TopicPartition partition) {
        return 0;
    }
    //提交该消费者所有分区的 offset，把本地维护的offset（即currentOffset）全部提交过去
    private static void commitOffset(Map<TopicPartition, Long> currentOffset) {

    }
}
```

