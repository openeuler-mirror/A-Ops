#  配置文件介绍

## 介绍

gala-spider运行必须的外部参数通过配置文件定义；主要的配置项包括：设置DB、UI类型、DB信息、UI信息、服务支持类型、例外处理等；

## 配置文件详解

配置文件开发路径归档在 `A-Ops/gala-spider/config/gala-spider.conf`；配置文件各部分详解；

### global

```
[global]                                          -- gala-spider引擎配置
    data_source = "kafka"                         -- DB类型配置
    ui_source = "neo4j"                           -- UI类型配置
```

### kafka

```
[kafka]                                           -- kafka配置信息
    topic = gala_gapher
    broker = ["10.137.17.123:9092"]
```

### promecheus

```
[promecheus]								   -- promecheus配置信息
    broker =
```

### neo4j

```
[neo4j]										  -- neo4j配置信息
address = http://localhost:7474
username = xxxx
password = xxxx
```

### table_info

请不要删除每个列表现有的配置信息，如有修改请在列表末依次新增；

```
[table_info]                                     -- 可支持的技术点
base_table_name = ["tcp_link", "lvs_link"]
other_table_name = ["nginx_statistic" , "lvs_link" , "haproxy_link" , "dnsmasq_link"]
```

### option

```
[option]                                         -- 一些其他的配置项
exclude_addr = ["1.2.3.4"]                       -- 例外处理配置项，默认为1.2.3.4即不做例外处理；设置后可以对某类IP不进行算法处理
```