---

Created at: 2021-08-26
Last updated at: 2021-12-07
Source URL: about:blank


---

# 9-Shuffle之排序


排序是MapReduce框架最重要的操作之一，MapTask 和 ReduceTask 的 Shuffle阶段都会对k-v键值对按k的大小进行排序，所以作为key的对象除了必须实现Hadoop的序列化之外，还必须要求能比较大小，而作为value的对象只要求实现序列化。可以看出序列化是key和value都必须实现，而比较大小只是key必须实现，所以自定义对象时，作为key的类必须实现WritableCompare接口，作为value的类可以只实现Writable接口。

案例：在前面讲序列化时统计了每一个手机号耗费的总上行流量、 总下行流量、总流量，本案例的要求是按每个手机号的总流量从大到小排序输出。
分析：1.本案例只能基于上一个案例的结果作为输入，并不能一步到位，只用一个MapReduce过程解决 
          2.需要按总流量的大小排序，所以应该把包含总流量的bean对象作为key

自定义的bean对象的类需要实现WritableComparable接口，重写compareTo方法
```
public class FlowBean implements WritableComparable<FlowBean> {
    private long upFlow; // 上行流量
    private long downFlow; // 下行流量
    private long sumFlow; // 总流量

    // 空参构造
    public FlowBean() {
    }

    public long getUpFlow() {
        return upFlow;
    }

    public void setUpFlow(long upFlow) {
        this.upFlow = upFlow;
    }

    public long getDownFlow() {
        return downFlow;
    }

    public void setDownFlow(long downFlow) {
        this.downFlow = downFlow;
    }

    public long getSumFlow() {
        return sumFlow;
    }

    public void setSumFlow(long sumFlow) {
        this.sumFlow = sumFlow;
    }

    public void setSumFlow() {
        this.sumFlow = this.upFlow + this.downFlow;
    }

    @Override
    public void write(DataOutput out) throws IOException {
        out.writeLong(upFlow);
        out.writeLong(downFlow);
        out.writeLong(sumFlow);
    }

    @Override
    public void readFields(DataInput in) throws IOException {
        this.upFlow = in.readLong();
        this.downFlow = in.readLong();
        this.sumFlow = in.readLong();
    }

    @Override
    public String toString() {
        return upFlow + "\t" + downFlow + "\t" + sumFlow;
    }

 `@Override`
 `public int compareTo(FlowBean o) {`
 `// 总流量的倒序排序`
 `if (this.sumFlow > o.sumFlow) {`
 `return -1;`
 `} else if (this.sumFlow < o.sumFlow) {`
 `return 1;`
 `} else {`
 `return 0;`
 `}`
 `}`
}
```

Map的输出需要将bean对象作为key，将手机号作为value，与统计上个案例中统计每个手机号总流量时正好相反
```
public class FlowMapper extends Mapper<LongWritable, Text, FlowBean, Text> {

    private FlowBean outK = new FlowBean();
    private Text outV = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // 获取一行
        String line = value.toString();
        // 切割
        String[] split = line.split("\t");
        // 封装
        outV.set(split[0]);
        outK.setUpFlow(Long.parseLong(split[1]));
        outK.setDownFlow(Long.parseLong(split[2]));
        outK.setSumFlow();
        // 写出
        context.write(outK, outV);
    }
}
```

Reduce的输入已经是Shuffle阶段排好序的结果，仍要以手机号、总上行流量、 总下行流量、总流量的格式输出的话，那么Reduce的任务就是将输入k-v互换位置。
```
public class FlowReducer extends Reducer<FlowBean, Text, Text, FlowBean> {

