**docker官方安装教程：**

https://docs.docker.com/engine/install/centos/#install-using-the-repository

**阿里云docker镜像加速器：**

https://cr.console.aliyun.com/cn-shenzhen/instances/mirrors

```
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://lvq55l26.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**CentOs常用命令：**

- 开启docker服务
  
  ```
  systemctl start docker
  ```

- 查看进程状态
  
  ```
  systemctl status docker
  ```

- 查看系统全部的进程
  
  ```
  ps -ef
  ```

- 添加路由
  
  ```
   ip route add 172.16.0.0/16 via 172.16.5.1 dev ens192
  ```

- 删除路由
  
  ```
   ip route del 172.16.0.0/16
  ```

- 停止docker
  
  ```
  systemctl stop docker
  systemctl stop docker.socket
  ```

**docker常用命令：**

- 查看docker版本
  
  ```
  docker version
  ```

- 列出本地镜像
  
  ```
  docker images
    Options:
      -a             列出本地所有镜像（含中间映像层）
      -q             只显示镜像ID
      --digests    显示镜像的摘要信息
      --no-trunc  显示完整的镜像信息
  docker images -qa
  ```

- 在官方的Docker Hub上搜索某个镜像
  
  ```
  docker search <镜像名>
    Options:
      -s    指定最少的star数
  ```

- 拉取镜像
  
  ```
  docker pull <镜像>
  ```

- **根据镜像创建容器并运行**
  
  不带 -d 参数时会在前台启动容器，所谓在前台启动就是调度的优先级高并且占用标准输入输出，如果这时程序没有任何阻塞（比如 *等待建立连接*  或者 *等待从标准输入读入* 等）、也没有向标准输出写任何内容，还没有执行繁重的计算任务，那么容器很快就在前台执行完成并结束，表现成好像什么都没有发生过。加上-d参数就是让程序在后台运行，不会占用标准输入输出。
  
  加上 -it 参数会在启动容器的同时开启并进入交互式终端，主要是-i ，它会把标准输入，输出，错误流都交给容器，当然这要求被启动的程序必须能等待从标准输入读入，如果程序没有等待从标准输入读入，那么即使docker给你开启了标准输入也是白搭；还有，即使程序是在等待从标准输入读入，但是你启动容器时，没有用-i参数指定docker为其开启标准输入，那也不行。比如运行centos时，缺省命令是'/bin/bash'（构建时Dockerfile文件最后一行是 CMD /bin/bash），从而开启了终端等待从标准输入读入，如果这时没有为其开启标准输入，那也不行。
  
  ```
  docker run <镜像名>
    Options:
        -d      后台启动
        -it     启动的同时开启并进入交互式终端（-i和-t的合体），
            -i (interactive) 开启标准输入，以交互式的方式启动
            -t (pseudo-tty) 分配一个伪终端
      --name  给容器起一个名字
      -p <宿主机端口>:<容器端口> 启动容器时做端口映射
      -P 启动容器时随机分配宿主机端口
      -v <宿主机目录>:<容器目录>[:ro] 绑定挂载数据卷
      --volume-from <容器> 挂载指定的容器中的数据卷
      --restart 设置容器的重启策略，默认不重启
          always 只有使用docekr stop命令停止容器才不会重启，其它情况导致容器停止，docker都会重新启动容器，包括docker重启                 也会重新启动该容器
          unless-stopped 与always的只有一个差别就是docker重启时不会启动该容器
          on-failure[:<失败重启次数>] 容器退出时返回值不是0的时候就会重启容器
      --rm 如果容器已经存在那就自动移除
  ```
  
  例子：
  
  ```
  docker run centos /bin/sh -c "while true; do echo hello world; sleep 1; done"
  ```
  
  - 运行mysql镜像
    
    ```
    docker run -p 3306:3306 --name mysql \
    -v /mysql/cof:/etc/mysql/conf.d -v /mysql/logs \
    -v /mysql/logs:/logs \
    -v /mysql/data:/var/lib/mysql \
    -e MYSQL_ROOT_PASSWORD=123456 \
    -d mysql:8.0
    ```
  
  - 运行redis镜像
    
    ```
    docker run -p 6379:6379 \
    -v /myredis/data:data \
    -v /myredis/conf/redis.conf:/usr/local/etc/redis/redis.conf \
    -d redis:3.2 redis-server /usr/local/etc/redis/redis.conf --appendonly yes
    ```

- 显示容器
  
  ```
  docker ps
    不带参数表示显示正在运行的容器
    Options:
      -a 显示所有容器，包括停掉了的（所有状态）
      -l 显示上一次创建的容器（所有状态）
      -n <数量> 显示前n次创建的容器（所有状态）
      -q 只显示容器的编号，需要与-a或-l搭配使用
  ```

- 查看容器日志
  
  ```
  dockers logs <容器>
    Options:
      -f  跟随日志最新输出
      -t  显示时间戳
      --tail <数字>  显示日志末尾几行（这是linux的常用命令）
  ```

- 查看容器内的进程
  
  ```
  docker top <容器>
  ```

- 查看细节
  
  ```
  docker inspect <容器/镜像>
    Options:
      --format 使用给定的Go模板格式化输出
      例如：
        查看镜像的分层信息：docker inspect --format {{.RootFS}} <镜像>
        查看镜像的数据卷信息：docker inspect --format {{.ContainerConfig.Volumes}} <镜像>
  ```

- 退出交互式终端并停止正在运行的容器
  
  ```
  exit
  ```

- 退出交互式终端但不停止正在运行的容器
  
  ```
  ctrl 先按 p 再按 q （注：在ssh终端里无法操作，在linux的终端里可以）
  ```

- 重新进入与容器交互的终端，也就是把标准输入，输出，错误流都交给指定的容器
  
  ```
  docker attach <容器>
  ```

- 让容器执行命令（没有进入与容器交互的终端）
  
  ```
  docker exec <容器> <命令>
  ```
  
    如重新进入与容器交互的终端：`docker exec -it <容器> /bin/bash` ，这里 -i 会把标准输入，输出，错误流都交给指定的容器，-t 会在容器里新开一个伪终端（与attach命令不同，attach命令是不会新开终端，而是进入已有的进程），如果这时在这个新开的伪终端里输入exit会退出该终端，但不会导致容器关闭，**只有当杀死容器中的主进程，也即PID为1的进程，才会杀死容器**。

- 在容器和宿主机之间拷贝文件
  
  ```
  docker cp src_path dest_path    注意：容器中路径的写法是<容器>:<文件路径>
  ```

- **在后台**启动已经停止的容器
  
  ```
  docker start <容器>
  ```

- 重启正在运行的容器
  
  ```
  docker restart <容器>
  ```

- 停止容器
  
  ```
  docker stop <容器>
  ```

- 强制停止容器
  
  ```
  docker kill <容器>
  ```

- 删除容器
  
  ```
  docker rm <容器>
  删除全部的容器的两条命令：
    docker rm $(docker ps -qa) ，docker -qa返回的是全部容器的ID
    docker ps -qa | xargs docker rm
  ```

- 删除镜像
  
  如果通过镜像创建了容器，那么该镜像就被容器所依赖了，删除操作将不被允许。
  
  ```
  docker rmi <镜像>
  ```

- 提交容器生成镜像
  
  ```
  docker commit -a -m <容器> 镜像名:tag
  -a 作者
  -m 提交信息 
  镜像名如 jmoon/tomcat:1.0
  ```

- 根据DockerFile构建镜像
  
  ```
  docker build -f <dockerfile> -t <镜像名:tag> <构建上下文>
  ```
  
  不加 -f 选项默认读取当前路径下的 Dockerfile，构建上下文（Build Context）就是应用文件的目录，所以最佳实践就是把Dockerfile文件放在应用文件的根目录下，然后在应用文件根目录下执行`docker build -t <镜像名:tag> .`

- 查看镜像构建的历史信息
  
  ```
  docker history <镜像>
  ```

- 推送镜像到Hub
  
  ```
  1.登录阿里云Docker Registry
      docker login registry.cn-shenzhen.aliyuncs.com
  2.给要推送镜像再命一个名并标记上版本号，命名规范是 阿里云DockerRegistry地址/命名空间/镜像仓库:[镜像版本号]
      docker tag <镜像> registry.cn-shenzhen.aliyuncs.com/jmoon531/myalpine:[镜像版本号]
  3.推送镜像
      docker push registry.cn-shenzhen.aliyuncs.com/jmoon531/myalpine:[镜像版本号]
  ```
  
  镜像注册（`image register` ）、镜像仓库（`image repository`）、镜像（ `image`）的关系：
  
  `image register`翻译是镜像注册簿或镜像登记簿，也就是DockerHub的地址，默认是docker.io，如果使用的是第三方Hub如阿里云，那么需要明确指出registry.cn-shenzhen.aliyuncs.com。命令`docker pull jmoon/mycentos` 表示在docker.io，拉取二级命名空间jmoon下的mycentos镜像仓库里的标签为latest的镜像，主要是要知道mycentos镜像仓库里有许多不同版本的mycentos镜像。

**Dockerfile文件用于构建镜像**

```
FROM 父镜像
MAINTAINER 创建镜像的作者信息
RUN 执行命令，一条RUN命令执行完后会在当前镜像层创建一个新的镜像层
EXPOSE 指明容器向外开放的端口
WORKDIR 为接下来的指令指定工作目录
ENV 设置容器的环境变量
ADD 向镜像文件添加文件，如果是压缩文件会被解压
COPY 向镜像文件添加文件，不会解压
VOLUME 在指定路径创建挂载点
CMD 设置容器启动时默认运行的命令，覆盖的方式
ENTRYPOINT 设置容器启动时默认运行的命令，追加的方式
ONBUILD 被作为父镜像构建时触发的命令
USER 为指定接下来的RUN、ENTRYPOINT、CMD命令的用户
```

新增镜像层的指令包括FROM、RUN、ADD以及COPY，而其它命令只会新增元数据 ，区分命令是否会新增镜像层的一个基本原则是，如果指令的作用是向镜像中添加新的文件或程序，那么这条指令就会新增镜像层；如果只是告诉Docker如何完成构建或者如何运行应用程序，那么就只会增加镜像的元数据。

官方hello-world的Dockerfile

```
FROM scratch
COPY hello /
CMD ["/hello"]
```

官方centos8的Dockerfile

```
FROM scratch
ADD centos-8-x86_64.tar.xz /
LABEL org.label-schema.schema-version="1.0"     org.label-schema.name="CentOS Base Image"     org.label-schema.vendor="CentOS"     org.label-schema.license="GPLv2"     org.label-schema.build-date="20201204"
CMD ["/bin/bash"]
```

测试用例

```
FROM centos
ENV loginpath /temp
WORKDIR $loginpath
RUN echo "success✌"
CMD /bin/bash
```

一、镜像

1.关键理解

docker镜像由一些松耦合的只读镜像层组成，所有的docker镜像都起始于一个基础镜像层，当进行修改或增加新的内容时，就会在当前镜像层之上创建新的镜像层。镜像本身就是一个配置对象，其中包含了镜像层的列表以及一些元数据信息，镜像层才是实际数据存储的地方。多个镜像之间会共享镜像层，在删除镜像时，被多个镜像共享的镜像层并不会被删除，只有当依赖该镜像层的全部镜像都被删除后，该镜像层才会被删除。

docker通过存储引擎的方式实现镜像层堆栈，并保证多镜像层对外展示为统一的文件系统。Linux上可用的存储引擎有AUFS、Overlay2、Device、Mapper、Btrfs以及ZFS，而docker在Windows上仅支持windowsfilter一种存储引擎。每个存储引擎都有自己的镜像分层、镜像共享以及写时复制(Cow)技术的实现。

2.写时复制机制

通过docker run命令指定镜像创建容器时，实际上是在该镜像之上创建一个空的可读写的文件系统层级，可以将这个文件系统当成一个新的临时镜像，而命令里所指的镜像称为父镜像。父镜像里的内容都是以只读的方式挂载进来的，容器会读取父镜像的内容，不过一旦需要修改父镜像文件，便会触发docker从父镜像中复制这个文件到临时镜像中来，所有的修改均发生在临时文件系统中，而不会对父镜像造成任何影响，这就是Docker镜像的**写时复制**机制。

二、数据卷

数据卷在docker commit时不会被打包进镜像；数据卷可以让宿主机和容器之间，多个容器之间共享数据；数据卷可以是单个文件，比如socket。

创建数据卷的方式：

1.创建镜像时，在Dockerfile中使用VOLUME指令：

```
VOLUME /path1 /path2 或 VOLUME ["/path1", "path2"]
```

2.创建容器时，使用-v

```
docker run -v <宿主机目录>:<容器目录> <镜像>
设置容器中目录是只读的：dockers run -v <宿主机目录>:<容器目录>:ro <镜像>，此时不能对容器内的目录进行写操作，但是可以对宿主机的目录进行写操作。
```

如果没有声明宿主机目录，默认会在宿主机/var/lib/docker/vfs/dir下分配一个具有唯一名字的目录

`--volume-from` 会挂载指定容器的所有数据卷到当前容器，这时数据卷中的数据在多个容器中共享。

三、网络

1.`docker run -P` 大写P会随机分配主机端口，然后映射到容器向外暴露的端口，容器向外开放的端口是由Dockerfile的EXPOSE指定的，如：

```
docker run -d -it -P tomcat
docker ps -a查看到的结果：PORTS 0.0.0.0:49153->8080/tcp 表示将宿主机所有ip的49153端口都映射到容器的8080端口
```

2.`docker run -p` 小写p指定宿主机网络接口的端口到容器开放端口的映射，如：

```
docker run -d -it -p 80:8080 tomcat 将宿主机所有ip的80端口映射到容器的8080端口
docker run -d -it -p 127.0.0.1:80:8080 tomcat 将宿主机的127.0.0.1的80端口映射到容器的8080端口，用本机的其它ip是访问不到的
docker run -d -it -p 127.0.0.1::8080 tomcat 随机分配宿主机的127.0.0.1的一个端口映射到容器的8080端口
```
