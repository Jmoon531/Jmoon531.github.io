---

Created at: 2024-01-08
Last updated at: 2024-03-28
Source URL: about:blank


---

# 4-抽象类GenericServlet（内含 模板方法模式）


每次实现Servlet都要重写很多方法，而仅仅只有service方法是必要的，这样未必过于麻烦，所以Servlet规范还提供了一个方便的抽象类GenericServlet，实现类似于下面：
```
public abstract class GenericServlet implements Servlet {

    private transient ServletConfig config;

    @Override
    public `final` void init(ServletConfig servletConfig) throws ServletException {
        this.config = servletConfig;
        `init();`
    }

 `public void init() {`
 `}`

    @Override
    public ServletConfig getServletConfig() {
        return config;
    }

    @Override
    public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
    }

    @Override
    public String getServletInfo() {
        return "";
    }

    @Override
    public void destroy() {
    }

    ////////////////////额外提供的方法/////////////////
    public String getInitParameter(String name) {
        return this.getServletConfig().getInitParameter(name);
    }

    public Enumeration<String> getInitParameterNames() {
        return this.getServletConfig().getInitParameterNames();
    }

    public ServletContext getServletContext() {
        return this.getServletConfig().getServletContext();
    }
}
```
非常值得学习的编程思想（设计模式-模板方法模式）：因为里面有为实例变量config赋值的代码，如果子类覆盖但是没有调用super.init(config)，就埋下了空指针异常的隐患，所以不想被子类覆盖 init(ServletConfig)方法，就必须为 init(ServletConfig)加上fianl关键字，但是这样子类就不能在初始化Servlet时做操作了，于是这里提供了空的init()方法供子类重写。

