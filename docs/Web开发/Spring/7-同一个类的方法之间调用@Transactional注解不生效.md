---

Created at: 2024-03-27
Last updated at: 2025-03-10
Source URL: https://www.jianshu.com/p/083605986c8f


---

# 7-同一个类的方法之间调用@Transactional注解不生效


在以下示例中，通过insertStudent()调用insert()方法会导致@Transactional注解不生效，原因是声明式事务基于AOP实现，只有通过代理类对象调用@Transactional方法才会开启事务。@Async注解也有相同的问题。
```
public class StudentServiceImpl implements StudentService {
    @Autowired
    private StudentMapper studentMapper;

    @Override
    public void insertStudent() {
        insert();
    }

    @Transactional(rollbackFor = Exception.class)
    public void insert() {
        StudentDO studentDO = new StudentDO();
        studentDO.setName("小明");
        studentDO.setAge(22);
        studentMapper.insert(studentDO);
    }
}
```
注意：除了@Transactional，@Async同样需要代理类调用，异步才会生效。

解决方法的核心是拿到代理类对象之后再调用方法（参考：https://www.jianshu.com/p/083605986c8f）
方法一、自己@Autowired自己
```
@Service
public class StudentServiceImpl implements StudentService {
    @Autowired
    private StudentMapper studentMapper;
    @Autowired
    private StudentService studentService;

    @Override
    public void insertStudent(){
        studentService.insert();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void insert() {
        StudentDO studentDO = new StudentDO();
        studentDO.setName("小明");
        studentDO.setAge(22);
        studentMapper.insert(studentDO);
    }
}
```

方法二、使用AopContext获取到当前代理类，需要在启动类加上@EnableAspectJAutoProxy(exposeProxy = true)。
```
@Service
public class StudentServiceImpl implements StudentService {
    @Autowired
    private StudentMapper studentMapper;

    @Override
    public void insertStudent(){
        getService().insert();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void insert() {
        StudentDO studentDO = new StudentDO();
        studentDO.setName("小明");
        studentDO.setAge(22);
        studentMapper.insert(studentDO);
    }

    /**
     * 通过AopContext获取代理类
     * @return StudentService代理类
     */
    private StudentService getService(){
        return Objects.nonNull(AopContext.currentProxy()) ? (StudentService)AopContext.currentProxy() : this;
    }
}
```
exposeProxy = true用于控制AOP框架公开代理，公开后才可以通过AopContext获取到当前代理类（默认情况下不会公开代理，因为会降低性能）。
注意：不能保证这种方式一定有效，使用@Async时，本方式可能失效。

方法三（推荐）、通过spring上下文获取到当前代理类：
当一个类实现ApplicationContextAware接口后，就可以方便的获得ApplicationContext中的所有bean。
```
@Component
public class SpringBeanUtil implements ApplicationContextAware {

    private static ApplicationContext applicationContext;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }

    /**
     * 通过class获取Bean
     */
    public static <T> T getBean(Class<T> clazz) {
        return applicationContext.getBean(clazz);
    }
}
```
```
@Service
public class StudentServiceImpl implements StudentService {
    @Autowired
    private StudentMapper studentMapper;

    @Override
    public void insertStudent(){
        StudentService bean = SpringBeanUtil.getBean(StudentService.class);
        if (null != bean) {
            bean.insert();
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void insert() {
        StudentDO studentDO = new StudentDO();
        studentDO.setName("小明");
        studentDO.setAge(22);
        studentMapper.insert(studentDO);
    }
}
```

