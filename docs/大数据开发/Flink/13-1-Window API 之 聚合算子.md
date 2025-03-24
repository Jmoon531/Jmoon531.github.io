---

Created at: 2021-10-10
Last updated at: 2025-03-02


---

# 13-1-Window API 之 聚合算子


KeyedStream调用window()、countWindow() 和 timeWindow()方法开窗之后就变成了WindowedStream，WindowedStream并不继承自KeyedStream，所以WindowedStream与 KeyedStream 和 DataStream 并没有继承关系。WindowedStream 和 KeyedStream 一样有sum()、min()、max()、minBy()、maxBy() 以及 reduce() 这些聚合算子，它们功能都是相似的，但是基于两个流各自的特点，所以这些聚合算子都是在各自类中独立实现。并且由于只有 DataStream 及其子类如 KeyedStream 才有Sink，所以WindowedStream必须调用聚合算子做聚合运算转换成 DataStream 之后才可以输出结果，也就是说开窗的唯一目的就是做聚合运算。
WindowedStream的聚合算子需要传入的函数分为两类： 增量聚合函数（ incremental aggregation functions）和 全窗口函数（ full window functions）。
增量聚合函数包括：ReduceFunction 和 AggregateFunction。增量聚合的意思是，窗口中每来一条数据，算子就会调用增量聚合函数对数据进行一次计算，每次计算都会保存中间结果，这个中间结果称为状态，也就是每次计算其实是对该状态的更新。
全窗口函数包括：ProcessWindowFunction 和 WindowFunction。全窗口聚合的意思是，窗口中每来一条数据，算子并不会立即进行计算，而是先把窗口内的所有数据收集起来，等到窗口关闭时再调用全窗口函数遍历所有数据一次性地计算，类似于批处理。全窗口函数没有增量聚合函数计算效率高，因为全窗口函数要等到窗口内的数据都到齐了之后才计算，但是使用全窗口函数可以拿到窗口对象的信息，并且有些需求只能使用全窗口函数来解决。而且ProcessWindowFunction属于ProcessFunctionAPI，不仅继承自RichFunction，还提供其它很多功能。

