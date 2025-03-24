---

Created at: 2024-08-06
Last updated at: 2024-08-09
Source URL: https://www.cnblogs.com/54chensongxia/p/11414923.html


---

# 1-RestTemplate


Spring 提供了一个Http Rest API 的客户端，RestTemplate提供了不同封装程度的接口让我们非常方便地进行 Rest API 调用。
1、创建RestTemplate
```
@Bean
public RestTemplate restTemplate(ClientHttpRequestFactory factory) {
    RestTemplate restTemplate = new RestTemplate(factory);
    return restTemplate;
}

@Bean
public ClientHttpRequestFactory simpleClientHttpRequestFactory() {
    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
    factory.setReadTimeout(5000);
    factory.setConnectTimeout(15000);
    // 设置代理
    //factory.setProxy(null);
    return factory;
}
```

2、getForObject()、getForEntity()、postForObject()、postForEntity()，这类方法是常规的 Rest API（GET、POST、DELETE 等）方法调用。

```
Map<String, String> vars = Collections.singletonMap("hotel", "42");
// 通过 GET 方式调用，返回一个 String 值，还可以给 URL 变量设置值（也可通过 uriTemplateHandler 这个属性自定义）
String result = restTemplate.getForObject("https://example.com/hotels/{hotel}/rooms/{hotel}", String.class, vars);

String url = "http://127.0.0.1:8080/hello";
JSONObject param = new JSONObject();
//restTemplate 会根据 params 的具体类型，调用合适的 HttpMessageConvert 将请求参数写到请求体 body 中，并在请求头中添加合适的 content-type；
// 也会根据 responseType 的类型（本列子中是 JSONObject），设置 head 中的 accept 字段，当响应返回的时候再调用合适的 HttpMessageConvert 进行响应转换
ResponseEntity<JSONObject> responseEntity=restTemplate.postForEntity(url,params,JSONObject.class);
int statusCodeValue = responseEntity.getStatusCodeValue();
HttpHeaders headers = responseEntity.getHeaders();
JSONObject body = responseEntity.getBody();
```

3、exchange()，接收一个 RequestEntity 参数，可以自己设置 HTTP method，URL，headers 和 body，返回 ResponseEntity。
```
UriComponents uriComponents = UriComponentsBuilder.fromHttpUrl("127.0.0.1:8080").path("/test").build(true);
URI uri = uriComponents.toUri();
RequestEntity<JSONObject> requestEntity = RequestEntity.post(uri).
                // 添加 cookie(这边有个问题，假如我们要设置 cookie 的生命周期，作用域等参数我们要怎么操作)
                header(HttpHeaders.COOKIE,"key1=value1").
                // 添加 header
                header(("MyRequestHeader", "MyValue")
                accept(MediaType.APPLICATION_JSON).
                contentType(MediaType.APPLICATION_JSON).
                body(requestParam);
ResponseEntity<JSONObject> responseEntity = restTemplate.exchange(requestEntity,JSONObject.class);
// 响应结果
JSONObject responseEntityBody = responseEntity.getBody();
```

参考： [RestTemplate 最详解 - 程序员自由之路 - 博客园 (cnblogs.com)](https://www.cnblogs.com/54chensongxia/p/11414923.html)

