---

Created at: 2024-04-02
Last updated at: 2024-04-06
Source URL: about:blank


---

# 2-@RequestMapping注解


**一、@RequestMapping注解**
@RequestMapping注解的功能和位置
功能：@RequestMapping注解的作用是将请求和处理请求的方法关联起来。
位置：

* @RequestMapping 标注在类上为所有方法指定一个基准路径。
* @RequestMapping 标注在方法上为方法指定一个访问路径，这个路径与方法名没有关系。

**1、 value属性**
value属性设置请求路径，是一个字符串类型的数组，表示能够匹配多个请求地址。
支持ant风格的模糊匹配路径：

* ? 替代任意一个字符
* \* 替代任意多个字符，或者是一层路径
* \*\* 替代多层路径

```
@RequestMapping("/handler?")
@RequestMapping("/handler*") //* 替代任意多个字符
@RequestMapping("/*/handler06")  //* 替代一层路径
@RequestMapping("/**/handler07")
```

路径中支持占位符，常用于RESTful风格的URL地址，使用@PathVariable注解将占位符所表示的数据赋值给控制器方法的形参：
```
@RequestMapping("/user/{id}")
public String pathVariableTest(@PathVariable("id") String id){
    System.out.println(id);
    return "success";
}
```

**2、 method属性**
method：限定请求方式，默认接受所有类型的请求。HTTP协议中的所有请求方式：GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS, TRACE。
对于处理指定请求方式的控制器方法，SpringMVC中提供了方便的@RequestMapping派生注解：

* 处理get请求的映射-->**@GetMapping**
* 处理post请求的映射-->**@PostMapping**
* 处理put请求的映射-->@PutMapping
* 处理delete请求的映射-->@DeleteMapping

若当前请求的请求地址满足请求映射的value属性，但是请求方式不满足method属性，则报错405，比如405：Request method 'POST' not supported。

**3、 params属性（了解）**
params：规定请求参数，只响应请求参数符合要求的请求。

* param1: 表示请求必须包含名为 param1 的请求参数。
* !param1: 表示请求不能包含名为 param1 的请求参数。
* param1 != value1: 表示请求包含名为 param1 的请求参数，但其值不能为 value1。
* {“param1=value1”, “param2”}: 请求必须包含名为 param1 和 param2 的两个请求参数，且 param1 参数的值必须为 value1。

```
@RequestMapping(value = "/handler02", params = {"username", "password!=123456"})
public String handler02(){
    return "success";
}
```
当不满足params属性，此时页面回报错400：Parameter conditions "username, password!=123456" not met for actual request parameters: username={admin}, password={123456}

**4、 headers属性（了解）**
headers：规定请求头，只响应请求头符合要求的请求，格式同params属性。

* "header"：要求请求必须携带header请求头信息
* "!header"：要求请求不能携带header请求头信息
* "header=value"：要求请求必须携带header请求头信息且header=value
* "header!=value"：要求请求必须携带header请求头信息且header!=value

当前请求满足@RequestMapping注解的value和method属性，但是不满足headers属性，此时页面显示404错误，即资源未找到。
```
@RequestMapping(value = "/handler03", headers = "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
public String handler03(){
    return "success";
}
```

**5、 consumes属性（了解）**
规定请求头中的Content-Type。

**6、 produces属性（了解）**
设置响应头的Content-Type。

