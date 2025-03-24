---

Created at: 2024-01-07
Last updated at: 2024-03-10
Source URL: about:blank


---

# 0-Servlet的本质


Servlet是一套规范（接口），类似于JDBC，只不过JDBC是JavaSE的内容，JDK中包含，但是Servlet是JavaEE的内容，JDK中不包含，所以这套接口还需要另外导包。当然，无论是Servlet，还是JDBC，都是接口，真正运行还需要实现类，比如如果连接的是MySQL，那么就需要将MySQL官方提供的JDBC包导入到项目中，类似的，Tomcat就是Servlet接口的一种实现。

模拟一下Servlet的原理

**Servlet规范（接口）**
```
public interface Servlet {
    void service();
}
```

**Tomcat**
```
public class Tomcat {
    public static void main(String[] args) throws Exception {
        System.out.println("Tomcat 启动成功！");
        Scanner scanner = new Scanner(System.in);
        FileReader fileReader = new FileReader("D:\\Project\\IdeaProjects\\servlet\\src\\main\\java\\web.xml");
        Properties properties = new Properties();
        properties.load(fileReader);
        fileReader.close();
        HashMap<String, Servlet> map = new HashMap<>();
        while (true) {
            System.out.println("请输入访问路径：");
            String path = scanner.next();
            String ser = (String) properties.get(path);
            Servlet servlet = map.getOrDefault(ser, (Servlet) Class.forName(ser).newInstance());
 `servlet.service();`
        }
    }
}
```

**Web程序开发的Servlet**
LoginServlet
```
public class LoginServlet implements Servlet {
    @Override
    public void service() {
        System.out.println("成功登录!");
    }
}
```

SaveConfigServlet
```
public class SaveConfigServlet implements Servlet{
    @Override
    public void service() {
        System.out.println("成功保存配置！");
    }
}
```

使用web.xml配置请求路径与Servlet的对应关系
```
/login=LoginServlet
/save=SaveConfigServlet
```

