---

Created at: 2024-01-07
Last updated at: 2024-03-28
Source URL: about:blank


---

# 2-ServletConfig接口


**ServletConfig接口：**
1、ServletConfig是Servlet的配置信息对象（Servlet将配置信息配置在web.xml中）。
2、一个Servlet对象对应一个ServletConfig对象。
3、如果要在service方法中使用ServletConfig对象，可以在init方法中将ServletConfig赋给实例变量。
4、ServletConfig接口常用的方法：
```
public class HelloServlet implements Servlet {

    private ServletConfig servletConfig;

    //对象创建的时候执行一次
    @Override
    public void init(ServletConfig servletConfig) throws ServletException {
        this.servletConfig = servletConfig;
    }

    //用户每次请求时执行一次
    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
        servletResponse.setContentType("text/html;charset=UTF-8");
        PrintWriter writer = servletResponse.getWriter();
        //servletConfig的4个方法
        //1、通过key获取value
        String value1 = `servletConfig.getInitParameter("key1");`
        String value2 = servletConfig.getInitParameter("key2");
        writer.println(value1);
        writer.println(value2);
        //2、获取所有key
        Enumeration<String> keys = `servletConfig.getInitParameterNames();`
        while (keys.hasMoreElements()) {
            writer.println(keys.nextElement());
            writer.println(servletConfig.getInitParameter(keys.nextElement()));
        }
        //3、获取<servlet-name>标签中的值
        String servletName = `servletConfig.getServletName();`
        writer.println(servletName);
        `//**4、获取ServletContext对象（重点）**`
 `ServletContext application = servletConfig.getServletContext();`
    }

    //对象即将销毁时执行一次
    @Override
    public void destroy() {

    }

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

在web.xml中写配置信息
```
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">
    <servlet>
        <servlet-name>HelloServlet</servlet-name>
        <servlet-class>t2.HelloServlet</servlet-class>
 `<init-param>`
 `<param-name>key1</param-name>`
 `<param-value>value1</param-value>`
 `</init-param>`
 `<init-param>`
 `<param-name>key2</param-name>`
 `<param-value>value2</param-value>`
 `</init-param>`
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>HelloServlet</servlet-name>
        <url-pattern>/hello</url-pattern>
    </servlet-mapping>
</web-app>
```

