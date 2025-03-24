---

Created at: 2024-08-09
Last updated at: 2024-11-15
Source URL: https://spring.io/projects/spring-cloud-openfeign#overview


---

# 4-OpenFeign


Feign是一个声明式的Web客户端（Declarative REST Client）。前面使用RestTemplate需要拼串得到URL，调用也比较繁琐，OpenFeign采用接口调用的方式简化了RPC调用的方式，因为Fegin会动态创建接口的实现。
**一、基本使用**
1、引入Fegin的依赖
```
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
```
2、在主程序上使用@EnableFeignClients注解
```
@SpringBootApplication
@EnableFeignClients
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
3、声明远程调用的接口
@FeignClient中填被调用服务的名称
```
@FeignClient(value = "cloud-payment-service")
public interface PayFeignApi {
    /**
     * 按照主键记录查询支付流水信息
     */
    @GetMapping(value = "/pay/get/{id}")
    public ResultData getPayInfo(@PathVariable("id") Integer id);
    /**
     * `openfeign天然支持负载均衡演示`
     */
    @GetMapping(value = "/pay/get/info")
    public String mylb();
}
```
4、调用服务
```
@RestController
public class FeignTestController {
    @Resource
    private PayFeignApi payFeignApi;

    @RequestMapping("/feign/req1")
    public String req1() {
        ResultData resultData = payFeignApi.getPayInfo(1);
        System.out.println(resultData);
        return resultData.toString();
    }

    @RequestMapping("/feign/req2")
    public String req2() {
        String mylb = payFeignApi.mylb();
        System.out.println(mylb);
        return mylb;
    }
}
```
注意，和RestTemplate一样，如果被调用的服务如果返回500的http状态吗，那么在调用者这里会抛异常，也将返回500。默认情况下，‌Feign在遇到非2xx的HTTP状态码时，‌会抛出一个feign.FeignException。‌这个异常包含了响应的状态码、‌请求的方法、‌URL等信息，‌但可能不足以直接反映具体的业务错误。‌为了更灵活地处理异常，‌你可以实现一个自定义的ErrorDecoder。‌ErrorDecoder接口定义了一个decode方法，‌它接收一个Response对象，‌并根据响应的状态码和内容来决定是否抛出异常，‌以及抛出什么类型的异常。‌
5、最佳实践
对于多个模块都要调用的api接口，把feign接口声明写在common模块，如果仅在某个模块中调用，那就把feign接口声明写在自己所在的模块中。

**二、OpenFeign其他设置**
1、超时设置
```
spring:
  cloud:
    openfeign:
      client:
        config:
          #全局设置
          default:
            #连接超时时间
            connectTimeout: 3000
            #读取超时时间
            readTimeout: 3000
          #给某个服务单独设置超时设置
          cloud-payment-service:
            #连接超时时间
            connectTimeout: 5000
            #读取超时时间
            readTimeout: 5000
```
2、失败重试
默认没有重试，调用一次就结束，无论失败与否，可以设置重试策略：
```
@Configuration
public class FeignConfig {
    @Bean
    public Retryer myRetryer() {
        //return Retryer.NEVER_RETRY; //Feign默认配置是不走重试策略的
        //最大请求次数为3(1+2)，初始间隔时间为100ms，重试间最大间隔时间为1s
        return new Retryer.Default(100,1,3);
    }
}
```

