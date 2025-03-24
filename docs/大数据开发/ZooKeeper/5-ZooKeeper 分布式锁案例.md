---

Created at: 2021-08-30
Last updated at: 2021-08-31
Source URL: https://blog.csdn.net/weixin_39654122/article/details/120017293


---

# 5-ZooKeeper 分布式锁案例


利用zookeeper可以实现分布式排他锁，和分布式共享锁

以下讲两种分布式排他锁的实现方法
第一种方法，不断尝试创建同一个临时节点，如果创建节点成功就表示获得了锁，这样能行是因为两点，一是zookeeper会顺序执行同一个客户端的请求，这样能保证同一个客户端只有一个请求能创建节点成功；二是zookeeper还能保证不同客户端的请求也只有一个请求能创建成功。
总之一句话，用户根本就不用去考虑他连接的具体是哪一台zookeeper，也不要考虑zookeeper集群之间的数据是否一致，最重要的是用户不用考虑并发的修改请求会不会打乱整个树形结构，因为在用户看来zookeeper集群就是一个并发安全的树形存储结构，类似于并发安全的CurrentHashMap。
```
public class XLock {

    private ZooKeeper zkClient;
    private static final String LOCKNODE = "/exclusive_lock/lock";

    public XLock() {
        try {
            String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
            int sessionTimeout = 2000;
            zkClient = new ZooKeeper(connectString, sessionTimeout, null);
            // 判断节点 /locks 是否存在
            if (zkClient.exists("/exclusive_lock", false) == null) {
                // 不存在则创建节点
                zkClient.create("/exclusive_lock", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void lock() {
        while (true) {
            try {
                zkClient.create(LOCKNODE, null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL);
                System.out.println(Thread.currentThread().getName() + "获取锁成功");
                break;
            } catch (Exception e) {
                try {
                    TimeUnit.MILLISECONDS.sleep(300);
                } catch (InterruptedException ex) {
                    ex.printStackTrace();
                }
            }
        }
    }

    public void unlock() {
        try {
            System.out.println(Thread.currentThread().getName() + "释放了锁");
            zkClient.delete(LOCKNODE, -1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

测试类需要new 两个XLock的原因是，在同一台机器里的并发线程都是用的同一个锁对象，而在在不同主机里的线程那就用的是不同的锁对象，这里模拟的是分布式锁的场景，所以需要new 两个锁对象。
```
public class XLockTest {
    public static void main(String[] args) {
        XLock xLock01 = new XLock();
        Runnable task01 = () -> {
            xLock01.lock();
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            xLock01.unlock();
        };

        XLock xLock02 = new XLock();
        Runnable task02 = () -> {
            xLock02.lock();
            try {
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            xLock02.unlock();
        };

        for (int i = 0; i < 10; i++) {
            new Thread(task01, "server01-thread-" + i).start();
            new Thread(task02, "server02-thread-" + i).start();
        }
    }
```

方法一需要不断重试，没有利用到zookeeper的监听机制，第二种方法利用通知机制来唤醒自己，具体做法是，每个线程都创建一个带序号的临时节点，其中创建序号最小的临时节点的线程获得锁，其它线程挂起并监听它前一个节点的变化，如果前一个节点删除了，那么它的监听线程收到通知，然后唤醒它。
threadLocal用来在释放锁时删除节点，因为要threadMap在回调函数里唤醒线程，所以必须要把ThreadLocal对象放在map中，通过前一个节点删除时返回的路径拿到Thread对象

```
public class XLock {

    private ZooKeeper zkClient;
    private final ConcurrentHashMap<String, Thread> threadMap = new ConcurrentHashMap<>();
    ThreadLocal<String> threadLocal = new ThreadLocal<>();

    public XLock() {
        try {
            String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
            int sessionTimeout = 2000;
            zkClient = new ZooKeeper(connectString, sessionTimeout, watchedEvent -> {
                if (watchedEvent.getType() == Watcher.Event.EventType.NodeDeleted) {
                    String key = watchedEvent.getPath();
                    Thread thread = threadMap.remove(key);
                    LockSupport.unpark(thread);
                }
            });
            // 判断节点 /exclusive_lock 是否存在
            if (zkClient.exists("/exclusive_lock", false) == null) {
                // 不存在则创建节点
                zkClient.create("/exclusive_lock", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void lock() {
        try {
            // 创建对应的临时带序号节点
            String currentLockNode = zkClient.create("/exclusive_lock/" + "seq-", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
            // 判断创建的节点是否是最小的序号节点，如果是获取到锁；如果不是，监听他序号前一个节点
            List<String> children = zkClient.getChildren("/exclusive_lock", false);
            // 如果children 只有一个值，那就直接获取锁；如果有多个节点，需要判断谁最小
            if (children.size() > 1) {
                Collections.sort(children);
                // 获取节点名称 seq-00000000
                String thisNode = currentLockNode.substring("/exclusive_lock/".length());
                // 通过seq-00000000 获取该节点在children集合的位置
                int index = children.indexOf(thisNode);
                /**
                 * 因为在zkClient.create和zkClient.getChildren("/exclusive_lock", false);可能有其它线程也创建了节点，
                 * 所以并不是说只有 children.size() == 1 这个线程才是第一个创建节点的线程
                 */
                if (index == 0) {// 如果自己就是第一个节点，那么获得锁，
                    System.out.println(Thread.currentThread().getName() + "获得锁");
                    threadLocal.set(currentLockNode);
                    return;
                }
                // 监听它前一个节点变化
                String preNode = "/exclusive_lock/" + children.get(index - 1);
                zkClient.getData(preNode, true, null);
                /**
    * 把自己放到map中，key是前一个节点路径，因为前一个节点删除时会返回它的路径，
    * 这样就能通过前一个节点路径在map中找到自己，从而让监听线程唤醒自己
    */ 
                threadMap.put(preNode, Thread.currentThread());
                LockSupport.park();
            }
            threadLocal.set(currentLockNode);
            System.out.println(Thread.currentThread().getName() + "获得锁");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void unlock() {
        try {
            System.out.println(Thread.currentThread().getName() + "释放了锁");
            zkClient.delete(threadLocal.get(), -1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

把回调函数写在创建zookeeper客户端那里来实现唤醒，实在太麻烦，可以直接把回调函数写在getData里，这样就不要HashMap了。
```
public class XLock {

    private ZooKeeper zkClient;
    ThreadLocal<String> threadLocal = new ThreadLocal<>();

    public XLock() {
        try {
            String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
            int sessionTimeout = 2000;
            zkClient = new ZooKeeper(connectString, sessionTimeout, null);
            // 判断节点 /exclusive_lock 是否存在
            if (zkClient.exists("/exclusive_lock", false) == null) {
                // 不存在则创建节点
                zkClient.create("/exclusive_lock", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void lock() {
        try {
            // 创建对应的临时带序号节点
            String currentLockNode = zkClient.create("/exclusive_lock/" + "seq-", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
            // 判断创建的节点是否是最小的序号节点，如果是获取到锁；如果不是，监听他序号前一个节点
            List<String> children = zkClient.getChildren("/exclusive_lock", false);
            // 如果children 只有一个值，那就直接获取锁；如果有多个节点，需要判断谁最小
            if (children.size() > 1) {
                Collections.sort(children);
                // 获取节点名称 seq-00000000
                String thisNode = currentLockNode.substring("/exclusive_lock/".length());
                // 通过 seq-00000000 获取该节点在children集合的位置
                int index = children.indexOf(thisNode);
                /**
                 * 因为在zkClient.create和zkClient.getChildren("/exclusive_lock", false);可能有其它线程也创建了节点，
                 * 所以并不是说只有 children.size() == 1 这个线程才是第一个创建节点的线程
                 */
                if (index == 0) {// 如果自己就是第一个节点，那么获得锁，
                    System.out.println(Thread.currentThread().getName() + "获得锁");
                    threadLocal.set(currentLockNode);
                    return;
                }
                //
                String preNode = "/exclusive_lock/" + children.get(index - 1);
                Thread thread = Thread.currentThread();
                // 监听它前一个节点的变化，如果前一个节点删除了，会调用回调函数把自己唤醒
                zkClient.getData(preNode, watchedEvent -> LockSupport.unpark(thread), null);
                // 把自己挂起
                LockSupport.park();
            }
            threadLocal.set(currentLockNode);
            System.out.println(Thread.currentThread().getName() + "获得锁");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void unlock() {
        try {
            System.out.println(Thread.currentThread().getName() + "释放了锁");
            zkClient.delete(threadLocal.get(), -1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

从上述代码可以看出自己实现一个分布式锁还是很复杂的，下面是使用Curator 框架实现分布式锁的例子：
导入依赖：
```
<dependency>
    <groupId>org.apache.curator</groupId>
    <artifactId>curator-framework</artifactId>
    <version>4.3.0</version>
</dependency>
<dependency>
    <groupId>org.apache.curator</groupId>
    <artifactId>curator-recipes</artifactId>
    <version>4.3.0</version>
</dependency>
<dependency>
    <groupId>org.apache.curator</groupId>
    <artifactId>curator-client</artifactId>
    <version>4.3.0</version>
</dependency>
```

实例代码：
```
public class CuratorLockTest {

    public static void main(String[] args) {
        // 创建分布式锁1
        InterProcessMutex lock01 = new InterProcessMutex(getCuratorFramework(), "/locks");
        // 创建分布式锁2
        InterProcessMutex lock02 = new InterProcessMutex(getCuratorFramework(), "/locks");

        Runnable task01 = () -> {
            try {
                lock01.acquire();
                System.out.println(Thread.currentThread().getName() + "获得锁");
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread().getName() + "释放了锁");
                lock01.release();
            } catch (Exception e) {
                e.printStackTrace();
            }
        };

        Runnable task02 = () -> {
            try {
                lock02.acquire();
                System.out.println(Thread.currentThread().getName() + "获得锁");
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread().getName() + "释放了锁");
                lock02.release();
            } catch (Exception e) {
                e.printStackTrace();
            }
        };

        for (int i = 0; i < 10; i++) {
            new Thread(task01, "server01-thread-" + i).start();
            new Thread(task02, "server02-thread-" + i).start();
        }
    }
    private static CuratorFramework getCuratorFramework() {
        ExponentialBackoffRetry policy = new ExponentialBackoffRetry(3000, 3);
        CuratorFramework client = CuratorFrameworkFactory.builder().connectString("hadoop102:2181,hadoop103:2181,hadoop104:2181")
                .connectionTimeoutMs(2000)
                .sessionTimeoutMs(2000)
                .retryPolicy(policy).build();
        // 启动客户端
        client.start();
        System.out.println("zookeeper Curator客户端启动成功");
        return client;
    }
}
```

