---

Created at: 2021-10-05
Last updated at: 2021-10-05
Source URL: about:blank


---

# 26-SparkStreaming获取数据的方式


WordCount
1.从套接字中采集数据
```
def main(args: Array[String]): Unit = {
  // TODO 创建环境对象
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("SparkStreaming")
  // StreamingContext创建时，需要传递两个参数，第一个参数表示环境配置，第二个参数表示批量处理的周期（采集周期）
  val ssc: StreamingContext = new StreamingContext(sparkConf, Seconds(3))

  // TODO 逻辑处理
  // 获取端口数据
  val lines: ReceiverInputDStream[String] = ssc.socketTextStream("localhost", 9999)
  val words = lines.flatMap(_.split(" "))
  val wordToOne = words.map((_,1))
  val wordToCount: DStream[(String, Int)] = wordToOne.reduceByKey(_+_)
  wordToCount.print()

  // 由于SparkStreaming采集器是长期执行的任务，所以不能直接关闭ssc.stop()
  // 1. 启动采集器
  ssc.start()
  // 2. 等待采集器的关闭
  ssc.awaitTermination()
}
```
通过 netcat 发送数据：
```
nc -l -p 9999
```

2.从队列中采集数据
```
def main(args: Array[String]): Unit = {
  // TODO 创建环境对象
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("SparkStreaming")
  // StreamingContext创建时，需要传递两个参数，第一个参数表示环境配置，第二个参数表示批量处理的周期（采集周期）
  val ssc: StreamingContext = new StreamingContext(sparkConf, Seconds(3))

  val rddQueue = new mutable.Queue[RDD[Int]]()

  val inputStream: InputDStream[Int] = ssc.queueStream(rddQueue, oneAtATime = false)
  val mappedStream: DStream[(Int, Int)] = inputStream.map((_, 1))
  val reducedStream: DStream[(Int, Int)] = mappedStream.reduceByKey(_ + _)
  reducedStream.print()

  ssc.start()

  for (_ <- 1 to 5) {
    rddQueue += ssc.sparkContext.makeRDD(1 to 300, 10)
    Thread.sleep(2000)
  }

  ssc.awaitTermination()
}
```

3使用自定义数据采集器
```
/**
* 自定义数据采集器
* 1. 继承Receiver，定义泛型, 传递参数
* 2. 重写方法
*/
class MyReceiver extends Receiver[String](StorageLevel.MEMORY_ONLY) {
  private var flag = true

  override def onStart(): Unit = {
    new Thread(() => {
      while (flag) {
        val message = "采集的数据为：" + new Random().nextInt(10).toString
        store(message)
        Thread.sleep(500)
      }
    }).start()
  }

  override def onStop(): Unit = {
    flag = false;
  }
}
```
```
def main(args: Array[String]): Unit = {
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("SparkStreaming")
  val ssc = new StreamingContext(sparkConf, Seconds(3))

  //使用自定义数据采集器
  val messageDS: ReceiverInputDStream[String] = ssc.receiverStream(new MyReceiver())
  messageDS.print()

  ssc.start()
  ssc.awaitTermination()
}
```

4.从Kafka中获取数据
引入依赖
```
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-streaming-kafka-0-10_2.12</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-core</artifactId>
    <version>2.10.1</version>
</dependency>
```
```
def main(args: Array[String]): Unit = {
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("SparkStreaming")
  val ssc: StreamingContext = new StreamingContext(sparkConf, Seconds(3))

  //Kafka 参数
  val kafkaPara: Map[String, Object] = Map[String, Object](
    ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG -> "hadoop102:9092,hadoop103:9092,hadoop104:9092",
    ConsumerConfig.GROUP_ID_CONFIG -> "ssc",
    "key.deserializer" -> "org.apache.kafka.common.serialization.StringDeserializer",
    "value.deserializer" -> "org.apache.kafka.common.serialization.StringDeserializer"
  )

  //创建用于读取Kafka topic数据的DStream
  val kafkaDataDS: InputDStream[ConsumerRecord[String, String]] = KafkaUtils.createDirectStream[String, String](
    ssc,
    LocationStrategies.PreferConsistent,
    ConsumerStrategies.Subscribe[String, String](Set("spark-streaming"), kafkaPara)
  )

  //将每条消息的value取出
  kafkaDataDS.map(_.value()).print()
  ssc.start()
  ssc.awaitTermination()
}
```

