---

Created at: 2024-03-19
Last updated at: 2024-03-21
Source URL: about:blank


---

# 2-XML配置Bean


**一、创建Bean**
**1、创建Bean**
id不能重复
```
<bean id="user01" class="pojo.User"></bean>
```
还可以创建ArrayList对象，但是是空的ArrayList对象，后面可以获取这个bean，然后往里add元素
```
<bean id="aList" class="java.util.ArrayList"></bean>
```

**2、依赖注入之setter注入**
```
<bean id="user01" class="pojo.User">
    <!-- property标签：通过组件类的setXxx()方法给组件对象设置属性 -->
    <!-- name属性：指定属性名（这个属性名是getXxx()、setXxx()方法定义的，和成员变量无关） -->
    <!-- value属性：指定属性值 -->
    <property name="id" value="1001"></property>
    <property name="name" value="张三"></property>
    <property name="age" value="23"></property>
    <property name="sex" value="男"></property>
</bean>
```

**3、依赖注入之构造器注入**
```
<bean id="user01" class="pojo.User">
    <constructor-arg value="1002"></constructor-arg>
    <constructor-arg value="李四"></constructor-arg>
    <constructor-arg value="33"></constructor-arg>
    <constructor-arg value="女"></constructor-arg>
</bean>
```
还可以创建Integer对象：
```
<bean id="aInt" class="java.lang.Integer">
  <constructor-arg value="111111"></constructor-arg>
</bean>
```
注意：
constructor-arg标签还有两个属性可以进一步描述构造器参数：
\* index属性：指定参数所在位置的索引（从0开始）
\* name属性：指定参数名
```
<bean id="stu04" class="pojo.Student">
  <constructor-arg name="name" value="mike"/>
  <constructor-arg name="id" value="03"/>
  <constructor-arg name="age" value="23"/>
</bean>

<bean id="stu05" class="pojo.Student">
  <constructor-arg value="bob" index="1"/>
  <constructor-arg value="04" index="0"/>
  <constructor-arg value="25" index="2"/>
</bean>
```

**4、为引用类型赋值**（依然使用的是property标签，**属于setter注入**，只不过与前面的基本数据类型或包装类型不一样）
4.1 引用外部bean
```
<bean id="person01" class="pojo.Person">
    <!-- ref表示引用外部的bean对象 -->
    <property name="cat" ref="cat"/>
    <!-- 级联属性赋值，修改了上面引用的cat的属性值-->
    <property name="cat.color" value="red"/>
</bean>
```

4.2 内部bean
```
<bean id="person01" class="pojo.Person">
    <!-- 给引用类型赋值 -->
    <property name="dog">
      <!-- 内部bean的id属性无效，无法通过id获取到内部bean -->
      <bean class="pojo.Dog">
        <property name="name" value="旺财"/>
        <property name="color" value="yellow"/>
      </bean>
    </property>
</bean>
```

4.3 为数组类型赋值
```
<bean id="person01" class="pojo.Person">
    <property name="hobbies">
        <array>
            <value>抽烟</value>
            <value>喝酒</value>
            <value>烫头</value>
        </array>
    </property>
</bean>
```

4.4 为集合类型属性赋值
```
<bean id="person01" class="pojo.Person">
    <property name="students">
        <list>
            <ref bean="studentOne"></ref>
            <ref bean="studentTwo"></ref>
            <bean class="pojo.Student">
                <property name="id" value="1001"></property>
                <property name="name" value="张三"></property>
                <property name="age" value="23"></property>
                <property name="sex" value="男"></property>
            </bean>
        </list>
    </property>
</bean>
```

4.5 为Map集合类型属性赋值
```
<bean id="person01" class="pojo.Person">
    <property name="map">
      <!-- 相当于 map = new LinkedHashMap<>(); -->
      <map>
        <entry key="key01" value="value01"/>
        <entry key="key02" value="10.3" value-type="java.lang.Double"/>
        <entry key="key03" value-ref="person01"/>
        <entry key="key04">
          <bean class="pojo.Book" c:name="红楼梦" c:author="曹雪芹" c:price="100.9"/>
        </entry>
      </map>
    </property>
</bean>
```

4.6 为Properties属性赋值
```
<bean id="person01" class="pojo.Person">
    <!-- 给properties属性赋值 -->
    <property name="properties">
      <!-- properties = new Properties(); -->
      <props>
        <prop key="username">root</prop>
        <prop key="password">123456</prop>
      </props>
    </property>
</bean>
```

