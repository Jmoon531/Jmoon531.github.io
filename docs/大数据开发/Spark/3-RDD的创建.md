---

Created at: 2021-09-23
Last updated at: 2021-09-29
Source URL: about:blank


---

# 3-RDD的创建


**创建 RDD 的四种方式：**
**1\. 从集合（内存）中创建 RDD**
从集合中创建 RDD， Spark 主要提供了两个方法： parallelize 和 makeRDD
```
def main(args: Array[String]): Unit = {
 val conf = new SparkConf().setMaster("local[*]").setAppName("RDD")
 val sc = new SparkContext(conf)

 // 从内存中创建RDD，将内存中集合的数据作为处理的数据源
 val seq: Seq[Int] = Seq(1, 2, 3, 4)
 `//使用parallelize方法创建`
 `val rdd_1: RDD[Int] = sc.parallelize(seq)`
 rdd_1.collect().foreach(println)

 `//使用makeRDD方法创建`
 `val rdd_2: RDD[Int] = sc.makeRDD(seq)`
 rdd_2.collect().foreach(println)

 sc.stop()
}
```
其实makeRDD 方法调用了 parallelize 方法
```
def makeRDD[T: ClassTag](
   seq: Seq[T],
   numSlices: Int = defaultParallelism): RDD[T] = withScope {
 parallelize(seq, numSlices)
}
```

**2\. 从外部存储（文件）创建 RDD**
从外部存储系统的数据集创建 RDD 包括：本地的文件系统、HDFS 等。
2.1 使用textFile方法，textFile以行为单位读取所有文件的内容
```
def main(args: Array[String]): Unit = {
 val conf = new SparkConf().setMaster("local[*]").setAppName("RDD")
 val sc = new SparkContext(conf)

 `//从本地文件中创建RDD，将本地文件中的数据作为处理的数据源`
 `//以项目的根路径作为基准`
 `val rdd_1: RDD[String] = sc.textFile("data/1.txt")`
 `//可以指定目录，此时读取目录中所有文件的数据`
 `val rdd_2: RDD[String] = sc.textFile("data")`
 `//还可以使用通配符来指定文件，比如只读取data目录下以1开头的txt文件`
 `val rdd_3: RDD[String] = sc.textFile("data/1*.txt")`
 `//从HDFS中创建RDD，将HDFS上的数据作为处理的数据源`
 `val rdd_4: RDD[String] = sc.textFile("hdfs://hadoop102:8020/1.txt")`

 rdd_1.collect().foreach(print)
 rdd_2.collect().foreach(print)
 rdd_3.collect().foreach(print)
 rdd_4.collect().foreach(print)
 sc.stop()
}
```
2.2 使用wholeTextFiles方法可以在读取数据的时候获取文件的绝对路径。wholeTextFiles会将数据封装进一个二元组，第一个元素的值是文件的绝对路径，第二个元素的值是该文件中的所有数据。也就是wholeTextFiles以文件为单位进行读取，而textFile则是以行为单位读取。
```
`//从本地文件中创建RDD，将本地文件中的数据作为处理的数据源 ,以项目的根路径作为基准`
`val rdd_1: RDD[(String, String)] = sc.wholeTextFiles("data")`
val res: Array[(String, String)] = rdd_1.collect()
```

3\. 从其他 RDD 创建，即一个 RDD 运算完后再产生新的 RDD
4\. 直接创建 RDD（new），使用 new 的方式直接构造 RDD，一般由 Spark 框架自身使用。

