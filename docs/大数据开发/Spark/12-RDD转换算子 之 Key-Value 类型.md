---

Created at: 2021-09-25
Last updated at: 2025-02-28
Source URL: about:blank


---

# 12-RDD转换算子 之 Key-Value 类型


**Key-Value 类型**，只能对元素是二元组的数据源进行操作

**1.partitionBy**
将数据按照指定 Partitioner 重新进行分区，注意：

1. 分区器直接决定了分区的个数 以及 每条数据经过 Shuffle 后进入哪个分区。
2. 只有 Key-Value 类型的 RDD 才有分区器，非 Key-Value 类型的 RDD 分区的值是 None。
3. 每个 RDD 的分区 ID 范围： 0 ~ (numPartitions - 1)。

Spark 默认的分区器是 HashPartitioner，计算过程是，先计算key的hashCode，然后除以分区个数后取余
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "partitionBy")
    val rdd = sc.makeRDD(List((1, "1"), (2, "2"), (3, "3"), (4, "4")))
 `rdd.partitionBy(new HashPartitioner(2))`
       .saveAsTextFile("output")
    sc.stop()
}
```
输出：
```
文件1：
(2,2)
(4,4)
文件2：
(1,1)
(3,3)
```
注意：
1.如果使用相同的分区器对数据再次分区，并且分区数量与之前还相等，那么partitionBy将不会做任何操作。
2\. Spark 不光只有HashPartitioner，还有一个RangePartitioner
3.可以自定义分区器

自定义分区器
1\. 继承Partitioner
```
class MyPartitioner extends Partitioner {
  // 分区数量
  override def numPartitions: Int = 3
  // 根据数据的key值返回数据所在的分区索引（从0开始）
  override def getPartition(key: Any): Int = {
    key match {
      case "a" => 0
      case "b" => 1
      case _ => 2
    }
  }
}
```
2.在partitionBy中使用
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "WordCount")
    val rdd = sc.makeRDD(List(("a", 1), ("b", 2), ("c", 3), ("d", 4)), 1)
   ` rdd.partitionBy(new MyPartitioner)`.saveAsTextFile("output")
    sc.stop()
}
```

