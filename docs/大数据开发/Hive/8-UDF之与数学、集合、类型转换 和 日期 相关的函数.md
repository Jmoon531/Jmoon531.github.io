---

Created at: 2021-10-27
Last updated at: 2022-09-09


---

# 8-UDF之与数学、集合、类型转换 和 日期 相关的函数


**数学函数**
与**取整**有关的函数：
round： 四舍五入
```
select round(3.14);
select round(3.54);
```
ceil：  向上取整
```
select ceil(3.14);
select ceil(3.54);
```
floor： 向下取整
```
select floor(3.14);
select floor(3.54);
```

**集合函数**
size： 集合中元素的个数
```
select size(friends) from test3;
```
map\_keys： 返回map中的key
```
select map_keys(children) from test3;
```
map\_values: 返回map中的value
```
select map_values(children) from test3;
```
array\_contains: 判断array中是否包含某个元素
```
select array_contains(friends,'bingbing') from test3;
```
sort\_array： 将array中的元素排序
```
select sort_array(friends) from test3;
```

**类型转换函数**
cast(expr as <type>)：将表达式expr的结果转换成指定的类型
例如，把string类型的'100'转化成BIGINT类型的100
```
select cast('100' as BIGINT);
```
把日期转换成string
```
select cast(date_format('2021-10-27 14:45:55', 'yyyy-MM-dd') as string);
```

**日期函数**
unix\_timestamp：返回当前或指定时间的时间戳 （单位：秒）
```
select unix_timestamp();
select unix_timestamp("2020-10-28",'yyyy-MM-dd');
```
from\_unixtime：将时间戳转为日期格式
```
select from_unixtime(1603843200);
```
current\_date：当前日期
```
select current_date;
```
current\_timestamp：当前的日期加时间
```
select current_timestamp;
```
to\_date：抽取日期部分
```
select to_date('2020-10-28 12:12:12');
```
year：获取年
```
select year('2020-10-28 12:12:12');
```
month：获取月
```
select month('2020-10-28 12:12:12');
```
day：获取日
```
select day('2020-10-28 12:12:12');
```
hour：获取时
```
select hour('2020-10-28 12:12:12');
```
minute：获取分
```
select minute('2020-10-28 12:13:12');
```
second：获取秒
```
select second('2020-10-28 12:12:14');
```
weekofyear：当前时间是一年中的第几周
```
select weekofyear('2020-10-28 12:12:12');
```
dayofmonth：当前时间是一个月中的第几天
```
select dayofmonth('2020-10-28 12:12:12');
```
months\_between： 两个日期间相差的月份，MySQL那里面没有这个函数
```
select months_between('2020-04-01','2020-10-28');
```
add\_months：日期加减月
```
select add_months('2020-10-28',-3);
```
datediff：两个日期相差的天数
```
select datediff('2020-11-04','2020-10-28');
```
**date\_add：日期加天数**
```
select date_add('2020-10-28',4);
```
date\_sub：日期减天数
```
select date_sub('2020-10-28',-4);
```
last\_day：当月的最后一天
```
select last_day('2020-02-30');
```
**date\_format(): 格式化日期**
第一个参数输入的日期必须是 yyyy-MM-dd HH:mm:ss 的标准格式，然后以第二个参数的格式输出
```
select date_format('2020-10-28 12:12:12','yyyy/MM/dd HH:mm:ss');
```
next\_day：下一个周几的日期是哪一天
比如2021-10-27是周三，那么下一个周五是：
```
> select next_day('2021-10-27','friday');
2021-10-29
```
再比如2021-10-27是周三，那么本周的周一是：
```
> select date_add(next_day('2021-10-27','MO'),-7);
2021-10-25
```

