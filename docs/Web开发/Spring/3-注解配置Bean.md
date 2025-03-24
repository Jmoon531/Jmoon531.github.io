---

Created at: 2024-03-19
Last updated at: 2025-02-25
Source URL: about:blank


---

# 3-注解配置Bean


Springboot提供了通过注解配置替代XML文件配置的方式，极大地方便了开发。
**一、开启组件扫描**
**1、XML配置开启组件扫描**
Spring 默认不使用注解装配 Bean，需要在 Spring 的 XML 配置中通过 context:component-scan 元素开启 Spring Beans的自动扫描功能。开启此功能后，Spring 会自动从扫描指定的包（base-package 属性设置）及其子包下的所有类，如果类上使用了 @Component 注解，就将该类装配到容器中。
```
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       `xmlns:context="http://www.springframework.org/schema/context"`
       xsi:schemaLocation="http://www.springframework.org/schema/beans
    http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
    http://www.springframework.org/schema/context
            http://www.springframework.org/schema/context/spring-context.xsd">
    <!--开启组件扫描功能-->
    `<context:component-scan base-package="com.atguigu.spring6"></context:component-scan>`
</beans>
```
注意：在使用 context:component-scan 元素开启自动扫描功能前，首先需要在 XML 配置的一级标签 <beans> 中添加 context 相关的约束。

1、最基本的扫描方式
```
<context:component-scan base-package="dao,service,controller"></context:component-scan>
```

* base-package属性指定一个需要扫描的基类包，Spring容器将会扫描这个基类包及其子包中的所有类。
* 当需要扫描多个包时可以使用逗号分隔。

2、指定要排除的组件
```
<context:component-scan base-package="com.atguigu.spring6">
    <!-- context:exclude-filter标签：指定排除规则 -->
    <!--
         type：设置排除或包含的依据
        type="annotation"，根据注解排除，expression中设置要排除的注解的全类名
        type="assignable"，根据类型排除，expression中设置要排除的类型的全类名
    -->
    <context:exclude-filter type="annotation" expression="org.springframework.stereotype.Controller"/>
        <!--<context:exclude-filter type="assignable" expression="com.atguigu.spring6.controller.UserController"/>-->
</context:component-scan>
```

3、仅扫描指定组件
因为默认是扫描全部，所以如果要指定扫描时包含的类就需要先关闭默认的扫描规则，use-default-filters="false"
```
<context:component-scan base-package="com.atguigu" use-default-filters="false">
    <!-- context:include-filter标签：指定在原有扫描规则的基础上追加的规则 -->
    <!-- use-default-filters属性：取值false表示关闭默认扫描规则 -->
    <!-- 此时必须设置use-default-filters="false"，因为默认规则即扫描指定包下所有类 -->
    <!--
         type：设置排除或包含的依据
        type="annotation"，根据注解排除，expression中设置要排除的注解的全类名
        type="assignable"，根据类型排除，expression中设置要排除的类型的全类名
    -->
    <context:include-filter type="annotation" expression="org.springframework.stereotype.Controller"/>
    <!--<context:include-filter type="assignable" expression="com.atguigu.spring6.controller.UserController"/>-->
</context:component-scan>
```

**2、注解配置开启组件扫描**
通过配置类代替配置文件：在类上加上@Configuration注解表示这是一个配置类，然后通过@ComponentScan注解指明需要扫描的包，不指定的话就是默认扫描配置类所在的包以及子包，指定的话只扫描指定的包。
```
@Configuration
@ComponentScan({"dao", "service", "controller"})
public class ScanConfig {
}
```
@ComponentScan注解也支持 排除扫描指定的注解 和 仅扫描指定组件，但是有点麻烦，这两个配置也不常用，所以不展开。由此可以看到，通过注解完全可以替代XML配置，虽然我们在使用注解配置的时候，总感觉没有XML配置功能强大，但是话又说回来，使用注解配置功能虽然稍弱，但是也完全能支撑开发，也就是说我们其实用不到XML很多花里胡哨的配置。
使用AnnotationConfigApplicationContext读取配置类创建IOC容器：
```
ApplicationContext iocContainer01 = new AnnotationConfigApplicationContext(ScanConfig.class);
BookServlet bookServlet = iocContainer01.getBean("bookServlet", BookServlet.class);
```
@Configuration的属性 proxyBeanMethods 指明在ioc容器内创建配置类的对象，还是创建配置类的代理对象。

