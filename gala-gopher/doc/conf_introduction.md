配置文件介绍
================

## 介绍

gala-gopher启动必须的外部参数通过配置文件定义；主要的配置项包括：设置数据上报周期、数据库信息、探针定义、cache数据库配置等；

## 配置文件详解

配置文件开发路径归档在 `A-Ops/gala-gopher/config/gala-gopher.conf`。

配置文件各部分详解如下：

### global

```shell
global =									  -- gala-gopher引擎配置
{
    log_directory = "/var/log/gala-gopher";		-- gala-gopher引擎日志路径
    log_level = "debug";					   -- gala-gopher日志级别，可配置 "debug | info | error | warnning | fatal"
    egress = "kafka";						   -- 选择egress对接的数据库，可配置："kafka | prometheus | OpenTelemetry"；
};
```

### ingress 

```shell
ingress =									 -- 数据采集相关配置
{
    interval = 5;							  -- 探针数据采集周期(s)，如每5s触发探针数据采集
};
```

### egress

```shell
egress =									  -- 数据上报相关配置
{
    interval = 5;							   -- 探针数据上报egress周期(s)
    time_range = 5;							   -- 未用
};
```

### imdb

```shell
imdb =							       -- cache缓存规格，定义了支持的指标项规格
{
    max_tables_num = 1024;				-- cache最大支持的表个数，通常不可以比max_metrics_num小，每个metric对应一个table
    max_records_num = 1024;				-- 每张cache表最大记录数，通常每个metric在一个观测周期内产生1/N条观测记录
    max_metrics_num = 1024;				-- metric最大个数，定义了单节点最大的metric指标个数
    record_timeout = 60;                -- 记录的超时时间（秒），从cached表中读取记录时，若记录超过该时间未更新，则删除
};
```

### egress适配层配置

不同egress对应不同的配置，在conf中定义

```shell
web_server =							-- egress配置为prometheus，需要启动一个web server，对外提供查询metric指标的接口，promecheus会基于该接口查询节点指标信息；
{
    port = 8888;						-- 监听端口
};

kafka =									-- egress配置为kafka
{
    kafka_broker = "localhost:9092";
    kafka_topic = "gala_gopher";
    switch = "on";
};
```

### probes 

```shell
probes =								 -- native探针开关配置，定义gala-gopher需要启动的探针
(
    {
        name = "example";				   -- 探针名称，要求与native探针名一致，如example.probe 探针名为 example
        switch = "on";					   -- 运行时是否启动，native探针可配置 on | off
        interval = 1;					   -- 探针执行周期(s)
    },
    {
        name = "system_meminfo";
        switch = "off";
        interval = 1;
    },
);
```

### extend_probes

```shell
extend_probes =							 -- 三方探针开关配置
(
    {
        name = "redis";					  -- 探针名称，唯一即可
        command = "python3 /opt/gala-gopher/extend_probes/redis_probe.py"; -- 探针启动命令，自定义
        param = "";						  -- 启动参数设置，如设置执行周期
        switch = "on";					  -- 运行时是否启动，可配置 on | off | auto
    },
    {
        name = "dnsmasq";
        command = "/opt/gala-gopher/extend_probes/trace_dnsmasq";
        param = "";
        start_check = "ps axf | grep dnsmasq | grep -v grep | wc -l";	-- switch为auto时会根据start_check的执行结果判定是否需要启动探针；
        check_type = "count";	-- start_check执行结果的检查类型，count：表示执行结果>0时表示检查通过，否则检查失败，不启动探针
        switch = "auto";
    },
);
```

