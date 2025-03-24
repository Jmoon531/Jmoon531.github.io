---

Created at: 2021-11-07
Last updated at: 2021-11-08


---

# 15-shell工具


1.cut
从文件中裁剪字符：
```
cut -d 分隔符 -f 列号(从1开始) 文件名
```
比如提取环境变量PATH的第二个值
```
# echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin
# echo $PATH | cut -d : -f 2
/usr/local/bin
```

2.sed
sed编辑器被称作流编辑器（ stream editor），和普通的交互式文本编辑器恰好相反。在交互式文本编辑器中（比如vim），你可以用键盘命令来交互式地插入、删除或替换数据中的文本。流编辑器则会在编辑器处理数据之前基于预先提供的一组规则来编辑数据流。
sed的执行过程：
(1) 一次从输入中读取一行数据。
(2) 根据所提供的编辑器命令匹配数据。
(3) 按照命令修改流中的数据。
(4) 将新的数据输出到STDOUT。
在流编辑器将所有命令与一行数据匹配完毕后，它会读取下一行数据并重复这个过程。
sed命令的格式如下：
```
sed [选项] 命令 文件
```
选项：-e，指定多条命令；-i 从文件中读取并将处理后的结果写回文件
命令：a 新增一行；d 删除；s 查找并替换

数据：
```
# vim sed.txt
i
love
you
```
新增一行：
```
# sed '2a\this is a new line' sed.txt
i
love
this is a new line
you
```
删除一行：
```
# sed '2d' sed.txt
i
you
```
删除包含love的行：
```
# sed '/love/d' sed.txt
i
you
```
把you替换成her：
```
# sed 's/you/her/g' sed.txt
i
love
her
```
删除第一行并把把you替换成her：
```
# sed -e '2d' -e 's/you/her/g' sed.txt
i
her
```

3.awk
一个强大的文本分析工具，把文件逐行的读入，以空格为默认分隔符将每行切片，切开的部分再进行分析处理。
```
awk [选项] 'pattern1{action1}  pattern2{action2} ...' filename
```

* 选项：\-F：指定分隔符；-v 定义一个变量
* pattern：awk在数据中查找的内容，就是匹配模式
* action：在找到匹配内容时所执行的一系列命令

awk内置变量：
```
FILENAME           awk浏览的文件名
NF                 浏览记录的域的个数（切割后，列的个数）
NR                 已读的记录数
```

搜索/etc/passwd文件以root关键字开头的所有行，并输出该行的第1列和第7列，中间以 "," 号分割，注意$0是当前行的内容，$1是分割后的第一个元素，$7是分割后的第7个元素，以此类推。
```
# awk -F : '/^root/{print $1","$7}' /etc/passwd
root,/bin/bash
```

只显示/etc/passwd的第一列和第七列，以逗号分割，且在所有行前面添加列名user，shell，每一行需要在前面显示行号，在最后一行显示读取了多少行
BEGIN模式在读取文件之前执行，END模式在读取文件之后执行：
```
# awk -F : 'BEGIN{print "user, shell"} {print NR" "$1","$7} END{print "rows:" NR}' /etc/passwd
user, shell
1 root,/bin/bash
2 bin,/sbin/nologin
...
rows:28
```

对文件里的数求和
```
# vim num.txt
3
2
1
# awk '{sum+=$1; print $1} END{print "sum="sum}' num.txt
3
2
1
sum=6
```

查询空行的行号：
```
awk '/^$/{print NR}' sed.txt
```

选项-v示例：向控制台每输入一个数字，就会立马输出这个数字加1之后的结果
```
awk -v i=1 '{print $1+i}'
```

4.sort
对文件的内容排序
```
sort [选项] 文件列表
```
选项：

* \-n 依照数值的大小排序
* \-r 以相反的顺序来排序
* \-t 设置排序时所用的分隔字符
* \-k 指定需要排序的列

数据：
```
# vim sort.txt
a:1
c:3
b:2
```

```
# sort sort.txt
a:1
b:2
c:3

# sort -r sort.txt
c:3
b:2
a:1

# sort -t : -k 2 -r sort.txt
c:3
b:2
a:1
```

5.uniq
连续重复的数据只取一个
选项：

* \-i ：忽略大小写
* \-c ：进行计数

数据：
```
# vim uniq.txt
a
a
b
b
c
```
```
# uniq uniq.txt
a
b
c
```
```
# uniq -c uniq.txt
      2 a
      2 b
      1 c
```
统计每个人的登录总次数：
```
# last | cut -d ' ' -f 1 | sort | uniq -c
      1
     45 reboot
    117 root
      1 wtmp
```

