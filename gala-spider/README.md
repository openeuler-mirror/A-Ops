# gala-spider

## 介绍
gala-spider是用于架构感知拓扑绘制服务，该程序提供一个配置文件，支持拓扑算法可替换、DB源可替换、UI程序可替换以及metric信息可配置等，方便用户使用；

## 快速开始

### 基于源码编译、安装、运行

- 安装依赖

  依赖模块安装

  ```bash
  yum install -y configparser multiprocessing
  # DB源采用kafka
  yum install -y python3-kafka-python
  # UI程序采用neo4j
  yum install -y python3-py2neo
  ```

- 构建

  ```
  /usr/bin/python3 setup.py build
  ```

- 安装

  ```
  /usr/bin/python3 setup.py install
  ```

- 运行

  ```bash
  python3 -m spider
  ```

### 基于rpm包安装运行

- 安装

  ```
  yum localinstall gala-spider.rpm
  ```

- 运行

  ```
  gala-spider
  ```

## 总体介绍

gala-spider用于架构感知探测结果呈现，可以根据各个节点上报的观测数据，整合分析得到整个集群的拓扑关系以及拓扑指标信息。库上代码支持数据库是kafka、UI是neo4j的链路拓扑绘制服务；gala-spider有良好的扩展性，DB可支持prometheus、telemetry 等，UI层可替换，以及拓扑算法可替换，可以发挥社区的力量丰富展示能力；gala-spider中的几个部件：

- 实现源码

  主要包括db_agent、data_process和ui_agent目录，分别实现数据库数据初步处理、拓扑绘制算法处理和对接UI展示等功能；gala-spide支持DB、UI以及拓扑算法可替换，需要在config/gala-spider.conf中配置正确的db_agent和ui_agent，主程序会读取配置信息并拉起相关处理进程。

- 部署配置文件

  gala-spider运行配置文件，可自定义具体使用的DB（kafka/promecheus等）、UI（neo4j等）；当前拓扑绘制算法不支持自定义；

### 运行架构

![topo_logic](doc/pic/topo_logic.png)

### 接口文档

[Restful API](doc/swagger.yaml)

## 详细介绍

### 配置文件介绍

配置文件介绍

### 如何开发其他呈现服务

开发指南

