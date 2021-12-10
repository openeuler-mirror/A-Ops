# 1、开发指南

### 目录结构

```
├── db_process           # 从DB获取数据的处理程序
│   ├── data_collector.py    # 公共接口定义
│   ├── kafka_collector.py   # kafka采集器源码
│   ├── prometheus_collector.py # prometheus采集器源码
│   └── xxx_collector.py     # xxx采集器源码
├── controllers          # MVC控制器定义
│   └── gala_spider.py       # gala-spider REST API实现源码
├── daemon.py            # 主程序2(开发自验用，DB采用kafka、UI采用neo4j)
├── data_process         # 数据处理目录
│   ├── data_to_entity.py    # 原始数据转换为各种对象以及对象间关系，整合成entity实例
│   ├── models.py			# 内部数据结构定义
│   ├── prometheus_process.py# DB为prometheus的数据预处理流程
│   └── xxx_process.py       # DB为xx的数据预处理流程
├── encoder.py
├── __init__.py
├── __main__.py          # 主进程
├── models               # MVC模型定义
├── swagger              # 对外接口定义
│   └── swagger.yaml         # REST API接口文档
├── test                 # 开发者自测试程序
│   └── test_gala_spider_controller.py  # REST API测试源码
├── ui_agent             # 数据对接UI处理目录
│   ├── show_process.py      # UI为neo4j的对接处理程序
│   └── xxx_show_process.py  # UI为xxx的对接处理程序
├── util                 # 基础库文件
│   └── conf.py              # 配置文件解析程序
└── util.py
```

### 如何新增DB agent

​	DB用于存放gala-gopher采集的实时数据，gala-spider会从DB获取数据进行处理。目前gala-spider支持DB为kafka、promecheus，可以根据实际增加对其他数据库的支持。

下面以增加prometheus为例介绍：

1. 在配置文件gala-spider.yaml中增加对应配置项：

   ```
   global:
       data_source: "prometheus         ---切换为“prometheus”采集数据
   
   prometheus:                          ---新增prometheus的配置信息 
       broker:
       base_url: "http://localhost:9090/"
       instant_api: "/api/v1/query"
       range_api: "/api/v1/query_range"
       step: 1
   ```

2. 在db_agent目录增加xx_collector.py文件：

   ```
   1、配置信息获取：
      base_url=prometheus_conf.get("base_url")
      instant_api=prometheus_conf.get("instant_api")
      range_api=prometheus_conf.get("range_api")
      
   2、当前时间点观测数据获取：
      PrometheusCollector              ---主要从Prometheus获取数据，并做有效信息过滤
   ```

3. 在data_process目录增加xxx_process.py文件，并在data_to_entity.py中增加预处理函数挂钩：

   ```
   1、定义PrometheusProcessor数据处理流程
   	collect_observe_entities        ---获取数据
   	aggregate_entities_by_label     ---聚合数据，prometheus需要聚合
   	...
   	
   2、在拓扑绘制程序data_to_entity.py中get_observe_entities函数增加prometheus预处理函数挂钩
   	def get_observe_entities() -> List[dict]:
           ...
           if _db_agent == "prometheus":
               entities = g_prometheus_processor.get_observe_entities()
   ```

### 如何新增UI agent

​	UI可以图形化呈现实时的拓扑结构，目前gala-spider支持的UI为neo4j和A-Ops UI，可以根据实际增加对其他UI的支持。下面以新增neo4j为例：

1. 在配置文件gala-spider.yaml中增加对应配置项：

   ```
   global：
       ui_source: "neo4j"            ---切换为“neo4j”UI显示器
   
   neo4j:                            ---新增neo4j的配置信息
       address: http://localhost:7474
       username: 
       password: 
       timer: 5
   ```

2. 在ui_agent目录增加xxx_show_process.py拓扑绘制对接处理文件：

   ```
   1、引入对应的python子包
       from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
   
   2、获取data_to_entity.py处理后的拓扑绘制数据实例
      entity包含了各个对象间关系，比如进程和link间、进程和进程之间、link和host之间等等
       res, code = get_observed_entity_list()  ---entity实例可参考swagger/swagger.yaml文件   
       
   3、将entity实例信息转化成UI绘制信息
       Node()                        ---转换为节点
       Relationship()                ---转换为关系
       ...
       
   备注：gala-spider提供了REST API接口：http://x.x.x.x:11115/gala-spider/api/v1/get_entities，可以参考A-Ops UI获取数据，绘制拓扑。
   ```

### 如何变更处理逻辑

```
目前暂不支持。
```