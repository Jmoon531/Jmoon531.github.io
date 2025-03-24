---

Created at: 2021-09-29
Last updated at: 2022-06-28


---

# 6-RDD Value 类型转换算子 之 groupBy


**6\. groupBy，分组**
groupBy函数的处理结果是一个二元组的列表，二元组的第一个元素是分组的key，二元组的第二个元素是该分组的所有元素的集合。
以下按奇偶性对数据分组
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "groupBy")
`val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
`val groupRDD: RDD[(Int, Iterable[Int])] = rdd.groupBy(a => {`
 `val currentThread = Thread.currentThread`
 `println(currentThread.getId + ":" + currentThread.getName + " >> " + a)`
 `a % 2`
`})`
val mapRDD: RDD[(Int, Iterable[Int])] = groupRDD.map(kv => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + kv)
   kv
})
val array: Array[(Int, Iterable[Int])] = mapRDD.collect
array.foreach(kv => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + kv)
})
}
```
输出结果：
```
77:Executor task launch worker for task 0 >> 1
79:Executor task launch worker for task 2 >> 7
78:Executor task launch worker for task 1 >> 4
77:Executor task launch worker for task 0 >> 2
78:Executor task launch worker for task 1 >> 5
79:Executor task launch worker for task 2 >> 8
78:Executor task launch worker for task 1 >> 6
79:Executor task launch worker for task 2 >> 9
77:Executor task launch worker for task 0 >> 3
78:Executor task launch worker for task 3 >> (0,CompactBuffer(2, 4, 6, 8))
79:Executor task launch worker for task 4 >> (1,CompactBuffer(1, 3, 5, 7, 9))
1:main >> (0,CompactBuffer(2, 4, 6, 8))
1:main >> (1,CompactBuffer(1, 3, 5, 7, 9))
```
从输出结果可以看到，groupBy分组后的同一组的数据会发往一个相同的分区中，接下的map算子会成为一个新的task，然后被executor执行。

**实验一：**
如果将groupBy分组后的数据使saveAsTextFile函数按分区写到文件中，会发现还是3个分区，分区数并没有变，只不过只有前两个分区有数据，而最后一个分区没有数据。
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "groupBy")
`val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
val groupRDD: RDD[(Int, Iterable[Int])] = rdd.groupBy(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
 `a % 2`
})
groupRDD.saveAsTextFile("output")
}
```
输出结果：
```
文件1：
(0,CompactBuffer(2, 4, 6, 8))
文件2：
(1,CompactBuffer(1, 3, 5, 7, 9))
文件3：


```

如果将数据分成4个组，还是用saveAsTextFile函数按分区将数据写到文件中，会发现还是3个分区，分区数并没有变，只不过会有两组数据进入到一个分区之中。
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "groupBy")
`val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
val groupRDD: RDD[(Int, Iterable[Int])] = rdd.groupBy(a => {
  val currentThread = Thread.currentThread
  println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
 `a % 4`
})
groupRDD.saveAsTextFile("output")
}
```
输出结果：
```
文件1：
(0,CompactBuffer(4, 8))
(3,CompactBuffer(3, 7))
文件2：
(1,CompactBuffer(1, 5, 9))
文件3：
(2,CompactBuffer(2, 6))
```

实验一结论：由此可见将数据按 groupBy指定的规则进行分组，分区默认不会发生改变，只是数据会被打乱并重新组合进到不同分区之中，如果分组数小于分区数，那么会有分区没有数据，而如果分组数大于分区数，那么一个分区内将会有多组数据，所以分区数与分组数并没有太大的关系，只不过是会优先将分组均分给每个分区。

