## 绘制3D拓扑图的功能设计

### 接口设计
#### UI接口：获取所有的观测实体信息

该接口返回用于绘制3D拓扑图的所有观测实体信息，主要包括：

- 每个观测实体的详细信息，包括：标识信息、属性信息、指标信息以及分层信息等。
- 实体之间的关联关系。


接口定义如下。详细的接口定义参见接口配置文件：[swagger.yaml](./swagger.yaml)

```json
{
  "code": "",
  "msg": "",
  "timestamp": "",
  "entityids": [],
  "entities": [
    {
      "entityid": "",
      "type": "",
      "name": "",
      "level": "",
      "dependingitems": [
        {
          "relation_id": "",
          "layer": "",
          "target": {
            "type": "",
            "entityid": ""
          }
        },
      ],
      "dependeditems": [
        {
          "relation_id": "",
          "layer": "",
          "target": {
            "type": "",
            "entityid": ""
          }
        }
      ],
      "attrs": [
        {
          "key": "",
          "value": "",
          "vtype": ""
        }
      ],
      "anomaly": {}
    }
  ]
}
```

关键字段说明：
- entity type：观测实体类型，例如 host、container、task、tcp_link 等。
- entity id：观测实体唯一标识符。
- entity name：观测实体的名称。
- entity level：观测实体所在的拓扑图分层，例如 host 层、container 层、process 层等。
- entity attrs：观测实体的属性信息，是一个<属性名，属性值>对组成的集合。不同观测实体之间的差异在实体属性中体现。
- entity dependingitems: 观测实体作为关联关系的主体集合。假设当前观测实体为A，关联关系格式为：`实体A 关联关系类型 实体B` 。
- entity dependeditems：观测实体作为关联关系的客体集合。假设当前观测实体为A，关联关系格式为：`实体B 关联关系类型 实体A` 。
- entity anomaly：观测实体的异常检测结果信息。


### 功能设计
#### 配置观测对象
我们通过配置文件的方式来支持新增的观测对象。通过配置每个观测对象的元数据信息，包括标识信息、属性信息、指标信息以及观测对象之间的关联关系等信息，就能知道如何获取该观测对象的实例信息，以及如何在3D拓扑图中呈现。这种方式提供很好的可扩展性。

下面以 task 观测对象为例来介绍观测对象的配置结构。详细的配置信息参见配置文件：[observe.yaml](../config/observe.yaml)
```yaml
observe_entities:
  -
    type: task
    keys:
      - pid
      - machine_id
    labels:
      - &task_name task_name
      - tgid
      - pidns
      - container_id
    name: *task_name
    metrics:
      - fork_count
    level: PROCESS
    dependingitems:
      -
        id: runs_on
        layer: direct
        toTypes:
          - container
          - host
      -
        id: connect
        layer: indirect
        toTypes:
          - task
    dependeditems:
      -
        id: belongs_to
        layer: direct
        fromTypes:
          - task
          - endpoint
          - tcp_link
          - ipvs_link
          - nginx_link
  
```

配置说明：

- type：观测对象类型。代码中会添加所有支持的观测对象类型，如果不符合则加载配置时check不通过。
- keys：作为全局唯一标识该观测对象的一个实例的标签信息集合。用于在spider中生成一个全局唯一的entity id。
- labels：观测对象的非metrics的标签信息，keys也是一种标签信息。
- name：观测对象的实例名称，它的值会关联到标签信息里面对应的字段值。用于在UI呈现。
- metrics：观测对象的观测指标信息。
- level：观测对象所在3d拓扑架构的分层。
- dependingitems：观测对象作为关系主体所涉及的关联关系，关系客体为其他类型的观测对象。
  - id：关联关系名称。
  - toTypes：关联关系的观测对象客体。
- dependeditems：观测对象作为关系客体所涉及的关联关系，关系主体为其他类型的观测对象。
  - id：关联关系名称。
  - fromTypes：关联关系的观测对象主体。


#### 观测对象定义

目前支持的观测对象有：

| 观测对象   | 描述信息   |
| ---------- | ---------- |
| host            | 主机/虚拟机节点    |
| container       | 容器节点    |
| task            | 进程节点 |
| endpoint        | 进程的通信端点 |
| tcp_link        | tcp连接信息 |
| ipvs_link       | ipvs连接信息 |
| nginx_link      | nginx连接信息 |
| haproxy_link    | haproxy连接信息 |


#### 关联关系定义

关联关系可分为两种。一种是直接的（direct）关联关系，是指物理上直观可见的关系。另一种是间接的（indirect）关联关系，是指在物理上不存在但逻辑上可建立的关系。

目前支持的直接关联关系有：

| 关系主体   | 关系名称   | 关系客体             |
| ---------- | ---------- | -------------------- |
| container  | runs_on    | host                 |
| task       | runs_on    | host/container       |
| task       | belongs_to | task                 |
| endpoint   | belongs_to | task                 |
| tcp_link   | belongs_to | task                 |
| ipvs_link  | belongs_to | task                 |
| nginx_link | belongs_to | task                 |
| tcp_link   | is_server  | ipvs_link/nginx_link/haproxy_link |
| tcp_link   | is_client  | ipvs_link/nginx_link/haproxy_link |
| tcp_link   | is_peer    | tcp_link             |



支持的间接关联关系有：

| 关系主体  | 关系名称 | 关系客体  |
| --------- | -------- | --------- |
| task      | connect  | task      |
| container | connect  | container |
| host      | connect  | host      |

#### 拓扑分层定义

目前支持的拓扑分层有：

| 拓扑分层   | 描述信息   |
| ---------- | ---------- |
| HOST            | 主机层    |
| CONTAINER       | 容器层    |
| RUNTIME        | 运行时层 |
| PROCESS         | 进程层 |
| RPC        | RPC层 |
| LB       | LB层 |
| MB      | MB层 |

#### 实体 ID 生成

观测对象的实例 ID 通过观测对象中定义的 `type` 和 `keys` 组合生成。

#### 实体 name 获取

在观测对象配置文件中通过添加 name 字段，关联到观测对象 labels 中指定的字段获取。

#### 实体 attrs 获取

实体的属性信息包含观测对象的配置文件中的： keys 、 labels 、metrics 。
