---

Created at: 2024-11-15
Last updated at: 2025-03-10
Source URL: https://juejin.cn/post/7176123079813726265


---

# 6-Micrometer Tracing + Zipkin


Micrometer是一个分布式系统监控工具，其有三大可观测性支柱：Metrics、Tracing、Logging，Tracing只是其中一个用于全链路追踪的门面，Zipkin就是这个门面的实现，并提供了可视化界面。

Micrometer Tracing主要术语：

* Trace id：整个调用链使用同一个Trace id
* Span id：每到一处生成一个Span id，并把上游传递下来的Span id、此次生成的Span id 以及 Trace id上报，通过Trace id、Span id、parent Span id就可以把整条调用链可视化了。

Micrometer是无侵入的，使用方式很简单：
1、引入Micrometer依赖
2、下载Zipkin
3、启动Zipkin，访问http://localhost:9411/zipkin/

同类型的产品还有：SkyWalking、PinPoint

SkyWalking：[40 张图搞懂分布式日志追踪，强大的traceId](https://mp.weixin.qq.com/s/_PcT6GpR0snzZQNNe6r1aw)

