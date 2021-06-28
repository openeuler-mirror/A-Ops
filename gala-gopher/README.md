# gala-gopher

## 介绍
gala-gopher是A-OPS中的探针组件


## 使用说明
#### 1、安装依赖
i. 安装开发库
```bash
yum install cmake -y
yum install gcc-c++ -y
yum install libconfig-devel -y
yum install librdkafka-devel -y
yum install libmicrohttpd-devel -y
```

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