4.7 为特殊值赋值
赋null值
```
<property name="name">
    <null />
</property>
```
xml实体
```
<!-- 小于号在XML文档中用来定义标签的开始，不能随便使用 -->
<!-- 解决方案一：使用XML实体来代替 -->
<property name="expression" value="a &lt; b"/>
```
CDATA节
```
<property name="expression">
    <!-- 解决方案二：使用CDATA节 -->
    <!-- CDATA中的C代表Character，是文本、字符的含义，CDATA就表示纯文本数据 -->
    <!-- XML解析器看到CDATA节就知道这里是纯文本，就不会当作XML标签或属性来解析 -->
    <!-- 所以CDATA节中写什么符号都随意 -->
    <value><![CDATA[a < b]]></value>
</property>
```

**5、命名空间**

* p名称空间(property)：通过setter方法赋值的快捷方式
* c名称空间(constructor)：通过构造器赋值的快捷方式
* util名称空间：创建集合类型的bean

```
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:p="http://www.springframework.org/schema/p"
       xmlns:c="http://www.springframework.org/schema/c"
       xmlns:util="http://www.springframework.org/schema/util"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       https://www.springframework.org/schema/beans/spring-beans.xsd
       http://www.springframework.org/schema/util
       https://www.springframework.org/schema/util/spring-util.xsd">

<!-- 导入p名称空间(property)，通过setter方法赋值的快捷方式 -->
<bean id="stu02" class="pojo.Student" p:id="05" p:name="jerry" p:age="20"/>

<!-- 导入c名称空间(constructor)，通过构造器赋值的快捷方式 -->
<bean id="stu06" class="pojo.Student" c:name="tom" c:id="6" c:age="25"/>

<!-- util名称空间创建集合类型的bean -->
<util:list id="stuList" value-type="pojo.Student" list-class="java.util.ArrayList">
  <ref bean="stu01"/>
  <ref bean="stu02"/>
  <ref bean="stu03"/>
  <ref bean="stu04"/>
  <ref bean="stu05"/>
  <ref bean="stu06"/>
</util:list>

<util:map id="map">
  <entry key="key01" value="value01"/>
</util:map>

<util:properties id="locale">
  <prop key="locale">zh_CN</prop>
</util:properties>

<util:set id="set">
  <value type="java.lang.Integer">100</value>
</util:set>

</beans>
```

**6、abstract属性创建一个模板bean**
通过abstract属性创建一个模板bean，通过继承实现bean配置信息的重用
```
<!-- abstract=true的bean只能被继承 -->
<bean id="person02" class="pojo.Person" abstract="true">
  <property name="name" value="张三"/>
  <property name="dog">
    <bean class="pojo.Dog" c:name="小黑" c:color="black"/>
  </property>
</bean>
<!-- 继承id=person02的bean的配置信息，只是继承配置信息-->
<bean id="person03" parent="person02"/>
```

**7、引用外部属性文件**
druid.properties文件
```
#username是spring中的一个关键字，所以引用外部属性配置文件时，用${username}会冲突，于是改名为jdbc.username
jdbc.driverClassName=com.mysql.cj.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/test?serverTimezone=UTC&characterEncoding=utf-8&rewriteBatchedStatements=true
jdbc.username=root
jdbc.password=079335
```
需要导入context名称空间
```
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd http://www.springframework.org/schema/context https://www.springframework.org/schema/context/spring-context.xsd">

  <!-- 需要导入context名称空间 -->
  <context:property-placeholder location="classpath:druid.properties"/>
  <!-- 单例的数据库连接池 -->
  <bean class="com.alibaba.druid.pool.DruidDataSource" id="druidDataSource">
    <!-- username是spring中的一个关键字，所以引用外部属性配置文件时，用${username}会冲突，于是改名为jdbc.username-->
    <property name="username" value="${jdbc.username}"/>
    <property name="password" value="${jdbc.password}"/>
    <!--    <property name="url"><value><![CDATA[ jdbc:mysql://localhost:3306/test?serverTimezone=UTC&characterEncoding=utf-8]]></value></property>-->
    <property name="url" value="${jdbc.url}"/>
    <property name="driverClassName" value="${jdbc.driverClassName}"/>
  </bean>

</beans>
```

**8、bean的作用域**
通过配置bean标签的scope属性来指定bean的作用域范围，各取值含义参加下表：