* 属性 proxyBeanMethods默认为true，表示创建配置类的代理类对象，通过代理对象调用@Bean方法返回的始终是单实例bean，这是FULL Mode，因为代理类对象每次都要检查容器中有没有这个bean。
* 改为false，则表示在容器中创建的是配置类的对象，那么每次调用@Bean方法就只是单纯地调用方法，都会返回一个新创建的对象，这是Lite Mode，因为这是直接的方法调用。

配置类的@Bean方法在IOC容器创建时被调用，一般都不会手动通过配置类调用@Bean方法，所以这个属性应该很少用。

**二、创建Bean**
**1、创建Bean**
下面的注解标识在类上，组件扫描时会实例化类的对象到IOC容器中。

|     |     |
| --- | --- |
| 注解  | 说明  |
| @Component | 普通组件，标识一个受Spring IOC容器管理的组件 |
| @Repository | 持久化层组件，标识一个受Spring IOC容器管理的持久化层组件 |
| @Service | 业务逻辑层组件，标识一个受Spring IOC容器管理的业务逻辑层组件 |
| @Controller | 表述层控制器组件，标识一个受Spring IOC容器管理的表述层控制器组件 |
| @Configuration | 配置组件，标识一个受Spring IOC容器管理的配置组件 |

bean的id的命名规则：

* 默认情况下使用组件的简单类名首字母小写作为bean的id。
* 可以使用注解的value属性指定bean的id。

bean的作用域：同样，默认是单例，可以使用注解`@Scope("prototype")`指明为多实例。

使用上面4个注解创建bean与使用XML创建bean的区别：
1、XML可以创建多个id不同的单实例bean（单实例bean指scope=singleton，不是指全局单例bean；包括两种情况，一是多个不同的id对应同一个bean；二是多个不同的id各自对应一个bean，但这些bean都是同一个类型），但是使用以上4个注解只能创建一个id的单实例bean（一个类，一个id，一个bean），所以`如果需要直接发现并注册组件可以使用这4个注解`。
2、XML可以创建JDK内置的对象到容器，上面4个注解不行。
这个两个问题都可以通过`@Bean注解`解决，比如创建有多个不同id的单实例bean：
```
@Configuration //注意：配置类中组件的注册顺序就是方法声明的顺序。
@ComponentScan({"dao", "service", "controller"})
public class ScanConfig {
    `@Bean({"user1", "user2", "user3"}) //一个bean多个id`
    User getUser01() {
        Random random = new Random();
        return new User();
    }

    @Bean("u1")
    @Scope("prototype")
    User getUse02r() {
        Random random = new Random();
        return new User();
    }
}
```
@Bean注解还可以指定 创建的bean是否自动装配autowire（和XML配置的自动注入一样，本质是Setter注入，依赖Setter方法，创建完对象立即调用Setter方法）、初始化方法 和 销毁方法。
可以说@Bean注解才是XML配置bean的完整替代，通过XML能实现的配置，@Bean方法都能实现，即`@Bean注解和xml配置中的bean标签的作用是一样的`，比如如果需要引用外部bean，直接在@Bean方法中添加对应类型的参数即可，Spring会给@Bean方法的参数自动注入。
而@Component、@Repository、@Service、@Controller是为了方便定义的，当类只需要创建一个单实例bean时可以通过这4个注解快速定义，然而事实上这种情况占百分之九十，所以是真的方便。
总结：一个@Configuration相当于是一个XML配置文件，一个@Bean方法相当于是一个bean标签。不过需要注意，@Bean方法不仅可以放在@Configuration类中，还可以放在@Component、@Repository、@Service、@Controller标注的类中。

**id与bean的关系总结：**
id与bean是N:1，即 一个id只能对应一个bean（scope=singleton的bean），一个bean可以有多个id。

**2、依赖注入**

**1、@Autowired注入**

* 单独使用@Autowired注解，默认根据类型装配（默认是byType）。
* 该注解有一个required属性，默认值是true，表示在注入的时候要求被注入的Bean必须是存在的，如果不存在则报错。如果required属性设置为false，表示注入的Bean存在或者不存在都没关系，存在的话就注入，不存在的话，也不报错。

1.1 属性注入：@Autowired标注在字段上
字段被赋值在构造函数执行之后，@Autowired方法执行之前
```
@Service
public class BookService {
    @Autowired
    private BookDao bookDao;

