# Gala-anteater

## Background

Gala-anteater 是一款时序数据的异常检测平台，它主要涵盖时序数据预处理、异常点发现、以及异常上报等功能。基于线下预训练、线上模型的增量学习与模型更新，能够很好的适应于多种时序数据类型。

## Quickstart Guid

* 项目依赖
  该项目依赖于Kafka和Prometheus，请预先安装！

* Docker镜像安装

  请在工程`./gala-anteater`目录下，执行下面的命令，将`gala-anteater`工程文件打包成Docker镜像。
  
  ```docker build -f Dockerfile -t gala-anteater:1.0.0 .```

* Docker镜像运行

  执行下面的命令，运行Docker镜像，请提供对应的Kakfa和Prometheus的server ip和port！

  ```docker run -d --env kafka_server={kafka_server} --env kafka_port={kafka_port} --env prometheus_server={prometheus_server} --env prometheus_port={prometheus_port} -it gala-anteater:1.0.0```

* 日志文件

  该工程生成的日志文件存储在`./gala-anteater/logs/`文件夹中!

* 运行结果
  
  如果检测到异常，会将异常结构输出到`Kafka`中，指定的`Topic`为：`gala_anteater_hybrid_model`，你也可以在`./cnfiguration/`中看到具体配置

* 故障注入

  为了方便该工程的测试，可以主动注入故障，进行测试用例模拟。此处采用[chaosblade](https://github.com/chaosblade-io/chaosblade)工具，进行故障注入，这里是它的[指导文档](https://chaosblade-io.gitbook.io/chaosblade-help-zh-cn/blade-create-network-delay)。例如执行下面的命令，进行网络延迟的故障注入：

     ```blade create network delay --time 80 --offset 90 --interface enp2s2 --local-port {port} --timeout 100```