---

Created at: 2024-04-06
Last updated at: 2024-04-07
Source URL: about:blank


---

# 11-SpringMVC的执行流程


**一、DispatcherServlet初始化流程**
DispatcherServlet本身就是一个Servlet，遵循Servlet的初始化流程。
![img005.png](./_resources/11-SpringMVC的执行流程.resources/img005.png)
HttpServletBean的init()方法
```
public final void init() throws ServletException {
   // Set bean properties from init parameters.
//初始化参数比如SpringMVC的配置文件contextConfigLocation参数在ServletConfig中
   PropertyValues pvs = new ServletConfigPropertyValues(`getServletConfig()`, this.requiredProperties);
   if (!pvs.isEmpty()) {
      try {
         BeanWrapper bw = PropertyAccessorFactory.forBeanPropertyAccess(this);
         ResourceLoader resourceLoader = new ServletContextResourceLoader(getServletContext());
         bw.registerCustomEditor(Resource.class, new ResourceEditor(resourceLoader, getEnvironment()));
         initBeanWrapper(bw);
         bw.setPropertyValues(pvs, true);
      }
      catch (BeansException ex) {
         if (logger.isErrorEnabled()) {
            logger.error("Failed to set bean properties on servlet '" + getServletName() + "'", ex);
         }
         throw ex;
      }
   }
   // Let subclasses do whatever initialization they like.
   initServletBean();
}
```
FrameworkServlet的initServletBean方法
```
protected final void initServletBean() throws ServletException {
    getServletContext().log("Initializing Spring " + getClass().getSimpleName() + " '" + getServletName() + "'");
    if (logger.isInfoEnabled()) {
       logger.info("Initializing Servlet '" + getServletName() + "'");
    }
    long startTime = System.currentTimeMillis();

    try {
`//创建IOC容器`
       `this.webApplicationContext = initWebApplicationContext();` 
       initFrameworkServlet();
    }
    catch (ServletException | RuntimeException ex) {
       logger.error("Context initialization failed", ex);
       throw ex;

    if (logger.isDebugEnabled()) {
       String value = this.enableLoggingRequestDetails ?
             "shown which may lead to unsafe logging of potentially sensitive data" :
             "masked to prevent unsafe logging of potentially sensitive data";
       logger.debug("enableLoggingRequestDetails='" + this.enableLoggingRequestDetails +
             "': request parameters and headers will be " + value);
    }

    if (logger.isInfoEnabled()) {
       logger.info("Completed initialization in " + (System.currentTimeMillis() - startTime) + " ms");
    }
}
```
FrameworkServlet的initWebApplicationContext方法
```
protected WebApplicationContext initWebApplicationContext() {
    WebApplicationContext rootContext =
          WebApplicationContextUtils.getWebApplicationContext(getServletContext());
    WebApplicationContext wac = null;

    if (this.webApplicationContext != null) {
       // A context instance was injected at construction time -> use it
       wac = this.webApplicationContext;
       if (wac instanceof ConfigurableWebApplicationContext) {
          ConfigurableWebApplicationContext cwac = (ConfigurableWebApplicationContext) wac;
          if (!cwac.isActive()) {
             // The context has not yet been refreshed -> provide services such as
             // setting the parent context, setting the application context id, etc
             if (cwac.getParent() == null) {
                // The context instance was injected without an explicit parent -> set
                // the root application context (if any; may be null) as the parent
                cwac.setParent(rootContext);
             }
             configureAndRefreshWebApplicationContext(cwac);
          }
       }
    }
    if (wac == null) {
       // No context instance was injected at construction time -> see if one
       // has been registered in the servlet context. If one exists, it is assumed
       // that the parent context (if any) has already been set and that the
       // user has performed any initialization such as setting the context id
       wac = findWebApplicationContext();
    }
    if (wac == null) {
       // No context instance is defined for this servlet -> create a local one
`//创建IOC容器`
    `wac = createWebApplicationContext(rootContext);`
    }

    if (!this.refreshEventReceived) {
       // Either the context is not a ConfigurableApplicationContext with refresh
       // support or the context injected at construction time had already been
       // refreshed -> trigger initial onRefresh manually here.
       synchronized (this.onRefreshMonitor) {
`//等IOC容器创建完成之后刷新DispatcherServlet的实例变量`
 `onRefresh(wac);`
       }
    }

    if (this.publishContext) {
       // Publish the context as a servlet context attribute.
       String attrName = getServletContextAttributeName();
       getServletContext().setAttribute(attrName, wac);
    }

    return wac;
}
```
FrameworkServlet的createWebApplicationContext方法
```
protected WebApplicationContext createWebApplicationContext(@Nullable ApplicationContext parent) {
    Class<?> contextClass = getContextClass();
    if (!ConfigurableWebApplicationContext.class.isAssignableFrom(contextClass)) {
       throw new ApplicationContextException(
             "Fatal initialization error in servlet with name '" + getServletName() +
             "': custom WebApplicationContext class [" + contextClass.getName() +
             "] is not of type ConfigurableWebApplicationContext");
    }
`//实例化IOC容器，其中的Bean还没有被创建`
 `ConfigurableWebApplicationContext wac =`
 `(ConfigurableWebApplicationContext) BeanUtils.instantiateClass(contextClass);`

    wac.setEnvironment(getEnvironment());
`//与Spring的IOC合并`
 `wac.setParent(parent);`
`//SpringMVC配置文件的位置`
 `String configLocation = getContextConfigLocation();`
    if (configLocation != null) {
       wac.setConfigLocation(configLocation);
    }
`//创建并初始化Bean`
 `configureAndRefreshWebApplicationContext(wac);`

    return wac;
}
```
FrameworkServlet的configureAndRefreshWebApplicationContext方法
```
protected void configureAndRefreshWebApplicationContext(ConfigurableWebApplicationContext wac) {
    if (ObjectUtils.identityToString(wac).equals(wac.getId())) {
       // The application context id is still set to its original default value
       // -> assign a more useful id based on available information
       if (this.contextId != null) {
          wac.setId(this.contextId);
       }
       else {
          // Generate default id...
          wac.setId(ConfigurableWebApplicationContext.APPLICATION_CONTEXT_ID_PREFIX +
                ObjectUtils.getDisplayString(getServletContext().getContextPath()) + '/' + getServletName());
       }
    }

`//往IOC容器里添加ServletContext对象、ServletConfig对象等，这就是Web的IOC容器与Spring的IOC容器最大区别`
 `wac.setServletContext(getServletContext());`
 `wac.setServletConfig(getServletConfig());`
 `wac.setNamespace(getNamespace());`
 `wac.addApplicationListener(new SourceFilteringListener(wac, new ContextRefreshListener()));`

    // The wac environment's #initPropertySources will be called in any case when the context
    // is refreshed; do it eagerly here to ensure servlet property sources are in place for
    // use in any post-processing or initialization that occurs below prior to #refresh
    ConfigurableEnvironment env = wac.getEnvironment();
    if (env instanceof ConfigurableWebEnvironment) {
       ((ConfigurableWebEnvironment) env).initPropertySources(getServletContext(), getServletConfig());
    }

    postProcessWebApplicationContext(wac);
    applyInitializers(wac);
`////创建并初始化Bean`
 `wac.refresh();`
}
```
DispatcherServlet的onRefresh方法负责给从容器中找到九大组件然后给实例变量赋值
```
protected void onRefresh(ApplicationContext context) {
    initStrategies(context);
}

