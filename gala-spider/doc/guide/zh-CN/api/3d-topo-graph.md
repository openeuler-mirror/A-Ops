# 拓扑图查询 API 文档
spider 将生成的 OS 级别的拓扑关系图存储到图数据 arangodb 中，并通过 arangodb 服务器的 API 向外提供拓扑图的查询能力。关于 spider 和 arangodb 的安装部署参见文档：[安装指导](../install-spider.md)。

本文档将介绍与拓扑图查询相关的 API ，更加详细的 API 定义参见 [arangodb 官方文档](https://www.arangodb.com/docs/stable/http/)。

## 图结构说明

### 图的节点

图的节点表示了拓扑图中的观测对象的一个观测实例，它的数据结构如下：

| 属性      | 描述                                                         |
| --------- | ------------------------------------------------------------ |
| _id       | 节点ID，数据库中的全局唯一标识符                             |
| _key      | 节点索引，数据库中给定节点集合下的唯一标识符                 |
| type      | 表示观测实例的类型                                           |
| timestamp | 表示观测实例采集的时间点                                     |
| level     | 节点所在的拓扑分层                                           |
| metrics   | 表示观测实例采集的指标信息，它是一个字典结构，key表示指标名，value表示指标的值 |
| 其它属性  | 表示观测实例的标签信息，包括标识字段、标签字段，不同观测类型包含不同的标签信息 |

示例：下面展示了一个观测类型为线程（thread）的节点内容，

```json
{
    "_key": "THREAD_4c739ef759c142c18e8c3c29f115e873_928",
    "_id": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_928",
    "type": "thread",
    "level": "PROCESS",
    "timestamp": 1654930858,
    "machine_id": "4c739ef759c142c18e8c3c29f115e873",
    "pid": "928",
    "comm": "dbus-daemon",
    "major": "8",
    "minor": "0",
    "tgid": "928",
    "metrics": {
    	"fork_count": "0",
    	"task_hang_count": "0",
    	"task_io_count": "26209396",
    	"task_io_time_us": "0",
    	"task_io_wait_time_us": "1"
    }
}
```

### 节点集合

不同时间点对应的拓扑图是不同的，因此，我们针对每个时间戳定义一个节点集合，节点集合的名称由 `ObserveEntities_<timestamp>` 组成，表示给定时间戳 `timestamp` 下的节点集合。通过指定节点集合，我们可以查询给定时间点下所有观测实例的集合。

### 图的边

图的边表示了拓扑图中观测实例之间的拓扑依赖关系，它的数据结构如下：

| 属性      | 描述                                   |
| --------- | -------------------------------------- |
| _id       | 边ID，数据库中的全局唯一标识符         |
| _key      | 边索引，数据中给定边集合下的唯一标识符 |
| _from     | 表示关系主体的节点ID                   |
| _to       | 表示关系客体的节点ID                   |
| type      | 表示拓扑关系的类型                     |
| timestamp | 表示拓扑关系生成的时间点               |
| layer     | 表示拓扑关系的属性                     |

示例：下面展示了一个表示线程（thread）观测实例和进程（system_proc）观测实例具有从属关系（belongs_to）的边内容，

```json
{
    "_key": "1300212",
    "_id": "belongs_to/1300212",
    "_from": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_1687278",
    "_to": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219",
    "type": "belongs_to",
    "timestamp": 1654930858,
    "layer": "direct"
}
```

### 边集合

针对每种拓扑关系类型，我们定义一个相应的边集合，边集合的名称与拓扑关系类型相同。通过指定边集合，我们可以查询具有指定拓扑依赖关系的拓扑子图。

### 时间戳集合

由于拓扑图是每隔一段时间（比如每隔 1 分钟）生成的，我们定义一个名为 `Timestamps` 的时间戳集合，用于记录所有已生成拓扑图的时间点。通过查询时间戳集合，我们可以获取距离指定时间点最近一次生成拓扑图的时间点，进而查询对应的拓扑图。

时间戳集合中一条记录的内容很简单，它的数据结构如下：

| 属性 | 描述                                   |
| ---- | -------------------------------------- |
| _id  | 时间戳ID                               |
| _key | 时间戳索引，它的值为时间戳的字符串表示 |

示例：在时间点 1654930858 的时间戳内容如下，

```json
{
    "_key": "1654930858",
    "_id": "Timestamps/1654930858"
}
```

## 拓扑图查询API

### 1. 查询距离指定时间戳最近的拓扑图时间戳

#### 1.1 接口描述

Arangodb 提供的 AQL 语句查询接口，我们用它来查询距离指定时间戳最近一次生成的拓扑图的实际时间戳。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [AQL查询接口](https://www.arangodb.com/docs/stable/http/aql-query-cursor-accessing-cursors.html)。

#### 1.2 请求方法

`POST /_api/cursor`

#### 1.3 输入参数

**请求体参数**：

- `query`（string类型，必选）：包含要执行的查询字符串，这里它的内容为 `"FOR t IN Timestamps FILTER TO_NUMBER(t._key) <= @timestamp SORT t._key DESC LIMIT 1 RETURN t._key"` 。
- `batchSize`（integer类型，可选）：一次往返中从服务器传输到客户端的最大返回记录数量，这里设置为 1。
- `bindVars`（字典类型，必选）：表示 `query` 中绑定查询参数的键/值对。这里它包含一个名为 `timestamp` 的键，表示要查询的指定时间戳。

#### 1.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容包括，

- `error`（boolean类型）：发生错误时标记为 true
- `code`（integer类型）：HTTP 状态码
- `result`（数组类型）：返回内容，这里只返回一个元素，它的值为拓扑图的时间戳。

#### 1.5 请求示例

```shell
[root@k8s-node3 ~]# curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://10.137.17.122:8529/_db/spider/_api/cursor <<EOF
> {
>   "query": "FOR t IN Timestamps FILTER TO_NUMBER(t._key) <= @ts SORT t._key DESC LIMIT 1 RETURN t._key",
>   "batchSize": 1,
>   "bindVars": { "ts": 1654930859 }
> }
> EOF
HTTP/1.1 201 Created
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 279

{
    "result": [
        "1654930858"
    ], 
    "hasMore": false, 
    "cached": false, 
    "extra": {...}, 
    "error": false, 
    "code": 201
}
```



### 2. 查询指定节点/边信息

#### 2.1 接口描述

查询指定节点（或边）的详细信息。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [节点查询接口](https://www.arangodb.com/docs/stable/http/document-working-with-documents.html#read-document)。

#### 1.2 请求方法

#### 2.2 请求方法

`GET /_api/document/{collection}/{key}`

#### 2.3 输入参数

**路径参数**

- `collection`（string类型，必选）：节点（或边）所在的集合
- `key`（string类型，必选）：节点（或边）的索引 `_key`

#### 2.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容为节点（或边）的内容。

#### 2.5 请求示例

```shell
[root@k8s-node3 ~]# curl --header 'accept: application/json' --dump - http://10.137.17.122:8529/_db/spider/_api/document/ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_928
HTTP/1.1 200 OK
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Etag: "_eTEPW----S"
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 465

{
    "_key": "THREAD_4c739ef759c142c18e8c3c29f115e873_928", 
    "_id": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_928", 
    "_rev": "_eTEPW----S", 
    "name": "dbus-daemon", 
    "type": "thread", 
    "level": "PROCESS", 
    "timestamp": 1654930858, 
    "machine_id": "4c739ef759c142c18e8c3c29f115e873", 
    "pid": "928", 
    "comm": "dbus-daemon"
}
```



### 3. 查询指定节点的邻边信息

#### 3.1 接口描述

查询指定节点的邻边信息。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [邻边查询接口](https://www.arangodb.com/docs/stable/http/edge-working-with-edges.html)。

#### 3.2 请求方法

`GET /_api/edges/{collection-id}`

#### 3.3 输入参数

**路径参数**

- `collection-id`（string类型，必选）：边集名称

**查询参数**

- `vertex`（string类型，必选）：节点ID
- `direction`（string类型，可选）：选择边的方向（入方向或出方向）。如果未设置，则返回任意方向。

#### 3.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容为节点的邻边数组。

#### 3.5 请求示例

```shell
[root@k8s-node3 ~]# curl --header 'accept: application/json' --dump - http://10.137.17.122:8529/_db/spider/_api/edges/belongs_to?vertex=ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219
HTTP/1.1 200 OK
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 1333

{
    "edges": [
        {
            "_key": "1300211", 
            "_id": "belongs_to/1300211", 
            "_from": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_1687277", 
            "_to": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219", 
            "_rev": "_eTEPW-m--F", 
            "type": "belongs_to", 
            "layer": "direct"
        }, 
        {
            "_key": "1300212", 
            "_id": "belongs_to/1300212", 
            "_from": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_1687278", 
            "_to": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219", 
            "_rev": "_eTEPW-m--G", 
            "type": "belongs_to", 
            "layer": "direct"
        }
    ], 
    "error": false, 
    "code": 200, 
    "stats": {...}
}
```



### 4. 查询满足过滤条件的节点信息

#### 4.1 接口描述

Arangodb 提供的 AQL 语句查询接口，我们用它来查询满足过滤条件的节点信息。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [AQL查询接口](https://www.arangodb.com/docs/stable/http/aql-query-cursor-accessing-cursors.html)。

#### 4.2 请求方法

`POST /_api/cursor`

#### 4.3 输入参数

**请求体参数**：

- `query`（string类型，必选）：包含要执行的 AQL 查询语句的字符串形式。这里它的内容为 `"FOR v IN  @@collection FILTER v.type == @entity_type return v"` ，其中，`v.type == @entity_type` 子串是一个过滤条件，它表示过滤出观测类型为变量 `entity_type` 的值的节点，其中变量 `entity_type` 的值在 `bindVars` 参数中指定，该子串可以按需替换成其他的过滤条件。当有多个过滤条件时，可通过 `and` 关键字连接多个过滤条件，并替换上述子串，例如替换成 `v.type == @entity_type and v.level == @level` ，同时在 `bindVars` 参数中指定对应的变量值即可。
- `count`（boolean类型，可选）：指示是否应在输出参数的 “count” 属性中返回结果集中的文档数量，这里设置为 true。
- `batchSize`（integer类型，可选）：一次往返中从服务器传输到客户端的最大返回记录数量。如果未设置此属性，将使用服务器控制的默认值。
- `bindVars`（字典类型，必选）：表示 `query` 中绑定查询参数的键/值对。这里它包含两个属性，
  - `@collection`（string类型，必选）：节点集合
  - `entity_type`（string类型，可选）：根据过滤条件中涉及的变量按需设置

#### 4.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容包括：

- `error`（boolean类型）：发生错误时标记为 true
- `code`（integer类型）：HTTP 状态码
- `result`：当前批次的文档（节点或边）列表
- `hasMore`：是否还有下一批查询结果，如果这是最后一批，则为 false
- `count`：文档的总数量
- `id`：光标标识符，用于查询剩余的结果集，用法参见本文档的第5个API：**从光标处读取下一批查询内容**

#### 4.5 请求示例

```shell
[root@k8s-node3 ~]# curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://10.137.17.122:8529/_db/spider/_api/cursor <<EOF
{
  "query": "FOR v IN  @@collection FILTER  v.type == @entity_type return v",
  "batchSize": 2,
  "count": true,
  "bindVars": { "@collection": "ObserveEntities_1654930858", "entity_type": "system_proc"}
}
EOF
HTTP/1.1 201 Created
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 2434

{
  "result": [
    {
      "_key": "SYSTEM_PROC_4f2eb1a8378b428f85af0a6c0cde9288_2133032",
      "_id": "ObserveEntities_1654930858/SYSTEM_PROC_4f2eb1a8378b428f85af0a6c0cde9288_2133032",
      "_rev": "_eTEPW-----",
      "name": "redis-server",
      "type": "system_proc",
      "level": "PROCESS",
      "timestamp": 1654930858,
      "machine_id": "4f2eb1a8378b428f85af0a6c0cde9288",
      "pid": "2133032",
      "cmdline": "/opt/redis/redis-server 10.137.16.172:3742   ",
      "comm": "redis-server"
    },
    {
      "_key": "SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219",
      "_id": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1687219",
      "_rev": "_eTEPW----_",
      "name": "redis-server",
      "type": "system_proc",
      "level": "PROCESS",
      "timestamp": 1654930858,
      "machine_id": "4c739ef759c142c18e8c3c29f115e873",
      "pid": "1687219",
      "cmdline": "/opt/redis/redis-server 10.137.16.176:3746   ",
      "comm": "redis-server"
    }
  ],
  "hasMore": true,
  "id": "2206881",
  "count": 20,
  "extra": {...},
  "cached": false,
  "error": false,
  "code": 201
}
```



### 5. 从光标处读取下一批查询内容

#### 5.1 接口描述

当 `POST /_api/cursor` 接口的 AQL 语句查询结果比较多的时候，需要分批返回给用户，本接口通过  `POST /_api/cursor` 接口返回的光标标识 `cursor-identifier` 来不断读取下一批查询结果。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [AQL查询接口](https://www.arangodb.com/docs/stable/http/aql-query-cursor-accessing-cursors.html)。

#### 5.2 请求方法

`POST /_api/cursor/{cursor-identifier}`

#### 5.3 输入参数

**路径参数**

- `cursor-identifier`（string类型，必选）：光标标识符

#### 5.4 输出参数

**HTTP 200**：请求成功时的响应码，返回内容包括：

- `id`：光标标识符
- `result`：当前批次的文档（节点或边）列表
- `hasMore`：是否还有下一批查询结果，如果这是最后一批，则为 false
- `count`：文档的总数量
- `error`（boolean类型）：发生错误时标记为 true
- `code`（integer类型）：HTTP 状态码

#### 5.5 请求示例

```shell
[root@k8s-node3 ~]# curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://10.137.17.122:8529/_db/spider/_api/cursor/2204099 <<EOF
> {
>   "query": "FOR v IN  @@collection FILTER  v.type == @entity_type return v",
>   "batchSize": 2,
>   "count": true,
>   "bindVars": { "@collection": "ObserveEntities_1654930858", "entity_type": "system_proc"}
> }
> EOF
HTTP/1.1 201 Created
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 2434

{
  "result": [
    {
      "_key": "SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1673685",
      "_id": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1673685",
      "_rev": "_eTEPW----A",
      "name": "redis-server",
      "type": "system_proc",
      "level": "PROCESS",
      "timestamp": 1654930858,
      "machine_id": "4c739ef759c142c18e8c3c29f115e873",
      "pid": "1673685",
      "cmdline": "/opt/redis/redis-server 10.137.16.176:3747   ",
      "comm": "redis-server"
    },
    {
      "_key": "SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1676378",
      "_id": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1676378",
      "_rev": "_eTEPW----B",
      "name": "redis-server",
      "type": "system_proc",
      "level": "PROCESS",
      "timestamp": 1654930858,
      "machine_id": "4c739ef759c142c18e8c3c29f115e873",
      "pid": "1676378",
      "cmdline": "/opt/redis/redis-server 10.137.16.176:3747   ",
      "comm": "redis-server"
    }
  ],
  "hasMore": true,
  "id": "2204099",
  "count": 88,
  "extra": {...},
  "cached": false,
  "error": false,
  "code": 200
}
```



### 6. 查询拓扑子图

#### 6.1 接口描述

Arangodb 提供的 AQL 语句查询接口，我们用它来查询拓扑子图。这里只提供与本功能相关的说明，详细的 API 定义参见 arangodb 官方文档： [AQL查询接口](https://www.arangodb.com/docs/stable/http/aql-query-cursor-accessing-cursors.html)。

#### 6.2 请求方法

`POST /_api/cursor`

#### 6.3 输入参数

**请求体参数**：

- `query`（string类型，必选）：包含要执行的查询字符串，这里它的内容为 `"WITH @@collection FOR v, e IN 1..@depth ANY @start_id @edge_coll return {\"vertex\": v, \"edge\": e}"` ，其中，`@edge_coll` 子串是一个过滤条件，它表示只遍历变量 `edge_coll` 的值指定的边集合，其中变量 `edge_coll` 的值在 `bindVars` 参数中指定。当需要遍历多个边集合时，可通过 `,` 分隔多个边集合变量，并替换上述子串，例如替换成 `@edge_coll1, @edge_coll2`，同时在 `bindVars` 参数中指定对应的变量值即可。
- `count`（boolean类型，可选）：指示是否应在输出参数的 “count” 属性中返回结果集中的文档数量，这里设置为 true。
- `batchSize`（integer类型，可选）：一次往返中从服务器传输到客户端的最大返回记录数量。如果未设置此属性，将使用服务器控制的默认值。
- `bindVars`（字典类型，必选）：表示 `query` 中绑定查询参数的键/值对。这里它包含4个属性，
  - `@collection`（string类型，必选）：节点集合
  - `depth`（string类型，必选）：子图遍历的深度
  - `start_id`（string类型，必选）：子图遍历的起始节点ID
  - `edge_coll`（string类型，必选）：需要遍历的边集名称

#### 6.4 输出参数

**HTTP 201**：请求成功时的响应码，返回内容包括：

- `error`（boolean类型）：发生错误时标记为 true
- `code`（integer类型）：HTTP 状态码
- `result`：当前批次的查询结果列表。其中每个元素的内容为一个字典结构，它可在 `query` 参数中指定，这里它的属性如下，
  - `edge`：当前节点的邻边信息
  - `vertex`：`edge` 边另一侧的节点信息
- `hasMore`：是否还有下一批查询结果，如果这是最后一批，则为 false
- `count`：文档的总数量
- `id`：光标标识符，用于查询剩余的结果集，用法参见本文档的第5个API：**从光标处读取下一批查询内容**

#### 6.5 请求示例

```shell
[root@k8s-node3 ~]# curl -X POST --header 'accept: application/json' --data-binary @- --dump - http://10.137.17.122:8529/_db/spider/_api/cursor <<EOF
> {
>   "query": "WITH @@collection FOR v, e IN  1..10 ANY @start_id @@edge_coll1, @@edge_coll2 return {\"vertex\": v, \"edge\": e}",
>   "batchSize": 2,
>   "count": true,
>   "bindVars": { "@collection": "ObserveEntities_1654930858", "start_id": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1676378", "@edge_coll1": "belongs_to", "@edge_coll2": "runs_on"}
> }
> EOF
HTTP/1.1 201 Created
X-Arango-Queue-Time-Seconds: 0.000000
X-Content-Type-Options: nosniff
Server: ArangoDB
Connection: Keep-Alive
Content-Type: application/json; charset=utf-8
Content-Length: 1053

{
    "result": [
        {
            "vertex": {
                "_key": "THREAD_4c739ef759c142c18e8c3c29f115e873_1676378", 
                "_id": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_1676378", 
                "_rev": "_eTEPW-C--E", 
                "name": "redis-server", 
                "type": "thread", 
                "level": "PROCESS", 
                "timestamp": 1654930858, 
                "machine_id": "4c739ef759c142c18e8c3c29f115e873", 
                "pid": "1676378", 
                "comm": "redis-server", 
                "major": "8", 
                "minor": "0", 
                "tgid": "1676378"
            }, 
            "edge": {
                "_key": "1300207", 
                "_id": "belongs_to/1300207", 
                "_from": "ObserveEntities_1654930858/THREAD_4c739ef759c142c18e8c3c29f115e873_1676378", 
                "_to": "ObserveEntities_1654930858/SYSTEM_PROC_4c739ef759c142c18e8c3c29f115e873_1676378", 
                "_rev": "_eTEPW-m--B", 
                "type": "belongs_to", 
                "layer": "direct"
            }
        }
    ], 
    "hasMore": false, 
    "count": 1, 
    "cached": false, 
    "extra": {...}, 
    "error": false, 
    "code": 201
}
```

