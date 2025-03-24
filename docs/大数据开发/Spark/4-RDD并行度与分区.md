---

Created at: 2021-09-23
Last updated at: 2025-02-28
Source URL: about:blank


---

# 4-RDD并行度与分区


**RDD 并行度与分区**
一个阶段内分区数等于task数，Executor会为每一个task启动一个线程执行，同一时刻并行执行的线程数就是并行度，可见task数并不等于并行度。比如Spark集群有10台主机，每台主机的cpu线程数为4，并且每台主机有一个Executor，假设此时Spark正在执行的阶段有100个task，那么这10个Executor会启动100线程来执行task，但是因为整个集群最多只能并行执行10x4=40个线程，于是此时Spark集群并行度最大只能是40，所以应该说task数总是大于等于并行度的。

task数等于分区数，可以创建RDD时指定分区的数量。
**1.集合（内存）中数据的分区**
1.1 设置分区数
1.1.1 明确指定分区数
makeRDD方法创建的是ParallelCollectionRDD的对象，可以在创建时指定分区数量。makeRDD方法的第二个参数numSlices表示分区的数量，saveAsTextFile方法可以将每个分区处理后的数据保存成文件，一个分区对应于一个文件。
```
def main(args: Array[String]): Unit = {
   val sc = new SparkContext("local[*]", "RDD")
   // makeRDD方法的第二个参数numSlices表示分区的数量
   val rdd_1: RDD[Int] = sc.makeRDD(List(1, 2, 3, 4), 2)
   //将处理后的数据保存成文件
   rdd_1.saveAsTextFile("output")
    sc.stop()
}
```
1.1.2 默认分区数
makeRDD方法的numSlices参数的默认值是defaultParallelism方法的返回值，最终执行的是LocalSchedulerBackend的defaultParallelism方法，该方法的逻辑就是默认分区数的指定逻辑。
```
def makeRDD[T: ClassTag](
   seq: Seq[T],
   `numSlices: Int = defaultParallelism`): RDD[T] = withScope {
 parallelize(seq, numSlices)
}
```
```
override def defaultParallelism(): Int =
 scheduler.conf.getInt("spark.default.parallelism", totalCores)
```
如果没有在创建时指定分区数量，则分区数量等于默认并行度。默认的并行度由setMaster("local\[\*\]")指定，\*表示并行度等于本地cpu线程数，Spark会使用与本地CPU线程数同样多的线程来执行任务。setMaster("local\[4\]")表示并行度等于4，spark会使用4个线程来执行任务。setMaster("local")表示使用单线程来执行任务。
也可由 SparkConf 的 spark.default.parallelism 参数指定默认并行度，这个值会覆盖setMaster("local\[\*\]")指定的值。
比如当使用makeRDD创建RDD时没有指定分区数量，并且setMaster("local\[\*\]")，如果有set("spark.default.parallelism", "8")，那么分区数等于并行度等于8，saveAsTextFile()最后就会保存8个文件。
综上就是，
（1）任务数＝分区数
（2）并行度 ≠ 任务数
（3）如果没有设置分区数，那么分区数＝默认并行度；如果设置了分区数，那么分区数就是你所设置的数量。

分区就是数据，任务就是计算，在分布式集群中，移动数据不如移动计算，也就是设置好分区数之后，会就近地在HDFS上读取数据，然后task作为计算分发给分一个节点。

**总结 流式计算 和 批计算 分区并行特点区别：**
流式计算Flink的每一步算子都可以设置并行度，因为流式计算在开始处理数据之前就构建好了整个计算流图；而批计算Spark只能在最开始读数据的时候设置分区数（不等于并行度，如果单核cpu，那么所有task在一个线程上执行），或者在shuffle时设置分区数（因为map阶段是窄依赖分区数不变，shuffle是宽依赖，分区数可以发生改变），如果在shuffle时没有设置分区数，那么shuffle后的分区数应该也不会超过最开始时设置的分区数。