protected void initStrategies(ApplicationContext context) {
    initMultipartResolver(context);
    initLocaleResolver(context);
    initThemeResolver(context);
    initHandlerMappings(context);
    initHandlerAdapters(context);
    initHandlerExceptionResolvers(context);
    initRequestToViewNameTranslator(context);
    initViewResolvers(context);
    initFlashMapManager(context);
}
```
比如initMultipartResolver方法给multipartResolver赋值
```
private void initMultipartResolver(ApplicationContext context) {
    try {
       this.multipartResolver = context.getBean(MULTIPART_RESOLVER_BEAN_NAME, MultipartResolver.class);
       if (logger.isTraceEnabled()) {
          logger.trace("Detected " + this.multipartResolver);
       }
       else if (logger.isDebugEnabled()) {
          logger.debug("Detected " + this.multipartResolver.getClass().getSimpleName());
       }
    }
    catch (NoSuchBeanDefinitionException ex) {
       // Default is no multipart resolver.
       this.multipartResolver = null;
       if (logger.isTraceEnabled()) {
          logger.trace("No MultipartResolver '" + MULTIPART_RESOLVER_BEAN_NAME + "' declared");
       }
    }
}
```

**二、DispatcherServlet的执行流程**
Servlet的service方法最后会执行到DispatcherServlet的doDispatch方法
```
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
    HttpServletRequest processedRequest = request;
