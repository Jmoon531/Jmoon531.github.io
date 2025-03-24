---

Created at: 2021-09-16
Last updated at: 2021-11-12


---

# 1-Hello Scala


Scala是一个多范式的编程语言，多范式指的是Scala既是面向对象的又可以函数式编程。用Scala写的优秀的框架有：spark、Kafka、akka。

安装配置Scala
1.下载并解压Scala的SDK，scala-2.12.11.zip
2.配置环境变量
SCALA\_HOME=D:\\Program Files\\scala-2.12.11
Path环境变量加上%SCALA\_HOME%\\bin

Scala的Hello World程序
1.HelloScala.scala
```
object HelloScala {
  def main(args: Array[String]): Unit = {
    println("hello scala")
  }
}
```
2.编译，Scala也是运行在jvm上的，所以编译的结果也是字节码.class文件
```
scalac HelloScala.scala
```
3.运行
```
scala HelloScala
```
4.因为Scala编译结果也是字节码文件，所以按道理来讲，使用java命令也可运行Scala编译的字节码，确实可以，但是使用java命令运行字节码时，只会默认指明java的sdk的路径，而从Scala反编译的结果来看Scala默认import scala.Predef.; 所以使用java命令运行Scala编译的字节码时还需要指明Scala的SDK的路径。还有一个问题，Scala编译的结果有两个字节码文件，那程序的入口，即公有静态main方法应该在那个字节码文件中呢，直观的来看应该在不带$符号的字节码文件，因为我们写的main方法就是在不带$符号的object中，通过反编译的结果看来，也确实是在不带$符号的字节码文件（但这个不带$符号的object却不是这个不带$符号的字节码的类的对象，而是那个带$符号的字节码的类的对象，下一篇笔记会解释这个问题，以及为什么会生成两个字节码文件 和 程序的入口方法为什么在不带$符号的字节码文件中）。
```
java -cp %SCALA_HOME%/lib/scala-library.jar HelloScala
```

idea中配置Scala的编写环境
1.下载Scala的插件
2.新建Maven工程
3.右键工程，Add FrameWrok Support，选择Scala

