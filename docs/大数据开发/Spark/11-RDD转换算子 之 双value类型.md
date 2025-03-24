---

Created at: 2021-09-25
Last updated at: 2021-09-29
Source URL: about:blank


---

# 11-RDD转换算子 之 双value类型


**双value类型**，即对两个数据源数据的操作
```
val sc = new SparkContext("local[*]", "zip")
val rdd1 = sc.makeRDD(List(1,2,3,4))
val rdd2 = sc.makeRDD(List(3,4,5,6))
```

**1.交集，intersection**
```
// 交集 : 【3，4】
val rdd3: RDD[Int] = rdd1.intersection(rdd2)
println(rdd3.collect().mkString(","))
```

**2.并集，union**
```
// 并集 : 【1，2，3，4，3，4，5，6】
val rdd4: RDD[Int] = rdd1.union(rdd2)
println(rdd4.collect().mkString(","))
```

**3.差集，subtract**
```
// 差集 : 【1，2】
val rdd5: RDD[Int] = rdd1.subtract(rdd2)
println(rdd5.collect().mkString(","))
```

**4.拉链，zip**
```
// 拉链 : 【(1,3),(2,4),(3,5),(4,6)】，得到的是一个元组的集合
val rdd6: RDD[(Int, Int)] = rdd1.zip(rdd2)
println(rdd6.collect().mkString(","))
```
拉链有两点需要注意：
1.要求两个数据源分区数量要保持一致
2.要求两个数据源各个分区中数据量要保持一致

另外还需要注意一点，交集，并集和差集要求两个数据源数据类型保持一致，拉链操作两个数据源的类型可以不一致

以下3个算子即是双value类型的算子，也是key-value类型的算子，即均是对两个kv类型的数据源的操作。
**5.join**
在类型为(K,V)和(K,W)的 RDD 上调用，返回一个相同 key 对应的所有元素连接在一起的 (K,(V,W)) 的 RDD。注意一点就是两数据源的value的类型可以不同。
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "combineByKey")
  val rdd1 = sc.makeRDD(List(("a", 1), ("a", 2), ("c", 3), ("f", 3)))
  val rdd2 = sc.makeRDD(List(("a", 5), ("c", 6), ("a", 4)))
  val joinRDD: RDD[(String, (Int, Int))] = rdd1.join(rdd2)
  joinRDD.collect.foreach(println)
  sc.stop()
}
```
输出结果：
```
(a,(1,5))
(a,(1,4))
(a,(2,5))
(a,(2,4))
(c,(3,6))
```
可见：

1. 两个不同数据源中相同的key的value会连接在一起，形成二元组
2. 如果两个数据源中key没有匹配上，那么数据不会出现在结果中
3. 如果两个数据源中有多个相同的key，会依次匹配

**6\. leftOuterJoin 和 rightOuterJoin**
leftOuterJoin输出的value的第二个元素是Option类型
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "combineByKey")
  val rdd1 = sc.makeRDD(List(("a", 1), ("b", 2), ("c", 3)))
  val rdd2 = sc.makeRDD(List(("a", 4), ("b", 5)))
  val leftOuterJoinRDD: RDD[(String, (Int, Option[Int]))] = rdd1.leftOuterJoin(rdd2)
  leftOuterJoinRDD.collect.foreach(println)
  sc.stop()
}
```
输出：
```
(a,(1,Some(4)))
(b,(2,Some(5)))
(c,(3,None))
```

而rightOuterJoin输出的value的第一个元素是Option类型
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "combineByKey")
  val rdd1 = sc.makeRDD(List(("a", 1), ("b", 2)))
  val rdd2 = sc.makeRDD(List(("a", 4), ("b", 5), ("c", 6)))
  val rightOuterJoinRDD: RDD[(String, (Option[Int], Int))] = rdd1.rightOuterJoin(rdd2)
  rightOuterJoinRDD.collect.foreach(println)
  sc.stop()
}
```
输出：
```
(a,(Some(1),4))
(b,(Some(2),5))
(c,(None,6))
```

**7\. cogroup**
cogroup可以操作两个及以上的kv类型数据源，其功能是，先对每个数据源的数据根据key分组，然后再连接所有数据源的数据
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "cogroup")
  val rdd1 = sc.makeRDD(List(("a", 1), ("a", 2), ("b", 3) ))
  val rdd2 = sc.makeRDD(List(("a", 4), ("b", 5), ("c", 6)))
  val rdd3 = sc.makeRDD(List(("c", 4), ("d", 5), ("d", 6)))
  val cogroupRDD: RDD[(String, (Iterable[Int], Iterable[Int], Iterable[Int]))] = rdd1.cogroup(rdd2,rdd3)
  cogroupRDD.collect.foreach(println)
  sc.stop()
}
```
输出结果如下，value是一个三元组，因为有3个数据源，三元组的每一个元素是对应数据源中key对应的value的集合。
```
(a,(CompactBuffer(1, 2),CompactBuffer(4),CompactBuffer()))
(b,(CompactBuffer(3),CompactBuffer(5),CompactBuffer()))
(c,(CompactBuffer(),CompactBuffer(6),CompactBuffer(4)))
(d,(CompactBuffer(),CompactBuffer(),CompactBuffer(5, 6)))
```

