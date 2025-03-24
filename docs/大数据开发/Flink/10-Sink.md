---

Created at: 2021-10-09
Last updated at: 2021-10-09


---

# 10-Sink


Sink就是将数据输出，通用的添加Sink的方法是DataStream的addSink方法，addSink方法需要传入一个实现了SinkFunction接口的类，主要是实现SinkFunction接口的invoke方法。
1.print
print其实是addSink(new PrintSinkFunction<>())，PrintSinkFunction继承自抽象类RichSinkFunction，RichSinkFunction实现了SinkFunction接口，RichSinkFunction是比SinkFunction接口功能更丰富的富函数。
```
@PublicEvolving
public DataStreamSink<T> print() {
   PrintSinkFunction<T> printFunction = new PrintSinkFunction<>();
   return addSink(printFunction).name("Print to Std. Out");
}
```

2.writeToSocket
writeToSocket其实是addSink(new SocketClientSink<>(hostName, port, schema)
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.fromElements(1, 2, 3)
            .broadcast()
            .map(Object::toString)
            .writeToSocket("hadoop102", 7777, new SimpleStringSchema());
    env.execute();
}
```

将数据输出到外部系统可以自定义Sink，也可以直接导入官方已经写好的依赖
3.Kafka Sink
引入依赖
```
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-kafka-0.11_2.12</artifactId>
    <version>1.10.1</version>
</dependency>
```

```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.fromElements(1, 2, 3, 4, 5, 6, 7, 8, 9)
            .map(Objects::toString)
            `.addSink(new FlinkKafkaProducer011<>("hadoop102:9092", "flink-topic", new SimpleStringSchema()));`
    env.execute();
}
```

4.自定义Sink
比如自定义Sink将数据写到MySQL，继承RichSinkFunction可以在open方法中回去MySQL的连接，open方法只会在Sink的每个子任务开始时执行一次，而invoke方法会在每一条数据到来的时候执行。
```
public class MySQLSink extends RichSinkFunction<Tuple3<Integer, String, Integer>> {
    // 声明连接和预编译语句
    Connection connection = null;
    PreparedStatement preStmt = null;

    @Override
    public void open(Configuration parameters) throws Exception {
        connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/test?serverTimezone=UTC&characterEncoding=utf-8", "root", "079335");
        preStmt = connection.prepareStatement(`"insert into user (id, name, age) values (?, ?, ?) on DUPLICATE KEY UPDATE name=?, age=?"`);
    }

    @Override
    public void close() throws Exception {
        preStmt.close();
        connection.close();
    }

    @Override
    public void invoke(Tuple3<Integer, String, Integer> value, Context context) throws Exception {
        preStmt.setInt(1, value.f0);
        preStmt.setString(2, value.f1);
        preStmt.setInt(3, value.f2);
        preStmt.setString(4, value.f1);
        preStmt.setInt(5, value.f2);
        preStmt.execute();
    }
}
```
测试，插入一条数据，如果主键重复则更新数据：
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.fromElements(
            new Tuple3<>(1, "zhangsan", 18),
            new Tuple3<>(2, "lisi", 19),
            new Tuple3<>(3, "wangwu", 20)
    )`.addSink(new MySQLSink());`
    env.execute();
}
```