`//处理器执行链，包括三个实例变量：HandlerMethod handler、 List<HandlerInterceptor> interceptorList、int interceptorIndex = -1;`
`//作用是，调用目标方法执行 和 调用拦截器执行`
 `HandlerExecutionChain mappedHandler = null;`
    boolean multipartRequestParsed = false;
    WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);

    try {
 `ModelAndView mv = null;`
       Exception dispatchException = null;

       try {
          processedRequest = checkMultipart(request);
          multipartRequestParsed = (processedRequest != request);

          // Determine handler for the current request.
`//从HandlerMapping中找到请求对应的HandlerExecutionCha``in，HandlerMapping``的作用就是保存请求与Controller方法的映射关系`
 `mappedHandler = getHandler(processedRequest);`
          if (mappedHandler == null) {
             noHandlerFound(processedRequest, response);
             return;
          }

`//找到HandlerMethod对应的处理器适配器，最常见的是RequestMappingHandlerAdapter`
 `// Determine handler adapter for the current request.`
 `HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());`

          // Process last-modified header, if supported by the handler.
          String method = request.getMethod();
          boolean isGet = "GET".equals(method);
          if (isGet || "HEAD".equals(method)) {
             long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
             if (new ServletWebRequest(request, response).checkNotModified(lastModified) && isGet) {
                return;
             }
          }

`//通过处理器执行链调用拦截器的preHandle方法`
 `if (!mappedHandler.applyPreHandle(processedRequest, response)) {`
 `return;`
 `}`

`//核心步骤，通过处理器适配器调用目标方法，核心是反射调用目标方法，关键解决的问题是数据绑定，即如何为控制器方法的参数赋值，比如将请求参数转换成Jav``a对象（参数是否标有注解``）、``原生Ser``vlet对象赋值、从Request域或者Session域中获取值、Model对象赋值等。`
 `// Actually invoke the handler.`
 `mv = ha.handle(processedRequest, response, mappedHandler.getHandler());`

          if (asyncManager.isConcurrentHandlingStarted()) {
             return;
          }

          applyDefaultViewName(processedRequest, mv);
`//通过处理器执行链调用拦截器的postHandle方法`
 `mappedHandler.applyPostHandle(processedRequest, response, mv);`
       }
       catch (Exception ex) {
          dispatchException = ex;
       }
       catch (Throwable err) {
          // As of 4.3, we're processing Errors thrown from handler methods as well,
          // making them available for @ExceptionHandler methods and other scenarios.
          dispatchException = new NestedServletException("Handler dispatch failed", err);
       }
`//通过ModelAndView渲染视图`
 `processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);`
    }
    catch (Exception ex) {
`//通过处理器执行链调用拦截器的afterCompletion方法`
 `triggerAfterCompletion(processedRequest, response, mappedHandler, ex);`
    }
    catch (Throwable err) {
`//通过处理器执行链调用拦截器的afterCompletion方法`
 `triggerAfterCompletion(processedRequest, response, mappedHandler,`
 `new NestedServletException("Handler processing failed", err));`
    }
    finally {
       if (asyncManager.isConcurrentHandlingStarted()) {
          // Instead of postHandle and afterCompletion
          if (mappedHandler != null) {
             mappedHandler.applyAfterConcurrentHandlingStarted(processedRequest, response);
          }
       }
       else {
          // Clean up any resources used by a multipart request.
          if (multipartRequestParsed) {
             cleanupMultipart(processedRequest);
          }
       }
    }
}
```
从HandlerMapping中找到请求URL对应的HandlerExecutionChain（每次请求都会创建一个新的HandlerExecutionChain对象）。HandlerMapping的作用就是保存请求与Controller方法的映射关系，HandlerMapping最常见的实现类是RequestMappingHandlerMapping。
```
protected HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {
    if (this.handlerMappings != null) {
       for (HandlerMapping mapping : this.handlerMappings) {
          HandlerExecutionChain handler = mapping.getHandler(request);
          if (handler != null) {
             return handler;
          }
       }
    }
    return null;
}
```

总结：
doDispatcher涉及的核心组件有：
1、HandlerExecutionChain，处理器执行链，包括处理器方法对象和拦截器列表，简化模型如下：
```
public class HandlerExecutionChain {
    /**
     * 处理器方法：实际上底层对象是 HandlerMethod对象。
     */
    private Object handler;
    /**
     * 本次请求需要执行的拦截器
     */
    private List<HandlerInterceptor> interceptors;
    /**
     * 当前拦截器执行到哪个拦截器了，当前拦截器的下标
     */
    private int interceptorIndex = -1;

