---

Created at: 2021-09-30
Last updated at: 2021-09-30


---

# 21-SparkSQL IDEA中使用


引入依赖
```
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql_2.12</artifactId>
    <version>3.0.0</version>
</dependency>
```

**DataFrame**
1.创建和展示
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  // TODO DataFrame
  val df: DataFrame = spark.read.json("data/user.json")
  df.show()
  // TODO 关闭环境
  spark.close()
}
```

2.SQL
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  // TODO DataFrameSQL
  val df: DataFrame = spark.read.json("data/user.json")
  `df.createOrReplaceTempView("user")`
  spark.sql("select name,age from user").show
  spark.sql("select avg(age) from user").show
  // TODO 关闭环境
  spark.close()
}
```

3.DSL
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  // TODO DataFrame DSL
 `// 在使用DataFrame时，如果涉及到转换操作，需要引入转换规则，implicits是spark对象里面的一个对象，它里面包含着所有隐式转换所需要的东西`
 `import spark.implicits._`
  val df: DataFrame = spark.read.json("data/user.json")
 `df.select($"name", $"age" + 1).show`
 `df.select('name, 'age + 1).show`
  // TODO 关闭环境
  spark.close()
}
```

**DataSet**
1.创建和展示
```
case class User(name: String, age: Int)
```
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  import spark.implicits._
  // TODO DataSet
  val list = List(User("zhangsan", 18), User("lisi", 19), User("wangwu", 20))
 `//toDS不是List的方法，这里应该是隐式转换，隐式转换真的特别复合开闭原则`
 `val ds: Dataset[User] = list.toDS()`
  ds.show()
  // TODO 关闭环境
  spark.close()
}
```

2.DataFrame其实就是泛型是Row的DataSet，所以DataFrame的方法DataSet都能用
```
type DataFrame = org.apache.spark.sql.Dataset[org.apache.spark.sql.Row]
```

**RDD 、DataFrame 、DataSet 三者之间的转换**
1.RDD 与 DataFrame 之间的转换
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  import spark.implicits._

  // TODO RDD 与 DataFrame 之间的转换
  // RDD => DataFrame
 `val rdd = spark.sparkContext.makeRDD(List((1, "zhangsan", 30), (2, "lisi", 40)))`
 `val df: DataFrame = rdd.toDF("id", "name", "age")`
  df.show

  // DataFrame => RDD
 `val rowRDD: RDD[Row] = df.rdd`
  rowRDD.collect.foreach(println)
  // TODO 关闭环境
  spark.close()
}
```

2.DataFrame 与 DataSet 之间的转换
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  import spark.implicits._
  val rdd = spark.sparkContext.makeRDD(List(User("zhangsan",18), User("lisi", 19), User("wangwu", 20)))
  val df = rdd.toDF()

  // TODO DataFrame 与 DataSet 之间的转换
  // DataFrame => DataSet
  `val ds: Dataset[User] = df.as[User]`
  ds.show

  // DataSet => DataFrame
 `val df1 = ds.toDF()`
  df1.show

  // TODO 关闭环境
  spark.close()
}
case class User(name: String, age: Int)
```

3.RDD 与 DataSet 之间的转换
```
def main(args: Array[String]): Unit = {
  // TODO 创建SparkSQL的运行环境
  val sparkConf = new SparkConf().setMaster("local[*]").setAppName("sparkSQL")
  val spark = SparkSession.builder().config(sparkConf).getOrCreate()
  import spark.implicits._
  val rdd = spark.sparkContext.makeRDD(List(User("zhangsan", 18), User("lisi", 19), User("wangwu", 20)))

  // TODO RDD 与 DataSet 之间的转换
  // RDD => DataSet
 `val ds = rdd.toDS()`
  ds.show

  // DataSet => RDD
 `val userRDD: RDD[User] = ds.rdd`
  userRDD.collect.foreach(println)

  // TODO 关闭环境
  spark.close()
}

case class User(name: String, age: Int)
```

