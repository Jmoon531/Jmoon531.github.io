---

Created at: 2021-10-13
Last updated at: 2025-03-02


---

# 22-ProcessFunction API


Flink提供的API的抽象层级见下图，越往下限制越小，使用越灵活，能实现的功能越多，但编程的难度越大。前面所使用的API属于Flink的Core APIs，能实现绝大多数需求，Flink还提供更加底层的API，即Stateful Stream Processing，它就是每一种流（DataStream、KeyedStream等）里面提供的process()方法，process()方法都需要传一个抽象类的实现，这些抽象类的名字中带有ProcessFunction，所以也称最底层的API为ProcessFunction API，Flink SQL 就是使用ProcessFunction 实现的。
![levels_of_abstraction.svg](https://nightlies.apache.org/flink/flink-docs-release-1.14/fig/levels_of_abstraction.svg)

Flink里有如下8个Process Function，实现特定需求的主要任务就是给如下抽象类的实现，然后传给对应流的process()方法。

* ProcessFunction
* KeyedProcessFunction
* CoProcessFunction
* ProcessJoinFunction
* BroadcastProcessFunction
* KeyedBroadcastProcessFunction
* ProcessWindowFunction
* ProcessAllWindowFunction

ProcessFunction都继承自RichFunction接口，所以它能获取到RuntimeContext。不止是RuntimeContext，ProcessFunction还可以获取当前的watermark和ProcessingTime等信息，还可设置定时器，以及自由的将数据输出到侧输出流，所以ProcessFunction功能要比富函数的提供功能更加强大。ProcessFunction处理数据的过程类似于flatMap，即一条数据的输入可以映射成零条、一条、或多条数据的输出。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
    env.setParallelism(1);
    env.socketTextStream("localhost", 7777)
            .map(new MapFunction<String, Tuple3<String, Long, Integer>>() {
                @Override
                public Tuple3<String, Long, Integer> map(String value) throws Exception {
                    String[] split = value.split(",");
                    return new Tuple3<>(split[0], Long.parseLong(split[1]), Integer.parseInt(split[2]));
                }
            })
            .assignTimestampsAndWatermarks(new BoundedOutOfOrdernessTimestampExtractor<Tuple3<String, Long, Integer>>(`Time.seconds(2)`) {
                @Override
                public long extractTimestamp(Tuple3<String, Long, Integer> element) {
                    return element.f1;
                }
            })
            .keyBy(0)
            .process(`new MyKeyedProcessFunction()`)
            .print();
    env.execute();
}
```
使用ProcessFunction获取Keyed State、watermark、ProcessingTime 和 设置定时器的示例程序如下。**需要特别注意的是processElement()和onTimer()中拿到的watermark并不相等，这是因为数据来了之后会立即向下游传递，此时在processElement()处理该数据时拿到的watermark还是之前的watermark，并不是基于此条数据算出来的watermark；之后生成watermark的周期到了，此时更新watermark向下游传递，于是定时器触发，所以在onTimer()中拿到的watermark一定是最新的。**所以不能在processElement()方法中通过定时器有没有触发这一条件，来判断本条数据与上一条设置该定时器时处理的数据之间的时间间隔有没有达到定时器触发延时。
```
static class MyKeyedProcessFunction `extends KeyedProcessFunction`<Tuple, Tuple3<String, Long, Integer>, String> {

    ValueState<Long> tsTimerState;

    @Override
    public void open(Configuration parameters) throws Exception {
        tsTimerState = getRuntimeContext().getState(new ValueStateDescriptor<Long>("ts-timer", Long.class));
    }

    @Override
    public void processElement(Tuple3<String, Long, Integer> value, Context ctx, Collector<String> out) throws Exception {
        //getRuntimeContext()
        `// 通过Context对象拿到时间戳，这个值就是数据中的时间戳，所以也可以通过传进来的数据value拿到，`
 `// 使用ctx.timestamp()拿到时间戳的要求是时间语义得是EventTime，不然获取到的就是null`
 `Long ctxTimestamp = ctx.timestamp();`
        Tuple currentKey = ctx.getCurrentKey();
        TimerService timerService = ctx.timerService();
        long processingTime = timerService.currentProcessingTime();
        `// 这时拿到的watermark并不是基于这条数据生成的watermark，`
 `// 因为数据来的时候并不会立即生成watermark，而是要等到生成watermark的周期到了之后才会生成，`
 `// 也就是数据来了之后会立即向下游传递，而watermark需要等待周期到了生成之后才会向下游传递`
 `long watermark = timerService.currentWatermark();`
        out.collect("processingTime=" + processingTime +
                ", currentKey=" + currentKey +
                ", ctxTimestamp=" + ctxTimestamp +
                ", watermark=" + watermark);
        //将定时器的时间放在键控状态中，以便后面可以取消定时器
        tsTimerState.update(processingTime + 1000L); //当前processingTime后1s触发定时器
        //设置定时器
        timerService.registerProcessingTimeTimer(tsTimerState.value());
        //根据定时器设置的时间点取消定时器
        //timerService.deleteProcessingTimeTimer(tsTimerState.value());
    }