**实验二：**
当有4个分组3个分区时，如果将每个分组的数据乘以2，那会有多少个task呢？
（注意：kv.\_2.map(\_ \* 2) 这map操作不是RDD的算子，只是Scala的集合操作的方法，被包含在RDD算子中了）
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "groupBy")
 `val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
 rdd.groupBy(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
 `a % 4`
 `}).map(kv => {`
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + kv)
   kv._2.map(_ * 2)
 }).collect
}
```
从输出结果可以看到，只有3个task在执行map算子，也就是说处于同一个分区的多个分组只由一个task负责计算
```
78:Executor task launch worker for task 1 >> 4
79:Executor task launch worker for task 2 >> 7
77:Executor task launch worker for task 0 >> 1
79:Executor task launch worker for task 2 >> 8
78:Executor task launch worker for task 1 >> 5
79:Executor task launch worker for task 2 >> 9
77:Executor task launch worker for task 0 >> 2
77:Executor task launch worker for task 0 >> 3
78:Executor task launch worker for task 1 >> 6
`79:Executor task launch worker for task 3 >> (0,CompactBuffer(4, 8))`
78:Executor task launch worker for task 4 >> (1,CompactBuffer(1, 5, 9))
77:Executor task launch worker for task 5 >> (2,CompactBuffer(2, 6))
`79:Executor task launch worker for task 3 >> (3,CompactBuffer(3, 7))`
```

上面所说的默认情况下是指只为groupBy指定一个参数的情况，其实还可为groupBy指定分区数，比如：
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "groupBy")
`val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
val groupRDD: RDD[(Int, Iterable[Int])] = rdd.groupBy(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
   a % 4
`}, 4)`
groupRDD.saveAsTextFile("output")
}
```
此时输出的结果就是：
```
文件1：
(0,CompactBuffer(4, 8))
文件2：
(1,CompactBuffer(1, 5, 9))
文件3：
(2,CompactBuffer(2, 6))
文件4：
(3,CompactBuffer(3, 7))
```

当分区从3个变为4个，分组仍为4个时，同样将每个分组的数据乘以2，那会有多少个task呢？
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "groupBy")
  `val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)`
  rdd.groupBy(a => {
    val currentThread = Thread.currentThread
    println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
 `a % 4`
 `}, 4)`.map(kv => {
    val currentThread = Thread.currentThread
    println(currentThread.getId + ":" + currentThread.getName + " >> " + kv)
    kv._2.map(_ * 2)
  }).collect
}
```
从输出结果可以看到，此时会有4个task执行map算子
```
78:Executor task launch worker for task 1 >> 4
77:Executor task launch worker for task 0 >> 1
79:Executor task launch worker for task 2 >> 7
79:Executor task launch worker for task 2 >> 8
77:Executor task launch worker for task 0 >> 2
78:Executor task launch worker for task 1 >> 5
79:Executor task launch worker for task 2 >> 9
77:Executor task launch worker for task 0 >> 3
78:Executor task launch worker for task 1 >> 6
`83:Executor task launch worker for task 6 >> (3,CompactBuffer(3, 7))`
`79:Executor task launch worker for task 3 >> (0,CompactBuffer(4, 8))`
`78:Executor task launch worker for task 4 >> (1,CompactBuffer(1, 5, 9))`
`77:Executor task launch worker for task 5 >> (2,CompactBuffer(2, 6))`
```

实验二结论：当有3个分区4个分组时，会有3个新的task来执行map算子，分别处理3个分区中的数据；当有4个分区4个分组时，会有4个新的task；由此可知一个分区对应于一个task。

从输出结果还可以看到，执行grouoBy算子的任务是task0、task1、task2，执行map算子的任务是task3、task4、task5、task6，也就是说同一阶段的task封装的是相同的算子，处理的是不同分区的数据，不同阶段的task封装不同的算子，只有前一个阶段的任务完成了才会执行后一个阶段的任务。

**总结，分区、task、executor的关系：**
1.Spark把数据划分在分区里，把操作划分在task里（根据宽依赖划分），所以分区是装数据的地方，task是装操作的地方，而Executor是一个进程（实际上进程的名字叫YarnCoarseGrainedExecutorBackend，Executor是Spark源代码里的一个类），数据和操作需要在进程里结合才能起来运作。
2.根据宽依赖划分的每一个阶段都会根据此阶段的分区数启动对应数目的task，每个task负责处理对应分区中的数据，所以**一个阶段内的task数等于分区数**。（没有数据的空分区也会有task，也会占用task编号，只不过是没有数据的空分区的task并不会被执行，所以上面的打印结果中没有，下一个阶段的task的编号会继续上一个阶段的task编号。大数据的场景下是没有空分区的，所以也就没有对空分区数量优化的代码，也就是没有当数据量很小时取消空分区等类似的优化手段，小数据量只在测试时才会出现，并且我们在测试时也希望模拟的是大数据的场景，所以也就更加没有必要加上空分区优化的代码了。）
3.Yarn集群中的一台主机最多启动一个Executor，所以分区数可能会大于Executor数，当分区数大于Executor数时，每个Executor就会被分配到不止一个分区。（因为一个Executor可以并行执行多个线程，所以可能即使当分区数小于Executor数时，一个Executor会被分配到不止一个分区。）
4.因为每个Executor会被分配到不止一个分区，所以每个Executor也就会有不止一个task，这时Executor会为分配到的每个task启动一个线程来执行。