    public void addBook() {
        System.out.println("BookService正在添加图书...");
        bookDao.saveBook();
        System.out.println("BookService添加图书完成");
    }
}
```

1.2 @Autowired标注在构造器上
如果有多个构造器：

* 当有一个构造器的标注了一个required=true的@Autowired，那么其他构造器则都不能被标记@Autowired（required=false也不行）。
* 多个构造器都标注了required=false的@Autowired，那么最后会选择能成功注入最多参数的构造器，如果成功注入最多的构造器有多个，那么会选择在类中最后声明的构造器。
* 如果只有一个构造器，那么无论这个构造器是否标有@Autowired注解，这个构造器都会被自动注入。绝大多数情况下我们都希望给类的所有字段都自动注入，这时你只需要加上一个全参数构造器就搞定了，连@Autowired都不用，十分方便，再配上lombok的注解直接引入全参数构造器，更加方便。

```
@Service
public class UserServiceImpl implements UserService {

    private UserDao userDao;

    @Autowired
    public UserServiceImpl(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

1.3@Autowired标注在方法上，该方法的参数会被注入，并且这个方法会在构造器执行之后被Spring自动调用
典型的例子是标注在Setter方法上，标注了才有Setter注入（使用XML和@Bean可以使用autowire属性直接指定开启Setter注入，这里的这种方式需要为Setter方法一个一个添加注解）。
```
@Service
public class UserServiceImpl implements UserService {

    private UserDao userDao;

    @Autowired
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

1.4 @Autowired标注也可以标注在方法的参数上，但是这个特性只在spring-test模块下的Junit Jupiter中支持

**2、@Qualifier注解**
@Autowired注解根据类型byType注入，当容器中存在多个该类型的对象时会报错，于是就需要@Qualifier指定id根据id注入。加上@Qualifier后会直接根据id进行注入，找不到直接报错。
```
@Service
public class BookService {
    @Autowired
    `@Qualifier("bd")`
    private BookDao bookDao;
}
```
@Qualifier不仅可以加上字段上，还可以加在方法的参数上：
```
@Service
public class UserServiceImpl implements UserService {
    private UserDao userDao;

    @Autowired
    public void setUserDao(`@Qualifier("bd") UserDao userDao`) {
        this.userDao = userDao;
    }
}
```

**3、@Resource注入**
@Resource注解是JDK扩展包中的(JSR-250标准中制定的注解类型，JSR是Java规范提案） ，所以该注解是标准注解，更加具有通用性。@Resource注解属于JDK扩展包，所以不在JDK当中，需要额外引入以下依赖（如果是JDK8的话不需要额外引入依赖。高于JDK11或低于JDK8需要引入以下依赖。）：
```
<dependency>
    <groupId>jakarta.annotation</groupId>
    <artifactId>jakarta.annotation-api</artifactId>
    <version>2.1.1</version>
</dependency>
```
@Resource 和 @Autowired 作用一样，都是完成依赖注入的，差别主要是在容器中找对象的流程不同：

* @Resource注解默认先根据类型名首字母小写作为id找，然后再根据变量名作为id找，最后再根据类型找。
* @Autowired则是直接根据类型找。

注意上面的差异可能随着Spring的版本出现变化

`不管是@Resource 还是 @Autowired，只要用了@Qualifier注解，一律直接按id找，找不到直接报错。`