**2.reduceByKey**
相同key的数据进行value的两两聚合，
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "partitionBy")
    val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("a", 4), ("b", 5)), 2)
    val reduceByKeyRDD: RDD[(String, Int)] = rdd.reduceByKey((x: Int, y: Int) => {
        println(s"${Thread.currentThread.getId} : ${Thread.currentThread.getName} >> ${x}+${y}=${x + y}")
        x + y
    })
    reduceByKeyRDD.collect().foreach(println)
    sc.stop()
}
```
输出如下，可以看到如果相同key的数据只有1个，那么它是不会走reduceByKey的，并且reduceByKey会先在分区内做聚合（预聚合），然后在分区间做聚合
```
78 : Executor task launch worker for task 1 >> 3+4=7
77 : Executor task launch worker for task 0 >> 1+2=3
78 : Executor task launch worker for task 3 >> 3+7=10
(b,5)
(a,10)
```

**3.groupByKey**
按key进行分组形成一个二元组的集合，其中二元组的第一个元素就是key，二元组的第二个元素是相同key的数据的value形成的一个集合。
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "groupByKey")
    val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("b", 4)))
    val groupByKeyRDD: RDD[(String, Iterable[Int])] = rdd.groupByKey()
    groupByKeyRDD.collect.foreach(println)
    sc.stop()
}
```
输出：
```
(a,CompactBuffer(1, 2, 3))
(b,CompactBuffer(4))
```
如果是groupBy则：
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "groupByKey")
    val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("b", 4)))
    val groupByRDD: RDD[(String, Iterable[(String, Int)])] = rdd.groupBy(_._1)
    groupByRDD.collect.foreach(println)
    sc.stop()
}
```
输出：
```
(a,CompactBuffer((a,1), (a,2), (a,3)))
(b,CompactBuffer((b,4)))
```
所以，groupByKey和groupBy有两点不同：
1.groupByKey不需要指定如何分组，groupByKey是对k-v类型数据的操作，所以默认就是按key分组；而 groupBy必须指定分组的规则。
2\. groupByKey会将value封装成集合，而 groupBy是直接将原来的元素封装成集合。

**reduceByKey 和 groupByKey 的区别？**
从 shuffle 的角度： reduceByKey 和 groupByKey 都存在 shuffle 的操作，但是 reduceByKey可以在 shuffle 前对同一分区内相同 key 的数据进行预聚合（combine）功能，这样可以减少落盘的数据量，而 groupByKey 只是进行分组，不存在数据量的减少，也就不存在预聚合，所以reduceByKey 性能比较高。
从功能的角度： reduceByKey 其实包含分组和聚合的功能。 GroupByKey 只能分组，不能聚合，所以在分组聚合的场合下，推荐使用reduceByKey；如果仅仅是分组而不需要聚合，那么只能使用 groupByKey。

**4\. aggregateByKey**
reduceBykey在对分区间数据进行聚合之前会先对分区内的数据进行一次预聚合，两次聚合操作的计算逻辑是完全相同的。aggregateByKey也有分区内和分区间的两次聚合操作，但两次聚合的计算逻辑可以分别指定。
aggregateByKey是柯里化函数，有两个参数列表。第一个参数列表需要传递一个初始值，用于当碰见第一个key的时候，和value进行分区内计算。第二个参数列表需要传递2个匿名函数，第一个匿名函数是分区内计算规则，第二个匿名函数是分区间计算规则。
```
def aggregateByKey[U: ClassTag](zeroValue: U)(seqOp: (U, V) => U, combOp: (U, U) => U): RDD[(K, U)]
```
示例：取分区内相同key的value的最大值后，将分区间相同key的value相加
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "aggregateByKey")
    val rdd: RDD[(String, Int)] = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("a", 4), ("b", 5), ("b", 6)), 2)
    //首先两个分区中的数据分别是：【("a", 1), ("a", 2), ("a", 3)】、【("a", 4), ("b", 5), ("b", 6)】
    //然后aggregateByKey先分区内groupByKey：【("a", (1, 2, 3))】、【("a", 4), ("b", (5, 6))】
    //接着分区内聚合Math.max：【("a", 3)】、【("a", 4), ("b", 6)】，计算过程是都是先用0与第一个数比较取大值，然后循环比较取大值
    //接着分区间groupByKey：【("a", (3, 4))】、【("b", 6)】
    //最后分区间聚合_ + _：【("a", 7)】、【("b", 6)】
 `val aggRDD: RDD[(String, Int)] = rdd.aggregateByKey(zeroValue = 0)(Math.max, _ + _)`
    aggRDD.collect.foreach(println)
    sc.stop()
}
```
从aggregateByKey函数的签名可以到，分区内的计算规则seqOp: (U, V) => U，zeroValue的类型可以和原本数据的value的类型不一致，但是返回值的类型必须和zeroValue类型一致，然后再进行分区间的计算combOp: (U, U) => U，输入肯定是分区内计算结果的返回值，所以类型是U，不过返回值也必须是U。
案例：计算相同Key的数据的value的平均值
使用groupByKey：
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "aggregateByKey")
    //两个分区：【("a", 1), ("a", 2), ("b", 3)】、【("b", 4), ("b", 5), ("a", 6)】
    val rdd: RDD[(String, Int)] = sc.makeRDD(List(("a", 1), ("a", 2), ("b", 3), ("b", 4), ("b", 5), ("a", 6)), 2)
 `rdd.groupByKey().mapValues(c`ollection => {
        collection.sum / collection.size
    }).collect.foreach(println)
     sc.stop()
}
```
如果不使用groupByKey+mapValues的组合，而是使用aggregateByKey分两次聚合同样也能得到结果：
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "aggregateByKey")
    //两个分区：【("a", 1), ("a", 2), ("b", 3)】、【("b", 4), ("b", 5), ("a", 6)】
    val rdd: RDD[(String, Int)] = sc.makeRDD(List(("a", 1), ("a", 2), ("b", 3), ("b", 4), ("b", 5), ("a", 6)), 2)
    //怎么想：计算的时候都是在和value进行计算，不过是针对相同的key
    //zeroValue是一个元组(Int,Int)，第一个元素是原数据中相同key出现的次数，第二个元素是相同key的value的累加
 `val aggRDD: RDD[(String, (Int, Int))] = rdd.aggregateByKey(zeroValue = (0, 0))((t, v) => {`
 `(t._1 + 1, t._2 + v)`
 `}, (t1, t2) => {`
 `(t1._1 + t2._1, t1._2 + t2._2)`
 `})`
    aggRDD.mapValues(t => t._2 / t._1).collect.foreach(println)
    sc.stop()
}
```
`所以如果能用aggregateByKey代替groupByKey+mapValues得到结果，要尽量用aggregateByKey，因为会预聚合，所以效率更高。reduceByKey、 foldByKey、 aggregateByKey、 combineByKey原理是一样的，都会预聚合，只不过使用上有点差别，所以能用这四个聚合算子代替groupByKey+mapValues的地方，要尽量用聚合算子。`

