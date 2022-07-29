# gala-anteater 介绍

gala-anteater是一款基于AI的操作系统异常检测平台。主要涵盖时序数据预处理、异常点发现、以及异常上报等功能。基于线下预训练、线上模型的增量学习与模型更新，能够很好地适应于多维多模态数据故障诊断。

## 1. 安装gala-anteater

支持的python版本：3.7+

### 1.1 方法一：Docker镜像安装（适用于普通用户）

#### 1.1.1 Docker镜像制作

请在工程`./gala-anteater`目录下，执行下面的命令，将`gala-anteater`工程文件打包成Docker镜像。

```
docker build -f Dockerfile -t gala-anteater:1.0.0 .
```

注：根据环境网络情况，可能需要修改`Dockfile`文件中的`pip`源地址

#### 1.1.2 Docker镜像运行

执行下面的命令，运行Docker镜像，请配置相应的kafka和prometheus信息

```
docker run -d --env kafka_server={kafka_server} --env kafka_port={kafka_port} --env prometheus_server={prometheus_server} --env prometheus_port={prometheus_port} -it gala-anteater:1.0.0
```



#### 1.1.3 日志查看

日志文件路径：`./gala-anteater/logs/`

#### 1.1.4 运行结果查看

如果检测到异常，检测结果输出到`Kafka`中，默认`Topic`为：`gala_anteater_hybrid_model`，也可以在`./cnfiguration/`中修改配置



### 1.2 方法二：从本仓库源码安装运行（适用于开发者）

#### 1.2.1 下载源码

```
 git clone https://gitee.com/openeuler/A-Ops.git
```

#### 1.2.2 安装python依赖包  

工程`./gala-anteater`目录下执行下面命令：

```bash
pip3 install requirements.txt
```
或者
```bash
pip3 install apscheduler confluent_kafka joblib numpy pandas requests scikit-learn torch
```
#### 1.2.3 程序运行

```
python main.py --kafka_server localhost --kafka_port 9092 --prometheus_server localhost --prometheus_port 9090
```

注：其中kafka_server、kafka_port、prometheus_server、prometheus_port换成实际配置

#### 1.2.4 日志查看

日志文件路径：`./gala-anteater/logs/`

#### 1.2.5 运行结果查看

如果检测到异常，检测结果输出到`Kafka`中，默认`Topic`为：`gala_anteater_hybrid_model`，也可以在`./cnfiguration/`中修改配置。

## 2. 快速使用指南

### 2.1 启动gala-anteater服务

按照1中的方式启动服务，命令如下：

```shell
docker run -d --env kafka_server={kafka_server} --env kafka_port={kafka_port} --env prometheus_server={prometheus_server} --env prometheus_port={prometheus_port} -it gala-anteater:1.0.0
```

或者

```shell
python main.py --kafka_server localhost --kafka_port 9092 --prometheus_server localhost --prometheus_port 9090
```

启动结果，可查看运行日志。

### 2.2 异常检测结果信息查看

gala-anteater输出异常检测结果到kafka，可使用kafka命令查看异常检测结果，具体命令如下：

```bash
bin/kafka-console-consumer.sh --topic gala_anteater_hybrid_model --from-beginning --bootstrap-server localhost:9092
```

## 3. 异常检测结果API文档

### 3.1 API说明

异常检测结果默认输出到`kafka`中，也可存储到`arangodb`中，供第三方运维系统查询、集成。数据格式遵循`OpenTelemetry V1`规范。

本文档介绍异常检测格式，`kafka、arangodb`的API参考其官方文档。

### 3.2 数据示例

```json
{
"Timestamp": 1659075600, 
"Attributes": {"Entity_ID": "4f2eb1a8378b428f85af0a6c0cxxxxxx_ksliprobe_1513_18"}, 
"Resource": {
	"anomaly_score": 1.0, 
	"anomaly_count": 13, 
	"total_count": 13, 
	"duration": 60, 
	"anomaly_ratio": 1.0, 
	"metric_label": {"machine_id": "4f2eb1a8378b428f85af0a6c0cxxxxxx", "tgid": "1513", "conn_fd": "18"}, 
	"recommend_metrics": {
		"gala_gopher_tcp_link_notack_bytes": {
			"label": {
				"__name__": "gala_gopher_tcp_link_notack_bytes", 
				"client_ip": "x.x.x.165", 
				"client_port": "51352", 
				"hostname": "localhost.localdomain", 
				"instance": "x.x.x.172:8888", 
				"job": "prometheus-x.x.x.172", 
				"machine_id": "4f2eb1a8378b428f85af0a6c0cxxxxxx", 
				"protocol": "2", 
				"role": "0", 
				"server_ip": "x.x.x.172", 
				"server_port": "8888", 
				"tgid": "3381701"}, 
			"score": 0.24421279500639545}, 
		"gala_gopher_file_system_Used": {
			"label": {
				"Blocks": "46203120", 
				"File_sys": "/dev/mapper/xxxxxxos-root", 
				"Inodes": "2951536", 
				"MountOn": "/", 
				"__name__": "gala_gopher_file_system_Used", 
				"hostname": "localhost.localdomain", 
				"instance": "x.x.x.172:8888", 
				"job": "prometheus-x.x.x.172", 
				"machine_id": "4f2eb1a8378b428f85af0a6c0cxxxxxx"}, 
			"score": 4.191468075953953}, 
		"gala_gopher_file_system_Free": {
			"label": {
				"Blocks": "46203120", 
				"File_sys": "/dev/mapper/euleros-root", 
				"Inodes": "2951536", 
				"MountOn": "/", 
				"__name__": "gala_gopher_file_system_Free", 
				"hostname": "localhost.localdomain", 
				"instance": "x.x.x.172:8888", 
				"job": "prometheus-x.x.x.172", 
				"machine_id": "4f2eb1a8378b428f85af0a6c0cxxxxxx"}, 
			"score": 4.098333158568109}, 
		}, 
    "metric_id": "gala_gopher_ksliprobe_recent_rtt_nsec"}, 
"SeverityText": "WARN", 
"SeverityNumber": 14, 
"Body": "Abnormal: this unusual event may be impacting client-side sli performance."
}
```