    @Override
    protected void reduce(FlowBean key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        for (Text value : values) {
            context.write(value, key);
        }
    }
}
```
这里需要注意一点的是，在前面讲WordCount时，我们说map的输出结果是 (a,1)、(b,1)、(a,1)，经过Shuffle排序之后，Reduce的输入变成了 (a, (1,1))、(b,1) 是不对的，其实是这样的(a,1)、(a,1)、(b,1)，具有相同key的k-v键值对会作为一组进入reduce()方法，这里所说的相同的key，并不是说key完全一模一样，而是说在compareTo的比较规则下一样，之后在for循环里处理时，看似只是改变了value，其实key也跟在在一起变，这就是为什么只需要在for循环里将value和key互换位置即可输出正确的结果。

那为什么key也会跟着一起变呢？追溯源码就知道为什么了。

首先Reducer的模板方法run里的 while (context.nextKey()) ，context是抽象内部类Context的引用，Context有个子类是WrappedReducer的内部类Context，所以context.nextKey()最终调用的是WrappedReducer的内部类Context的方法，而WrappedReducer::Context的方法都是委托给了ReduceContext的方法，ReduceContext只是一个接口，它的实现类是ReduceContextImpl，所以最终都是调用的ReduceContextImpl的方法。key和value是ReduceContextImpl的成员变量，当调用其nextKey()方法时，如果还有下一个，就会调用nextKeyValue()方法并返回true，在nextKeyValue()方法的142行key = keyDeserializer.deserialize(key);和146行value = valueDeserializer.deserialize(value);是反序列k-v到内存中并赋给ReduceContextImpl的成员变量key和value，至此context.nextKey()就执行完了。然后调用reduce(context.getCurrentKey(), context.getValues(), context);拿到ReduceContextImpl的成员变量key和value进入自定义的reduce()方法。

reduce()方法中的增强for循环编译的结果其实是使用迭代器完成遍历，values的返回的迭代器是 ReduceContextImpl的内部类ValueIterator，遍历的过程就是调用ValueIterator的hasNext()方法判断有没有下一个，调用next()方法拿到下一个，在next()方法的239行调用了nextKeyValue()方法，也就是说ReduceContextImpl的成员变量key和value所引用的对象被反序列化赋予了新的值，虽然在reduce()方法的for循环里没有调用重新调用context.getCurrentKey(), context.getValues()拿到成员变量key和value，但我想是反序列化方法其实并没有在内存中创建新的对象，而只是修改了原来的对象的值，所以虽然key和value的引用值没有改变，但是引用的对象中的内容却发生了改变，这就是`使用迭代器遍历的优势和特点——取下一个值的逻辑都封装在了next()方法中`。

总结一句话，在reduce()方法中key和value的值自始至终都没有改变，改变的是它们所引用的对象。

最后的Driver类只需要把输入路径改成上一个案例输出的文件，把输出路径改成新文件夹即可。
```
public class FlowDriver {

    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        // 1 获取job
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf);

        // 2 设置jar
        job.setJarByClass(FlowDriver.class);

        // 3 关联mapper 和Reducer
        job.setMapperClass(FlowMapper.class);
        job.setReducerClass(FlowReducer.class);

        // 4 设置mapper 输出的key和value类型
        job.setMapOutputKeyClass(FlowBean.class);
        job.setMapOutputValueClass(Text.class);

        // 5 设置最终数据输出的key和value类型
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(FlowBean.class);

        String classPath = Thread.currentThread().getContextClassLoader().getResource("").getPath();

 `// 6 设置数据的输入路径和输出路径`
 `FileInputFormat.setInputPaths(job, new Path(classPath + "/output/part-r-00000"));`
 `FileOutputFormat.setOutputPath(job, new Path(classPath + "/output2"));`

        // 7 提交job
        boolean result = job.waitForCompletion(true);
        System.exit(result ? 0 : 1);
    }
}
```

`分区排序综合案例`：按手机号的归属地输出到不同的文件中，每个文件中的记录按每个手机号的总流量从大到小排序，如果总流量相同则按下行流量排序，如果下行流量相同则按上行流量排序。
自定义的bean对象的类需要实现WritableComparable接口，重写write()方法、readFields()方法、compareTo方法
```
public class FlowBean implements WritableComparable<FlowBean> {
    private long upFlow; // 上行流量
    private long downFlow; // 下行流量
    private long sumFlow; // 总流量

    // 空参构造
    public FlowBean() {
    }

    public long getUpFlow() {
        return upFlow;
    }

    public void setUpFlow(long upFlow) {
        this.upFlow = upFlow;
    }

    public long getDownFlow() {
        return downFlow;
    }

    public void setDownFlow(long downFlow) {
        this.downFlow = downFlow;
    }

    public long getSumFlow() {
        return sumFlow;
    }

