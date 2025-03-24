---

Created at: 2021-10-08
Last updated at: 2022-07-12


---

# 8-DataStream 的 Transform 算子（续）


以下算子均是对多条流的操作：Split 和 Select、Connect 和 CoMap、Union

**7.Split 和 Select**
split算子 和 SplitStream的select算子 搭配使用可以实现分流的效果。split算子按条件给流的每一个数据打上标签，一个数据可以有多个标签，用集合表示；然后使用SplitStream的select算子拿到标签对应的流。split算子会将DataStream转化成SplitStream，SplitStream是DataStream的子类，SplitStream的select算子会将SplitStream转换成DataStream，SplitStream只有select这一个方法可以调用。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Tuple2<Character, Integer>> tuple2DataStream = env.fromCollection(Arrays.asList(
            new Tuple2<>('a', 1), new Tuple2<>('b', 2), new Tuple2<>('c', 3),
            new Tuple2<>('d', 4), new Tuple2<>('e', 5), new Tuple2<>('f', 6)
    ));
    `SplitStream`<Tuple2<Character, Integer>> splitStream = `tuple2DataStream.split(tuple2 -> {`
 `if (tuple2.f1 <= 2) {`
 `return List.of("one", "<=2");`
 `} else if (tuple2.f1 <= 4) {`
 `return List.of("two", ">2 && <=4");`
 `} else {`
 `return List.of("three", ">4");`
 `}`
 `});`

    DataStream<Tuple2<Character, Integer>> oneStream = splitStream`.select("one");`
    DataStream<Tuple2<Character, Integer>> twoStream = splitStream`.select("two");`
    DataStream<Tuple2<Character, Integer>> threeStream = splitStream`.select("three");`
    oneStream.print("oneStream");
    twoStream.print("twoStream");
    threeStream.print("threeStream");

    DataStream<Tuple2<Character, Integer>> stream01 = splitStream`.select("<=2");`
    DataStream<Tuple2<Character, Integer>> stream02 = splitStream`.select(">2 && <=4");`
    DataStream<Tuple2<Character, Integer>> stream03 = splitStream`.select(">4");`
    stream01.print("stream01");
    stream02.print("stream02");
    stream03.print("stream03");

    env.execute();
}
```
输出：
```
oneStream:14> (a,1)
twoStream:13> (d,4)
threeStream:1> (e,5)
twoStream:12> (c,3)
oneStream:15> (b,2)
threeStream:2> (f,6)
stream01:10> (a,1)
stream01:11> (b,2)
stream02:8> (c,3)
stream02:9> (d,4)
stream03:14> (f,6)
stream03:13> (e,5)
```

**8.Connect 和 CoMap**
Connect算子 和 ConnectedStreams的map算子 搭配使用可以实现合流的效果。Connect的两个DataStream的数据类型可以不同，两个DataStream在调用Connect之后就变成了ConnectedStreams，实现了形式上的合流，所谓形式上的合流，就是在调用ConnectedStreams的算子时还是分别对ConnectedStreams中两条流在进行计算，只有在调用ConnectedStreams的map算子将两个DataStream中的数据转换成一种数据数据类型后才真正地实现合流的效果。
Connect算子会将DataStream转换成ConnectedStreams，ConnectedStreams不是DataStream的子类，ConnectedStreams的map算子会将 ConnectedStreams转换成DataStream，ConnectedStreams除map算子外还有许多其它的算子可以使用，但都是分别对 ConnectedStreams中的两条流进行计算，包括map算子也是分别对两条流进行计算。map的参数CoMapFunction的三个泛型参数分别是，ConnectedStreams中的两条流的数据类型 和 转换之后的数据类型。
如下程序将两条流合并成ConnectedStreams后，再将ConnectedStreams中的两条流的数据转换成String类型
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(1);

    DataStream<Integer> integerDS = env.fromCollection(Arrays.asList(1, 2, 3, 4, 5, 6));
    DataStream<Character> characterDS = env.fromCollection(Arrays.asList('a', 'b', 'c', 'd', 'e', 'f'));

    `ConnectedStreams`<Integer, Character> connectedStreams = `integerDS.connect(characterDS);`
    `DataStream`<String> coStream = `connectedStreams.map(new CoMapFunction<Integer, Character, String>() {`
 `@Override`
 `public String map1(Integer value) throws Exception {`
 `return value.toString();`
 `}`
 `@Override`
 `public String map2(Character value) throws Exception {`
 `return value.toString();`
 `}`
 `});`

    coStream.print();
    env.execute();
}
```
输出：
```
1
a
2
b
3
c
4
d
5
e
6
f
```

**9.Union**
union算子可以合并多条数据类型相同的流。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> integerDS1 = env.fromCollection(Arrays.asList(1, 2, 3));
    DataStream<Integer> integerDS2 = env.fromCollection(Arrays.asList(4, 5, 6));
    DataStream<Integer> integerDS3 = env.fromCollection(Arrays.asList(7, 8, 9));

    `DataStream<Integer> unionDS = integerDS1.union(integerDS2, integerDS3);`

    unionDS.print();
    env.execute();
}
```
输出：
```
1> 1
8> 5
7> 4
9> 6
2> 7
3> 8
4> 9
3> 3
2> 2
```

