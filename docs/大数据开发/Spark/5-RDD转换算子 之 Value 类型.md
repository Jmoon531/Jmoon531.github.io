---

Created at: 2021-09-23
Last updated at: 2021-11-14


---

# 5-RDD转换算子 之 Value 类型


Spark三大数据结构分别是：

1. RDD : 弹性分布式数据集
2. 累加器：分布式共享只写变量
3. 广播变量：分布式共享只读变量

RDD的方法也称为算子(operator)，可分为两类，一类是转换(transform)，另外一类是行动(action)。转换是指对数据的操作，比如map、flatMap、groupBy等操作，转换只是操作的声明，并不是立即就已经对数据进行了操作，因为每一步转换操作都是将前一个RDD对象的封装后一个RDD对象中，真正的操作数据要等到行动方法被调用。行动算子是指会触发任务的调度和作业的执行的操作，如collect、saveAsTextFile等操作。
之所以将RDD的方法称为算子，是为了与Scala操作集合的方法区分，因为二者在处理数据的思想上确实很像，但是Spark算子实际的执行原理却与Scala操作集合的方法的执行原理有着很大区别，比如正如上面所说，转换算子只是声明操作，并没真正计算，真正的计算要等到行动算子被执行；还有就是Spark的RDD算子是分布式并行执行的，操作的是不同主机内存中的数据，不像Scala的集合的方法只是对本机内存中数据的操作。

转换算子根据数据处理方式的不同将算子整体上分为 Value 类型、双 Value 类型和 Key-Value 类型。

* Value 类型指的是可以对任何数据源进行操作的算子
* 双value类型指的是只能对两个数据源数据进行操作的算子
* Key-Value 类型指的是只能对元素是二元组的数据源进行操作的算子

以下代码均是以Local模式运行，Local模式下只有一个Executor，所有分区都在这个Executor里面，每个分区对应于一个task，Executor会为每个task都会启动一个线程来执行。

Value 类型
**1\. map，映射**
对每一个数据做映射，从以下程序输出的结果可以看到collect之前的两个map算子都是在一个线程中执行，只不过是多个线程进行相同的操作处理不同的数据，所以数据确实是被分散在不同的线程中计算的。
```
def main(args: Array[String]): Unit = {
   val sc = new SparkContext("local[*]", "map")
   val rdd = sc.makeRDD(List(1, 2, 3, 4))
   rdd.map(a => {
     val currentThread = Thread.currentThread
     println(currentThread.getId + ":" + currentThread.getName + " -> " + a)
     a * 2
   }).map(a => {
     val currentThread = Thread.currentThread
     println(currentThread.getId + ":" + currentThread.getName + " => " + a)
     a * 2
   }).collect().foreach(a => {
     val currentThread = Thread.currentThread
     println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
   })
   sc.stop()
}
```
```
80:Executor task launch worker for task 3 -> 1
88:Executor task launch worker for task 11 -> 3
92:Executor task launch worker for task 15 -> 4
84:Executor task launch worker for task 7 -> 2
92:Executor task launch worker for task 15 => 8
88:Executor task launch worker for task 11 => 6
80:Executor task launch worker for task 3 => 2
84:Executor task launch worker for task 7 => 4
1:main >> 4
1:main >> 8
1:main >> 12
1:main >> 16
```

如果只有一个数据分区：
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "map")
`val rdd = sc.makeRDD(List(1, 2, 3, 4), 1)`
rdd.map(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " -> " + a)
   a * 2
}).map(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " => " + a)
   a * 2
}).collect().foreach(a => {
   val currentThread = Thread.currentThread
   println(currentThread.getId + ":" + currentThread.getName + " >> " + a)
})
sc.stop()
}
```
输出结果：
```
`77:Executor task launch worker for task 0 -> 1`
`77:Executor task launch worker for task 0 => 2`
77:Executor task launch worker for task 0 -> 2
77:Executor task launch worker for task 0 => 4
77:Executor task launch worker for task 0 -> 3
77:Executor task launch worker for task 0 => 6
77:Executor task launch worker for task 0 -> 4
77:Executor task launch worker for task 0 => 8
`1:main >> 4`
1:main >> 8
1:main >> 12
1:main >> 16
```
从输出结果中可以看到，如果只有一个分区，那么所有数据的计算将在一个线程中执行，并且数据是一个接着一个进行计算，只有等上一个数据处理完才会处理下一条数据，总之就是分区内数据的处理是有序的。

**2.mapPartitions**
map是对分区内的数据一条一条的做映射处理，也就相当于是对所有数据一条一条的做映射处理，而mapPartitions是将同一个分区内的所有数据作为一个集合进行映射处理，所以mapPartitions参数的匿名函数输入是一个迭代器，输出也是一个迭代器，相当于是一个集合映射到另一个集合。使用Map是每一个task都是来一条数据就处理一条数据，处理完就可以释放掉这条数据的内存空间了，但是在使用mapPartitions时，每一个task都需要等待该分区内所有数据都加载到内存之后才能开始计算，并且如果没有处理完集合中的所有数据，这个集合所占用的内存空间就无法被释放掉，这就对内存压力比较大了，搞不好就容易OOM。
案例：获取每个数据分区的最大值
3个分区，获取每个分区的最大值然后输出
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "map")
val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)
rdd.mapPartitions(iter => {
   val max = iter.max
   println(Thread.currentThread().getName + " -> " + max)
   List(max).iterator
}).collect().foreach(println)
sc.stop()
}
```

**3.mapPartitionsWithIndex**
mapPartitionsWithIndex和mapPartitions一样是将同一个分区内的所有数据作为一个集合进行映射处理，但是mapPartitionsWithIndex会给每个分区一个编号，这样就能在每个task执行mapPartitionsWithIndex中的匿名函数时走不同的分支，从而实现以不同的逻辑处理不同分区的数据。
比如下面的例子，原样保留第一个分区的数据，去掉第二个分区的数据，将第三个分区中的数据乘以2：
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "mapPartitionsWithIndex")
val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)
rdd.mapPartitionsWithIndex((index, iter) => {
   println(Thread.currentThread.getName+ ">>" + index)
   index match {
     case 0 => iter
     case 1 => Nil.iterator
     case _ => iter.map(_ * 2)
   }
}).collect().foreach(println)
sc.stop()
}
```

**4.flatMap，扁平映射**
对每一条数据先做映射后做扁平化处理。以下用模式匹配（偏函数）实现可以处理不同类型的数据。
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "flatMap")
val rdd = sc.makeRDD(List(List(1, 2, 3), 4, 5, 6, List(7, 8, 9)))
rdd.flatMap {
   case list: List[_] => list
   case elem => List(elem)
}.collect().foreach(println)
sc.stop()
}
```

**5.glom**
将同一个分区内的所有数据包装成一个数组，方便使用数组的方法进行计算
对所有分区的最大值求和（分区内取最大值，分区间最大值求和）
```
def main(args: Array[String]): Unit = {
val sc = new SparkContext("local[*]", "map")
val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)
//val sum = rdd.glom().map(_.max).reduce(_ + _)
val glomRDD: RDD[Array[Int]] = rdd.glom()
val maxRDD: RDD[Int] = glomRDD.map(array => {
   println(Thread.currentThread.getName)
   array.max
})
val sum = maxRDD.collect.sum
println(sum)
}
```

