---

Created at: 2021-09-26
Last updated at: 2025-02-28
Source URL: about:blank


---

# 13-RDD行动算子


行动(action)算子是触发作业(Job)执行的方法，底层代码调用的是环境对象sc的runJob方法，会创建ActiveJob，提交并执行。行动算子不会出现在DAG图上，只有转换算子才会出现在DAG图上，所以只有转换算子才会被划分成阶段封装成task被执行。

```
val sc = new SparkContext("local[*]", "sortByKey")
val rdd = sc.makeRDD(List(1, 2, 3, 4))
```
**1.reduce**
reduce是对全部数据进行聚合，而reduceByKey只是对key-value类型数据中相同key的数据进行聚合，并且 reduce是行动算子，会直接得到结果，而reduceByKey只是一个转换算子。
```
val i: Int = rdd.reduce(_ + _)
println(i)  //10
```

**2.collect**
方法会将不同分区的数据按照分区顺序采集到Driver端内存中，形成数组
```
val arr1: Array[Int] = rdd.collect
println(arr1.mkString(",")) //1,2,3,4
```

**3.count**
数据源中数据的个数
```
val count: Long = rdd.count
println(count)  //4
```

**4.first**
获取数据源中数据的第一个
```
val first: Int = rdd.first
println(first)  //1
```

**5.take**
获取N个数据
```
val arr2: Array[Int] = rdd.take(3)
println(arr2.mkString(","))  //1,2,3
```

**6.takeOrdered**
数据排序后，取N个数据
```
val arr3: Array[Int] = rdd.takeOrdered(3)(Ordering.Int.reverse)
println(arr3.mkString(","))  //4,3,2
```

**7.aggregate**
对所有数据进行聚合，第一个参数是zeroValue，第二个参数是分区内的聚合规则，第三个参数是分区间的聚合规则。
aggregate与aggregateByKey有点不同：aggregateByKey的初始值zeroValue只会参与分区内计算，而aggregate的初始值zeroValue不仅会参与分区内计算，并且还会参与分区间的计算。如下面的结果是40，而不是30。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "sortByKey")
 val rdd = sc.makeRDD(List(1, 2, 3, 4), 2)
 val result = rdd.aggregate(10)(_ + _, _ + _)
 println(result)  //40
}
```

**8.fold**
如果aggregate分区内和分区间的计算规则相同，那么可以直接使用fold简化调用，但是aggregate和fold还有点区别：aggregate的zeroValue不需要与数据源的数据类型保持一致，而fold需要与数据源的数据类型保持一致。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "sortByKey")
 val rdd = sc.makeRDD(List(1, 2, 3, 4), 2)
 val result = rdd.fold(10)(_ + _)
 println(result)  //40
}
```

**9.countByValue**
统计所有数据中的每个数据出现了几次
并不需要数据源的数据是key-value类型
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "count")
 val rdd = sc.makeRDD(List(1, 2, 3, 4, 4, 4), 2)
 val cnt: collection.Map[Int, Long] = rdd.countByValue()
 println(cnt) //Map(4 -> 3, 2 -> 1, 1 -> 1, 3 -> 1)
}
```
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "count")
 val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("b", 4)))
 val cnt: collection.Map[(String, Int), Long] = rdd.countByValue()
 println(cnt)  //Map((a,3) -> 1, (a,2) -> 1, (a,1) -> 1, (b,4) -> 1)
}
```

**10\. countByKey**
统计key-value类型数据源每个key出现了几次，所以此方法需要数据源的数据是key-value类型
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "count")
 val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("b", 4)))
 val cnt: collection.Map[String, Long] = rdd.countByKey()
 println(cnt)  //Map(a -> 3, b -> 1)
}
```

**11\. save 相关算子**
saveAsTextFile将数据保存成 Text 文件，如果是自定义对象，则将toString的结果保存到文件中；相应地，使用textFile算子可以从Text文件中读取数据，textFile算子是以行为单位读取数据的。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
  val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3)), 1)
  `rdd.saveAsTextFile("output1")`
  sc.stop()
}
```
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
  `val rdd: RDD[String] = sc.textFile("output1")`
  rdd.collect.foreach(println)
  sc.stop()
}
```
输出的结果：
```
文件中：
(a,1)
(a,2)
(a,3)
控制台打印：
(a,1)
(a,2)
(a,3)
```

saveAsObjectFile将对象序列化后保存到文件， 采用的是 Java 的序列化机制，所以如果是自定义对象需要混入Serializable特质；相应地，可以使用 objectFile算子从Object文件中读取数据。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
  val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3)), 1)
  `rdd.saveAsObjectFile("output2")`
  sc.stop()
}
```
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
 `val rdd: RDD[(String, Int)] = sc.objectFile[(String, Int)]("output2")`
  rdd.collect.foreach(println)
  sc.stop()
}
```

saveAsSequenceFile只能将K-V类型数据保存成 SequenceFile文件，SequenceFile文件采用的是Hadoop的序列化机制，所以如果是自定义对象那么需要混入Writable特质；相应的可以使用 sequenceFile算子在 SequenceFile文件读取数据。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
  val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3)), 1)
  `rdd.saveAsSequenceFile("output3")`
  sc.stop()
}
```
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "saveAsTextFile")
  `val rdd: RDD[(String, Int)] = sc.sequenceFile[String, Int]("output3")`
  rdd.collect.foreach(println)
  sc.stop()
}
```

**12\. foreach**
不同于Scala集合的foreach方法，这里foreach是RDD的行动算子，会被封装进task，然后在每个Executor端中执行，也就是这个遍历集合的操作会在所有的Executor中并行执行。
如果不是本地模式，那么rdd.foreach(println)会在不同主机上打印，如果是本地模式，那么就会由多个线程将数据并发写到标准输出上。而rdd.collect().foreach(println)则是由collect算子先会将不同分区的数据按照分区顺序采集到Driver端内存中，然后通过Scala集合的foreach方法遍历输出。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "count")
 val rdd = sc.makeRDD(List(1, 2, 3, 4))
 // collect方法会将不同分区的数据按照分区顺序采集到Driver端内存中
 // 所以这里的foreach方法并不是RDD操作，只是在Driver端内存遍历集合
 rdd.collect().foreach(v => {
   println(s"${Thread.currentThread.getId} : ${Thread.currentThread.getName} >> $v")
 })
 println("******************")
 // 这个foreach是RDD的行动算子，会被封装进task，然后在每个Executor端中执行，
 // 也就是这个遍历集合的操作会在所有的Executor中并行执行
 rdd.foreach(v => {
   println(s"${Thread.currentThread.getId} : ${Thread.currentThread.getName} >> $v")
 })
 sc.stop()
}
```
输出：
```
1 : main >> 1
1 : main >> 2
1 : main >> 3
1 : main >> 4
******************
87 : Executor task launch worker for task 31 >> 4
86 : Executor task launch worker for task 19 >> 1
77 : Executor task launch worker for task 23 >> 2
89 : Executor task launch worker for task 27 >> 3
```

