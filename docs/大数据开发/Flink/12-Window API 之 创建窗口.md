---

Created at: 2021-10-09
Last updated at: 2021-10-11


---

# 12-Window API 之 创建窗口


DataStream数据流并不对数据进行区分，所以如果对DataStream开窗，那么在对窗口进行计算时，必须要求所有数据都到这个窗口中来，于是DataStream只有windowAll()、timeWindowAll()、countWindowAll()三个方法，即所有数据都到同一个窗口中，也就是接下来基于窗口的计算会将所有数据汇聚到一个slot的任务中去。
windowAll()是创建窗口的通用方法，可以使用windowAll()创建时间窗口和计数窗口，timeWindowAll() 和 countWindowAll() 是对 windowAll()的封装，方便调用直接创建 时间窗口 和 计数窗口。
只有经过keyBy算子将DataStream转换成KeyedStream之后，才能在不同的窗口里对数据进行计算，而不是将所有数据汇聚到一个窗口中去，因为keyBy会对数据进行分组，所以对KeyedStream开窗后，同一个窗口里面都是同一组数据，不同组的数据会进入到不同窗口中去，也就是一个组会有一个窗口（并不是指开窗后下一步对窗口计算的算子的一个子任务里面只有一个窗口，事实上一个子任务中可有多个窗口的数据，也就是一个子任务中可以有多个组的数据），所以一般不建议直接对DataStream开窗，而应该对KeyedStream进行开窗。
KeyedStream有window()、countWindow() 和 timeWindow() 三个方法用于开窗，window()是创建窗口的通用方法， timeWindow() 和 countWindow() 是对 window()的封装，方便调用直接创建 时间窗口 和 计数窗口。

KeyedStream的window()方法的定义如下，需要传入抽象类WindowAssigner（ 窗口分配器）的一个子类对象。
```
public <W extends Window> WindowedStream<T, KEY, W> window(`WindowAssigner`<? super T, W> assigner) {
   return new WindowedStream<>(this, assigner);
}
```
抽象类WindowAssigner主要有7个具体的子类：

* SlidingProcessingTimeWindows
* SlidingEventTimeWindows
* TumblingEventTimeWindows
* TumblingProcessingTimeWindows
* ProcessingTimeSessionWindows
* EventTimeSessionWindows
* GlobalWindows

前面4个是用来创建时间窗口的，其中Sliding表示滑动窗口，Tumbling表示滚动窗口，ProcessingTime表示窗口的时间语义是数据到达窗口的时间，EventTime表示窗口的时间语义是数据产生时的时间。第5个和第6个是用来创建会话窗口的。最后一个GlobalWindows是用来创建计数窗口的。

比如创建 滚动时间窗口 和 滑动时间窗口，滚动窗口需要传递1个参数，滑动窗口需要传递2个参数。
```
//时间间隔为10s的滚动时间窗口
keyedStream.window(`TumblingProcessingTimeWindows.of(Time.seconds(10))`);
keyedStream.window(`TumblingEventTimeWindows.of(Time.seconds(10))`);
//时间间隔为10s，步长为5s的滑动时间窗口
keyedStream.window(`SlidingProcessingTimeWindows.of(Time.seconds(10), Time.seconds(5))`);
keyedStream.window(`SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5))`);
```

创建会话窗口：
```
//时间间隔为10s的会话窗口
keyedStream.window(`EventTimeSessionWindows.withGap(Time.seconds(10))`);
keyedStream.window(`ProcessingTimeSessionWindows.withGap(Time.seconds(10))`);
```

创建滚动计数窗口 和 滑动计数窗口
```
//计数为10的滚动计数窗口
keyedStream.window(`GlobalWindows.create()`).`trigger(PurgingTrigger.of(CountTrigger.of(10)))`;
//计数为10，步长为5的滑动计数窗口
keyedStream.window(`GlobalWindows.create()`).`evictor(CountEvictor.of(10))`.`trigger(CountTrigger.of(5))`;
```

直接使用KeyedStream的window()方法来创建窗口比较繁琐，所以建议直接使用 timeWindow() 和 countWindow() 来创建 时间窗口 和 计数窗口。注意会话窗口虽然属于时间窗口，但是并不能使用timeWindow()创建，只能使用window()方法创建。
比如创建 滚动时间窗口 和 滑动时间窗口：
```
//时间间隔为10s的滚动时间窗口
keyedStream.`timeWindow(Time.seconds(10));`
//时间间隔为10s，步长为5s的滑动时间窗口
keyedStream.`timeWindow(Time.seconds(10), Time.seconds(5))`;
```
在使用 timeWindow() 创建窗口时，无法直接指定是ProcessingTime 还是 EventTime，这需要在在运行环境中指定，默认是TimeCharacteristic.ProcessingTime，即以数据到达窗口的时间为准。
```
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.setStreamTimeCharacteristic(`TimeCharacteristic.EventTime`);
env.setStreamTimeCharacteristic(`TimeCharacteristic.ProcessingTime`);
```
因为timeWindow()会根据环境的时间属性来创建对应的类型窗口，timeWindow()的源码：
```
public WindowedStream<T, KEY, TimeWindow> timeWindow(Time size) {
   if (environment.getStreamTimeCharacteristic() == TimeCharacteristic.ProcessingTime) {
      return window(TumblingProcessingTimeWindows.of(size));
   } else {
      return window(TumblingEventTimeWindows.of(size));
   }
}
```

创建 滚动计数窗口 和 滑动计数窗口：
```
//计数为10的滚动计数窗口
keyedStream`.countWindow(10);`
//计数为10，步长为5的滑动计数窗口
keyedStream`.countWindow(10, 5);`
```

