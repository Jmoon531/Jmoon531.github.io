---

Created at: 2021-08-10
Last updated at: 2024-08-16
Source URL: https://blog.csdn.net/Pzzzz_wwy/article/details/106106555


---

# 04-Callable接口 和 FutureTask


Callable创建线程的流程：
1.实现Callable接口
```
class MyThreadCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        System.out.println("******come in here");
        return 1024;
    }
}
```
2.创建FutureTask对象
```
FutureTask futureTask = new FutureTask(new MyThreadCallable());
```
3.创建线程
```
new Thread(futureTask, "A").start();
```

为什么要三步？
实现Callable接口就是任务，创建FutureTask对象是为了能拿到返回值，创建Thread对象是为创建线程

主线程阻塞等待为了能拿到返回值（因为要拿返回值必须阻塞，所以最原始的Thread的run()方法肯定不能设计成有返回值）：
```
Integer result = futureTask.get()
```

完整代码：
```
class MyThreadCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        System.out.println("******come in here");
        Thread.sleep(5000);
        return 1024;
    }
}
public class CallableDemo {
    public static void main(String[] args) throws Exception {
        FutureTask<Integer> futureTask = new FutureTask<>(new MyThreadCallable());
        new Thread(futureTask, "A").start();
        //阻塞等待返回值
        Integer result = futureTask.get();
        System.out.println(result);
        System.out.println(Thread.currentThread().getName()+"***计算完成");
    }
}
```

原理：
创建线程的原理没变，还是new Thread().start();执行的是Thread的run方法，run方法没有返回值，为什么使用FutureTask后可以拿到返回值？
FutureTask实现了Runnable接口重写了run方法， 在重写的run方法中调用了result = c.call();，也就是Callable接口的call方法，这个是留给用户自定义的，执行完拿到结果之后之后调用set(result);，这个方法做两件事，一是保存结果到FutureTask的实例变量中，二是更新状态字段。之后我们就可以调用futureTask.get();拿到返回值了。
```
public void run() {
    if (state != NEW ||
        !RUNNER.compareAndSet(this, null, Thread.currentThread()))
        return;
    try {
        Callable<V> c = callable;
        if (c != null && state == NEW) {
            V result;
            boolean ran;
            try {
                `result = c.call();`
                ran = true;
            } catch (Throwable ex) {
                result = null;
                ran = false;
                setException(ex);
            }
            if (ran)
                `set(result);`
        }
    } finally {
        // runner must be non-null until state is settled to
        // prevent concurrent calls to run()
        runner = null;
        // state must be re-read after nulling runner to prevent
        // leaked interrupts
        int s = state;
        if (s >= INTERRUPTING)
            handlePossibleCancellationInterrupt(s);
    }
}
```
```
protected void set(V v) {
    if (STATE.compareAndSet(this, NEW, COMPLETING)) {
        outcome = v;
        STATE.setRelease(this, NORMAL); // final state
        finishCompletion();
    }
}
```
futureTask.get();会阻塞，是怎么实现的？因为awaitDone()返回调用了LockSupport.park();
```
public V get() throws InterruptedException, ExecutionException {
    int s = state;
    if (s <= COMPLETING)
        s = awaitDone(false, 0L);
    return report(s);
}
```
FutrueTask任务只会执行一次，比如下面程序只会打印一次 come in here，原因：从run()前两行可以看到，FutureTask只会调用Callable接口的call方法一次。
```
class MyThreadCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        System.out.println("******come in here");
        return 1024;
    }
}
public class CallableDemo01 {
    public static void main(String[] args) throws Exception {
        FutureTask<Integer> futureTask = new FutureTask<>(new MyThreadCallable());
        new Thread(futureTask, "A").start();
        new Thread(futureTask, "B").start();
    }
}
```

使用FutrueTask实现类似于前端Ajax那样的异步调用：
不用担心线程执行的时候抛异常，因为在FutureTask重写的run方法中已经把异常全吞了，只有在get()的时候才会再把异常吐出来。
```
public class AsyncCall<V> {
    private final FutureTask<V> futureTask;

    private AsyncCall(FutureTask<V> futureTask) {
        this.futureTask = futureTask;
    }

    public static <V> AsyncCall<V> call(Callable<V> callable) {
        FutureTask<V> futureTask = new FutureTask<>(callable);
        new Thread(futureTask).start();
        return new AsyncCall<>(futureTask);
    }

    public void then(Consumer<V> success, Consumer<Throwable> failure) {
        new Thread(() -> {
            try {
                V result = futureTask.get();
                success.accept(result);
            } catch (Exception e) {
                failure.accept(e);
            }
        }).start();
    }
}
```
测试：
```
public class TestAsyncCall {
    public static void main(String[] args) {
        AsyncCall.call(() -> {
            System.out.println("异步调用1");
            return 1 / 0;
        }).then(v -> System.out.println("异步调用1成功，结果是：" + v), e -> System.out.println("异步调用1失败，异常：" + e));
        AsyncCall.call(() -> {
            System.out.println("异步调用2");
            return 1;
        }).then(v -> System.out.println("异步调用2成功，结果是：" + v), e -> System.out.println("异步调用2失败，异常：" + e));
    }
}
```
不过其实上面的写法还是有点脱裤子放屁的感觉，因为call()和then()两个方法的执行有先后关系，一点也不重合，完全可以在一个线程里按顺序执行。
```
public class AsyncCall02<V> {
    private final Callable<V> callable;

    private AsyncCall02(Callable<V> callable) {
        this.callable = callable;
    }

    public static <V> AsyncCall02<V> call(Callable<V> callable) {
        return new AsyncCall02<>(callable);
    }

    public void then(Consumer<V> success, Consumer<Throwable> failure) {
        Runnable task = () -> {
            try {
                V result = callable.call();
                success.accept(result);
            } catch (Exception e) {
                failure.accept(e);
            }
        };
        new Thread(task).start();
    }
}
```

为什么前端使用异步调用比后端多？
这是两种不同场景所处理的任务类型的差异所决定的，前端是调用者，向后端取结果，当前端后续步骤不依赖这个结果的时候，他就不愿意等，要先干后面的活，等这个结果发送回来了再处理，比如把结果显示在页面上，前端的场景就是处理与用户交互，很多操作都没有依赖关系，所以异步任务要比后端多。