**reduc****e()**需要传入ReduceFunction接口的实现，使用reduce算子实现sum的功能：
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
    //时间间隔为3s的滚动时间窗口
    WindowedStream<Tuple2<String, Integer>, Tuple, TimeWindow> timeWindow = keyedStream.timeWindow(Time.seconds(3));
    DataStream<Tuple2<String, Integer>> result = timeWindow.reduce(`new ReduceFunction<Tuple2<String, Integer>>() {`
 `@Override`
 `public Tuple2<String, Integer> reduce(Tuple2<String, Integer> value1, Tuple2<String, Integer> value2) throws Exception {`
 `return new Tuple2<>(value1.f0, value1.f1 + value2.f1);`
 `}`
 `}`);
    result.print();
    env.execute();
}
```

**aggregate()**需要传入AggregateFunction 接口的实现，AggregateFunction的三个泛型参数是输入数据的类型，中间状态的类型，输出数据的类型。aggregate() 和 reduce() 都是增量聚合，但是 aggregate() 因为可以自定义中间状态，所以输出类型可以与输入类型不同，而reduce()不能自定义中间状态，于是输出类型必须与输入类型相同，也就是说aggregate() 比 reduce()更灵活，需要注意的是虽然reduce()不能自定义中间状态，但是它也是有中间状态的，因为它也是增量聚合，其reduce的返回值就是它的中间状态。
使用aggregate()计算输入数据的平均值：
```
// 中间状态
public class AverageAccumulator {
    public String id;
    public Integer count = 0;
    public Integer sum = 0;
}
```
每一个分组一个窗口，随着时间的推移，每个分组的窗口在不断地开启和关闭，窗口开启时会调用createAccumulator()方法创建此窗口的中间状态，窗口关闭时会调用getResult()方法返回结果。这个中间状态与键控状态有一点类似，即它们都对应于每个分组，但是窗口聚合函数的这个中间状态不会被保存在checkpoint，因为WindowedStream的每个窗口视为一个有界流中，这个中间状态只为聚合本窗口内数据而存在，它会随着这个分组的窗口的开启与关闭而创建和销毁；而键控状态可以保存在checkpoint中，因为键控状态只能用于KeyedStream，KeyedStream是无界流，键控状态需要在整个应用计算期间有效。注意aggregate()不能传入RichAggregateFunction。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<String> dataStream = env.socketTextStream("localhost", 7777);
    // k1,1
    // k1,2
    // k1,3
    KeyedStream<Tuple2<String, Integer>, Tuple> keyedStream = dataStream.map(new MapFunction<String, Tuple2<String, Integer>>() {
        @Override
        public Tuple2<String, Integer> map(String value) throws Exception {
            String[] split = value.split(",");
            return new Tuple2<>(split[0], Integer.parseInt(split[1]));
        }
    }).keyBy(0);
    //时间间隔为5s的滚动时间窗口
    WindowedStream<Tuple2<String, Integer>, Tuple, TimeWindow> timeWindow = keyedStream.timeWindow(Time.seconds(5));
    DataStream<Tuple2<String, Double>> result = timeWindow.aggregate(new AggregateFunction<Tuple2<String, Integer>, AverageAccumulator, Tuple2<String, Double>>() {

        //新开启一个窗口时会调用此方法创建中间状态
        @Override
        public AverageAccumulator createAccumulator() {
            return new AverageAccumulator();
        }

        //累加，即增量聚合，窗口中每来一条数据就会调用一次
        @Override
        public AverageAccumulator add(Tuple2<String, Integer> value, AverageAccumulator acc) {
            acc.id = value.f0;
            acc.count++;
            acc.sum += value.f1;
            return acc;
        }

        //窗口的关闭时调用此方法返回结果
        @Override
        public Tuple2<String, Double> getResult(AverageAccumulator acc) {
            return new Tuple2<>(acc.id, acc.sum * 1.0 / acc.count);
        }

        // 合并两个中间状态，这个方法只在会话窗口中会被调用，其它类型的窗口不需要合并，可以直接返回null
        // 会话窗口会为每一批相邻两条数据没有大于指定间隔时间的数据merge到以一起，
        @Override
        public AverageAccumulator merge(AverageAccumulator a, AverageAccumulator b) {
            a.sum += b.sum;
            a.count += b.count;
            return a;
        }
    });
    result.print();
    env.execute();
}
```
aggregate()传入增量聚合函数AggregateFunction的同时，还可以传入全窗口函数ProcessWindowFunction 或 WindowFunction。其计算过程是，窗口关闭时，AggregateFunction增量聚合的结果会作为全窗口函数的输入（在一个窗口内进行，不是所有窗口增量聚合的结果全部输入到一个全窗口函数中，所以此时AggregateFunction的apply方法的第三个参数Iterable里面一定是只有一个元素），然后再由全窗口函数处理后输出到DataStream。所以使用传两个参数的aggregate()不仅有增量聚合函数实时计算和占用内存低的优点，而且还可以在计算的第二步中通过全窗口函数拿到窗口对象等其它很多有用的信息。
WindowedStream其它聚合算子：sum()、min()、max()、minBy()、maxBy() 的实现都是直接调用aggregate()，只是传递的参数不同。

**apply()**需要传入 WindowFunction接口的实现，WindowFunction的4个泛型参数分别是：输入数据的类型、输出数据的类型、分组key的类型、窗口的类型。以下使用apply()计算平均值，并带上窗口的起始时间。
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
    SingleOutputStreamOperator<Tuple3<String, String, Double>> result = timeWindow.apply(new WindowFunction<Tuple2<String, Integer>, Tuple3<String, String, Double>, Tuple, TimeWindow>() {
        @Override
        public void apply(Tuple key, TimeWindow window, Iterable<Tuple2<String, Integer>> input, Collector<Tuple3<String, String, Double>> out) throws Exception {
            int sum = 0;
            int count = 0;
            for (Tuple2<String, Integer> tuple2 : input) {
                sum += tuple2.f1;
                count++;
            }
            double avg = sum * 1.0 / count;
            //分组字段,窗口的起始时间,平均值
            out.collect(new Tuple3<>(key.getField(0), String.valueOf`(window.getStart()`), avg));
        }
    });
    result.print();
    env.execute();
}
```