    boolean applyPreHandle(HttpServletRequest request, HttpServletResponse response) throws Exception {}
    public void applyPostHandle(HttpServletRequest request, HttpServletResponse response, ModelAndView mv) throws Exception {}
    public void triggerAfterCompletion(HttpServletRequest request, HttpServletResponse response, Object o) throws Exception {}
}
```
2、HandlerMapping，处理器映射器，通过请求拿到对应的处理器执行链，简化模型如下：
```
public class RequestMappingHandlerMapping implements HandlerMapping {
    /**
     * 处理器映射器，主要就是通过以下的map集合进行映射，以便通过请求拿到对应的控制器方法对象，最后与拦截器一起封装成处理器执行链返回。
     * key是：请求信息，RequestMappingInfo，包括请求URL和请求方式
     * value是：该请求对应要执行的处理器方法对象，可简单看作是java.lang.reflect.Method对象
     */
    private Map<RequestMappingInfo, HandlerMethod> map;

    //找到请求对应的HandlerExecutionChain
    @Override
    public HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {}
}
```
3、HandlerMethod，处理器方法，方便通过反射调用，简化模型如下：
```
public class HandlerMethod {
    /**
     * 控制器对象，Controller对象
     */
    private Object bean;
    /**
     * 控制器方法，Controller的方法，java.lang.reflect.Method对象
     */
    private Method method;
}
```
4、HandlerAdapter，处理器适配器，负责调用控制器方法，核心是反射调用目标方法，关键解决的问题是数据绑定，即如何为控制器方法的参数赋值，比如将请求参数转换成Java对象（参数是否标有注解）、原生Servlet对象赋值、从Request域或者Session域中获取值、Model对象赋值等，简化模型如下：
```
//HandlerMethod对应的处理器适配器HandlerAdapter
public class RequestMappingHandlerAdapter implements HandlerAdapter {
    //调用处理器方法（底层会真正的调用处理器方法，执行核心业务。）
    @Override
    public ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {}
}
```
5、ViewResolver，视图解析器，将viewName转换为View对象，简化模型如下：
```
public class InternalResourceViewResolver implements ViewResolver {
    private String prefix;
    private String suffix;
    //视图解析，将viewName转换为View对象。
    View resolveViewName(String viewName, Locale locale) throws Exception{}
}
```
6、View，视图，简化模型如下：
```
public class InternalResourceView implements View {
    /**
     * 响应的内容类型
     */
    private String contentType;
    /**
     * 获取内容类型
     */
    String getContentType();
    /**
     * 渲染
     */
    void render(Map<String, ?> model, HttpServletRequest request, HttpServletResponse response) throws Exception;
}
```
7、ModelAndView，简化模型如下：
```
public class ModelAndView {
    /** View instance or view name String. */
    @Nullable
    private Object view;
    /** Model Map. */
    @Nullable
    private ModelMap model;
    /** Optional HTTP status for the response. */
    @Nullable
    private HttpStatus status;
}
```

