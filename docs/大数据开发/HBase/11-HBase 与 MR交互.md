---

Created at: 2021-09-14
Last updated at: 2021-09-22
Source URL: about:blank


---

# 11-HBase 与 MR交互


**需求一：将HDFS上的文件的数据导入到HBase的表中**
1.新建 fruit.tsv 文件，并上传到HDFS
```
1001    Apple    Red
1002    Pear    Yellow
1003    Pineapple    Yellow
```
```
hdfs dfs -mkdir /input_fruit
hdfs dfs -put fruit.tsv /input_fruit/
```
2.新建HBase表
```
create 'fruit','info'
```
3.pom文件，带第三方jar包打包
```
<dependencies>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase-client</artifactId>
        <version>1.4.13</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase-server</artifactId>
        <version>1.4.13</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-client</artifactId>
        <version>3.3.1</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.6.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-assembly-plugin</artifactId>
            <version>3.3.0</version>
            <configuration>
                <archive>
                    <manifest>
                        <addClasspath>true</addClasspath>
                        <!--指定主类-->
                        <mainClass>MapReduce.FruitDriver</mainClass>
                    </manifest>
                </archive>
                <descriptorRefs>
                    <descriptorRef>jar-with-dependencies</descriptorRef>
                </descriptorRefs>
            </configuration>
            <executions>
                <execution>
                    <id>make-assembly</id>
                    <phase>package</phase>
                    <goals>
                        <goal>single</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

4.mapper类直接输出这一行即可
```
public class FruitMapper extends Mapper<LongWritable, Text, LongWritable, Text> {
    @Override
    protected void map(LongWritable key, Text value, Mapper<LongWritable, Text, LongWritable, Text>.Context context) throws IOException, InterruptedException {
        context.write(key, value);
    }
}
```

5.reducer类继承TableReducer，TableReducer继承自 Reducer，TableReducer类的输出value是Mutation，Put类是Mutation的子类，所以如果要往HBase表中插入数据，直接输出Put对象即可。
```
public class FruitReducer extends TableReducer<LongWritable, Text, NullWritable> {
    @Override
    protected void reduce(LongWritable key, Iterable<Text> values, Reducer<LongWritable, Text, NullWritable, Mutation>.Context context) throws IOException, InterruptedException {
        for (Text value : values) {
            String[] splits = value.toString().split("\t");
            Put put = new Put(Bytes.toBytes(splits[0]));
            put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"), Bytes.toBytes(splits[1]));
            put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("color"), Bytes.toBytes(splits[2]));
            context.write(NullWritable.get(), put);
        }
    }
}
```

6.Driver类，实现Tool接口
```
public class FruitDriver implements Tool {
    private Configuration configuration = null;

    @Override
    public int run(String[] args) throws Exception {
        //1.创建 Job 任务
        Job job = Job.getInstance(configuration);
        //2.设置jar包路径
        job.setJarByClass(FruitDriver.class);
        //3.设置 Mapper
        job.setMapperClass(FruitMapper.class);
        job.setMapOutputKeyClass(LongWritable.class);
        job.setMapOutputValueClass(Text.class);
        //4.设置 Reducer，第二个参数是输出路径，即HBase上的表名
        TableMapReduceUtil.initTableReducerJob(args[1], FruitReducer.class, job);
        //5.设置输入路径，第一个参数，即HDFS上文件的路径
        FileInputFormat.setInputPaths(job, new Path(args[0]));
        //6.提交任务
        return job.waitForCompletion(true) ? 0 : 1;
    }

    @Override
    public void setConf(Configuration configuration) {
        this.configuration = configuration;
    }

    @Override
    public Configuration getConf() {
        return configuration;
    }

    public static void main(String[] args) {
        try {
            Configuration configuration = new Configuration();
            ToolRunner.run(configuration, new FruitDriver(), args);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

7.打包之后上传到Linux，然后使用yarn来运行，第一个参数是输入路径，即HDFS上文件的路径，第二个参数是输出路径，即HBase上的表名
```
yarn jar HBase-1.0-SNAPSHOT-jar-with-dependencies.jar /input_fruit/fruit.tsv fruit
```
以上代码中并没有连接hbase部分，但是也能操作hbase，我也不知道为什么，可能环境变量的缘故，因为这是在把Linux上运行，如果直接在Windows上运行就需要连接hbase了。

**需求二：将上面的fruit表的数据导入到HBase的另一张表fruit2上，要求是只保留name列的数据**
1.创建fruit2表
```
create 'fruit2','info'
```
2.Mapper，ImmutableBytesWritable就是RowKey
```
public class Fruit2Mapper extends TableMapper<ImmutableBytesWritable, Put> {
    @Override
    protected void map(ImmutableBytesWritable key, Result value, Mapper<ImmutableBytesWritable, Result, ImmutableBytesWritable, Put>.Context context) throws IOException, InterruptedException {
        //遍历一行的每一列
        for (Cell cell : value.rawCells()) {
            //如果这一列是name列
            if ("name".equals(Bytes.toString(CellUtil.cloneQualifier(cell)))) {
                Put put = new Put(key.get());
                put.add(cell);
                context.write(key, put);
            }
        }
    }
}
```
3.Reducer
```
public class Fruit2Reducer extends TableReducer<ImmutableBytesWritable, Put, NullWritable> {
    @Override
    protected void reduce(ImmutableBytesWritable key, Iterable<Put> values, Reducer<ImmutableBytesWritable, Put, NullWritable, Mutation>.Context context) throws IOException, InterruptedException {
        for (Put put : values) {
            context.write(NullWritable.get(), put);
        }
    }
}
```
4.Driver
```
public class Fruit2Driver implements Tool {
    private Configuration configuration = null;

    @Override
    public int run(String[] args) throws Exception {
        //1.创建 Job 任务
        Job job = Job.getInstance(configuration);
        //2.设置jar包路径
        job.setJarByClass(Fruit2Driver.class);
        //3.设置 Mapper,第一个参数是输入路径，即HBase上的表名，第二参数设置扫描表的范围
        //第三个参数是设置map类，第四、五个参数是map的输出key和value的类型
        TableMapReduceUtil.initTableMapperJob("fruit",
                new Scan(),
                Fruit2Mapper.class,
                ImmutableBytesWritable.class,
                Put.class,
                job);
        //4.设置 Reducer，第一个参数是输出路径，即HBase上的表名
        TableMapReduceUtil.initTableReducerJob("fruit2", Fruit2Reducer.class, job);
        //6.提交任务
        return job.waitForCompletion(true) ? 0 : 1;
    }

    @Override
    public void setConf(Configuration configuration) {
        this.configuration = configuration;
    }

    @Override
    public Configuration getConf() {
        return configuration;
    }

    public static void main(String[] args) {
        try {
            Configuration configuration = new Configuration();
            ToolRunner.run(configuration, new Fruit2Driver(), args);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

