---

Created at: 2021-10-09
Last updated at: 2022-07-07


---

# 9-富函数(RichFunction)


在Fink的JavaAPI中，所有的Source、Transform、Sink算子都需要传递一个接口或者抽象类的实现类的对象（如果是Flink的ScalaAPI，则可以直接传递函数，而因为Java并不支持直接传递函数，所以必须以接口或类作为方法的载体），可以是这个接口或者抽象类的匿名子类对象，如果是函数式接口，还可以直接传递lambda表达式。这些接口或抽象类的名字都以Function结尾，都继承自Function接口，所以在Flink里面这些接口或抽象类也称为函数，因为它们的目的就是作为参数传递方法。并且这些接口或者抽象类都有一个以Rich开头以Function结尾的抽象子类，于是称为富函数，它提供了比原有接口和抽象类更丰富的功能，比如可以获取运行环境的上下文，并拥有一些生命周期方法，可以实现更复杂的功能。总结到一点就是Operator（算子）需要传入Function（函数）。
![unknown_filename.png](./_resources/9-富函数(RichFunction).resources/unknown_filename.png)

比如DataStream的map算子需要传入一个MapFunction
```
public <R> SingleOutputStreamOperator<R> map(MapFunction<T, R> mapper)
```
MapFunction继承自Function，是一个函数式接口，所以可以传入MapFunction匿名子类对象，也可以直接传入lambda表达式：
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> dataStream = env.fromElements(1, 2, 3, 4, 5, 6);
    dataStream.map(new MapFunction<Integer, Integer>() {
        int v;
        {
            v = 0;
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | " + v);
        }
        @Override
        public Integer map(Integer value) throws Exception {
            ++v;
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | " + v);
            return value * 2;
        }
    }).print();
    env.execute();
}
```
输出结果：
```
1 | main | 0
100 | Map -> Sink: Print to Std. Out (6/16) `| 1`
95 | Map -> Sink: Print to Std. Out (3/16) `| 1`
101 | Map -> Sink: Print to Std. Out (7/16) `| 1`
3> 2
102 | Map -> Sink: Print to Std. Out (8/16) `| 1`
97 | Map -> Sink: Print to Std. Out (5/16) `| 1`
5> 6
96 | Map -> Sink: Print to Std. Out (4/16) `| 1`
8> 12
7> 10
6> 8
4> 4
```
从输出的结果中可以看到，MapFunction的匿名子类实例只在主线程（JobManager）上实例化一次，然后被序列化传送到每一个map算子子任务所在的slot中，所以每个线程都会有一份MapFunction匿名子类对象，于是对实例字段v的更新就互不干扰。

RichFunction 有两个生命周期方法：
open()方法是 RichFunction 子类对象反序列化时会调用的方法。
close()方法是RichFunction 子类对象销毁时调用的方法，做一些清理工作。
比如给DataStream的map算子传入一个RichMapFunction的匿名子类对象，RichMapFunction是一个抽象类，继承自MapFunction。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> dataStream = env.fromElements(1, 2, 3, 4, 5, 6);
    dataStream.map(new RichMapFunction<Integer, Integer>() {
        int v;
        {
            v = 0;
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | " + v);
        }

        @Override
        public void open(Configuration parameters) throws Exception {
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | open");
        }

        @Override
        public void close() throws Exception {
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | close");
        }

        @Override
        public Integer map(Integer value) throws Exception {
            ++v;
            System.out.println(Thread.currentThread().getId() + " | " + Thread.currentThread().getName() + " | " + v);
            return value * 3;
        }
    }).print();
    env.execute();
}
```
输出如下，从输出的结果中可以看到，RichMapFunction的匿名子类实例只在主线程（JobManager）上实例化一次，然后被序列化传送到每一个map算子子任务所在的slot中，所以每个线程都会有一份RichMapFunction匿名子类对象，于是对实例字段v的更新就互不干扰。并且当taskManager的slot反序列化RichMapFunction匿名子类对象时还会调用open()方法，因为map算子的并行度等于cpu的线程数16，所以map算子有16个子任务，每个子任务都会反序列化一份RichMapFunction的匿名子类对象，于是就会输出16执行16次open方法，当任务结束时，还会调用close()方法，因为只有6个map算子的子任务会接收到数据，所以RichMapFunction的匿名子类对象的map方法只会执行6次。
```
1 | main | 0
102 | Map -> Sink: Print to Std. Out (8/16) | open
93 | Map -> Sink: Print to Std. Out (1/16) | open
96 | Map -> Sink: Print to Std. Out (4/16) | open
106 | Map -> Sink: Print to Std. Out (12/16) | open
110 | Map -> Sink: Print to Std. Out (13/16) | open
101 | Map -> Sink: Print to Std. Out (7/16) | open
107 | Map -> Sink: Print to Std. Out (15/16) | open
100 | Map -> Sink: Print to Std. Out (6/16) | open
97 | Map -> Sink: Print to Std. Out (5/16) | open
95 | Map -> Sink: Print to Std. Out (3/16) | open
103 | Map -> Sink: Print to Std. Out (9/16) | open
94 | Map -> Sink: Print to Std. Out (2/16) | open
109 | Map -> Sink: Print to Std. Out (14/16) | open
105 | Map -> Sink: Print to Std. Out (11/16) | open
108 | Map -> Sink: Print to Std. Out (16/16) | open
104 | Map -> Sink: Print to Std. Out (10/16) | open
`104 | Map -> Sink: Print to Std. Out (10/16) | 1`
`103 | Map -> Sink: Print to Std. Out (9/16) | 1`
`105 | Map -> Sink: Print to Std. Out (11/16) | 1`
`10> 6`
`106 | Map -> Sink: Print to Std. Out (12/16) | 1`
`109 | Map -> Sink: Print to Std. Out (14/16) | 1`
`14> 18`
`110 | Map -> Sink: Print to Std. Out (13/16) | 1`
`12> 12`
`9> 3`
`11> 9`
`13> 15`
93 | Map -> Sink: Print to Std. Out (1/16) | close
96 | Map -> Sink: Print to Std. Out (4/16) | close
106 | Map -> Sink: Print to Std. Out (12/16) | close
103 | Map -> Sink: Print to Std. Out (9/16) | close
107 | Map -> Sink: Print to Std. Out (15/16) | close
95 | Map -> Sink: Print to Std. Out (3/16) | close
109 | Map -> Sink: Print to Std. Out (14/16) | close
100 | Map -> Sink: Print to Std. Out (6/16) | close
97 | Map -> Sink: Print to Std. Out (5/16) | close
108 | Map -> Sink: Print to Std. Out (16/16) | close
101 | Map -> Sink: Print to Std. Out (7/16) | close
94 | Map -> Sink: Print to Std. Out (2/16) | close
104 | Map -> Sink: Print to Std. Out (10/16) | close
105 | Map -> Sink: Print to Std. Out (11/16) | close
110 | Map -> Sink: Print to Std. Out (13/16) | close
102 | Map -> Sink: Print to Std. Out (8/16) | close
```

RichMapFunction继承自AbstractRichFunction，AbstractRichFunction中有可以获取运行环境的上下文的方法，因此可以使用富函数获取运行环境的上下文，从而实现一些更加复杂的功能。
getRuntimeContext().getIndexOfThisSubtask()得到的是该算子当前子任务的编号。
```
public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> dataStream = env.fromElements(1, 2, 3, 4, 5, 6);
    dataStream.map(new RichMapFunction<Integer, Integer>() {
        @Override
        public Integer map(Integer value) throws Exception {
            System.out.println("Subtask: " + `getRuntimeContext().getIndexOfThisSubtask()` + " > " + value * 3);
            return value * 3;
        }
    }).print();
    env.execute();
}
```
输出：
```
Subtask: 10 > 18
11> 18
Subtask: 5 > 3
6> 3
Subtask: 8 > 12
9> 12
Subtask: 9 > 15
10> 15
Subtask: 7 > 9
8> 9
Subtask: 6 > 6
7> 6
```

