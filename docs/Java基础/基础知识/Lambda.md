---

Created at: 2024-06-27
Last updated at: 2024-08-16
Source URL: about:blank


---

# Lambda


帮助更好的在Java中使用函数式编程的库
```
<dependency>
    <groupId>io.vavr</groupId>
    <artifactId>vavr</artifactId>
    <version>0.10.4</version>
</dependency>
```
比如：
```
Try.success(sc.nextInt())
        .andThen(t -> {
            if (t == 0) {
                throw new RuntimeException("fail");
            } else {
                System.out.println("success");
            }
        })
        .failed()
        .andThen(cause -> System.out.println("调用失败了，原因是" + cause.getMessage() + "，请稍后重试！"));
```

