---

Created at: 2021-09-28
Last updated at: 2021-10-05
Source URL: about:blank


---

# 18-SparkCore案例实操


需求一：Top10 热门品类

统计每个品类的点击次数、下单次数、支付次数，然后根据这三个量对品类排序，点击次数相同后再比较下单次数，以此类推，最后取Top10 热门品类
1.其实就是一个WordCount
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "req01_top10")
  // 1. 读取原始日志数据
  sc.textFile("data/user_visit_action.txt")
    // 2. 将数据转换结构
    .flatMap(line => {
      val cols = line.split("_")
      if (cols(6) != "-1") {
        // 点击的场合 : ( 品类ID，( 1, 0, 0 ) )
        List((cols(6), (1, 0, 0)))
      } else if (cols(8) != "null") {
        // 下单的场合 : ( 品类ID，( 0, 1, 0 ) )
        cols(8).split(",").map((_, (0, 1, 0)))
      } else if (cols(10) != "null") {
        // 支付的场合 : ( 品类ID，( 0, 0, 1 ) )
        cols(10).split(",").map((_, (0, 0, 1)))
      } else {
        Nil
      }
    })
    // 3. 将相同的品类ID的数据进行分组聚合
    //    ( 品类ID，( 点击数量, 下单数量, 支付数量 ) )
    .reduceByKey((t1, t2) => {
      (t1._1 + t2._1, t1._2 + t2._2, t1._3 + t2._3)
    })
    // 4. 将统计结果根据数量进行降序处理，取前10名
    .sortBy(_._2, ascending = false).take(10).foreach(println)
}
```
2.使用累加器完成这个WordCount
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "req01_top10")

  // 1. 读取原始日志数据
  val data = sc.textFile("data/user_visit_action.txt")

  //创建累加器
  val acc = new MyAccumulator
  //注册累加器
  sc.register(acc)

  //对每一行数据做累加
  data.foreach(line => {
    val cols = line.split("_")
    if (cols(6) != "-1") {
      //如果是点击行为，那么就将点击的品类id传到累加器中累加，第一个参数0标识这是点击行为
      acc.add((0, cols(6)))
    } else if (cols(8) != "null") {
      //如果是下单行为，那么就将下单的所有品类id传到累加器中累加，第一个参数1标识这是下单行为
      acc.add((1, cols(8)))
    } else if (cols(10) != "null") {
      //如果是支付行为，那么就将支付的所有品类id传到累加器中累加，第一个参数2标识这是支付行为
      acc.add((2, cols(10)))
    }
  })

  //对累加器的结果排序，然后取top10输出
  acc.value.toList.sortWith((a, b) => {
    if (a._2(0) != b._2(0)) {
      a._2(0) > b._2(0)
    } else if (a._2(1) != b._2(1)) {
      a._2(1) > b._2(1)
    } else {
      a._2(2) > b._2(2)
    }
  }).take(10).foreach(println)
}
```
```
class MyAccumulator extends AccumulatorV2[(Int, String), mutable.Map[String, ArrayBuffer[Int]]] {

  private val map = mutable.Map[String, ArrayBuffer[Int]]()

  override def add(v: (Int, String)): Unit = {
    //虽然点击行为只有一个品类id，但是还是可以使用split方法的
    for (id <- v._2.split(",")) {
      val arrayBuffer = map.getOrElse(id, ArrayBuffer[Int](0, 0, 0))
      //根据行为把品类对应位置的数据加1
      arrayBuffer(v._1) += 1
      map.update(id, arrayBuffer)
    }
  }

  override def merge(other: AccumulatorV2[(Int, String), mutable.Map[String, ArrayBuffer[Int]]]): Unit = {
    //合并两个Map的常规操作
    other.value.foreach(kv => {
      val arrayBuffer = map.getOrElse(kv._1, ArrayBuffer[Int](0, 0, 0))
      for (i <- 0 until 3) {
        arrayBuffer(i) += kv._2(i)
      }
      map.update(kv._1, arrayBuffer)
    })
  }
  override def value: mutable.Map[String, ArrayBuffer[Int]] = map
  override def isZero: Boolean = map.isEmpty
  override def copy(): AccumulatorV2[(Int, String), mutable.Map[String, ArrayBuffer[Int]]] = new MyAccumulator
  override def reset(): Unit = map.clear()
}
```

