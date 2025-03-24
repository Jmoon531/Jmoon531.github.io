---

Created at: 2021-11-06
Last updated at: 2021-11-06
Source URL: https://www.runoob.com/linux/linux-shell-variable.html


---

# 10-shell脚本简介


shell是一个用c语言编写的命令解释器，用于接收用户的命令，然后调用操作系统内核，与Java、python等高级语言的解释器类似。打开一个控制台其实就是启动了一个可以和用户进行交互的shell进程，使用bash或sh命令执行一个shell脚本，其实是启动了另外一个shell进程来执行脚本中命令。
Linux 的 有很多不同的 Shell，常见的有：

* Bourne Shell（/usr/bin/sh或/bin/sh）
* Bourne Again Shell（/bin/bash）
* C Shell（/usr/bin/csh）
* K Shell（/usr/bin/ksh）
* Shell for Root（/sbin/sh）

centos提供的Shell解析器有：
```
cat /etc/shells
```
```
/bin/sh
/bin/bash
/usr/bin/sh
/usr/bin/bash
```
bash和sh的关，其实都是bash
```
ll /usr/bin/ | grep bash
```
```
-rwxr-xr-x. 1 root root   1150584 5月  27 11:11 bash
lrwxrwxrwx. 1 root root         4 5月  27 11:11 sh -> bash
```
查看默认shell
```
echo $SHELL
```
```
/bin/bash
```

执行shell脚本的两种方式
1.使用bash或sh命令，以这种方式执行脚本，不需要脚本有可执行权限，在脚本的第一行指定解释器信息没用
```
bash test.sh
```
```
sh test.sh
```
2.加上可执行权限之后
```
./tesh.sh
```
一定要写成 ./test.sh，而不是 test.sh，运行其它可执行的程序也一样，直接写 test.sh，linux 系统会去 PATH 里寻找有没有叫 test.sh 的，而只有 /bin，/sbin，/usr/bin，/usr/sbin 等在 PATH 里，你的当前目录通常不在 PATH 里，所以写成 test.sh 是会找不到命令的，要用 ./test.sh 告诉系统说，就在当前目录找。

脚本以#!/bin/bash开头，用于指定解析器
#用于注释

