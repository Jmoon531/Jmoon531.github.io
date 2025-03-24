---

Created at: 2024-01-07
Last updated at: 2024-03-10
Source URL: about:blank


---

# 3-ServletContext接口


ServletContext（Servlet上下文）：
1、一个webapp只有一个ServletContext对象，一个webapp只有一个web.xml文件，ServletContext是web.xml的化身。
2、一个web.xml文件中可以配置多个<servlet>标签，一个Servlet对应一个ServletConfig，ServletConfig是<servlet>标签的化身。
3、ServletContext对象在服务器启动时创建，在服务器关闭时销毁，所有Servlet共享一个ServletContext对象，是所有Servlet的上下文环境，比如，所有用户若要共享同一个数据，可以将这个数据放到ServletContext对象中；当然，因为是多线程共享的一个对象，所以修改`ServletContext中的数据时涉及到线程安全问题`。

ServletContext常用的方法：
**1、获取初始化参数**
在web.xml中配置上下文参数，这些信息会被自动封装到ServletContext对象中
```
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">

 `<context-param>`
 `<param-name>username</param-name>`
 `<param-value>zhangsan</param-value>`
 `</context-param>`
 `<context-param>`
 `<param-name>password</param-name>`
 `<param-value>xxxx</param-value>`
 `</context-param>`

    <servlet>
        <servlet-name>HelloServlet</servlet-name>
        <servlet-class>t2.HelloServlet</servlet-class>
        <init-param>
            <param-name>key1</param-name>
            <param-value>value1</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>HelloServlet</servlet-name>
        <url-pattern>/hello</url-pattern>
    </servlet-mapping>
</web-app>
```
拿到<context-param>标签中配置key-value键值对：
```
public class ServletTest02 implements Servlet {

    private ServletConfig servletConfig;

    //对象创建的时候执行一次
    @Override
    public void init(ServletConfig servletConfig) throws ServletException {
        this.servletConfig = servletConfig;
    }

    //用户每次请求时执行一次
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
        ServletContext context = servletConfig.getServletContext();
        //通过key获取value
        String username = `context.getInitParameter("username");`
        String password = context.getInitParameter("password");
        //获取所有key
        Enumeration<String> params = `context.getInitParameterNames();`
        while (params.hasMoreElements()) {
            String key = params.nextElement();
            String value = context.getInitParameter(key);
        }
    }

    //对象即将销毁时执行一次
    @Override
    public void destroy() {}

    @Override
    public ServletConfig getServletConfig() {
        return servletConfig;
    }

    @Override
    public String getServletInfo() {
        return null;
    }
}
```

**2、获取文件的绝对路径**
```
@Override
public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
    ServletContext context = servletConfig.getServletContext();
    //获取文件的绝对路径
    String realPath = `context.getRealPath("/index.html");` //c:\\tomcat8\\webapps\servlet-test\index.html
}
```

**3、向ServletContext中存取数据（重点）**
AServlet
```
@Override
public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
    ServletContext context = servletConfig.getServletContext();
    `context.setAttribute("zhangsan", 18);`
}
```
BServlet
```
@Override
public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
    ServletContext context = servletConfig.getServletContext();
    Integer age = (Integer) `context.getAttribute("zhangsan");`
    `context.removeAttribute("zhangsan");`
}
```