需求二： Top10 热门品类中每个品类点击 Top10 的session
就是求这10个品类的每一个品类点击前10的session及其点击数
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "req02_top10")
  // 1. 读取原始日志数据
  val data = sc.textFile("data/user_visit_action.txt")
  data.cache()
  // 2. Top10 热门品类
  val categoryTop10: Array[(String, (Int, Int, Int))] = data.flatMap(line => {
    val cols = line.split("_")
    if (cols(6) != "-1") {
      List((cols(6), (1, 0, 0)))
    } else if (cols(8) != "null") {
      cols(8).split(",").map((_, (0, 1, 0)))
    } else if (cols(10) != "null") {
      cols(10).split(",").map((_, (0, 0, 1)))
    } else {
      Nil
    }
  })
    .reduceByKey((t1, t2) => {
      (t1._1 + t2._1, t1._2 + t2._2, t1._3 + t2._3)
    })
    .sortBy(_._2, ascending = false).take(10)

  val top10 = categoryTop10.map(_._1)

  //3.Top10 热门品类中每个品类点击 Top10 的session及其点击数
  //思路：
  // 1.先过滤数据
  // 2.再根据品类和session做WordCount
  // 3.然后根据品类分组
  // 4.组内根据WordCount的结果排序取前10
  data.map(line => {
    val cols = line.split("_")
    //((click_category_id, session_id) ,1)
    ((cols(6), cols(2)), 1)
  }).filter(kv => top10.contains(kv._1._1))
    .reduceByKey(_ + _)
    //(click_category_id, (session_id ,sum))
    .map(kv => (kv._1._1, (kv._1._2, kv._2)))
    //同一品类分组
    .groupByKey
    //排序取前10
    .mapValues(iter => iter.toList.sortBy(_._2)(Ordering.Int.reverse).take(10))
    .collect.foreach(println)
}
```

需求三：页面跳转率统计
从 1号页面跳转到3号页面的总次数 除以 1号页面被访问的总次数 就是 1号页面到3号页面的跳转率
1.求每个跳转的页面跳转率
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "req03")
  // 1. 读取原始日志数据
  val data = sc.textFile("data/user_visit_action.txt")

  // TODO 计算分母
  //计算每个页面访问的总次数，比如2号页面访问了99次 (2,99)，其实就是WordCount
  data.cache()
  val pageAccessSum = data.map(line => {
    val cols = line.split("_")
    //(page_id, 1)
    (cols(3), 1)
  })
    .reduceByKey(_ + _)
    .collect
    //转换成Map，方便后面直接根据页面取访问总次数
    .toMap

  val bc = sc.broadcast(pageAccessSum)

  // TODO 计算分子
  // 计算页面跳转到的总次数，如从2号页面跳到3号页面一共100次 ((2,3),100)
  // 思路：
  // 1.按session分组
  // 2.按时间排序(升序)
  // 3.拉链，比如某个session内页面访问顺序是3,5,7,6，那么页面跳转情况就是(3,5)(5,7)(7,6),或者使用滑窗sliding可以得到同样的效果
  // 4.计算全局每个跳转的次数，又是WordCount
  data.map(line => {
    val cols = line.split("_")
    //(session_id, (page_id, action_time))
    (cols(2), (cols(3), cols(4)))
  })
    //按sessionID分组
    .groupByKey()
    .flatMap {
      case (_, page_action) =>
        //按时间排序后只取page_id
        val page = page_action.toList.sortBy(_._2).map(_._1)
        //page_id拉链，(page_id, page_id)，然后在后面加个1，((page_id, page_id),1)，WordCount常规做法
        `page.zip(page.tail)`.map((_, 1))
    }
    .reduceByKey(_ + _)
    //TODO 计算页面跳转率
    .foreach(kv => {
      val percent = kv._2.toDouble / bc.value(kv._1._1)
      println(s"${kv._1._1} -> ${kv._1._2} = ${percent}")
    })
}
```

2.求指定连续跳转的页面跳转率
比如求连续跳转 (1,2)、(2,3)、(3,4)、(5,6)、(6,7) 中的每一跳的页面跳转率
```
def main(args: Array[String]): Unit = {
  val sc = new SparkContext("local[*]", "req03")
  //指定页面
  val pages = List("1", "2", "3", "4", "5", "6", "7")
  //连续跳转
  val hop = pages.zip(pages.tail)
  // 1. 读取原始日志数据
  val data = sc.textFile("data/user_visit_action.txt")
  data.cache()

  // TODO 计算分母
  //计算指定页面的访问总次数，比如2号页面访问了99次 (2,99)，还是WordCount
  val pageAccessSum = data.map(line => {
    val cols = line.split("_")
    //(page_id, 1)
    (cols(3), 1)
  })
    //过滤，只留下指定页面的访问总次数，注意此时根本不需要统计最后一个页面也就是7号页面的访问次数
    // 使用init方法可以得到不包含最后一个元素的集合
    .filter(kv => `pages.init.`contains(kv._1))
    .reduceByKey(_ + _)
    .collect
    //转换成Map，方便后面直接根据页面取访问总次数
    .toMap

  val bc = sc.broadcast(pageAccessSum)

  // TODO 计算分子
  // 计算指定页面跳转的总次数，如从2号页面跳到3号页面一共100次 ((2,3),100)
  // 思路：
  // 1.按session分组
  // 2.按时间排序(升序)
  // 3.拉链，比如某个session内页面访问顺序是3,5,7,6，那么页面跳转情况就是(3,5)(5,7)(7,6)，使用滑窗可以完成这个效果
  // 4.过滤，只留下指定页面
  // 5.计算指定页面跳转的总次数，又是WordCount
  data.map(line => {
    val cols = line.split("_")
    //(session_id, (page_id, action_time))
    (cols(2), (cols(3), cols(4)))
  })
    //不能在这里过滤页面，因为如果页面访问顺序是1,6,2，过滤之后就会是1,2，于是(1,2)就增加了一次
    //.filter(kv => pages.contains(kv._2._1))
    //按sessionID分组
    .groupByKey()
    .flatMap {
      case (_, page_action) =>
        //按时间排序后只取page_id
        val page = page_action.toList.sortBy(_._2).map(_._1)
        // page_id拉链，(page_id, page_id)，拉链后过滤，
        // 然后后面加个1，((page_id, page_id),1)，WordCount常规做法
        page.zip(page.tail).filter(kv => hop.contains(kv)).map((_, 1))
    }
    .reduceByKey(_ + _)
    //TODO 计算页面跳转率
    .foreach(kv => {
      //计算指定页面的跳转率
      val percent = kv._2.toDouble / bc.value(kv._1._1)
      println(s"${kv._1._1} -> ${kv._1._2} = ${percent}")
    })
}
```

