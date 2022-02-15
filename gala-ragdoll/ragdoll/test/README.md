# gala-ragdoll测试框架介绍

gala-ragdoll 提供了基于flask_testing的单元测试框架，并实现了对配置溯源提供的REST API的基本功能测试。

## flask_testing 简介

Flask-testing是对unittest的一个封装，是为Flask提供的单元测试工具。
使用以前须要先用`create_app()`返回一个app便可使用，可使用`client`属性模拟客户端访问，
例如：`client.get('/', headers={'Cookie':cookie})`，
例如：`client.post('/', data=parama, follow_redirects=True)`。
其余使用方式与unittest类似。

详细的flask-testing介绍参考：http://www.pythondoc.com/flask-testing/index.html

## gala-ragdoll 的测试框架

gala-ragdoll 针对配置溯源服务提供了flask_testing的单元测试框架，主要分为基本功能测试和开发自测。

### 基本功能测试

- test_domain_controller

  针对域的三种操作提供其REST API的测试，每个测试模块中进行具体的功能测试。包括：设置域、查询域、删除域。

- test_host_controller

  针对node的三种操作提供其REST API的测试，每个测试模块中进行具体的功能测试。包括：添加node、查询域内的node、删除域内的node。

- test_management_controller

  针对纳管配置的三种操作提供其REST API的测试，每个测试模块中进行具体的功能测试。包括：添加配置、查询纳管配置、删除纳管配置

- test_confs_controller

  针对配置的四种操作提供其REST API的测试，每个测试模块中进行具体的功能测试。包括：查询实际配置、查询总支持的配置、配置校验、配置同步

### 开发自测

- test_yang.py

  测试yang模型是否合规

- test_config_model.py

  测试转换脚本的object是否能进行转换

- test_reverse_config_model.py

  测试反转换脚本是否能转换成object

