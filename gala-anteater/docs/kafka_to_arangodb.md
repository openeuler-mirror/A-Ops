# 异常检测&根因定位数据ArangoDB接口使用指导
异常检测、根因定位结果数据默认输出到kafka中，由其它子系统订阅消费使用。本文档提供另外一种数据对接方式，指导将kafka中的数据实时同步到ArangoDB中，其它子系统可以直接使用ArangoDB的接口获取异常检测、根因定位的数据。

本数据对接方案的原理，通过开源数据采集工具logstash将kafka中的数据实时消费并转存到ArangoDB中。

## 1. ArangoDB环境准备
ArangoDB的安装部署参考[官网](https://www.arangodb.com/)，详细过程略。下面介绍创建异常检测&根因定位对应的db和collection。

### 1.1 db创建
```
shell> curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://ip:8529/_api/database <<EOF
{ 
    "name" : "gala_event", 
    "options" : { 
        "sharding" : "flexible", 
        "replicationFactor" : 3 
    } 
}
EOF

HTTP/1.1 201 Created
content-type: application/json
connection: Keep-Alive
content-length: 40
server: ArangoDB
x-arango-queue-time-seconds: 0.000000
x-content-type-options: nosniff

{ 
"error" : false, 
"code" : 201, 
"result" : true 
}
```

### 1.2 collection创建
```
shell> curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://ip:8529/_db/gala_event/_api/collection <<EOF
{ 
    "name" : "gala_event_anteater" 
}
EOF

HTTP/1.1 200 OK
content-type: application/json
connection: Keep-Alive
content-length: 436
server: ArangoDB
x-arango-queue-time-seconds: 0.000000
x-content-type-options: nosniff

{ 
    "error" : false, 
    "code" : 200, 
    "waitForSync" : false, 
    "status" : 3, 
    "globallyUniqueId" : "h1466B7768774/66935", 
    "isSystem" : false, 
    "internalValidatorType" : 0, 
    "isSmartChild" : false, 
    "id" : "66935", 
    "name" : "gala_event_anteater", 
    "type" : 2, 
    "objectId" : "66934", 
    "usesRevisionsAsDocumentIds" : true, 
    "schema" : null, 
    "writeConcern" : 1, 
    "syncByRevision" : true, 
    "cacheEnabled" : false, 
    "keyOptions" : { 
    "allowUserKeys" : true, 
    "type" : "traditional", 
    "lastValue" : 0 
    }, 
    "statusString" : "loaded" 
}

```

## 2. logstash安装配置
### 2.1 下载安装
下载 [logstash](https://www.elastic.co/cn/downloads/logstash)


### 2.2 配置
在$logstash安装路径，$logstash/config目录下新建kafka_to_arangodb.conf文件，内容如下（其中ip地址、端口、topic等用实际信息替换）：
```
input {
    kafka {
        bootstrap_servers => "ip:9092"
        topics => ["gala_anteater"]
        group_id => "gala_group"
        client_id => "gala_client"
        decorate_events => "true"
    }
}

filter {
    json {
        source => "message"
    }

    date {
        match => ["Timestamp", "UNIX_MS"]
        target => "@timestamp"
    }

}

output {
    stdout { codec => rubydebug }

    http {
        http_method => "post"
        url => "http://ip:8529/_db/gala_event/_api/document?collection=gala_event_anteater"
        format => "json"
    }
}
```
### 2.3 启动运行
```
bin/logstash -f config/kafka_to_arangodb.conf
```

或者以后台服务的方式运行：
```
bin/logstash -f config/kafka_to_arangodb.conf -d
```

## 3. 数据获取接口
### 3.1 接口描述

Arangodb 提供的 AQL 语句查询接口，详细的 API 定义参见 arangodb 官方文档： [AQL查询接口](https://www.arangodb.com/docs/stable/http/aql-query-cursor-accessing-cursors.html)。

### 3.2 请求方法

`POST /_api/cursor`

### 3.3 输入参数

**请求体**：

`query`（string类型，必选）：包含要执行的查询字符串，这里它的内容为 `"FOR t IN gala_event_anteater LIMIT 10 RETURN t"` 。

### 3.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容包括，

- `error`（boolean类型）：发生错误时标记为 true
- `code`（integer类型）：HTTP 状态码
- `result`（数组类型）：返回内容，这里只返回一个元素，它的值为拓扑图的时间戳。

### 3.5 请求示例
```
curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://ip:8529/_db/gala_event/_api/cursor <<EOF
{
         "query": "FOR t IN gala_event_anteater LIMIT 10 RETURN t"
}
EOF
{
  "result": [
    {
      "_key": "6127900",
      "_id": "gala_event_anteater/6127900",
      "_rev": "_epRnG5C---",
      "@version": "1",
      "tags": [
        "_jsonparsefailure"
      ],
      "message": "",
      "event": {
        "original": ""
      },
      "@timestamp": "2022-08-19T07:02:27.302593Z"
    },
    {
      "_key": "6127928",
      "_id": "gala_event_anteater/6127928",
      "_rev": "_epRo-1m---",
      "Resource": {
        "metrics": "gala_gopher_system_net_net_device_rx_drops"
      },
      "SeverityText": "WARN",
      "@version": "1",
      "SeverityNumber": 13,
      "Attributes": {
        "Entity ID": "4c739ef759c142c18e8c3c29fxxxx_system_net_enp2s2"
      },
      "Body": "Thu Aug 11 00:21:51 2022 WARN Entity(enp2s2) net device rx queue drops(13).",
      "Timestamp": "1660892578591",
      "@timestamp": "2022-08-19T07:02:58.591Z"
    }
  ],
  "hasMore": false,
  "cached": false,
  "extra": {
    "warnings": [],
    "stats": {
      "writesExecuted": 0,
      "writesIgnored": 0,
      "scannedFull": 2,
      "scannedIndex": 0,
      "filtered": 0,
      "httpRequests": 0,
      "executionTime": 0.0003535151481628418,
      "peakMemoryUsage": 0
    }
  },
  "error": false,
  "code": 201
}
```
