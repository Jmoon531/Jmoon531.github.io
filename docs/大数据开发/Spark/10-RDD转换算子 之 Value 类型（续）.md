---

Created at: 2021-09-25
Last updated at: 2025-02-28
Source URL: about:blank


---

# 10-RDD转换算子 之 Value 类型（续）


**7.filter，过滤**
对分区内的每一条进行过滤，分区数不会改变，但是分区之间可能会出现数据倾斜。
示例：只保留偶数
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "filter")
    val rdd: RDD[Int] = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)
    rdd.filter(_ % 2 == 0).collect.foreach(println)
}
```

**8.sample，抽样**
从数据集中抽取数据
函数签名如下，第一个参数表示数据被抽到后是否放回，不放回就是伯努利算法，放回就是泊松算法；第二个参数是一个小数，范围在\[0, 1\]之间，第一个参数的取值不同，该数的含义就不同；第三个参数是一个随机数种子，如果不指定就是当前系统时间。
第一个参数为false就是伯努利算法，抽样的过程是，首先根据随机数种子生成一连串的随机数，RDD中每一条数据都会对应到相应的随机数上，当数据对应的随机数大于第二参数时，该数据就会被选取。也就是说当第二个参数是0时表示全不取，是1时表示全取。
第一个参数为true时就是泊松算法，此时第二参数表示是啥我也不知道。
反正就是第一个参数为true时就表示可以重复抽取数据，为false就是不会重复抽取数据。
```
def sample(
   withReplacement: Boolean,
   fraction: Double,
   seed: Long = Utils.random.nextLong): RDD[T]
```

**9.distinct，去重**
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "distinct")
  val rdd = sc.makeRDD(List(1, 2, 3, 4, 1, 2, 3, 4), 3)
  rdd.distinct.foreach(println)
}
```
Scala集合的distinct方法去重的原理是把元素添加到HashSet中，而RDD的distinct算子的计算过程是
```
map(x => (x, null)).reduceByKey((x, _) => x, numPartitions).map(_._1)
```
首先会把每一个元素映射成(x,null)，然后reduceByKey，所有相同的(x,null)变成一个(x,null)，最后映射只取元组的第一个元素，这样做是为分布式计算。

**10.coalesce，合并分区**
如果分区数过多，就会存在过多的小任务，这反而会程序的性能降低，因为增加了调度和通信的成本，可以通过 coalesce 方法，收缩合并分区，减少分区的个数。
示例：首先三个分区中的数据分别是【1, 2, 3】、【 4, 5, 6】、【7, 8, 9】，然后合并成两个分区的结果是【1, 2, 3】、【4, 5, 6, 7, 8, 9】，可见coalesce 方法只有一个参数时只会进行简单的分区合并，并不会重新均匀的分配数据。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "coalesce")
  val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 3)
 `val rddCoalesce: RDD[Int] = rdd.coalesce(2)`
  rddCoalesce.saveAsTextFile("output")
  sc.stop()
}
```
重新均匀的为每个分区分配数据的过程称为Shuffle，coalesce 方法的第二参数可以指定是否要进行Shuffle。这样合并成两个分区的结果就是将数据随机均匀的分配到每个分区，如结果可能是这样的：【1, 3, 5, 7, 9】、【2, 4, 6, 8】
```
rdd.coalesce(2, true)
```

coalesce不仅可以合并分区，还可以增加分区，因为增加分区数据必须要被打乱，所以当想使用coalesce增加分区时，第二参数必须设置为true。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "coalesce")
 val rdd = sc.makeRDD(List(1, 2, 3, 4, 5, 6, 7, 8, 9), 2)
 `rdd.coalesce(3, shuffle = true).saveAsTextFile("output")`
 sc.stop()
}
```

**11.repartition**
还可以使用repartition来合并或者增加分区，repartition其实调用的就是 coalesce，默认shuffle=true
```
def repartition(numPartitions: Int)(implicit ord: Ordering[T] = null): RDD[T] = withScope {
 coalesce(numPartitions, shuffle = true)
}
```

**12.sortBy，排序**
sortBy可以对所有数据进行排序，默认排序前后分区数不会改变，sortBy会把排好序的数据平均分散在每个分区中，所以数据就会形成分区内有序和全局有序的效果。因为这中间存在对分区间数据的调整，所以sortBy是有Shuffle的。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "sortBy")
 val rdd = sc.makeRDD(List(1, 5, 2, 3, 4, 6, 8, 7), 2)
 rdd.sortBy(num => num).saveAsTextFile("output")
}
```
输出结果如下，可见分区内数据有序
```
文件1：
1 2 3 4
文件2：
5 6 7 8
```
如果不把分区数据保存在文件，而是直接输出，那么输出结果是1 2 3 4 5 6 7 8，可见全局也是有序的。
sortBy的第二个参数默认为true，表示升序，可以指定为false，表示降序。sortBy第三个参数还可指定排序后分区的数量。
```
def main(args: Array[String]): Unit = {
 val sc = new SparkContext("local[*]", "sortBy")
 val rdd = sc.makeRDD(List(1, 5, 2, 3, 4, 6, 8, 7), 2)
 rdd.sortBy(num => num, ascending = false, 4).saveAsTextFile("output")
}
```

