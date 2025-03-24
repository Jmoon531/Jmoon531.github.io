---

Created at: 2024-08-16
Last updated at: 2024-08-16
Source URL: https://blog.csdn.net/zsx_xiaoxin/article/details/123898171


---

# 05-CompletableFuture


在前面为了模拟Ajax的异步调用方式，我写了一个AsyncCall类，可以使用该类完成这样的普遍且通用的编程范式：Async.call(你的任务).then(调用成功了的动作, 调用失败了的动作) ，其实JDK8引入的CompletableFuture类正是来完成这样的任务的，它额外还提供了更多方便的调用，比如多个Future组合处理的能力，使Java在处理多任务的协同工作时更加顺畅便利。

参考： [CompletableFuture使用详解（全网看这一篇就行）_supplyasync-CSDN博客](https://blog.csdn.net/zsx_xiaoxin/article/details/123898171)
[优雅处理并发：Java CompletableFuture最佳实践 - 个人文章 - SegmentFault 思否](https://segmentfault.com/a/1190000044543793)

1、创建CompletableFuture任务
supplyAsync是创建带有返回值的异步任务；runAsync是创建没有返回值的异步任务。分别有两个重载方法，一个使用的是默认线程池（ForkJoinPool.commonPool()）的方法，另一个可以自定义线程池。
```
// 带返回值异步请求，默认线程池
public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier)
// 带返回值的异步请求，可以自定义线程池
public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier, Executor executor)
// 不带返回值的异步请求，默认线程池
public static CompletableFuture<Void> runAsync(Runnable runnable)
// 不带返回值的异步请求，可以自定义线程池
public static CompletableFuture<Void> runAsync(Runnable runnable, Executor executor)
```
```
public static void main(String[] args) throws ExecutionException, InterruptedException {
    CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
        // 模拟耗时的计算
        System.out.println(("数据加载中"));
        return "结果";
    });
    CompletableFuture<Void> future2 = CompletableFuture.runAsync(() -> {
        System.out.println(("正在执行一些处理"));
    });
}
```
```
数据加载中
正在执行一些处理
```
获取任务返回值的方法
```
// 如果完成则返回结果，否则就抛出具体的异常
public T get() throws InterruptedException, ExecutionException
// 最大时间等待返回结果，否则就抛出具体异常
public T get(long timeout, TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException
// 完成时返回结果值，否则抛出unchecked异常。为了更好地符合通用函数形式的使用，如果完成此 CompletableFuture所涉及的计算引发异常，则此方法将引发unchecked异常并将底层异常作为其原因
public T join()
// 如果完成则返回结果值（或抛出任何遇到的异常），否则返回给定的 valueIfAbsent。
public T getNow(T valueIfAbsent)
// 如果任务没有完成，返回的值设置为给定值
public boolean complete(T value)
// 如果任务没有完成，就抛出给定异常
public boolean completeExceptionally(Throwable ex)
```
```
public static void main(String[] args) throws ExecutionException, InterruptedException {
    CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
        // 模拟耗时的计算
        System.out.println(("数据加载中"));
        return "future1结果";
    });
    System.out.println("结果->" + future1.get());
    CompletableFuture<Void> future2 = CompletableFuture.runAsync(() -> {
        System.out.println(("正在执行一些处理"));
    });
    System.out.println("结果->" + future2.get());
}
```
```
数据加载中
结果->future1结果
正在执行一些处理
结果->null
```

2、异步回调处理
```
public static void main(String[] args) {
    CompletableFuture.supplyAsync(() -> {
        System.out.println("查询数据库");
        return "查询结果";
    }).thenApply(result -> {
        // 对结果进行处理
        return "thenApply处理后的结果：" + result;
    }).thenAccept(processedResult -> {
        // 消费处理后的结果
        System.out.println("thenAccept最终结果：" + processedResult);
    }).thenRun(() -> {
        // 执行一些不需要前一个结果的操作
        System.out.println("所有操作完成");
    });
}
```
```
查询数据库
thenAccept最终结果：thenApply处理后的结果：查询结果
所有操作完成
```

3、多任务组合处理
```
public static void main(String[] args) throws ExecutionException, InterruptedException {
    CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
        System.out.println("加载用户数据");
        return "用户小黑";
    });
    CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> {
        System.out.println("加载配置信息");
        return "配置信息";
    });
    // 组合两个future，等待它们都完成
    CompletableFuture<String> combinedFuture = future1.thenCombine(future2, (user, config) -> {
        return "处理结果: " + user + "，" + config;
    });
    System.out.println(combinedFuture.get());
}
```