    //定时器触发所执行的方法
    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<String> out) throws Exception {
        `//这时候拿到的watermark才是最新的watermark（基于前面那条数据算出来的watermark）`
 `long watermark = ctx.timerService().currentWatermark();`
        TimeDomain timeDomain = ctx.timeDomain();
        Tuple currentKey = ctx.getCurrentKey();
        out.collect("定时器触发" +
                ", timestamp=" + timestamp +
                ", currentKey=" + currentKey +
                ",timeDomain=" + timeDomain +
                ", watermark=" + watermark);
    }

    @Override
    public void close() throws Exception {
        tsTimerState.clear();
        super.close();
    }
}
```
输入：
```
k1,1633947870000,1
k1,1633947872000,1
```
输出：
```
processingTime=1634526697096, currentKey=(k1), ctxTimestamp=1633947870000, `watermark=-9223372036854775808`
定时器触发, timestamp=1634526698096, currentKey=(k1),timeDomain=PROCESSING_TIME, `watermark=1633947868000`
processingTime=1634526708474, currentKey=(k1), ctxTimestamp=1633947872000, `watermark=1633947868000`
定时器触发, timestamp=1634526709474, currentKey=(k1),timeDomain=PROCESSING_TIME, `watermark=1633947870000`
```

**使用ProcessFunction实现分流的操作**，类似于DataStream的split 和 select，DataStream的split 和 select已经弃用，推荐使用ProcessFunction实现分流，实现方式是输出到侧输出流中。
以a开头的数据输出到侧输出流aStream中，以b开头的数据输出到侧输出流bStream中，剩下的保留在主流中：
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
    env.setParallelism(1);
    OutputTag<String> aStreamTag = new OutputTag<>("a-stream") {};
    OutputTag<String> bStreamTag = new OutputTag<>("b-stream") {};
    SingleOutputStreamOperator<String> mainStream = env.socketTextStream("localhost", 7777)
            .process(new ProcessFunction<String, String>() {
                @Override
                public void processElement(String value, Context ctx, Collector<String> out) throws Exception {
                    if (value.startsWith("a")) {
                        ctx.output(aStreamTag, value);
                    } else if (value.startsWith("b")) {
                        ctx.output(bStreamTag, value);
                    } else {
                        out.collect(value);
                    }
                }
            });
    mainStream.print("main-stream");
    DataStream<String> aStream = mainStream.getSideOutput(aStreamTag);
    aStream.print("a-stream");
    DataStream<String> bStream = mainStream.getSideOutput(bStreamTag);
    bStream.print("b-stream");
    env.execute();
}
```
输入：
```
aaa
bbb
ddd
```
输出：
```
a-stream> aaa
b-stream> bbb
main-stream> ddd
```

**案例：监控温度传感器的温度值，如果温度值在 10 秒钟之内连续上升， 则报警。**
分析：使用滚动窗口肯定是不行的，如果使用滑动窗口那么需要将滑动步长设置为1ms，效率太低，这里可以使用定时器完成这个需求，10s的时间语义既可以是EventTime也可以是ProcessingTime。
```
// 传感器类
@Data
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class SensorReading {
    // 属性：id，时间戳，温度值
    private String id;
    private Long timestamp;
    private Double temperature;
}
```
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(1);
    env.socketTextStream("localhost", 7777)
            .map(line -> {
                String[] fields = line.split(",");
                return new SensorReading(fields[0], Long.parseLong(fields[1]), Double.parseDouble(fields[2]));
            })
            .keyBy("id")
            .process(new MyProcess())
            .print();
    env.execute();
}
```
```
// 实现自定义的ProcessFunction函数
static class MyProcess extends KeyedProcessFunction<Tuple, SensorReading, String> {
    ValueState<Double> temperatureState;
    ValueState<Long> timerState;

    @Override
    public void open(Configuration parameters) throws Exception {
        temperatureState = getRuntimeContext().getState(new ValueStateDescriptor<>("temperature-state", Double.class));
        timerState = getRuntimeContext().getState(new ValueStateDescriptor<>("timer-state", Long.class));
    }

    @Override
    public void processElement(SensorReading value, Context ctx, Collector<String> out) throws Exception {
        //上一次的温度值
        Double lastTemperature = temperatureState.value();
        //现在的温度值
        Double nowTemperature = value.getTemperature();
        //无论怎样都要把本次温度记录到键控状态中，作为下一次的上一次温度值
        temperatureState.update(nowTemperature);
        //如果是系统刚启动，那么第一次没有上一次温度值，直接返回
        if (lastTemperature == null) {
            return;
        }
        double diffTemperature = nowTemperature - lastTemperature;
        // 如果温度上升了并且没有注册定时器，那么表示这是第一次上升，
        // 所以要注册以当前ProcessingTime为起始的10s后触发的定时器，
        // 如果10s内该定时器没有被删除就表示温度连续7        //如果这时温度下降了，并且还有定时器，则表示这是10s内第一次下降，所以本次需要删除定时器，
        if (diffTemperature < 0 && timerState.value() != null) {
            ctx.timerService().deleteProcessingTimeTimer(timerState.value());
            timerState.clear();
        }
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<String> out) throws Exception {
        out.collect(ctx.getCurrentKey() + "传感器：" + timestamp + " - " + (timestamp + 10 * 1000L) + "内温度连续上升");
        timerState.clear();
    }

    @Override
    public void close() throws Exception {
        timerState.clear();
        temperatureState.clear();
    }
}
```
输入：
```
sensor_1,1633947870000,1
sensor_1,1633947870000,2
sensor_1,1633947870000,0
```
输出：
```
(sensor_1)传感器：1634178742772 - 1634178752772内温度连续上升
```

