## 如何新增观测对象

为了方便用户添加新的观测对象，我们通过配置文件的方式来配置需要新增的观测对象的元数据信息，从而支持对新观测对象的采集和拓扑绘制能力。

需要配置的观测对象的元数据信息包括：
- 观测对象的类型
- 全局唯一标识该观测对象的一个观测实例的字段集合
- 观测对象的标签字段集合
- 观测对象的名称字段
- 观测对象的观测指标集合
- 观测对象所在的拓扑分层
- 观测对象之间的关联关系

下面以观测对象 `task` 的为例，详细讲解如何配置新增的观测对象的元数据信息。系统默认支持的观测对象配置文件在 `gala-spider` 工程下的 [config/observe.yaml](../config/observe.yaml) 文件中。

### 1. 新增一个观测对象类型

`task` 观测对象对应 Linux 内核中的一个进程。在配置文件中，`observe_entities` 是一个对象的列表，所有新增的观测对象元数据信息都在 `observe_entities` 下。

为此，我们在 `observe_entities` 下新增一个对象，并指定 `type: task` 代表这是一个观测类型为 `task` 的观测对象的配置信息。 `type` 是一个必选的配置字段。

配置结果如下：
```yaml
observe_entities:
  -
    type: task
```

当前系统支持的观测对象类型如下。

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

### 2. 配置观测对象的标识字段

一台主机上的 `task` 可以通过进程ID `pid` 进行标识，这台主机可以通过一个全局的机器ID `machine_id` 进行唯一标识。

因此，`task` 观测对象的一个观测实例可通过 `pid` 和 `machine_id` 全局唯一标识。我们将它们配置到 `keys` 字段中。`keys` 是一个必须的配置字段。

此时，配置结果为：
```yaml
observe_entities:
  -
    type: task
    keys:
      - pid
      - machine_id
```

### 3. 配置观测对象的标签字段

`task` 还有一些非标识类的标签信息。比如进程名 `task_name` ，进程组ID `tgid` ，进程的命名空间 `pidns` 等信息。
如果 `task` 运行在一个容器中，它还包括一个所在的容器ID `container_id` 信息。

这些标签信息可以配置到 `labels` 字段中。`labels` 是一个可选的配置字段。

此时，配置结果为：
```yaml
observe_entities:
  -
    type: task
    keys:
      - pid
      - machine_id
    labels:
      - task_name
      - tgid
      - pidns
      - container_id
```

### 4. 配置观测对象的名称字段

每个观测对象的观测实例一般都会有一个名称字段，不同的观测对象的名称字段标签不尽相同，比如进程对象 `task` 中为进程名 `task_name`，主机对象 `hostname` 中为主机名 `hostname` 。

因此，我们在配置中新增一个 `name` 字段，它的值为对应观测对象的名称字段标签。`name` 是一个可选的配置字段。

此时，配置结果为，
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
```
这里，我们使用了yaml中锚点 `&` 和别名 `*` 的语法来实现 `name` 的值到 `task_name` 标签的映射。
当然，你也可以直接使用 `name: task_name` 进行代替。

### 5. 配置观测对象的观测指标字段

`task` 包含一个指标字段：进程调用 fork 的次数 `fork_count`。这些指标字段都在 `metrics` 中进行配置。如果 spider 的数据源是 Prometheus ，则 `metrics` 中至少需要配置一个指标字段，否则无法从 Prometheus 采集数据。

此时，配置结果为，
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
```

### 6. 配置观测对象所在的拓扑分层

该配置信息在绘制观测对象之间的3D拓扑关系图功能时会用到。拓扑分层通过 `level` 字段进行配置，是一个可选的配置字段。

`task` 对应于拓扑分层的进程层 `PROCESS` ，所以添加一行配置内容：
```yaml
level: PROCESS
```

当前系统支持的拓扑分层有，
```
- HOST
- CONTAINER
- RUNTIME
- RPC
- LB
- MB
```

### 7. 配置观测对象之间的关联关系

