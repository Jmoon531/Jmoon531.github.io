---

Created at: 2021-08-10
Last updated at: 2022-08-02
Source URL: about:blank


---

# 09-BolckingQueue


BolckingQueue，阻塞队列
先进先出的队列，有如下4组方法，方法都有加重入锁，所以能保证多线程下插入移除的安全性

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
|     | Throws exception | Special value | Blocks | Times out |
| Insert | add(e) | offer(e) | put(e) | offer(e, time, unit) |
| Remove | remove() | poll() | take() | poll(time, unit) |
| Examine | element() | peek() | not applicable | not applicable |

抛出异常组的三个方法的意思是，add(e)往一个满队列里插入元素，remove()往一个空队列里移除元素，element()查看空队列头的元素，都会抛异常。
特殊值组的三个方法的意思是，offer(e)往一个满队列里插入元素会返回false，或者poll()往一个空队列里移除元素会返回null，peek()查看空队列头的元素会返回null。
阻塞组的三个方法的意思是，往一个满队列里插入元素会阻塞，直到队列有空间，或往一个空队列里移除元素也会阻塞，直到队列里面有元素（其实内部实现就是条件变量Condition的await和signal）。
超时组的三个方法的意思是，往一个满队列里插入元素，或往一个空队列里移除元素都会阻塞，但有阻塞是时间的，超过时间就不等了。

BolckingQueue只是一个接口，要用的话就主要用它的三个实现类：
① ArrayBlockingQueue 数组构成的有界阻塞队列
② LinkedBlockingQueue 链表构成的有界（但最大值为Integer.MAX\_VALUE）阻塞队列
③ SynchronousQueue 不存储元素的阻塞队列
其他实现类：

1. PriorityBlockingQueue ：支持优先级排序的无界阻塞队列
2. DelayQueue：使用优先级队列实现的无界阻塞队列
3. LinkedTransferQueue：由链表结构组成的无界阻塞队列
4. LinkedBlockingDeque：由链表结构组成的双向阻塞队列

