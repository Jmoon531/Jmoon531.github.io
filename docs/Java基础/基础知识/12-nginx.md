#### **nginx常用命令**

- 查看nginx版本

    ```
    nginx -v
    ```

- 停止nginx

    ```
    nginx -s -stop
    ```

- 重新加载nginx配置文件

    ```
    nginx -s reload
    ```

- 不运行，仅测试配置文件语法是否正确，也可用来查看nginx配置文件位置

    ```
    nginx -t
    ```

#### **反向代理配置示例**

nginx的docker容器默认读取的主配置文件是`/etc/nginx/nginx.conf`，在主配置文件的http块中有这么一项`include /etc/nginx/conf.d/*.conf;`，也就是nginx还会读取`/etc/nginx/conf.d/`下的配置文件的配置，然后放在主配置文件的http块中，所以有两种方式修改nginx的配置，一种是直接修改`/etc/nginx/nginx.conf`，另外一种是在`/etc/nginx/conf.d/`下另外再写配置，下面采用另外再写配置的方式。

1.启动两个tomcat容器，自动分配的ip分别是`172.17.0.2`、`172.17.0.3`，部署同样的web工程。

```
docker run -d -v /root/webapps:/usr/local/tomcat/webapps --name tomcat01 tomcat
docker run -d -v /root/webapps:/usr/local/tomcat/webapps --name tomcat02 tomcat
docker run -d -v /root/webapps:/usr/local/tomcat/webapps --name tomcat03 tomcat
```

2.编辑nginx.conf，配置三个location来匹配不同路径，让nginx把不同路径的请求分派的不同的tomcat上，/service/分派给tomcat01，/static/分派给tomcat02，剩余所有分派给tomcat03。

```
server {
  listen 80;
  location /service/ {
    proxy_pass http://172.17.0.2:8080;
  }
  location /static/ {
    proxy_pass http://172.17.0.3:8080;
  }
  location / {
    proxy_pass http://172.17.0.4:8080;
  }
}
```

3.启动nginx容器，把宿主机的nginx.conf文件挂载到容器的`/etc/nginx/conf.d/`下

```
docker run -d -v /root/nginx.conf:/etc/nginx/conf.d/nginx.conf -p 80:80 --name master-nginx nginx
```

4.进入nginx容器，删除`/etc/nginx/conf.d/default.conf`并让nginx重新加载配置

```
docker exec -it master-nginx /bin/bash
rm /etc/nginx/conf.d/default.conf
nginx -s reload
```

#### **负载均衡配置示例**

1.为了验证负载均衡分离的效果，需要将web工程复制了一份，然后在相同的一个页面做点不一样的标记，接着启动两个tomcat容器，分别部署这两个web工程。

```
docker run -d -v /root/webapps01:/usr/local/tomcat/webapps --name tomcat01 tomcat
docker run -d -v /root/webapps02:/usr/local/tomcat/webapps --name tomcat02 tomcat
```

2.在宿主机上新建一个nginx的配置文件，并调整文件权限为777，不然挂载此文件到容器后，会出现在宿主机修改但在容器不同步的问题，只有重启容器才能同步，根本原因是vin编辑文件之后会改变文件的inode，把权限改成777后就不会改变inode了。

```
mkdir nginx.conf
chmod 777 nginx.conf
```

3.编辑nginx.conf

```
#tomcat服务器的ip地址列表
upstream loadingbalance{
  server 172.17.0.2:8080;
  server 172.17.0.3:8080;
}
server {
  listen 80;
  location / {
    proxy_pass http://loadingbalance;
  }
}
```

4.启动nginx容器，把宿主机的nginx.conf文件挂载到容器的`/etc/nginx/conf.d/`下

```
docker run -d -v /root/nginx.conf:/etc/nginx/conf.d/nginx.conf -p 80:80 --name master-nginx nginx
```

5.进入nginx容器，删除`/etc/nginx/conf.d/default.conf`并让nginx重新加载配置

```
docker exec -it master-nginx /bin/bash
rm /etc/nginx/conf.d/default.conf
nginx -s reload
```

#### **动静分离配置示例**

动静分离的思路是静态资源请求直接让nginx服务器返回，动态资源请求再让nginx转发到tomcat服务器。所以需要把整个web工程在nginx服务器上也放一份，当请求是以html、jpg等结尾时，直接由nginx服务器返回。因为要修改主配置文件中的user，所以下面采用直接修改`/etc/nginx/nginx.conf`然后挂载到容器的方式完成nginx的配置。

1.编辑nginx.conf，先把主配置文件`/etc/nginx/nginx.conf`里的内容复制出来，然后在此基础上修改。

```
#注意修改nginx访问本地资源文件时所用的用户，不然nginx无法访问所在服务器的本地资源从而报403 forbidden
user  root;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    upstream loadingbalance{
      server 172.17.0.2:8080;
      server 172.17.0.3:8080;
    }
    
    server {
      listen 80;
      
      #静态资源请求直接让nginx服务器返回
      location ~* \.(html|gif|jpg|jpeg|png|css|js|ico)$ {
        root /root/webapps/;
        expires 3d;
      }

      location / {
        proxy_pass http://loadingbalance;
      }
    }
}
```

2.启动nginx容器，把宿主机中的配置文件`nginx.conf`和web工程`/root/webapps01`挂载到容器中

```
docker run -d -v /root/nginx.conf:/etc/nginx/nginx.conf -v /root/webapps01:/root/webapps -p 80:80 --name master-nginx nginx
```