**2.数据的分区规则**
getPartitions为RDD类定义的抽象方法，每一个具体的RDD都需要继承RDD并重写getPartitions方法，用来实现自己的分区规则。
**2.1 ParallelCollectionRDD的分区规则**
ParallelCollectionRDD的getPartitions方法的核心逻辑在其伴生对象中，源码如下，该方法计算的每个分区在集合中的起始位置和结束位置（在真正对数据进行分片时是不包含结束位置的元素的，不然元素就重复了）。
```
def positions(length: Long, numSlices: Int): Iterator[(Int, Int)] = {
 (0 until numSlices).iterator.map { i =>
   val start = ((i * length) / numSlices).toInt
   val end = (((i + 1) * length) / numSlices).toInt
   (start, end)
 }
}
```
比如执行以下代码会生成三个文件，因为设置的分区数是3，三个文件中的数据分别是\[1\]、\[2,3\]、\[4,5\]
```
val rdd_1: RDD[Int] = sc.makeRDD(List(1, 2, 3, 4, 5), 3)
rdd_1.saveAsTextFile("output")
```
计算过程是：length = 5 ，numSlices = 3 ，然后按源码计算得到的(start, end)结果是(0,1)、(1,3)、(3,5)，于是三个分区中的数据依次是\[1\]、\[2,3\]、\[4,5\]

**2.2 文件中数据的分区**
textFile方法创建的是HadoopRDD，textFile方法的第二个参数numSlices表示分区的数量，虽然在创建时可以指定文件数据的分区数，但是最终的分区数并不一定是指定的分区数，numSlices只是HadoopRDD的getPartitions方法计算分区的一个基准，不像ParallelCollectionRDD的getPartitions方法一定会生成numSlices个分区（ParallelCollectionRDD的getPartitions方法的计算逻辑可以看到这一点）。
```
def main(args: Array[String]): Unit = {
   val conf = new SparkConf().setMaster("local").setAppName("RDD")
   val sc = new SparkContext(conf)
   `//textFile方法的第二个参数numSlices表示分区的数量`
 `val rdd_2: RDD[String] = sc.textFile("data/1.txt", 2)`
   rdd_2.saveAsTextFile("output")
   sc.stop()
}
```
textFile方法和defaultMinPartitions方法如下， minPartitions的默认值是默认并行度和2中的小值。
```
def textFile(
   path: String,
   `minPartitions: Int = defaultMinPartitions`): RDD[String] = withScope {
 assertNotStopped()
 hadoopFile(path, classOf[TextInputFormat], classOf[LongWritable], classOf[Text],
   minPartitions).map(pair => pair._2.toString).setName(path)
}
```
```
def defaultMinPartitions: Int = math.min(defaultParallelism, 2)
```
HadoopRDD的getPartitions方法会执行FileInputFormat的getSplits方法，这个是MapReduce计算分片计划的方法（并不是最新版的Hadoop），HadoopRDD的分区逻辑主要在这：
1.如果指定分区数量为0或者1的话，defaultMinPartitions值为1，则有多少个文件，就会有多少个分区。
2.如果不指定默认分区数量，则默认分区数量为2，如果指定分区数量大于等于2，则默认分区数量为指定值。FileInputFormat的getSplits方法则会计算所有文件的总字节大小totalSize，然后除以分区数量numSlices的值得到goalSize，接着比较goalSize和hdfs的块大小（这里是32M），以两者中的小值作为切片的大小。接着对每一个文件执行切片逻辑，即如果该文件大小超过切片大小的1.1倍，则将这个文件按一个切片大小切开，然后对剩余部分继续执行切片逻辑。最终的切片数量等于分区的数量。注意，切片并不是真的将一个文件划分成了两个文件，而只是计算了每一个分片的偏移量和最终分片的数目。
所以，从FileInputFormat的getSplits方法可以看到，使用textFile方法创建HadoopRDD时指定的numSlices并不是最终的分区数量，而是以getSplits方法最终的切片数量来决定，即切片数量等于分区的数量。注意，虽然分区数已经确定，但每一个分区的中数据并不完全等同每一个切片中的数据，因为spark在读取文件中数据时会将同一行数据放到一个分区中，不存在把一行数据从中间分开读到两个分区中的情况。

* * *

并行度表示可以使用的最大线程数，默认并行度等于CPU核心数；分区数就是任务数，如果小于并行度，那么只会用到分区数量个线程，如果大于并行度就会有多个任务由同一个线程执行；并行度和分区数设置大与设置小都有道理，拿不准就直接使用默认策略吧。

**spark如何保证内存不溢出？**
不用管spark如何读数据，比如有20个分区，每个分区负责1G的数据，并行度16，CPU有16个线程，内存有8G，此配置下，会有16个分区同时处理数据，你说Spark能一次性把16个分区中的数据都读到内存吗，显然是不可以的，这16个分区肯定是在分批读外存的数据，保证不内存溢出，这个读取的策略肯定就是由Spark来完成，所以使用Spark的时候，不用管数据大小，只需要考虑设置分区数和并行度，不需要要考虑分区如何读取数据。

<https://www.zhihu.com/question/23079001/answer/23569986>