关联关系可分为两种。一种是直接的（`direct`）关联关系，是指物理上直观可见的关系。另一种是间接的（`indirect`）关联关系，是指在物理上不存在但逻辑上可建立的关系。

目前支持的直接关联关系有：

| 关系名称    | 关系描述             |
| ---------- | -------------------- |
| runs_on    | 运行关系。例如，进程运行在主机上，则有关系：进程 runs_on 主机。                 |
| belongs_to | 从属关系。例如，通信端点是从属于某个进程，则有关系：通信端点 belongs_to 进程。                 |
| is_server  | 服务端通信关系。例如，nginx记录了一条和服务端tcp的连接，则有关系：服务端tcp连接 is_server nginx连接。 |
| is_client  | 客户端通信关系。例如，nginx记录了一条和客户端tcp的连接，则有关系：客户端tcp连接 is_client nginx连接。 |
| is_peer    | 对端通信关系。例如，客户端与服务端建立了一条tcp连接，则有关系：客户端tcp连接 is_peer 服务端tcp连接。反之亦然。             |


支持的间接关联关系有：

| 关系名称 | 关系描述  |
| -------- | --------- |
| connect  | 连接关系。例如，主机A和主机B上有tcp连接进行通信，则有关系：主机A connect 主机B 。      |

观测对象 `task` 与其他观测对象有多种关联关系。比如：`task runs_on host` 表示进程运行在某个主机上，`task runs_on container` 表示进程运行在某个容器上，`task connect task` 表示进程与另一个进程具有间接的连接关系。

`task` 的多个关联关系可通过 `dependingitems` 字段进行配置。
`dependingitems` 是一个关联关系的列表，列表中的每一项配置对应一种关联关系，其中 `task` 作为该关联关系的关系主体。
例如，对于一条关联关系 `task runs_on host` ，我们把 `task` 称作关联关系 `runs_on` 的关系主体，`host` 称作关联关系 `runs_on` 的关系客体。

每一条关联关系的配置信息包括如下字段：
- `id` ：关系名称。
- `layer` ：关系类型。值的范围为：`direct` 和 `indirect` ，分别表示直接关系和间接关系。
- `toTypes` ：关系客体的配置信息。它是一个列表，列表中的每一项对应一个关系客体的配置信息，内容为，
    - `type` : 关系客体对应的观测对象类型。
    - `matches` ：直接的关联关系可以通过观测对象的标识字段、标签字段等进行匹配。
      `matches` 字段配置了这种字段匹配的信息，它是一个列表，列表中的每一项表示一条匹配，
      具体内容为，
      - `from` ：关系主体的字段名称。
      - `to` ：关系客体的字段名称。
    - `requires` ：有一些关联关系成立的条件是要求关系主体或关系客体的某些字段的值为特定的值。
      `requires` 字段配置了这种约束条件。它是一个列表，列表中的每一项表示一个约束条件，具体内容为，
      - `side` ：约束的对象是关系主体还是关系客体。取值为：`from` 和 `to` ，分别表示关系主体和关系客体。
      - `label` ：约束的字段名称。
      - `value` ：约束的字段值。

对于 `task` 的一个关联关系 `task runs_on host` ，对应的配置内容如下。
```yaml
dependingitems:
  -
    id: runs_on
    layer: direct
    toTypes:
      -
        type: host
        matches:
          -
            from: machine_id
            to: machine_id
```
其中，`matches` 配置表明：当 `task.machine_id == host.machine_id` 成立时，关联关系 `task runs_on host` 成立。

### 一个完整的观测对象的配置结果

`task` 最终的配置信息为：
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
          -
            type: container
            matches:
              -
                from: container_id
                to: container_id
              -
                from: machine_id
                to: machine_id
          -
            type: host
            matches:
              -
                from: machine_id
                to: machine_id
      -
        id: connect
        layer: indirect
        toTypes:
          -
            type: task
```

当我们需要给一个观测对象添加新的指标字段、标签字段、关联关系等信息时，只需要在配置文件中添加相应的配置即可。
这种方式提供了很好的可扩展性。
