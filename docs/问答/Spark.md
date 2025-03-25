### 相比较于MapReduce，Spark为什么这么快？

1. **shuffle：** 使用MapReduce框架和Spark框架编写map-reduce程序，在理论上shuffle次数应该是一样多的，因为都是基于map-reduce思想的，但是由于使用MapReduce框架不够灵活，所以如果不经过良好的设计很容易造成使用MapReduce框架比使用Spark框架shuffle次数多。这是一个原因，但不是主要的原因，因为shuffle次数一样多。主要原因还是MapReduce框架的shuffle必须花费不少的时间进行排序操作，但是有时候排序操作并不是必须，Spark框架的shuffle就是这样的，更加灵活。

2. **DAG计算模型：** Spark框架比MapReduce框架快的根本原因在于DAG计算模型。编写复杂的map-reduce程序，在Spark框架中用户只需要编写一个DAG就可以完成了，而使用MapReduce框架的时候，用户可能需要写好几个map-reduce，（因为map-reduce必须成对出现，当然也可以不写reduce），然后多个map-reduce程序以进程的方式执行，前一个进程reduce的输出作为后一个进程的map输入，我们知道一个MapReduce程序最后reduce的输出是一定会落盘的，所以会造成reduce到map中间结果的IO，而在Spark的DAG中，reduce之后的map不必shuffle，减少了中间结果的落盘。

3. **进程与线程：** MapReduce框架基于进程，前一个MapReduce进程结束之后再启动下一个进程；而Spark是基于线程的，task运行在线程上，不同stage的task可以复用线程；进程的创建和销毁比线程的创建和销毁开销大。

### job、stage和task的关系？分区和task的关系？task和线程的关系？

有1个Driver和多个Executor，Driver负责把用户程序转化为作业（job），根据宽依赖将job划分为多个阶段stage，每个阶段根据分区数将生产相应的task，Driver将task分配给Executor执行，前一个阶段所有task执行完了之后才会执行下一个阶段的task。

注意：同一个阶段内的task数并不等于Executor**s**启动的线程数，如果线程数多于task数，那么可以做到一个task使用一个线程执行，如果task数多于线程数，那么同一个阶段的task就会复用同一个线程执行。值得注意的是，不同阶段的task肯定会复用线程。

分区数如何确定？创建RDD时可以指定分区数，如果没有指定默认等于并行度（local模式下）；此外，shuffle会调整数据的位置，所以一般有shuffle的转换算子都可以重新指定分区数。

### Spark运行模式有哪些？工作流程是怎么样的？

Spark的运行模式包括`Local`、`Standalone`、`Yarn`、`Mesos`、`k8s`几种。其中Local模式仅用于本地开发；Standalone模式使用的是Spark自带的资源调度器；YARN是一款更加成熟的资源调度器，Spark On Yarn模式用的更多。

资源调度器都是Master-slaves架构，只是在不同的资源调度器里的叫法不同。Standalone模式是Master和Worker；YARN是ResourceManager和NodeManager。

Spark作业分阶段执行也需要调度，同样也是Master-slaves架构，具体名称是Driver和Executor。这属于Spark计算引擎内部的工作，和资源调度器的工作不同，资源调度器的工作是物理机资源的分配，Spark作业分配得到物理机资源之后就可以启动Driver和Executor了，之后由Driver和Executor配合完成作业。

以YARN模式为例，稍微具体的流程是：

1. 客户端向ResourceManager提交任务，将任务加入到队列中。
2. NodeManager领取任务，启动Driver完成一系列初始化，比如初始化SparkContext，生成DAG、划分Stage等。
3. Driver将第一个阶段的task加入到队列中，也就是向ResourceManager申请资源执行task。
4. NodeManager 领取到任务之后启动Executor，Executor向Driver反向注册，之后Executor启动线程执行task。
5. 然后Driver调度下一个阶段的taskset执行。

### Spark三大数据结构？

RDD（弹性分布式数据集）、累加器（分布式共享只写变量）、广播变量（分布式共享只读变量）

**RDD( Resilient Distributed Dataset，弹性分布式数据集)**，Resilient弹性是指RDD具有容错的特性；Distributed分布式是指数据存在不同的机器上；Dataset数据集是指数据的元数据信息，RDD并不真正存储数据。总的来说RDD存了一下信息：

1. **分区：** 记录数据分区的信息，每个分区的数据交给一个task处理。

2. **task：** RDD有很多操作算子，使用这些操作算子可以对数据进行计算，从而让一个RDD转换成另外一个RDD，这时RDD之间就具有了依赖关系。

3. **血缘关系：** 记录了与其依赖的RDD的血缘关系，可以通过这个血缘关系重新计算丢失的分区数据，体现了RDD容错的特点。

**累加器：** 累加器是分布式共享只写变量，Saprk自带了3个简单的累加器：longAccumulator、doubleAccumulator、collectionAccumulator。累加器的计算过程是，Driver把累加器发送到每个task，task计算完毕后把累加器返回到Driver端聚合。

