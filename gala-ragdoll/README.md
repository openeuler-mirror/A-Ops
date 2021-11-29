# gala-ragdoll

## 介绍

gala-ragdoll是基于OS的配置托管服务，能够实现对OS配置的集群式管理，屏蔽不同OS类型的配置差异，实现统一的、可溯源的、预期配置可管理的可信的OS配置运维入口。

## 快速开始
### 基于源码编译、安装、运行
- 安装依赖

  配置21.09 Epol的镜像源（地址：[镜像源地址](https://repo.openeuler.org/openEuler-21.09/EPOL/main/x86_64/)），然后安装安装依赖
```
yum install -y python3-devel python3-cffi gcc cmake pcre2-devel libyang python3-libyang
pip3 install -r requirements.txt
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
```
python3 -m ragdoll
```

### 基于rpm包运行安装
- rpm安装
```
yum install python3-gala-ragdoll gala-ragdoll
```

- 运行
```
systemctl start gala-ragdoll
```

- 详情可以参考：

  [基于rpm安装指导](https://gitee.com/openeuler/A-Ops/blob/master/gala-ragdoll/installDoc)

## 运行后的REST API使用

- 默认提供的REST API地址为：

```
http://localhost:port/ui/
```

- 当前采用swagger框架定义REST API:


```
http://localhost:port/swagger.json
```

- 详情可以参考：

  [配置溯源使用指导](https://gitee.com/openeuler/A-Ops/blob/master/gala-ragdoll/doc/instruction_manual.md)

## 总体介绍

gala-ragdoll是一个OS场景下的配置托管服务，能够实现对OS配置的集群式管理，屏蔽不同OS类型的配置差异，实现统一的、可溯源的、预期配置可管理的可信的OS配置运维入口。

### 模块划分
- UI
基于配置溯源能力，提供UI界面，由系统的管理员进行业务的分配和管理，同时进行自定义管控OS中的配置文件。
附：UI为A-OPS对外提供的统一界面，再此不过多介绍。
- 配置溯源服务
  服务层对外提供七块功能，分别为：

  - 配置域的管理
    - 配置域的创建
    - 配置域的删除
  - 配置域关联node
    - 在配置域中增加管理的node信息
    - 查询配置域中已经管理的node信息
    - 删除配置域内的node
  - 配置域添加配置文件
    - 给指定配置域中添加纳管配置文件和预期值。预期值为非必填项，如果给出，则直接用给出的配置作为基线，否则采用node的实际配置作为基线值
    - 查询配置域中已经纳管的配置文件和预期值
    - 查询当前配置溯源服务纳管的配置文件和预期值的总列表
  - 配置校验
    - 查询实际配置
    - 查询预期配置
    - 获取配置域的同步状态
  - 配置同步
    - 发起同步请求，将预期配置生效到对应的node中
  - 配置监控
    - 设置哪些配置进行监控，按照设定频率进行定期获取实际配置，刷新配置域的同步状态
  - Git仓存储
    - 存储服务层相关的数据，包括：域与机器的关系、域与配置的关系、配置序列化之后的数据
- 节点配置文件读写
与真实节点之间进行交互，涉及配置的读、写和扩展模块的执行（配置生效）。
该部分也由A-OPS中提供基于基于ansible的node配置操作接口。

### 整体流程
![all_options](doc/pic/all_option)

### 运行框架
![runtime_arch](doc/pic/arch)

### 配置溯源差异样例

![diff_example](doc/pic/git_diff)

## 详细介绍
### 设计文档

[设计文档](doc/design.md)

### 使用指导

[使用指导](doc/instruction_manual.md)

### 开发其他类型配置
[开发指南](doc/development_guidelines.md)

### 测试框架介绍
[测试框架介绍](gala-ragdoll/test/README.md)

