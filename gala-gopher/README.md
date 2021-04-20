# gala-gopher

## 介绍
gala-gopher是A-OPS中的探针组件


## 使用说明
#### 1、安装依赖
i. 安装libconfig开发库
```bash
yum install libconfig-devel -y
yum install librdkafka-devel -y
```
ii. 安装taosdata客户端<br>
[TaoData安装指南](https://www.taosdata.com/cn/getting-started/#%E9%80%9A%E8%BF%87%E5%AE%89%E8%A3%85%E5%8C%85%E5%AE%89%E8%A3%85)

#### 2、构建
```bash
sh build.sh
```

#### 3、安装
```bash
sh install.sh
```

#### 4、运行
```bash
gala-gopher
```

#### 5、配置文件介绍
[配置文件介绍](doc/conf_introduction.md)

#### 6、数据流介绍
![dataflow](doc/dataflow.jpg)

## 探针开发技术规范
[如何开发探针](doc/how_to_add_probe.md)
