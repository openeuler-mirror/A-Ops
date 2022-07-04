#  配置文件介绍

gala-spider运行必须的外部参数通过配置文件定义，主要的配置项包括：设置DB、UI类型、DB信息、UI信息、服务支持类型、例外处理等；

## 配置文件详解

配置文件开发路径归档在 'A-Ops/gala-spider/config/gala-spider.yaml'；配置文件各部分详解；

### global

```
global:                                           -- gala-spider全局配置
    data_source: "prometheus"                     -- 指定观测指标采集的数据库，默认使用prometheus
    data_agent: "gala_gopher"                     -- 观测指标采集代理
```

### spider

```
spider:
    port: 11115
    log_conf:
        log_path: "/var/log/gala-spider/spider.log"  -- 日志文件路径
        # log level: DEBUG/INFO/WARNING/ERROR/CRITICAL
        log_level: INFO                            -- 日志打印级别
        # unit: MB
        max_size: 10                               -- 日志文件大小
        backup_count: 10                           -- 日志备份文件大小
```

### storage

```
storage:                                           -- 拓扑图存储服务的配置信息
    # unit: second
    period: 60                                     -- 存储周期
    database: arangodb                             -- 存储的图数据库
    db_conf:
        url: "http://localhost:8529"               -- 图数据库的服务器地址
        db_name: "spider"                          -- 数据库名称
```

### kafka

```
kafka:                                            -- kafka配置信息，用于获取观测对象元数据信息
    server: "localhost:9092"                      -- kafka服务器地址
    metadata_topic: "gala_gopher_metadata"        -- 观测对象元数据消息的topic
    metadata_group_id: "metadata-spider"          -- 观测对象元数据消息的消费者组ID
```

### prometheus

```
prometheus:                                       -- prometheus数据库配置信息
    base_url: "http://localhost:9090/"            -- prometheus服务器地址
    instant_api: "/api/v1/query"                  -- 单个时间点采集API
    range_api: "/api/v1/query_range"              -- 区间采集API
    step: 1                                       -- 采集时间步长，用于区间采集API
```

