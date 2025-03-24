---

Created at: 2021-10-08
Last updated at: 2021-10-08


---

# 10-Scala的方法 与 Java的方法引用


在Scala中，方法与函数除了以下两点不同外，在其它用法上是完全相同的，比如Scala中方法同样可以像函数一样赋值给变量。
1.函数没有重载和重写的概念，不能在同一个作用域内定义两个同名的函数，但是方法可以进行重载和重写。
2.方法只能提供类的对象来调用，而函数声明之后可以直接调用。
测试如下，伴生对象和实例对象都是对象，可以将对象的方法赋值给变量
```
object MyMethod {
  def func2(): Unit = {
    println("MyMethod func2")
  }
}

class MyMethod(val field: String) {
  def func1(): Unit = {
    println(field)
  }
}
```
```
def main(args: Array[String]): Unit = {
  val myMethod = new MyMethod("MyMethod field")
  val f1: () => Unit = myMethod.func1
  val f2: () => Unit = MyMethod.func2
  f1()
  f2()
}
```
输出结果：
```
MyMethod field
MyMethod func2
```

Java中的函数式接口是借鉴自Scala函数式编程的思想
```
@FunctionalInterface
interface FuncInterface {
    void method(String str);
}

class AClass {
    public static void invokeMethod(FuncInterface func) {
        func.method("AClass");
    }
}

public class BClass {
    void myPrint(String str) {
        System.out.println(str);
    }
    public static void main(String[] args) {
        BClass bClass = new BClass();
        AClass.invokeMethod(bClass::myPrint);
    }
}
```
可以将函数式接口直接看作是函数，bClass::myPrint赋值给func变量，其实就是将实例对象bClass的方法myPrint赋值给变量，等价于以后调用func.method其实就是调用bClass.myPrint

