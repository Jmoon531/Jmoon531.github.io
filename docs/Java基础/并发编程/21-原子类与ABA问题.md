---

Created at: 2021-08-12
Last updated at: 2021-08-13


---

# 21-原子类与ABA问题


JUC基于Unsafe类的CAS操作提供了许多原子类，实现了许多常用的线程安全的操作。

原子整数：
AtomicBoolean
AtomicInteger
AtomicLong

原子引用：
AtomicReference
AtomicMarkableReference
AtomicStampedReference

原子数组：
AtomicIntegerArray
AtomicLongArray
AtomicReferenceArray

对普通的成员变量：
AtomicReferenceFieldUpdater
AtomicIntegerFieldUpdater
AtomicLongFieldUpdater

原子累加器
LongAdder

在使用AtomicBoolean、AtomicInteger、AtomicLong、AtomicReference等原子类时，可以实现线程安全的加减乘除等修改操作，但这些操作有一个问题：T1线程读到变量的值是A，然后这时T2线程将A该为B，接着T3线程将B改为A，T1线程此时去更新变量的值也会成功，因为最后的值还是A，但是T1线程并不知道的是变量的值在它读取直到更新期间已经发生了多次修改，这就是所谓的ABA问题。

有些时候这个问题可能并不构成问题，但有些时候这就是个问题，那么当它是问题的时候如何解决呢？
答案是使用AtomicStampedReference带戳的原子引用类，它的compareAndSet方法如下：
```
public boolean compareAndSet(V   expectedReference,
                             V   newReference,
                             int expectedStamp,
                             int newStamp)
```
expectedReference是期望值，newReference是新值，expectedStamp是期望的戳，newStamp是新戳。

约定每一次更新成功都设置一个新的戳，这个戳就是版本号，在expectedStamp的基础上加1，更新时expectedReference和expectedStamp有一个不符合预期就更新失败。

