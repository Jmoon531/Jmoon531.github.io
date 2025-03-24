---

Created at: 2021-10-16
Last updated at: 2021-10-16


---

# 13-2-Window API 之 Trigger 和 Evictor


我们知道开窗的唯一目的就是对窗口中的数据进行聚合，trigger() 和 evictor() 是 AllWindowedStream 和 WindowedStream中的方法，在开窗之后，使用窗口聚合算子之前使用。
trigger() 可以决定窗口聚合算子什么时候被调用，比如apply()传入的WindowFunction默认是全窗口聚合，但是在apply()之前使用trigger()可以改变窗口聚合函数调用的时机，比如每来一条数据就调用一次：
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<String> dataStream = env.socketTextStream("localhost", 7777);
    KeyedStream<Tuple2<String, Integer>, Tuple> keyedStream = dataStream.map(new MapFunction<String, Tuple2<String, Integer>>() {
        @Override
        public Tuple2<String, Integer> map(String value) throws Exception {
            String[] split = value.split(",");
            return new Tuple2<>(split[0], Integer.parseInt(split[1]));
        }
    }).keyBy(0);
    //时间间隔为5s的滚动时间窗口
    WindowedStream<Tuple2<String, Integer>, Tuple, TimeWindow> timeWindow = keyedStream.timeWindow(Time.seconds(5));
    SingleOutputStreamOperator<Tuple3<String, String, Integer>> result = timeWindow
            .trigger(new Trigger<Tuple2<String, Integer>, TimeWindow>() {

                `//窗口中每来一条元素就会调用`
                @Override
                public TriggerResult onElement(Tuple2<String, Integer> element, long timestamp, TimeWindow window, TriggerContext ctx) throws Exception {
                    return TriggerResult.FIRE;
                }

                `//使用TriggerContext的registerProcessingTimeTimer()注册的定时器触发时会调用`
                @Override
                public TriggerResult onProcessingTime(long time, TimeWindow window, TriggerContext ctx) throws Exception {
                    return TriggerResult.CONTINUE;
                }

                `//使用TriggerContext的registerEventTimeTimer()注册的定时器触发时会调用`
                @Override
                public TriggerResult onEventTime(long time, TimeWindow window, TriggerContext ctx) throws Exception {
                    return TriggerResult.CONTINUE;
                }

                `//清理触发器持有的状态，比如删除使用TriggerContext.registerEventTimeTimer(long)Trigger.TriggerContext.registerProcessingTimeTimer(long)设置的定时器`
 `//或者使用TriggerContext.getPartitionedState(StateDescriptor)获得的状态`
                @Override
                public void clear(TimeWindow window, TriggerContext ctx) throws Exception {
                }
            })
            .apply(new WindowFunction<Tuple2<String, Integer>, Tuple3<String, String, Integer>, Tuple, TimeWindow>() {
                @Override
                public void apply(Tuple key, TimeWindow window, Iterable<Tuple2<String, Integer>> input, Collector<Tuple3<String, String, Integer>> out) throws Exception {
                    int sum = 0;
                    for (Tuple2<String, Integer> tuple2 : input) {
                        sum += tuple2.f1;
                    }
                    out.collect(new Tuple3<>(key.getField(0), String.valueOf(window.getStart()), sum));
                }
            });
    result.print();
    env.execute();
}
```
TriggerResult是一个枚举类，有4个取值：
```
public enum TriggerResult {

   //不触发窗口聚合
   CONTINUE(false, false),

   //触发窗口聚合并清除窗口中的数据
   FIRE_AND_PURGE(true, true),

   //触发窗口聚合
   FIRE(true, false),

   //清除窗口中的数据
   PURGE(false, true);
}
```

evictor()方法传入的Evictor接口实现的两个方法分别在窗口函数调用前后执行，用于过滤数据，在窗口函数执行后执行的目的应该是因为在允许迟到时间内到来的数据会调用窗口函数。