    public void setSumFlow(long sumFlow) {
        this.sumFlow = sumFlow;
    }

    public void setSumFlow() {
        this.sumFlow = this.upFlow + this.downFlow;
    }

    @Override
    public void write(DataOutput out) throws IOException {
        out.writeLong(upFlow);
        out.writeLong(downFlow);
        out.writeLong(sumFlow);
    }

    @Override
    public void readFields(DataInput in) throws IOException {
        this.upFlow = in.readLong();
        this.downFlow = in.readLong();
        this.sumFlow = in.readLong();
    }

    @Override
    public String toString() {
        return upFlow + "\t" + downFlow + "\t" + sumFlow;
    }

 `@Override`
 `public int compareTo(FlowBean o) {`
 `// 总流量从大到小排序`
 `int result =  Long.compare(this.sumFlow, o.sumFlow);`
 `if (result == 0) {`
 `// 下行流量从大到小排序`
 `result = Long.compare(this.downFlow, o.downFlow);`
 `if (result == 0) {`
 `// 上行流量从大到小排序`
 `result = Long.compare(this.upFlow, o.upFlow);`
 `}`
 `}`
 `return -result;`
 `}`
}
```

该案例还是需要基于统计每一个手机号耗费的总上行流量、 总下行流量、总流量的案例的结果
map的输出需要将bean对象作为key，将手机号作为value
```
public class FlowMapper extends Mapper<LongWritable, Text, `FlowBean, Text`> {
    private FlowBean outK = new FlowBean();
    private Text outV = new Text();
    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // 获取一行
        String line = value.toString();
        // 切割
        String[] split = line.split("\t");
        // 封装
        outV.set(split[0]);
        outK.setUpFlow(Long.parseLong(split[1]));
        outK.setDownFlow(Long.parseLong(split[2]));
        outK.setSumFlow();
        // 写出
        context.write(outK, outV);
    }
}
```

分区方法以map输出的value作为分区的依据，这也是与前面以key作为分区依据的不同
```
public class ProvincePartitioner extends Partitioner<`FlowBean, Text`> {
    @Override
    public int getPartition(`FlowBean flowBean, Text text`, int numPartitions) {
        // text 是手机号
        String phone = text.toString();
        String prePhone = phone.substring(0, 3);
        switch (prePhone) {
            case "136":
                return 0;
            case "137":
                return 1;
            case "138":
                return 2;
            case "139":
                return 3;
            default:
                return 4;
        }
    }
}
```

Reduce的任务是将Map输出的k-v的位置进行互换，以满足输出格式的要求
```
public class FlowReducer extends Reducer<FlowBean, Text, Text, FlowBean> {
    @Override
    protected void reduce(FlowBean key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        for (Text value : values) {
            context.write(value,key);
        }
    }
}
```

Driver类需要设置分区方法所在的类 job.setPartitionerClass(ProvincePartitioner.class); 和 ReduceTask的数量 job.setNumReduceTasks(5); 注意ReduceTask的数量必须要与分区数一致。
```
public class FlowDriver {
    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        // 1 获取job
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf);

        // 2 设置jar
        job.setJarByClass(FlowDriver.class);

        // 3 关联mapper 和Reducer
        job.setMapperClass(FlowMapper.class);
        job.setReducerClass(FlowReducer.class);

        // 4 设置mapper 输出的key和value类型
        job.setMapOutputKeyClass(FlowBean.class);
        job.setMapOutputValueClass(Text.class);

        // 5 设置最终数据输出的key和value类型
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(FlowBean.class);

 `//设置分区方法所在的类`
 `job.setPartitionerClass(ProvincePartitioner.class);`
 `//设置ReduceTask的数量`
 `job.setNumReduceTasks(5);`

        String classPath = Thread.currentThread().getContextClassLoader().getResource("").getPath();

        // 6 设置数据的输入路径和输出路径
        FileInputFormat.setInputPaths(job, new Path(classPath + "/output/part-r-00000"));
        FileOutputFormat.setOutputPath(job, new Path(classPath + "/output3"));

        // 7 提交job
        boolean result = job.waitForCompletion(true);
        System.exit(result ? 0 : 1);
    }
}
```

