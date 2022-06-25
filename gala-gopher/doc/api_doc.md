# API介绍

gala-gopher对外提供了三个接口，分别用于实现指标数据获取、元数据获取和异常结果获取功能。



## 1. 指标数据获取接口

gala-gopher支持将采集到的数据上报到Promethous、Kafka等数据库；可以通过配置文件开启/关闭某个数据上报通道。

### 1.1 http方式

采用本方式每条采集数据是基于指标粒度上报的，通常gala-gopher部署在1个到多个普通节点，管理节点的Promethous可以配置定时拉取各个普通节点的指标数据。

#### 默认提供的REST API地址

```http
http://localhost:port
```

支持自定义配置，详情参考[配置文件](conf_introduction.md)中 `webServer`部分。

#### 输出数据格式

指标数据遵循以下格式：

```basic
metric_name {"key1"="xx","key2"="xx","label1"="xx","label2"="xx",...} metric_value timestamp
```

metirc_name即指标名，遵循如下指标命名规范：gala_gopher_<table_name>_<metric_name>。metric_value即指标的值是一个float格式的数据。timestamp默认为当前时间(从1970-01-01 00:00:00以来的毫秒数)。每条数据由指标名metric_name和标签{key..label..}组合唯一确定。

#### 请求示例

##### 输入示例

```shell
curl http://localhost:8888
```

##### 输出示例

```basic
gala_gopher_thread_fork_count{pid="2494",tgid="2494",comm="hello",major="8",minor="0",machine_id="xxxxx",hostname="localhost.master"} 2 1656060116000
gala_gopher_thread_task_io_time_us{pid="2494",tgid="2494",comm="hello",major="8",minor="0",machine_id="xxxxx",hostname="localhost.master"} 3 1656060116000
```

### 1.2 kafka方式

本方式输出的数据是基于观测对象粒度的，即每条数据是观测对象的一个实例信息，包含了：观测对象名(table_name)和全量的keys、lables和metrics信息。

#### 默认提供的topic

```basic
gala_gopher
```

支持自定义配置，详情参考[配置文件](conf_introduction.md)中 ` kafka`部分。

#### 输出数据格式

```json
{
    "table_name": "xxxx",
    "timestamp": 1234567890,
    "machine_id": "xxxxx",
    "key1": "xx",
    "key2": "xx",
    ...,
    "label1": "xx",
    "label2": "xx",
    ...,
    "metric1": "xx",
    "metric2": "xx",
    ...
}
```

#### 请求示例

##### 输入示例

```shell
./bin/kafka-console-consumer.sh --bootstrap-server 10.10.10.10:9092 --topic gala_gopher
```

##### 输出示例

```json
 {"timestamp": 165606384400, "machine_id": "xxxxx", "hostname": "localhost.master","table_name": "thread","pid": "2494", "tgid": "2494", "comm": "hello", "major": "8", "minor": "0", "fd_count": "2", "task_io_wait_time_us": "1", "task_io_count": "2", "task_io_time_us": "3", "task_hang_count": "4"}
```



## 2. 元数据获取接口

元数据主要描述了每个观测对象的基本信息，如：观测对象名(table_name)、版本号，以及键值keys有哪些、标签labels有哪些、指标metrics有哪些。元数据会上报到kafka。

#### 默认提供的topic

```basic
gala_gopher_metadata
```

支持自定义配置，详情参考[配置文件](conf_introduction.md)中 ` kafka`部分。

#### 输出数据格式

```json
{
	"timestamp": 1234567890,
	"meta_name": "xxx",
	"version": "1.0.0",
	"keys": ["key1", "key2", ...],
	"labels": ["label1", "label2", ...],
	"metrics": ["metric1", "metric2", ...]
}
```

#### 请求示例

##### 输入示例

```shell
./bin/kafka-console-consumer.sh --bootstrap-server 10.10.10.10:9092 --topic gala_gopher_metadata
```

##### 输出示例

```json
{"timestamp": 1655888408000, "meta_name": "thread", "version": "1.0.0", "keys": ["machine_id", "pid"], "labels": ["hostname", "tgid", "comm", "major", "minor"], "metrics": ["fork_count", "task_io_wait_time_us", "task_io_count", "task_io_time_us", "task_hang_count"]}
```



## 3. 异常事件获取接口

gala-gopher运行中，如果开启了异常上报功能，就会在探测到数据根据入参阈值后进行检查，超出阈值就会上报异常事件到kafka，上报通道是单独的。

#### 默认提供的topic

```basic
gala_gopher_event
```

支持自定义配置，详情参考[配置文件](conf_introduction.md)中 ` kafka`部分。

#### 输出数据格式

```json
{
	"Timestamp": "1234567890",
	"Attributes": {
		"Entity ID": "<table_name>_<machine_id>_<key1>_<key2>_..."
	},
	"Resource": {
		"metrics": "<metric_name>"
	},
	"SeverityText": "WARN",
	"SeverityNumber": 13,
	"Body": "descriptions."
}
```

输出数据解释：

| 输出参数                    | 参数含义 | 描述                                                  |
| --------------------------- | -------- | ----------------------------------------------------- |
| Entity ID                   | 实体ID   | 命名规则：<table_name>_<machine_id>_<key1>_<key2>_... |
| metrics                     | 指标名   | 命名规则：gala_gopher_<table_name>_<metric_name>      |
| SeverityText/SeverityNumber | 异常事件 | INFO/9   WARN/13   ERROR/17   FATAL/21                |
| Body                        | 事件信息 | 字符串，描述了当前时间、异常事件等级以及具体时间信息  |

##### 输入示例

```shell
./bin/kafka-console-consumer.sh --bootstrap-server 10.10.10.10:9092 --topic gala_gopher_event
```

##### 输出示例

```json
{"Timestamp": "1656123876000", "Attributes": { "Entity ID": "system_disk_xxx_/honme"}, "Resource": { "metrics": "gala_gopher_system_disk_block_userd_per"}, "SeverityText": "WARN","SeverityNumber": 13,"Body": "Sat Jun 25 10:24:36 2022 WARN Entity(/home) Too many Blocks used(82%)."}
```

