# 1、开发指南

## 1.1 准备配置文件

确认想要增加到配置溯源的配置文件和其配置项

样例：

```shell
/etc/yum.repos.d/openEuler.repo

[OS]
name=OS
baseurl=https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
enabled=1
gpgcheck=0
gpgkey=http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler

```

## 1.2 准备yang文件

将配置文件采用yang语言表示，并将yang放置在python-flask-server\yang_modules路径下。

注意：按照“特性/配置文件/配置项”的维度进行编写yang文件，其中拓展字段为path表示其在os的路径。

支持定义三个拓展字段：

| 拓展字段名称 | 拓展字段格式           | 样例                                      |
| ------------ | ---------------------- | ----------------------------------------- |
| path         | OS类型：配置文件的路径 | openEuler:/etc/yum.repos.d/openEuler.repo |
| type         | 配置文件类型           | ini、key-value、json、text等              |
| spacer       | 配置项和配置值的中间键 | ” “、”=“、”：“等                          |

样例：

```
/******************************************************
* Copyright (C) 2021 Huawei Technologies Co., Ltd. All rights reserved.
* Module description & tree structure
******************************************************/
module openEuler-logos-openEuler.repo {
  namespace "urn:huawei:yang:openEuler-logos-openEuler.repo";
  prefix "repo";

  organization
    "Huawei Technologies Co., Ltd.";

  contact
    "Huawei Industrial Base
     Bantian, Longgang
     Shenzhen 518129
     People's Republic of China
     Website: http://www.huawei.com
     Email: support@huawei.com";

  description
    "This module contains a collection of YANG definitions for
     yum repo.
     The real path is : /etc/yum.repos.d/openEuler.repo";

  revision 2021-05-13 {
    description "Initial revision.";
    reference "";
  }

  extension path{
    argument "filePath";
    description "The real path corresponding to the repo file.";
  }

  extension type{
     argument "type";
     description "The type of this configuration file.";
  }

  extension spacer{
    argument "spacer";
    description "Spacer between configuration item and configuration value.";
  }

  container yum {

    description "the repo file in yum modules.";

    container openEuler.repo {

      description "The file name is openEuler.repo.";

      repo:path "openEuler:/etc/yum.repos.d/openEuler.repo";
      repo:type "ini";
      repo:spacer "=";

      list session {
        key "name";
        description "The first configuration item in repo, and the name of the configuration item is OS.";

        leaf name {
          type string;
          description "The name of the yum source of this OS.";
        }

        leaf baseurl {
          type string;
          description "The remote address of the yum source of this OS.";
        }

        leaf enabled {
          type string;
          description "Whether the yum source of this OS is enabled.";
        }

        leaf gpgcheck {
          type string;
          description "Whether the gpgcheck of the yum source of this OS is enabled.";
        }

        leaf gpgkey {
          type string;
          description "If gpgcheck is enabled, gpgkey is the corresponding key address.";
        }
      }
    }
  }
}
```

## 1.3 准备解析和反解析脚本

解析脚本需要实现从配置文件到object的转换。

当前的ini类型配置文件的解析脚本已经提供，开发者如果需要增加其他类型的配置溯源能力，则需要提供对应的解析脚本，注意通用性和拓展性。

代码存放目录样例：

```
├── swagger_server         // 源码目录
│   ├── analy			  // os配置文件 --> object
│   │   └── ini_config_parser.py    //ini类，如果需要增加其他类型的配置纳管，则需要自己写类似脚本
```

- ini类的解析脚本

  当前ini类对外提供的函数列表为：

| 函数名           | 函数功能                                         | 引用样例 |
| ---------------- | ------------------------------------------------ | -------- |
| read(content):   | 将配置文件解析成object类                         |          |
| items(key_path): | 获取key_path对应的所有option和value； dict风格； |          |
| write():         | 将ini_config_parser类反解析成原配置文件          |          |

# 2、 开发者自测

## 2.1 yang模型的测试

开发者测试框架中提供了test_yang.py，提供检测yang模型是否合规的检测。

将yang模型放置在python-flask-server\yang_modules路径下后，可以直接切换test目录下，直接运行test_yang.py。输出其yang结构则表示yang模型格式正确。

样例输出：

```
module example:
   module: openEuler-logos-openEuler.repo
     +--rw yum
     +--rw openEuler.repo
     +--rw sesstion* [name]
        +--rw name        string
        +--rw baseurl?    string
        +--rw gpgcheck?   string
        +--rw gpgkey?     string
```

## 2.2 解析脚本的测试

开发者测试框架中提供了test_analy.py。

- 开发者将自己新建的解析脚本和原配置文件内容作为test_analy.py的入参，进行调用，查看转换结果。

  ```
  测试样例：python3 test_analy.py openEuler_repo content
  输出样例：
  >>> type(repo)
  <class 'swagger_server.analy.ini_config_parser.IniConfigParser'>
  >>> repo.sections()
  odict_keys(['OS'])
  >>> repo.options('OS')
  odict_keys(['__name__', 'name', 'baseurl', 'enabled', 'gpgcheck', 'gpgkey'])
  >>> repo.items('OS')
  {
      'name': 'OS', 
      'baseurl': 'https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/', 
      'enabled': '1', 
      'gpgcheck': '0', 
      'gpgkey': 'http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler'
  }
  ```

## 2.3 反解析脚本的测试：

开发者测试框架中提供了test_reverse_analy.py。

- 开发者将自己新建的类作为test_reverse_analy.py的入参，进行调用，查看转换结果。

  ```
  测试样例：python3 test_reverse_analy.py openEuler_repo
  输出样例：
  [OS]
  name=OS
  baseurl=https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
  enabled=1
  gpgcheck=0
  gpgkey=http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler
  ```

