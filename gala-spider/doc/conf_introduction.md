#  配置文件介绍

## 介绍

gala-spider运行必须的外部参数通过配置文件定义；主要的配置项包括：设置DB、UI类型、DB信息、UI信息、服务支持类型、例外处理等；

## 配置文件详解

配置文件开发路径归档在 'A-Ops/gala-spider/config/gala-spider.yaml'；配置文件各部分详解；

### global

```
global:                                           -- gala-spider引擎配置
    data_source: "kafka"                          -- DB类型配置
    ui_source: "neo4j"                            -- UI类型配置
    observe_conf_path: /etc/spider/observe.yaml   -- 异常检测配置文件路径
```

### kafka

```
kafka:                                            -- kafka配置信息
    topic: gala_gopher
    broker: ["xx.xx.xx.xx:9092"]
    group_id: group_id
```

### promecheus

```
prometheus:                                       -- promecheus配置信息
    broker:
    base_url: "http://localhost:9090/"
    instant_api: "/api/v1/query"
    range_api: "/api/v1/query_range"
    step: 1
```

### neo4j

```
neo4j:                                            -- neo4j配置信息
    address: http://localhost:7474
    username: xxxxxx
    password: xxxxxx
    timer: 5                                      -- 配置获取拓扑数据的周期(>=5)
```

### table_info

请不要删除每个列表现有的配置信息，如有修改请在列表末依次新增；

```
temp_path:                                        -- 支持的技术点
    temp_tcp_file: "/var/tmp/spider/tcpline.txt"
    temp_other_file: "/var/tmp/spider/otherline.txt"
```

### option

```
option                                           -- 一些其他的配置项
exclude_addr = ["1.2.3.4"]                       -- 例外处理配置项，默认为1.2.3.4即不做例外处理；设                                                     置后可以对某类IP不进行算法处理
```

### spider

```
spider:
    port: 11115								  -- REST API的port配置为11115(配合A-Ops UI)
```

### anomaly_detection

```
anomaly_detection:                               -- 异常检测相关配置项
    tcp_link:                                    -- 观测对象：tcp_link，可配置
        detection_model_type: EXPERT_MODEL       -- 配置异常检测的模型(EXPERT_MODEL/AI_MODEL)
        detection_attributes:                    -- 配置具体的观测属性(对应EXPERT_MODEL模型)，包                                                       含：threshold：具体数值
            									    method：'>'、'>='、'<'、'<='
            retran_packets: {threshold: 1, method: ">"}   -- 观测属性1
            lost_packets: {threshold: 1, method: ">"}     -- 观测属性2
            rtt: {threshold: 1, method: ">"}              -- 观测属性3
```