|     |     |     |
| --- | --- | --- |
| **取值** | **含义** | **创建对象的时机** |
| singleton（默认） | 在IOC容器中，这个bean的对象始终为单实例 | IOC容器初始化时 |
| prototype | 这个bean在IOC容器中有多个实例 | 获取bean时 |

如果是在WebApplicationContext环境下还会有另外几个作用域（但不常用）：

|     |     |
| --- | --- |
| 取值  | 含义  |
| request | 在一个请求范围内有效 |
| session | 在一个会话范围内有效 |

```
<!--  bean的作用域：
        ① singleton（默认）：单例，容器创建时创建，任何时候获取的都是同一个实例
        ② prototype：多实例，容器创建时不创建，等到获取时才创建，每次获取都会创建一个新的实例
        以下在web应用中用，但是实际上基本不用
        ③ request ④ session ⑤ application ⑥ websocket
-->
<bean id="book04" class="pojo.Book" p:name="book04" scope="singleton"/>
<bean id="book05" class="pojo.Book" p:name="book05" scope="prototype"/>
```

**9、自动装配**
使用bean标签的autowire属性设置自动装配效果

* byType：根据类型匹配IOC容器中的某个兼容类型的bean，为属性自动赋值。若在IOC中，没有任何一个兼容类型的bean能够为属性赋值，则该属性不装配，即值为默认值null；若在IOC中，有多个兼容类型的bean能够为属性赋值，则抛出异常NoUniqueBeanDefinitionException。
* byName：将自动装配的属性的属性名，作为bean的id在IOC容器中匹配相对应的bean进行赋值。

这里的自动装配其实就是Setter注入
```
<!--
  autowire自动装配，默认不自动装配（xml配置的自动装配基本不用）：
      1.byName: 按照属性名作为id去容器中找对象然后赋值，相当于bean.getBean("cat")，找不到不会抛异常，而是赋null
      2.byType: 通过属性名的类型去容器中找对象然后赋值，相当于bean.getBean(cat.class)，如果容器中有多个就抛异常，没找到装配null
-->
<bean class="pojo.Person" id="person" autowire="constructor"/>
```

**10、通过工厂方法创建bean**
10.1 通过静态工厂方法创建的bean
```
/**
* Book的静态工厂，调用 getBook() 方法之前不需要创建 BookInstanceFactory 的对象，直接BookStaticFactory.getBook()即可
*/
public class BookStaticFactory {
    public static Book getBook(String name){
        System.out.println("BookStaticFactory 正在创建 Book");
        Book book = new Book();
        book.setName(name);
        book.setAuthor("anonymous");
        book.setPrice(99.9);
        return book;
    }
}
```
```
<!--  静态工厂创建Book对象-->
<bean id="book11" class="pojo.factory.BookStaticFactory" factory-method="getBook">
  <constructor-arg value="三国演义"/>
</bean>
```

10.2 通过实例工厂创建Book对象
```
/**
* Book的实例工厂，调用 getBook() 方法之前需要创建 BookInstanceFactory 的对象
*/
public class BookInstanceFactory {
    {
        System.out.println("实例工厂被创建了");
    }
    public Book getBook(String name){
        System.out.println("BookInstanceFactory 正在创建 Book");
        Book book = new Book();
        book.setName(name);
        book.setAuthor("anonymous");
        book.setPrice(99.9);
        return book;
    }
}
```
```
<!--  实例工厂创建Book对象-->
<bean id="bookInstanceFactory" class="pojo.factory.BookInstanceFactory"/>
<bean id="book12" class="pojo.Book" scope="prototype" factory-bean="bookInstanceFactory" factory-method="getBook">
  <constructor-arg value="一只特立独行的猪"/>
</bean>
```

