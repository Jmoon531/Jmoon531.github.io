---

Created at: 2021-08-12
Last updated at: 2024-08-16
Source URL: https://www.cnblogs.com/waterystone/p/4920797.html


---

# 22-AQS


AQS 全称是 AbstractQueuedSynchronizer，是阻塞式锁和相关的同步器工具的框架 ，许多同步类实现都依赖于它，比如JUC中的ReentrantLock、 Semaphore、 CountDownLatch等工具类都是基于AQS（AbstractQueuedSynchronizer）实现的，AQS又是基于Unsafe类提供的CAS操作、volatile关键字和Unsafe类提供的park()与unpark()方法实现的（AQS并没有直接使用Unsafe类的park()与unpark()方法，而是使用的是LockSupport的静态方法par()和unpark()方法，而LockSupport的park()和unpark()方法是使用Unsafe类的park()与unpark()方法实现的）。

这里要说明一点，原子类是基于Unsafe类提供的CAS操作再加上无锁（也就是一直循环重试）的方式实现的，而AQS是基于Unsafe类提供的CAS操作和park()与unpark()实现的。在前一种实现线程安全的方式中，线程是没有阻塞的；而在AQS中线程是有阻塞的，阻塞和等待唤醒的操作都有，这和synchronized一样，都是有阻塞的，只不过park()是基于parker实现的，而synchronized是基于monitor实现的。
parker和monitor都是由jvm底层实现的，用C++写的，区别就在于，monitor是锁，而parker并不是一种锁。monitor是锁的一种完整实现，包括了加锁成功和失败的逻辑、阻塞和唤醒的逻辑；而parker则没有，parker只是提供了阻塞和唤醒线程最基本的操作，与锁是两码事，锁的逻辑交由上层的AQS实现。不过只要是阻塞或唤醒一个线程都需要操作系统来帮忙，阻塞和唤醒线程的操作都需要在内核态中完成，所以都不可避免的涉及用户态与内核态的转换，这种状态转换需要很大的开销。

AQS在JUC包中扮演的角色与管程很类似，它提供的基于 FIFO 的等待队列，类似于 Monitor 的 EntryList；还提供了条件变量来实现等待、唤醒机制，并且支持多个条件变量，类似于 Monitor 的 WaitSet，不过Monitor只支持一个WaitSet；AQS从父类中继承而来的exclusiveOwnerThread字段以及对应的set和get方法类似于Monitor的Owner。但AQS比Monitor更强大，比如的ReentrantLock有很多synchronized不具备的特点，Semaphore、 CountDownLatch等工具类也基于AQS实现了很多强大方便的功能。

为什么AQS比Monitor更强大呢？因为synchronized的加解锁逻辑全部是由monitor来实现的（所以说是管程嘛），monitor又是jvm的底层实现；而AQS则是由Java来实现的，只有阻塞和唤醒操作是JVM的底层实现（当然还有CAS），相比于monitor的阻塞和唤醒，parker的阻塞唤醒更为灵活，AQS只实现了锁的框架，以方便具体锁实现的扩展，也比monitor灵活。

总结到一点就是：synchronized的实现全部交由jvm底层来完成，而AQS只使用了jvm底层提供的CAS和park两个操作，其它实现锁的数据结构和算法全部通过Java代码来实现。

ReentrantLock相比于synchronized可以：

1. 可中断
2. 可以设置超时时间
3. 可以设置为公平锁
4. 支持多个条件变量

ReentrantLock和synchronized的共同点是可重入。 可重入是指一个线程如果获得了锁，那么在它释放锁之前，可以重复加锁而不会阻塞，如果是不可重入锁，那么同一个线程在释放锁之前的再次加锁操作也会导致自己被阻塞挂起。

AQS实现不可重入锁，这是JDK中AQS的注释提供的一个例子：
```
class Mutex implements Lock, java.io.Serializable {

    private final Sync sync = new Sync();

    public void lock() {
        sync.acquire(1);
    }

    public boolean tryLock() {
        return sync.tryAcquire(1);
    }

    public void unlock() {
        sync.release(1);
    }

    public Condition newCondition() {
        return sync.newCondition();
    }

    public boolean isLocked() {
        return sync.isLocked();
    }

    public boolean isHeldByCurrentThread() {
        return sync.isHeldExclusively();
    }

    public boolean hasQueuedThreads() {
        return sync.hasQueuedThreads();
    }

    public void lockInterruptibly() throws InterruptedException {
        sync.acquireInterruptibly(1);
    }

    public boolean tryLock(long timeout, TimeUnit unit)
            throws InterruptedException {
        return sync.tryAcquireNanos(1, unit.toNanos(timeout));
    }

    // Our internal helper class
    private static `class Sync extends AbstractQueuedSynchronizer` {
        // Acquires the lock if state is zero
        public boolean tryAcquire(int acquires) {
            assert acquires == 1; // Otherwise unused
            if (compareAndSetState(0, 1)) {
                setExclusiveOwnerThread(Thread.currentThread());
                return true;
            }
            return false;
        }

        // Releases the lock by setting state to zero
        protected boolean tryRelease(int releases) {
            assert releases == 1; // Otherwise unused
            if (!isHeldExclusively())
                throw new IllegalMonitorStateException();
            setExclusiveOwnerThread(null);
            setState(0);
            return true;
        }

        // Reports whether in locked state
        public boolean isLocked() {
            return getState() != 0;
        }

        public boolean isHeldExclusively() {
            // a data race, but safe due to out-of-thin-air guarantees
            return getExclusiveOwnerThread() == Thread.currentThread();
        }

        // Provides a Condition
        public Condition newCondition() {
            return new ConditionObject();
        }

        // Deserializes properly
        private void readObject(ObjectInputStream s)
                throws IOException, ClassNotFoundException {
            s.defaultReadObject();
            setState(0); // reset to unlocked state
        }
    }
}

public class Test {
    public static void main(String[] args) {
        Mutex mutex = new Mutex();
        mutex.lock();
        System.out.println("上第一把锁");
        mutex.lock();
        System.out.println("因为是不可重入锁，所以上第二把锁的时候被阻塞了，这里不会打印出来");
        mutex.unlock();
        mutex.unlock();
        System.out.println("解锁");
    }
}
```
从以上实现可以看出AQS已经实现了通用的基础结构和功能，在它的基础之上我们就可以构建自己的加锁逻辑。

