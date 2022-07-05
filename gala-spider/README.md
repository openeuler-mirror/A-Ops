# gala-spider

gala-spider 提供 OS 级别的拓扑图绘制功能，它将定期获取 gala-gopher （一个 OS 层面的数据采集软件）在某个时间点采集的所有观测对象的数据，并计算它们之间的拓扑关系，最终将生成的拓扑图保存到图数据库 arangodb 中。

## 功能特性

gala-spider 项目提供了两个功能模块，它们分别是：

- **spider-storage**：提供 OS  级别观测对象的拓扑图绘制功能，拓扑图结果会存入图数据库 arangodb 中，可通过 arangodb 提供的 UI 界面查询。
- **cause-inference**：提供异常 KPI 的根因定位能力，它基于异常检测的结果和拓扑图作为输入，并将根因定位的结果输出到 kafka 中。

## 软件架构

![image-20220704203722478](docs/images/spider-soft-arch.png)

其中，虚线框内为 gala-spider 项目的 2 个功能组件，绿色部分为 gala-spider 项目直接依赖的外部组件，灰色部分为 gala-spider 项目间接依赖的外部组件。

- **spider-storage**：gala-spider 核心组件，提供拓扑图存储功能。它从 kafka 获取观测对象的元数据信息，进一步从 Prometheus 获取所有的观测实例信息，最终将生成的拓扑图存储到图数据库 arangodb 中。
- **cause-inference**：gala-spider 核心组件，提供根因定位功能。它通过订阅 kafka 的异常 KPI 事件触发异常 KPI 的根因定位流程，并基于 arangodb 获取的拓扑图来构建故障传播图，最终将根因定位的结果输出到 kafka 中。
- **Prometheus**：时序数据库，gala-gopher 组件采集的观测指标数据会上报到 Prometheus，再由 gala-spider 做进一步处理。
- **kafka**：消息中间件，用于存储 gala-gopher 上报的观测对象元数据信息，异常检测组件上报的异常事件，以及 cause-inference 组件上报的根因定位结果。
- **arangodb**：图数据库，用于存储 spider-storage 生成的拓扑图。
- **gala-gopher**：数据采集组件，详细内容参见 [gala-gopher 项目](https://gitee.com/openeuler/A-Ops/tree/master/gala-gopher)。
- **arangodb-ui**：arangodb 提供的 UI 界面，可用于查询拓扑图。

## 快速开始

### gala-spider 软件部署

#### spider-storage 软件部署

1. 基于源码编译、安装、运行

   - 构建

     ```
     /usr/bin/python3 setup.py build
     ```

   - 安装

     ```
     /usr/bin/python3 setup.py install
     ```

   - 运行

     ```
     spider-storage
     ```

2. 基于rpm包安装运行

   - 安装

     ```
     yum install gala-spider python3-gala-spider
     ```

   - 运行

     ```
     systemctl start spider-storage
     ```

#### cause-inference 软件部署

开发中……

### gala-spider 外部依赖软件部署

- prometheus 部署
- kafka 部署
- **arangodb 部署**

#### arangodb 部署

我们使用的 arangodb 版本是 3.9 ，arangodb 官方部署文档参见：[arangodb部署](https://www.arangodb.com/docs/3.9/deployment.html) 。

1. 通过 docker 部署

   ```shell
   docker run -e ARANGO_NO_AUTH=1 -p 192.168.0.1:10000:8529 arangodb/arangodb arangod \
     --server.endpoint tcp://0.0.0.0:8529\
   ```

   选项说明：

   - `arangod --server.endpoint tcp://0.0.0.0:8529`：在容器中启动 arangod 服务，`--server.endpoint` 指定了服务器地址。

   - `-e ARANGO_NO_AUTH=1`：配置 arangodb 的身份认证的环境变量，`ARANGO_NO_AUTH=1` 表示不启动身份认证，即无需用户名/密码即可访问 arangodb 数据库，该配置值用于测试环境。
   - `-p 192.168.0.1:10000:8529`：建立本地 IP 地址（如 `192.168.0.1` 的 1000 端口）到 arangodb 容器的 8529 端口的端口转发。

   详细的部署文档参见：[通过docker部署arangodb](https://www.arangodb.com/docs/3.9/deployment-docker.html)。

## 使用指南

### 配置文件介绍

[配置文件介绍](docs/conf_introduction.md)

### 3D 拓扑图分层架构

![hier_arch](docs/images/hier_arch.png)

观测对象说明：
1. Host：主机/虚拟机节点
    - machine_id：主机ID，用于标识网络中的一台主机/虚拟机。
  
2. Container：容器节点
    - container_id：容器ID，用于标识主机/虚拟机上的容器。
    - machine_id：主机ID，用于关联容器所属的主机/虚拟机。
    - netns：容器所在的 net namespace 。
    - mntns：容器所在的 mount namespace 。
    - netcgrp：容器关联的 net cgroup 。
    - memcgrp：容器关联的 memory cgroup 。
    - cpucgrp：容器关联的 cpu cgroup 。
    
3. Task：进程节点
    - pid：进程ID，用于标识主机/虚拟机或容器上运行的一个进程。
    - machine_id：主机ID，用于关联进程所属的主机/虚拟机。
    - container_id：容器ID，用于关联进程所属的容器。
    - tgid：进程组ID。
    - pidns：进程所在的 pid namespace 。
    
4. Endpoint：进程的通信端点
    - type：端点类型，如 TCP 、UDP 等。
    - ip：端点绑定的 ip 地址，可选项。
    - port：端点绑定的端口号，可选项。
    - pid：进程ID，用于关联端点所属的进程ID。
    - netns：端点所在的 net namespace 。
    
5. Jvm：Java程序运行时
6. Python：Python程序运行时
7. Golang：Go程序运行时

8. AppInstance: 应用实例节点
    - pgid：进程组ID，用于标识一个应用实例。
    - machine_id：主机ID，用于关联应用实例所属的主机/虚拟机。
    - container_id：容器ID，用于关联应用实例所属的容器。
    - exe_file: 应用可执行文件，用于标识一个应用。
    - exec_file：应用被执行文件，用于标识一个应用。

### 接口文档

[拓扑图查询Restful API](docs/guide/zh-CN/api/3d-topo-graph.md)

### 如何新增观测对象
[如何新增观测对象](docs/how_to_add_new_observe_object.md)

### 如何开发其他呈现服务

[开发指南](docs/development_guidelines.md)