**5.combineByKey**
从aggregateByKey第二个案例中可以看到，当聚合的结果的value与原本数据的value的类型不一致的时，就需要传入一个与最终结果数据类型一致的zeroValue作为聚合的起始值，而combineByKey可以不用转入zeroValue，而是在分区内聚合时先对第一个元素的value做一次转换，以后在这个转换后的值的基础之上做计算。
combineByKey方法的三个参数分别是：
第一个参数表示：分区内相同key的第一个元素的value的转换规则
第二个参数表示：分区内的计算规则
第三个参数表示：分区间的计算规则
需要注意的是：第二参数是以第一个参数的结果作为起始值进行计算，所以第二参数匿名函数的参数类型不能通过形参推断，必须明确给出，同样，第三个参数的匿名函数的参数类型和第一个参数的结果的类型是一致的，不能通过形参的类型推断得到，也必须明确指出。
案例：计算相同Key的数据的value的平均值
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "combineByKey")
    //两个分区：【("a", 1), ("a", 2), ("b", 3)】、【("b", 4), ("b", 5), ("a", 6)】
    val rdd: RDD[(String, Int)] = sc.makeRDD(List(("a", 1), ("a", 2), ("b", 3), ("b", 4), ("b", 5), ("a", 6)), 2)
    val combineByKeyRDD = rdd.combineByKey(
    v => (v, 1),
    (t: (Int, Int), v) => {
        (t._1 + v, t._2 + 1)
    },
    (t1: (Int, Int), t2: (Int, Int)) => {
        (t1._1 + t2._1, t1._2 + t2._2)
    }
    )
    combineByKeyRDD.mapValues(kv => kv._1 / kv._2).foreach(println)
    sc.stop()
}
```

**6\. foldByKey**
如果aggregateByKey的两次聚合操作完全相同，则可以直接使用foldByKey，foldByKey也可以看作是带zeroValue的reduceByKey。
不像aggregateByKey的zeroValue的类型可以和原本数据的value的类型不一致，foldByKey的zeroValue的类型必须和原本数据的value的类型一致。
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "partitionBy")
    val rdd = sc.makeRDD(List(("a", 1), ("a", 2), ("a", 3), ("a", 4), ("b", 5)), 2)
    val foldByKeyRDD = rdd.foldByKey(0)((x: Int, y: Int) => {
        println(s"${Thread.currentThread.getId} : ${Thread.currentThread.getName} >> ${x}+${y}=${x + y}")
        x + y
    })
    foldByKeyRDD.collect.foreach(println)
    sc.stop()
}
```
输出结果如下，同样可以看出先分区内聚合再分区间聚合
```
77 : Executor task launch worker for task 0 >> 0+1=1
78 : Executor task launch worker for task 1 >> 0+3=3
77 : Executor task launch worker for task 0 >> 1+2=3
78 : Executor task launch worker for task 1 >> 3+4=7
78 : Executor task launch worker for task 1 >> 0+5=5
77 : Executor task launch worker for task 3 >> 3+7=10
(b,5)
(a,10)
```

