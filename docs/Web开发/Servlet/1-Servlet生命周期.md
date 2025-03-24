---

Created at: 2024-01-07
Last updated at: 2024-01-10
Source URL: about:blank


---

# 1-Servlet生命周期


生命周期：对象从创建到销毁经历的过程。
```
public class HelloServlet implements Servlet {
    //对象创建的时候执行一次
    @Override
    public void init(ServletConfig servletConfig) throws ServletException {
    }

    //用户每次请求都会执行一次
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
    }

    //对象即将销毁时执行一次
    @Override
    public void destroy() {
    }

    @Override
    public ServletConfig getServletConfig() {
        return null;
    }

    @Override
    public String getServletInfo() {
        return null;
    }
}
```

Servlet生命周期：

1. 用户发送请求
2. Tomcat接收请求，找路径对应的Servlet对象
3. 没找到，利用发射机制创建对象（事实上Tomcat会将Servlet存在Map中，key是请求路径，value是Servlet对象的引用）

            3.1 调用无参构造
            3.2 调用init方法

4. 调用service方法
5. 当web容器关闭，或者该Servlet长时间没有被访问，那么调用destroy方法，完成销毁前的动作

注意：Tomcat会多线程处理用户的请求，但是不会每次请求都创建Servlet对象，所有用户相同的请求都是同一个Servlet对象处理的，所以`Servlet的实例变量涉及线程安全问题。`

可以进行配置让Servlet对象在web容器启动阶段完成创建。
```
<servlet>
    <servlet-name>HelloServlet</servlet-name>
    <servlet-class>t2.HelloServlet</servlet-class>
    `<load-on-startup>1</load-on-startup>`
</servlet>
<servlet-mapping>
    <servlet-name>HelloServlet</servlet-name>
    <url-pattern>/hello</url-pattern>
</servlet-mapping>
```