**广播变量：** 处于同一Executor的task可以共享同一个变量（所有线程共享堆内存上的一份副本）。

### Spark算子？

**转换算子**：

- 相当于map操作：filter、map、mapPartitions、mapPartitionsWithIndex、flatMap
- 有shuffle的操作：groupBy、sortBy、repartition、partitionBy、reduceByKey、groupByKey、aggregateByKey

**行动算子**：reduce、collect、count、aggregate、fold、save相关、foreach

**map、mapPartitions、mapPartitionsWithIndex：**

- map是对分区内的数据一条一条的做映射处理，处理完就可以释放掉这条数据的内存空间了

- 而mapPartitions是将同一个分区内的所有数据作为一个集合进行处理，需要等待该分区内所有数据都加载到内存之后才能开始计算，搞不好就容易OOM

- mapPartitionsWithIndex和mapPartitions一样是将同一个分区内的所有数据作为一个集合进行映射处理，但是mapPartitionsWithIndex会给每个分区一个编号

**repartition、partitionBy：**

- repartition可以对**非k-v类型的RDD**合并或者增加分区

- partitionBy可以对**k-v类型的RDD**按key重新分区，默认的分区器是 HashPartitioner

**groupBy 与 groupByKey：**

- groupBy对**非k-v类型的RDD**进行分组，必须指定分组的规则

- groupByKey对k-v类型RDD进行分组，默认就是按key分组

**reduce 与 reduceByKey** 同上，如果能用 reduceByKey 代替 groupByKey+ mapValues，就尽量用reduceByKey，因为reduceByKey会在map端预聚合。

**reduceByKey 与 aggregateByKey：** reduceBykey在对分区间数据进行聚合之前会先对分区内的数据进行一次预聚合，两次聚合操作的计算逻辑是完全相同的。aggregateByKey也有分区内和分区间的两次聚合操作，但两次聚合的计算逻辑可以分别指定。

### RDD的闭包？

RDD算子内的匿名函数不仅会闭包变量，还要求被闭包的变量能被序列化，因为算子以外的代码都是在 Driver 端执行，但算子里面的代码都是在 Executor端执行的，所以如果使用的算子外的数据无法序列化，就意味着无法传值给 Executor端执行，于是就会发生错误，Spark需要在执行任务计算前，检测闭包内的对象是否可以进行序列化，这个操作我们称之为闭包检测。

### 闭包变量 与 广播变量 的区别？

闭包的变量会被完整地发送到每个task中，所以当有多个task在同一Executor上执行时，该Executor进程就会有同一个闭包变量的多个副本。使用广播变量，可以让Executor只保存变量的一个副本，让处于这个Executor上的task共享这一个变量，但是要注意广播变量是只读变量，不可以修改。

### RDD的宽依赖和窄依赖？

- 宽依赖: 父RDD每个分区被多个子RDD分区使用

- 窄依赖: 父RDD每个分区被子RDD的一个分区使用

宽依赖会产生shuffle，shuffle会落盘，窄依赖不会。

### Spark容错机制？

Spark的容错依赖 **RDD的血缘关系** 和 **持久化**。当task计算失败之后，可以通过RDD的血缘关系找到最近一次shuffle或者使用持久化的位置重新开始，这样可以最大程度上减少冗余计算开销。持久化有三种方式：shuffle落盘、cache 和 checkpoint。

#### shuffle会落盘，为什么还要做持久化？

lineage过长会造成容错成本过高，这时在中间阶段做检查点容错，从做检查点的RDD开始重做Lineage，可以减少容错成本。

### 持久化？

spark主动持久化有两种方式：cache 和 checkpoint。

cache默认将数据缓存在内存中，也可以指定缓存在磁盘上，但是无论哪一种，在计算结束时都是会删除的。cache有两个作用，一是当Application有多个job，也就是有多个行动算子时，代码中复用的转换算子的计算结果也可以复用，如果没有用cache是不能复用的，每个行动算子都会从头开始算起。第二个作用是可以用于容错，做故障恢复用，也就是当算子计算任务失败后，可以通过血缘关系找到cache缓存的数据，不必从头开始重新计算，不过当cache缓存在内存中数据丢失了的话，还是会通过血缘关系从头开始计算（中间有shuffle就是从shuffle落盘的地方开始算）。

checkpoint会改变job的血缘关系，因为checkpoint是将数据保存在磁盘上，并且在程序结束的时候也不会删除，所以即使改变了血缘也不用担心后面的计算不能恢复。当有多个行动算子时，checkpoint不能复用中间结果，因为它只对一个job起作用。

#### cache和persist的异同？

cache()方法其实调用的是persist()方法，persist()方法默认将数据缓存在内存中，还可以使用persist(StorageLevel.DISK_ONLY)将数据缓存在磁盘中，程序结束时删除。

### Spark SQL的两种交互接口

Spark SQL的两种交互接口：SQL、DataSet API。DataSet有泛型，是强类型的，如果类型是Row，那么`DataSet<Row>`也称为DataFrame。

### Spark  on Hive和Hive on Spark的区别?