**reduceByKey、 foldByKey、 aggregateByKey、 combineByKey 的区别？**
通过查阅源码发现这四个聚合方法底层都是调用的combineByKeyWithClassTag方法，只是传递的参数不同。
```
reduceByKey:
combineByKeyWithClassTag[V](
    (v: V) => v, // 第一个值不会参与计算
    func, // 分区内计算规则
    func, // 分区间计算规则
)

aggregateByKey :
combineByKeyWithClassTag[U](
    (v: V) => cleanedSeqOp(createZero(), v), // 初始值和第一个key的value值进行的分区内数据操作
    cleanedSeqOp, // 分区内计算规则
    combOp,       // 分区间计算规则
)

foldByKey:
combineByKeyWithClassTag[V](
    (v: V) => cleanedFunc(createZero(), v), // 初始值和第一个key的value值进行的分区内数据操作
    cleanedFunc,  // 分区内计算规则
    cleanedFunc,  // 分区间计算规则
)

combineByKey :
combineByKeyWithClassTag(
    createCombiner,  // 相同key的第一条数据进行的处理函数
    mergeValue,      // 分区内计算规则
    mergeCombiners,  // 分区间计算规则
)
```
总结：
reduceByKey：相同 key 的第一个数据的value不进行任何计算，然后用此value与后面相同key的value做聚合，分区内和分区间计算规则相同
FoldByKey：相同 key 的第一个数据的value和初始值进行分区内计算，然后以用计算结果与后面相同key的value做聚合，分区内和分区间计算规则相同
AggregateByKey：相同 key 的第一个数据的value和初始值进行分区内计算，然后以用计算结果与后面相同key的value做聚合，分区内和分区间计算规则可以不相同
CombineByKey：可以对相同 key 的第一个数据的value做一次转换，然后以用转换与后面相同key的value做聚合，分区内和分区间计算规则可以不相同

**7\. sortByKey**
按key进行排序，第一个参数指定是否升序，默认升序，false为降序。
```
def main(args: Array[String]): Unit = {
    val sc = new SparkContext("local[*]", "sortByKey")
    val rdd: RDD[(String, Int)] = sc.makeRDD(List(("b", 6), ("b", 5), ("a", 3), ("a", 1), ("a", 4), ("a", 2)), 2)
    val sortByKeyRDD: RDD[(String, Int)] = rdd.sortByKey(ascending = false)
    sortByKeyRDD.collect.foreach(println)
}
```
输出：
```
(b,6)
(b,5)
(a,3)
(a,1)
(a,4)
(a,2)
```
如果是自定义类型，则key必须实现Ordered特质
```
class User(val name: String, val age: Int) extends Serializable with Ordered[User] {
  override def compare(that: User): Int = age - that.age
  override def toString = s"User(name=$name, age=$age)"
}
```
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "sortByKey")
  val rdd: RDD[(User, Int)] = sc.makeRDD(List(
    (new User("zs", 20), 2),
    (new User("li", 21), 5),
    (new User("ww", 22), 1),
    (new User("zl", 19), 6)
  ), 2)
  rdd.sortByKey().collect.foreach(println)
}
```
输出：
```
(User(name=zl, age=19),6)
(User(name=zs, age=20),2)
(User(name=li, age=21),5)
(User(name=ww, age=22),1)
```

**案例： 统计出每一个省份每个广告被点击数量排行的 Top3**
数据格式：时间戳、省份、城市、用户、广告，中间字段使用空格分隔。
第5、6步的group+mapValues实现的是分组内排序取前3的操作，不能使用aggregateByKey等聚合函数来实现相同的功能，所以不能用那4个聚合算子来代替。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "case")
  // 1. 获取原始数据：时间戳，省份，城市，用户，广告
  val rdd: RDD[String] = sc.textFile("data/agent.log")
  // 2. 转换原始数据的结构，方便统计
  //    时间戳，省份，城市，用户，广告
  //    =>
  //    ((省份, 广告), 1)
  rdd.map(line => {
    val cols = line.split(" ")
    ((cols(1), cols(4)), 1)
  })
    // 3. 将转换结构后的数据分组聚合
    //   ((省份, 广告), 1) => ((省份, 广告), sum)
    .reduceByKey(_ + _)
    // 4. 转换聚合结果的结构
    //   ((省份, 广告), sum) => (省份, (广告, sum))
    .map(kv => (kv._1._1, (kv._1._2, kv._2)))
    // 5. 将转换结构后的数据根据省份进行分组
    //   (省份, [(广告A, sumA), (广告B, sumB)])
    .groupByKey
    // 6. 将分组后的数据组内排序（降序），取前3名
    .mapValues(_.toList.sortBy(_._2)(Ordering.Int.reverse).take(3))
    // 7. 采集数据打印在控制台
    .collect.foreach(println)
  sc.stop()
}
```

