# gala-gopher 数据访问API

gala-gopher通过三种方式提供收集的原始数据，数据包含实体(被观测对象)数据和实体上的指标数据。API尽量在小版本间保持接口稳定性。

当前API版本是 `v0.1`

## http方式

本方式仅提供指标数据输出。

访问/metrics地址时返回如下内容：

```
# HELP tcp_link_rx_byte byte received of the tcp link.
# TYPE tcp_link_rx_byte gauge
tcp_link_rx_byte{pid="3426",client_ip="192.168.100.110",client_port="1235",server_ip="192.168.100.110",server_port="22"} 3812
```

返回的数据，由三部分组成：注释（HELP），类型（TYPE）和数据。

以# HELP开始的内容提供指标名和说明信息：

```
# HELP <metric_name> <doc_string>
```

以# TYPE开始的内容提供指标名和指标类型，TYPE注释行必须出现在指标的第一个样本之前。

```
# TYPE <metrics_name> <metrics_type>
```

除了# 开头的所有行是样本数据，遵循以下格式规范:

```
metric_name [
  "{" label_name "=" `"` label_value `"` { "," label_name "=" `"` label_value `"` } [ "," ] "}"
] value [ timestamp ]
```

metric_name和label_name必须遵循gala-gopher的观测对象和观测指标命名规范。value是一个float格式的数据，timestamp的类型为int64（从1970-01-01 00:00:00以来的毫秒数），timestamp默认为当前时间。具有相同metric_name的数据按照组的形式排列，每行由指标名称和标签键值对组合唯一确定。

## kafka方式

```
{"table_name": "tcp_link", "timestamp": 1301469816, "machine_id": "5002b12c68744d1a8e0309f7d00462a2", "pid": "35331", "process_name": "curl", "role": "1", "client_ip": "192.168.100.110", "client_port": "1235", "server_ip": "192.168.100.111", "server_port": "80", "protocol": "2", "rx_bytes": "1710139", "tx_bytes": "94", "packets_in": "324", "packets_out": "282", "retran_packets": "0", "lost_packets": "0", "rtt": "404", ...}
```

```
{"table_name": tablename, "timestamp": timestamp, "machine_id": machine_id, "key": value, ...}
```

## file方式

本方式仅提供实体数据输出。
提供gala-gopher.output.meta和gala-gopher.output.data文件分别描述元数据和数据，文件路径可配置。

文件gala-gopher.output.meta中内容：

```
tcp-link timestamp machine_id pid client_ip server_ip server_port [rx_bytes tx_bytes packets_in packets_out ...]
udp-link timestamp machine_id pid client_ip server_ip server_port [rx_bytes tx_bytes packets_in packets_out ...]
nginx-link timestamp machine_id pid client_ip virtual_ip virtual_port server_ip server_port ...
lvs-fullnat-link timestamp machine_id client_ip virtual_ip virtual_port local_ip server_ip server_port ...
lvs-dr-link timestamp machine_id client_ip virtual_ip virtual_port server_mac ...
haproxy-link timestamp machine_id pid client_ip virtual_ip virtual_port local_ip server_ip server_port ...
kafka-link timestamp machine_id pid producer_ip topic kafka_ip kafka_port consumer_ip consumer_port ...
rabbitmq-link timestamp machine_id pid producer_ip queue rabbit_ip rabbit_port consumer_ip consumer_port ...
etcd-link timestamp machine_id pid producer_ip url etcd_ip etcd_port watch_ip watch_port ...
process timestamp machine_id pid cmd path ...
container timestamp machine_id container_id [pids] ...
virtual_machine timestamp machine_id hostname [container_ids] [pids] [ips] [macs] ...
bare_matal timestamp machine_id hostname [vm_names] [container_ids] [pids] [ips] [macs] ...

```
每一行以实体类型开头，后面是该实体类型的属性以及指标，指标是可选的。

文件gala-gopher.output.data中内容：
tcp-link 1631351950 5002b12c68744d1a8e0309f7d00462a2 342695 192.168.100.110 1235 192.168.100.111 22 1710139 94 324 282 0 0 404
tcp-link 1631351950 5002b12c68744d1a8e0309f7d00462a2 342696 192.168.100.110 1238 192.168.100.111 80 1710139 94 324 282 0 0 404
```

```

## 命名规范

### 观测对象命名规范

### 观测指标命名规范
