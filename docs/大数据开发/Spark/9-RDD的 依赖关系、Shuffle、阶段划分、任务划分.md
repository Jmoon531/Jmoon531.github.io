---

Created at: 2021-09-26
Last updated at: 2021-10-12
Source URL: about:blank


---

# 9-RDD的 依赖关系、Shuffle、阶段划分、任务划分


1.相邻RDD之间的关系称为**依赖关系**，即后一个RDD依赖于前一个RDD。
使用dependencies可以获取RDD的依赖关系：
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "WordCount")
  val lines: RDD[String] = sc.makeRDD(List("Hello Spark", "Hello Scala", "Hello Flink"))
  println(lines.dependencies)
  println("***********************")
  val words: RDD[String] = lines.flatMap(_.split(" "))
  println(words.dependencies)
  println("***********************")
  val wordAndOne: RDD[(String, Int)] = words.map((_, 1))
  println(wordAndOne.dependencies)
  println("***********************")
  val wordToCount: RDD[(String, Int)] = wordAndOne.reduceByKey(_ + _)
  println(wordToCount.dependencies)
  println("***********************")
  val array: Array[(String, Int)] = wordToCount.collect()
  array.foreach(println)
  sc.stop()
}
```
输出：
```
List()
***********************
List(org.apache.spark.OneToOneDependency@7cca01a8)
***********************
List(org.apache.spark.OneToOneDependency@3003827c)
***********************
List(org.apache.spark.ShuffleDependency@51bddd98)
***********************
(Flink,1)
(Hello,3)
(Scala,1)
(Spark,1)
```
可以看到flatMap和map这种只对分区内数据进行操作的算子的依赖关系都称为OneToOneDependency，而org.apache.spark.OneToOneDependency继承自抽象类NarrowDependency，所以这种依赖关系也称为**窄依赖**。而对于reduceByKey这种会进行Shuffle操作的算子的依赖关系称为ShuffleDependency，虽然是直接继承自抽象类Dependency，但也将这种依赖称为**宽依赖**，因为reduceByKey操作依赖于多个分区之中的数据。
所以宽依赖意味着会有Shuffle操作，也就意味着会引起**阶段划分**，所以 阶段的数量=Shuffle的数量 + 1，而窄依赖不会引起阶段的划分。

**Shuffle**
**对分区间数据进行调整的过程叫Shuffle。**groupBy会对分区数据进行调整，所以它有Shuffle的操作，可见**只要有shuffle操作就会新开启一个阶段**。因为如果只是对一个分区内的数据进行操作（如map、filter算子），那么对于其它分区来说就是独立的，所以对各个分区的操作就是完全可以异步进行，于是它们就都属于同一个阶段的任务。而如果涉及分区间数据的调整，那么下一个算子就必须等待数据调整完毕之后才能开始，所以应该把调整分区数据之后的算子封装在新的task中组成一个新的阶段，只有当前一个阶段的所有task都完成了才可以开始下一个阶段的task，阶段间的顺序执行流程可以看作是同步。于是，**阶段的数量 = Shuffle的数量 + 1**，因为阶段划分是针对转换算子而言的，所以只有转换算子才会有Shuffle，对于reduce会聚合所有分区数据的操作不叫Shuffle。
从Shuffle的过程可以看到，Shuffle后的下一个算子所处理的一个分区的数据来自于Shuffle算子时的多个分区的数据，这种依赖称为宽依赖，没有Shuffle过程的两个算子处理的是同一个分区的数据，这是后一个算子所处理的分区必定来自前一个算子所处理的分区的数据，这种依赖称为窄依赖。
因为Shuffle是对分区间数据的重新调整，所以等待数据调整的过程不能在内存中进行，因为数据量太大了，所以**Shuffle过程一定伴随着落盘**。Shuffle操作既然都对分区间数据进行调整了，那么这时是顺便调整分区数量的好时机，所以**一般有Shuffle的算子都可以设置分区数量**。

2.当前RDD需要记录它及它之前所有RDD的信息，这个信息就是RDD的**血缘关系**。
每个RDD都需要记录血缘关系的目的是为了提高容错性，因为RDD不保存数据，RDD只是对数据的进行操作的算子，所以一旦当前RDD操作失败就需要从头开始，也就是必须从读取数据的RDD操作开始，这时就可以从RDD记录的血缘关系中恢复之前的操作。
使用toDebugString可以获取RDD的血缘关系：
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "WordCount")
  val lines: RDD[String] = sc.makeRDD(List("Hello Spark", "Hello Scala", "Hello Flink"))
  println(lines.toDebugString)
  println("***********************")
  val words: RDD[String] = lines.flatMap(_.split(" "))
  println(words.toDebugString)
  println("***********************")
  val wordAndOne: RDD[(String, Int)] = words.map((_, 1))
  println(wordAndOne.toDebugString)
  println("***********************")
  val wordToCount: RDD[(String, Int)] = wordAndOne.reduceByKey(_ + _)
  println(wordToCount.toDebugString)
  println("***********************")
  val array: Array[(String, Int)] = wordToCount.collect()
  array.foreach(println)
  sc.stop()
}
```
输出：
```
(16) ParallelCollectionRDD[0] at makeRDD at WordCount.scala:9 []
***********************
(16) MapPartitionsRDD[1] at flatMap at WordCount.scala:12 []
|   ParallelCollectionRDD[0] at makeRDD at WordCount.scala:9 []
***********************
(16) MapPartitionsRDD[2] at map at WordCount.scala:15 []
|   MapPartitionsRDD[1] at flatMap at WordCount.scala:12 []
|   ParallelCollectionRDD[0] at makeRDD at WordCount.scala:9 []
***********************
(16) ShuffledRDD[3] at reduceByKey at WordCount.scala:18 []
+-(16) MapPartitionsRDD[2] at map at WordCount.scala:15 []
    |   MapPartitionsRDD[1] at flatMap at WordCount.scala:12 []
    |   ParallelCollectionRDD[0] at makeRDD at WordCount.scala:9 []
***********************
(Flink,1)
(Hello,3)
(Scala,1)
(Spark,1)
```

**任务划分**

* RDD 任务切分中间分为： Application、 Job、 Stage 和 Task
* Application：初始化一个 SparkContext 即生成一个 Application
* Job：一个 Action 算子就会生成一个 Job
* Stage： Stage 等于宽依赖(ShuffleDependency)的个数加 1
* Task：一个 Stage 阶段中，分区个数就是 Task 的个数（不可能会有在一个Stage内的前后两个算子处理分区数不同的情况，因为如果前后两个算子处理的分区数不同的话，中间一定会发生shuffle，于是这两个算子也就会被划分到不同的 Stage中。）

注意： Application->Job->Stage->Task 每一层都是 1 对 n 的关系，即一个Application中可以有多个Job，一个Job中可以有多个Stage，一个Stage中可以有多个Task。

