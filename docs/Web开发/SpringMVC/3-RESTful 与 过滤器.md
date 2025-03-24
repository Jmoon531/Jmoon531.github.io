---

Created at: 2024-04-06
Last updated at: 2024-05-25
Source URL: about:blank


---

# 3-RESTful 与 过滤器


**一、RESTful**
REST 风格提倡 URL 地址使用统一的风格设计，从前到后各个单词使用斜杠分开，不使用问号键值对方式携带请求参数，而是将要发送给服务器的数据作为 URL 地址的一部分，以保证整体风格的一致性。并使用请求方式明确意图：GET 用来获取资源，POST 用来新建资源，PUT 用来更新资源，DELETE 用来删除资源。

|     |     |     |
| --- | --- | --- |
| **操作** | **传统方式** | **REST风格** |
| 查询操作 | getUserById?id=1 | user/1-->get请求方式 |
| 保存操作 | saveUser | user-->post请求方式 |
| 删除操作 | deleteUser?id=1 | user/1-->delete请求方式 |
| 更新操作 | updateUser | user-->put请求方式 |

发送put和delete请求有两种方式：
方式一：POST请求携带请求参数\_method，服务器端配置过滤器org.springframework.web.filter.HiddenHttpMethodFilter，HiddenHttpMethodFilter会将请求的请求方式转换为请求参数\_method的值。
1、web.xml中配置HiddenHttpMethodFilter过滤器：
```
<filter>
    <filter-name>HiddenHttpMethodFilter</filter-name>
    <filter-class>org.springframework.web.filter.HiddenHttpMethodFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>HiddenHttpMethodFilter</filter-name>
    <url-pattern>/*</url-pattern> <!--拦截所有请求-->
</filter-mapping>
```
2、请求必须是POST且携带\_method参数（\_method不一定必须放在请求体中，也可以放在请求头的URL后面）：
表单：
```
<!-- 作用：通过超链接控制表单的提交，将post请求转换为delete请求 -->
<form id="delete_form" method="post">
    <!-- HiddenHttpMethodFilter要求：必须传输_method请求参数，并且值为最终的请求方式 -->
    `<input type="hidden" name="_method" value="delete"/>`
</form>
```
Ajax请求：
```
$.ajax({
    url:"${pageContext.request.contextPath}/emp/" + id,
    type:"POST",
    data:$("#empModal form").serialize() + "`&_method=PUT`",
    success:function (result) {
        // 请求成功后的回调函数
    }
});
```

HiddenHttpMethodFilter的核心逻辑在doFilterInternal方法中，其中的this.methodParam的值就是"\_method"：
```
protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
       throws ServletException, IOException {
    HttpServletRequest requestToUse = request;
    if ("POST".equals(request.getMethod()) && request.getAttribute(WebUtils.ERROR_EXCEPTION_ATTRIBUTE) == null) {
       String paramValue = request.getParameter(`this.methodParam`);
       if (StringUtils.hasLength(paramValue)) {
          String method = paramValue.toUpperCase(Locale.ENGLISH);
          if (ALLOWED_METHODS.contains(method)) {
             requestToUse = new HttpMethodRequestWrapper(request, method);
          }
       }
    }
    filterChain.doFilter(requestToUse, response);
}
```

方式二：使用Ajax直接发送put和delete请求，服务器端配置过滤器org.springframework.web.filter.HttpPutFormContentFilter
1、web.xml中配置HttpPutFormContentFilter过滤器：
```
<filter>
    <filter-name>httpPutFormContentFilter</filter-name>
    <filter-class>org.springframework.web.filter.HttpPutFormContentFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>httpPutFormContentFilter</filter-name>
    <url-pattern>/*</url-pattern>
</filter-mapping>
```
2、使用Ajax直接发送put和delete请求：
```
$.ajax({
    url:"${pageContext.request.contextPath}/emp/" + id,
    `type:"PUT",`
    data:$("#empModal form").serialize(),
    success:function (result) {
        // 请求成功后的回调函数
    }
});
```

```
$.ajax({
    url:"${pageContext.request.contextPath}/emp/" + id,
    type:"DELETE",
    data:$("#empModal form").serialize(),
    success:function (result) {
        // 请求成功后的回调函数
    }
});
```

**二、过滤器**
这里的过滤器指原生Servlet中的三大组件之一的过滤器，SpringMVC中提供了两种有用的过滤器，一个是前面处理 put和delete请求的过滤器；另外一个是解决字符编码的过滤器org.springframework.web.filter.CharacterEncodingFilter。
web.xml中配置CharacterEncodingFilter过滤器：
```
<filter>
  <filter-name>characterEncodingFilter</filter-name>
  <filter-class>org.springframework.web.filter.CharacterEncodingFilter</filter-class>
  <init-param>
    <param-name>encoding</param-name>
    <param-value>utf-8</param-value>
  </init-param>
  <init-param>
    <param-name>forceEncoding</param-name>
    <param-value>true</param-value>
  </init-param>
</filter>
<filter-mapping>
  <filter-name>characterEncodingFilter</filter-name>
  <url-pattern>/*</url-pattern>
</filter-mapping>
```
在web.xml中注册时，必须先注册CharacterEncodingFilter，再注册HiddenHttpMethodFilter，因为在 CharacterEncodingFilter 中通过 request.setCharacterEncoding(encoding) 方法设置字符集时，要求前面不能有任何获取请求参数的操作，否则设置编码无效，而 HiddenHttpMethodFilter需要获取请求方式String paramValue = request.getParameter(this.methodParam);。

CharacterEncodingFilter的核心逻辑在doFilterInternal方法中：
```
@Override
protected void doFilterInternal(
       HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
       throws ServletException, IOException {
    String encoding = getEncoding();
    if (encoding != null) {
       if (isForceRequestEncoding() || request.getCharacterEncoding() == null) {
          request.setCharacterEncoding(encoding);
       }
       if (isForceResponseEncoding()) {
          response.setCharacterEncoding(encoding);
       }
    }
    filterChain.doFilter(request, response);
}
```
<init-param>标签中设置的正是CharacterEncodingFilter的这三个实例变量的值：
```
private String encoding;
private boolean forceRequestEncoding = false;
private boolean forceResponseEncoding = false;
```
```
public void setEncoding(@Nullable String encoding) {
    this.encoding = encoding;
}
```
```
public void setForceEncoding(boolean forceEncoding) {
    this.forceRequestEncoding = forceEncoding;
    this.forceResponseEncoding = forceEncoding;
}
```

