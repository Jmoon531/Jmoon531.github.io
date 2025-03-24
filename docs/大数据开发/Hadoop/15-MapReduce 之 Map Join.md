---

Created at: 2021-08-28
Last updated at: 2021-08-28
Source URL: about:blank


---

# 15-MapReduce 之 Map Join


在Reduce Join中，合并的操作是在 Reduce 阶段完成， Reduce 端的处理压力太大， Map节点的运算负载比Reduce节点的负载要低得多，所以Reduce 阶段极易产生数据倾斜。解决方案就是在 Map 端实现数据合并，具体做法是， 在 Driver 驱动类使用 job.addCacheFile()方法设置job先将商品表pd.txt的数据缓存到内存中，然后在setUp()方法中读取pd.txt的数据，分割后放到HashMap中，最后在Map()方法中完成join的操作。这种 Map Join 的方式适用于一张表十分小、一张表很大的场景，因为每个Map节点都要在map方法开始之前缓存整张小表到内存中，大表的数据只需要读取在本Map节点上的分片即可。

Driver 驱动类中设置缓存，如果有需要将多个map的结果合并成一个文件，那么可以设置ReduceTask的个数为1并写1个reduce，这里就不写了，直接设置ReduceTask的个数为0，将map的结果作为输出。
```
public class MapJoinDriver {
    public static void main(String[] args) throws IOException, URISyntaxException, ClassNotFoundException, InterruptedException {
        // 1 获取job信息
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf);
        // 2 设置加载jar包路径
        job.setJarByClass(MapJoinDriver.class);
        // 3 关联mapper
        job.setMapperClass(MapJoinMapper.class);
        // 4 设置Map输出KV类型
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(NullWritable.class);
        // 5 设置最终输出KV类型
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(NullWritable.class);

 `String classPath = Thread.currentThread().getContextClassLoader().getResource("").getPath();`
 `// 加载缓存数据`
 `job.addCacheFile(new URI(  "file://" + classPath + "input/join/product.txt"));`
 `// Map端Join的逻辑不需要Reduce阶段，设置reduceTask数量为0`
 `job.setNumReduceTasks(0);`

        // 6 设置输入输出路径
 `FileInputFormat.setInputPaths(job, new Path(classPath + "/input/join/order.txt"));`
        FileOutputFormat.setOutputPath(job, new Path(classPath + "/output666"));
        // 7 提交
        boolean b = job.waitForCompletion(true);
        System.exit(b ? 0 : 1);
    }
}
```

先在setUp()方法中读取pd.txt的数据，分割后放到HashMap中，最后在Map()方法中完成join的操作，因为不涉及map向reduce传输数据，所以不必定义bean，直接使用Text将文本写出即可。
```
public class MapJoinMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
    private HashMap<String, String> pdMap = new HashMap<>();
    private Text outK = new Text();
    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        // 获取缓存的文件，并把文件内容封装到集合 pd.txt
        URI[] cacheFiles = context.getCacheFiles();
        FileSystem fs = FileSystem.get(context.getConfiguration());
        FSDataInputStream fis = fs.open(new Path(cacheFiles[0]));
        // 从流中读取数据
        BufferedReader reader = new BufferedReader(new InputStreamReader(fis, "UTF-8"));
        String line;
        while (StringUtils.isNotEmpty(line = reader.readLine())) {
            // 切割
            String[] fields = line.split("\t");
            // 赋值
            pdMap.put(fields[0], fields[1]);
        }
        // 关流
        IOUtils.closeStream(reader);
    }

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // 处理 order.txt
        String line = value.toString();
        String[] fields = line.split("\t");
        // 根据pid获取pname
        String pname = pdMap.get(fields[1]);
        // 封装
        outK.set(fields[0] + "\t" + pname + "\t" + fields[2]);
        context.write(outK, NullWritable.get());
    }
}
```