10.3 通过FactoryBean创建Book对象
FactoryBean是Spring提供的一种整合第三方框架的常用机制。和普通的bean不同，配置一个FactoryBean类型的bean，在获取bean的时候得到的并不是class属性中配置的这个类的对象，而是getObject()方法的返回值。通过这种机制，Spring可以帮我们把复杂组件创建的详细过程和繁琐细节都屏蔽起来，只把最简洁的使用界面展示给我们。（比如整合Mybatis时，Spring就是通过FactoryBean机制来帮我们创建SqlSessionFactory对象的。）
```
/**
* FactoryBean接口是Spring的工厂接口，继承该接口的类在注册（注册即在xml配置）后，spring会默认调用该类的方法创建对象
*/
public class MyFactoryBeanImpl implements FactoryBean<Book> {
    /**
     * 工厂方法
     * @return 创建的对象
     * @throws Exception
     */
    @Override
    public Book getObject() throws Exception {
        Book book = new Book();
        book.setName(UUID.randomUUID().toString().substring(0, 8));
        book.setAuthor("anonymous");
        book.setPrice(39.3);
        return book;
    }
    @Override
    public Class<?> getObjectType() {
        return Book.class;
    }
    /**
     * 接口的默认实现是true，表示单例
     * 使用FactoryBean创建对象，不管是单例还是多例，都是在获取实例的时侯创建对象
     * @return
     */
    @Override
    public boolean isSingleton() {
        return true;
    }
}
```
```
<!-- MyFactoryBeanImpl是继承Spring的FactoryBean接口的工厂类，
ioc容器会自动调用MyFactoryBeanImpl类的getObject方法来创建bean,
不管该bean是单例的还是多例的，都是在获取时才创建对象-->
<bean id="book13" class="pojo.factory.MyFactoryBeanImpl"/>
```

**11、bean生命周期**
生命周期过程：

1. bean对象创建（调用无参构造器）
2. 给bean对象设置属性
3. bean的后置处理器（初始化之前）
4. bean对象初始化（需在配置bean时指定初始化方法）
5. bean的后置处理器（初始化之后）
6. 使用bean对象
7. bean对象销毁（需在配置bean时指定销毁方法）
8. IOC容器关闭

11.1 初始化方法 和 销毁方法
```
<!-- 不能使用实例工厂和实现FactoryBean的工厂来创建带有初始化方法和销毁方法的bean。
带有初始化方法和销毁方法的 单例bean 是和ioc容器一起创建和销毁的
如果是多实例的bean，则是在bean创建后调用init-method，在容器关闭时不调用destroy-method-->
<bean id="book21" class="pojo.Book" `init-method="bookInit" destroy-method="bookDestroy"`
      p:name="Spring编程"/>
```

11.2 bean的后置处理器
bean的后置处理器会在生命周期的初始化前后添加额外的操作，需要实现BeanPostProcessor接口，且配置到IOC容器中，需要注意的是，bean后置处理器不是单独针对某一个bean生效，而是针对IOC容器中所有bean都会执行。
创建bean的后置处理器：
```
public class BookPostProcessor implements BeanPostProcessor {
    /**
     *初始化之前调用
     */
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        System.out.println(beanName + "的postProcess Before Initialization调用了");
        return bean;
    }
    /**
     *初始化之后调用
     */
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        System.out.println(beanName + "的postProcess After Initialization调用了");
        return bean;
    }
}
```
```
<!-- Bean后置处理器BeanPostProcessor的作用是在init-method前后执行方法,
不过无论有没有init-method方法，后置处理器都会执行-->
<bean class="pojo.beanPostProcessor.BookPostProcessor" id="bookPostProcessor"/>
```

**二、获取Bean**
使用getBean()方法从IOC容器中获取Bean
1、根据id获取
```
public static void mian() {
    ApplicationContext applicationContext = `new ClassPathXmlApplicationContext("pojo.xml", "dao.xml", "service.xml"); //根据配置文件往IOC容器中创建Bean，可以指定多个配置文件`
    User user01 = `(User) applicationContext.getBean("user01"); //需要强转`
    System.out.println(user01);
}
```

拓展：
创建ApplicationContext时可以指定多个配置文件，也可以把配置文件集中到一个配置文件中，然后创建ApplicationContext时指定这个配置文件：
```
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
 `<import resource="di01.xml"/>`
  <import resource="ioc04.xml"/>
  <import resource="dataSource.xml"/>
</beans>
```

2、根据类型获取
注意：

* 当根据类型获取bean时，要求IOC容器中指定类型的bean有且只能有一个
* 可以根据接口类型获取实现类的对象，但是接口在容器中不能有多个实现类对象

```
public static void mian() {
    ApplicationContext applicationContext = new ClassPathXmlApplicationContext("pojo.xml", "dao.xml", "service.xml");
    User user01 = applicationContext.getBean(User.class); //不需要强转，但是容器中指定类型的bean有且只能有一个
    System.out.println(user01);
}
```

3、根据id和类型
```
public static void mian() {
    ApplicationContext applicationContext = new ClassPathXmlApplicationContext("pojo.xml", "dao.xml", "service.xml");
    User user01 = applicationContext.getBean("user01", User.class); //具备上述两种方式的优点
    System.out.println(user01);
}
```

