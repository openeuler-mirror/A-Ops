# 1、开发指南

## 1.1 准备配置文件

确认想要增加到配置溯源的配置文件和其配置内容，确认该配置文件类型是否在当前已经支持的配置类型中。

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

将配置文件采用yang语言表示，并将yang放置在gala-ragdoll-1.0.0/yang_modules路径下。

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

  container yum {                                    // 特性

    description "the repo file in yum modules.";

    container openEuler.repo {                       // 配置文件名称

      description "The file name is openEuler.repo.";

      repo:path "openEuler:/etc/yum.repos.d/openEuler.repo";   //拓展1：path
      repo:type "ini";										   //拓展2：type
      repo:spacer "=";										   //拓展3：spacer

      list session {                                //配置项
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

当前的```ini```类型配置文件的解析脚本已经提供，开发者如果需要增加其他类型的配置溯源能力，则需要提供对应的解析脚本，注意通用性和拓展性。

### 1.3.1 增加ini类型配置

由于当前已经提供 **ini** 类别的解析和反解析脚本，可以直接将yang模型存放在gala-ragdoll-1.0.0/yang_modules路径下之后，直接进行功能测试即可。

### 1.3.2 增加其他类型配置

#### 1.3.2.1 创建类

- 存放位置：

打开gala-ragdoll-1.0.0/ragdoll/analy目录，当前目录下建立新类型的解析脚本，脚本名称采用类型 + config_parser命名。

当前类<class 'IniConfigParser'>提供ini类的通用处理逻辑，仅需要提供添加配置项和配置值的能力，不需要将具体的配置项设置为该类的属性。

 样例解析文件: ```gala-ragdoll-1.0.0/ragdoll/analy/ini_config_parser.py```

```
[root@openeuler-development-2-pafcm snn]# tree gala-ragdoll-1.0.0/ragdoll/analy/
gala-ragdoll-1.0.0/ragdoll/analy/
└── ini_config_parser.py

0 directories, 1 file

```

- 限制：

  目前在配置溯源内部，通过json对象来存储配置内容序列化后的数据，所以需要该object能够与json对象进行相互转换，并进行存储。

  当前对外提供可以使用的object转json对象的类型有三种: ini类型、key-value、json。

#### 1.3.2.2 提供该类型配置项解析和反解析能力

增加内部function，提供几项功能，包括功能点：将配置内容解析成该object对象（```read()```）和将object反解析成配置内容(```write()```)。

此处以ini类型为例进行讲解。

- 确认**ini**的基本格式为section，则在```IniConfigParser```类中提供通用处理逻辑。

  ```
  [section]
  option1 = value
  option2 = value
  ```

  处理逻辑：

  | 内部接口名称                               | 功能描述                                                     | 样例 |
  | ------------------------------------------ | ------------------------------------------------------------ | ---- |
  | sections()                                 | 返回所有的section 列表                                       |      |
  | add_sections()                             | 在当前的object内添加section                                  |      |
  | has_sections(section)                      | 查看当前object的section列表中是否包含某个section             |      |
  | copy_sections(section, new_section_name)   | 复制一个section，新的section名称为：new_section_name，其包含的options和value都相同 |      |
  | change_sections（pre_section, new_section) | 更改section的name                                            |      |
  | remove_sections(section)                   | 删除object中的某个section                                    |      |
  | options(section)                           | 返回section内设置的options列表                               |      |
  | has_option(section, option)                | 查看section内的option列表中是否含有option                    |      |
  | set_option(section, option, value=None)    | 设置section的option和value，且value默认为空                  |      |
  | remove_option(section, option)             | 移除section中的某个option                                    |      |
  | get(section, option)                       | 返回某个section下的某个option的value                         |      |
  | items(section)                             | 以dict的形式展示当前section下包含的option和value             |      |

- 对外提供接口列表

  | 函数名        | 函数功能                                | 输入参数     | 输出参数                     |
  | ------------- | --------------------------------------- | ------------ | ---------------------------- |
  | read(content) | 将配置文件解析成object类                | 配置文件内容 | 填充object的配置项，返回为空 |
  | write()       | 将ini_config_parser类反解析成原配置文件 | 空           | 配置文件内容                 |

#### 1.3.2.3 配置内容校验

上述的read()方法并没有根据yang 模型进行匹配，无法对输入的content进行校验，所以需要对外提供校验接口。如果开发者能保证输入配置文件内容与yang模型完全一致，也可以直接进行第二步，解析content并进行创建object。

校验接口统一在：```gala-ragdoll-1.0.0/ragdoll/utils/object_parse.py```中，开发者可自行将接口添加在该文件中。

校验能力的步骤可以分为三步：

- 根据模型创建object

- 解析content创建object

- 将两个object进行模糊匹配，生成最终校验后的的object

下面具体讲述详细步骤：

- 根据模型创建object

  - 前提---初始化object

    object_parse.py 中已经提供初始化object的接口，仅需要输入配置文件类型，将自动加载analy路径下的解析object，并进行初始化。

    调用方式如下：

    ```
    module_obj = self.create_object_by_type("ini")
    ```

  - 接口名称：

    ```
    add_ini_module_info_in_object(module, module_obj)
    ```

  - 参数：

    | 参数名称   | 参数含义                                                     | 类型样例                        | 说明                                                         |
    | ---------- | ------------------------------------------------------------ | ------------------------------- | ------------------------------------------------------------ |
    | module     | 该配置对应的yang模型文件                                     | <class 'libyang.schema.Module'> | 当前utils/yang_modules.py, 对外提供了getModuleByFilePath接口，可以获取file_path对应的yang模型。<br />样例：<br />file_path = "/etc/yum.repo/openEuler.repo"<br/>module = yang_modules.getModuleByFilePath(file_path)<br/>self.add_ini_module_info_in_object(module, repo) |
    | module_obj | 创建的空object对象，可以采用create_object_by_type(conf_type)的输出 | <class 'IniConfigParser'>       | 在前提--初始化object中已经交代如何创建空object，仅需要调用create_object_by_type（type）即可 |

  - 样例：

    以ini类型为例，示例接口实现为：

    ```
    # yang_module中提供基于modlue返回xpath的接口（getXpathInModule），且ini类型的yang模型的xpath的形式为固定的：
    	特性/配置文件/section/option的形式
    # 可以直接定义section和option的index
    SECTIONINDEX = 2
    OPTIONINDEX = 3
    
    def add_ini_module_info_in_object(self, module, module_obj):
        """
        desc: add module info in object.
        """
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(module)
        for d_xpath in xpath:
        real_path = d_xpath.split('/')
        section = real_path[SECTIONINDEX]
        option = real_path[OPTIONINDEX]
        if module_obj.has_sections(section):
        	module_obj.set_option(section, option)
        else:
            module_obj.add_sections(section)
            module_obj.set_option(section, option)
    ```

- 解析content创建object

  object提供了read（）的接口对配置文件内容进行解析，解析成带有value值的object。

  样例：

  ```
  # 先创建个空的object：
  content_obj = self.create_object_by_type("ini")
  # 调用object中的read()方法：
  content_obj.read(contents)
  ```

- 将两个object进行模糊匹配，生成最终校验后的的object

  由于两个object是同一个class结构，按照yang 模型里定义的配置项进行模糊匹配，并生成新的object，作为校验后的object。

  匹配规则：ini类型的配置文件在进行配置匹配时，考虑到可能存在section名不固定的场景，采用option来进行匹配是否为一个section。

  样例：

  ```
  # 匹配规则：
  def get_mactch_section(self, option_list, obj):
      """
      desc: Blur matches two objects by option
      """
      res = None
      # print("get_mactch_section option_list is : {}".format(option_list))
      for m_section in obj.sections():
      	m_options = list(obj.options(m_section))
      	# print("section is : {}, the option is : {}".format(m_section, m_options))
      	# print("option_list is : {}".format(option_list))
      	count = 0
      	for d_option in list(option_list):
      		if d_option in m_options:
      			count = count + 1
          if len(option_list) == 1 and count == 1:
      		res = m_section
      		break
      	else:
      		if count > 2:
      			res = m_section
      			break
      return res
      
  # 匹配：
  def parse_ini_content_to_object(self, module_obj, content_obj):
  	"""
  	desc: Match the two objects to produce the final valid object
  	"""
  	sections_mod = module_obj.sections()
      sections_cont = content_obj.sections()
      for c_section in sections_cont:
      	cont_options = content_obj.options(c_section)
      	m_section = self.get_mactch_section(cont_options, module_obj)
          for d_opt in cont_options:
          	if d_opt is "__name__":
              	continue
              value = content_obj.get(c_section, d_opt)
              if m_section is not None:
              	if res.has_sections(c_section):
                  	res.set_option(c_section, d_opt, value)
                  else:
                  	res.add_sections(c_section)
                      res.set_option(c_section, d_opt, value)
          return res
  ```

#### 1.3.2.4 在序列化逻辑中添加解析代码

在```gala-ragdoll-1.0.0/ragdoll/utils/object_parse.py```中存在接口---```parse_content_to_json```，该接口实现调用上述1.3.2.1到1.3.2.3章节所有的接口，其中需要用户将上述解析和校验接口添加到该接口中，需要新类型的处理逻辑。

样例为：

```
# 将content的内容填充到object内，object_with_content为输出结果。其中module为yang模型文件，real_object为通过create_object_by_type进行创建的object，无需开发者提供。

object_with_content = ""
if conf_type == "ini":                                //需要增加新类型的处理逻辑
    self.add_ini_module_info_in_object(module, real_object)
    object_with_content = self.parse_ini_content_to_object(repo, contents)
print("object_with_content is : {}".format(object_with_content))
```



#### 1.3.2.5 在反序列化逻辑中添加反解析代码

由于反解析时，本身就已经是满足要求的object，此时需要将object反解析成配置文件。

- 创建该类别转换成content的接口，其中obj为已经创建后的object

  ```
  def parse_object_to_ini_content(self, obj):
      """
      desc: parse the object to the content of type INI accroding the yang file.
      """
      content = obj.write()
      content_string = json.dumps(content, indent = 4, ensure_ascii= False)
      return content
  ```

- 将该接口添加到反序列化逻辑中：

  在```gala-ragdoll-1.0.0/ragdoll/utils/object_parse.py```中存在接口---```parse_json_to_content```，需要用户将上述反解析接口的调用添加到该接口中，需要新类型的处理逻辑。

  ```
  if d_object and conf_type == "ini":
      contents = self.parse_object_to_ini_content(d_object)
      print("contents is : {}".format(contents))
  ```

  

# 2、 开发者测试

## 2.1 yang模型的测试

目前测试框架中提供了yang模型的测试脚本，用于检测yang模型是否合规的检测。

其存放路径为：

```
gala-ragdoll-1.0.0/ragdoll/test/test_yang.py
```

### 2.1.1 执行测试用例

将yang模型放置在```gala-ragdoll-1.0.0/yang_modules```路径下后，可以直接切换```test```目录下，直接运行:

```
python3 test_yang.py
```

### 2.1.2 测试用例介绍

当前yang模型测试，一共包括三个用例： test_yang_module 、 test_yang_extension 和 test_yang_xpath。

- test_yang_module 

  - 该用例检测yang模型的语法是否正确，如果正确则用例通过，同时打印语法正确的yang模型：

    ```
    The result of test_yang_module is : xxx
    ```

  - 样例：

    ```
    The result of test_yang_module is : 
    [
    	'/home/snn/gala-ragdoll-1.0.0/yang_modules/openEuler-logos-openEuler.repo.yang'
    ]
    ```

- test_yang_extension 

  - 该用例输出yang模型中定义的拓展字段，当前规定这三条都必填，如果存在未填写的拓展字段，则用例执行失败。同时会打印所有的模型拓展字段结果：

    ```
    The result of test_yang_extension is : xxx
    ```

  - 样例：

    ```
    The result of test_yang_extension is : 
    {
        'openEuler-logos-openEuler.repo': {
        'path': 'openEuler:/etc/yum.repos.d/openEuler.repo', 
        'type': 'ini', 
        'spacer': '='
        }
    }
    ```

- test_yang_xpath

  - 该用例返回yang模型中的path列表，如果path获取成功则用例成功，如果存在未成功的path，则用例执行失败。同时会打印所有的模型列表：

    ```
    The result of test_yang_xpath is : xxx
    ```

  - 样例输出：

    ```
    The result of test_yang_xpath is : 
    [
    	'yum/openEuler.repo/session/name', 
    	'yum/openEuler.repo/session/baseurl', 
    	'yum/openEuler.repo/session/enabled', 
    	'yum/openEuler.repo/session/gpgcheck', 
    	'yum/openEuler.repo/session/gpgkey'
    ]
    ```

## 2.2 配置解析测试

目前测试框架中提供了yang模型的测试脚本，用于检测yang模型是否合规的检测。

其存放路径为：

```
gala-ragdoll-1.0.0/ragdoll/test/test_analy.py
```

### 2.2.1 执行测试用例

该测试用例目前仅针对**ini**类型的解析测试，如果开发者提供其他类型的配置解析，则需要自己实现测试用例。

该测试用例包含两个必要参数：**module** 和**file**。module为需要进行测试yang模型， file为配置文件，用于读取配置文件的内容，要求**该文件已经存在当前OS环境中**，否则则无效。

执行样例：

```
python3 test_analy.py -m openEuler-logos-openEuler.repo -f /etc/yum.repos.d/openEuler.repo
```

### 2.2.2 测试用例介绍

当前测试针，一共包括两个方面：按照配置类型创建object、配置解析和校验。

- 创建object

  该用例测试首先按照模型的拓展字段type进行创建object。

  - 用例执性成功则会打印：

    ```
    The object was successfully created.
    ```

  - 如果失败，将会打印：

    ```
    Failed to create object.
    ```

- 配置解析和校验

  该用例先读取```-f```中指定的配置文件的内容，然后与yang模型创建的object进行匹配，测试最后的object是否可用。

  - 转换成功，将会打印转换成功的信息，并得到具体的object信息：

    ```
    The yang module is successfully converted to object!
    ######### object detail start #########
    the sections is : odict_keys(['OS', 'obs'])
    OS's items is : 
    {
    	'name': 'OS', 
    	'baseurl': 'https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/aarch64/', 
    	'enabled': '0', 
    	'gpgcheck': '0'
    }
    ######### object detail end #########
    ```

  - 将配置进行转换json测试，如果测试成功则会打印转换后的json值：

    ```
    content_string is : {
        "OS": {
            "name": "OS",
            "baseurl": "https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/aarch64/",
            "enabled": "0",
            "gpgcheck": "0"
        }
    }
    Current object is successfully to converted in this project!
    ```

## 2.3 配置反解析测试

目前测试框架中提供了yang模型的测试脚本，用于检测yang模型是否合规的检测。

其存放路径为：

```
gala-ragdoll-1.0.0/ragdoll/test/test_reverse_analy.py
```

### 2.3.1 执行测试用例

该测试用例目前仅针对**ini**类型的反解析测试，如果开发者提供其他类型的反配置解析，则需要自己实现测试用例。

但在该用例里需要调用上述2.2节的测试用例，获取已经填充了配置项的object。所以测试用例仍需要包含两个必要参数：**module** 和**file**。module为需要进行测试yang模型， file为配置文件，用于读取配置文件的内容，要求**该文件已经存在当前OS环境中**，否则则无效。

执行样例：

```
python3 test_reverse_analy.py -m openEuler-logos-openEuler.repo -f /etc/yum.repos.d/openEuler.repo
```

### 2.3.2 测试用例介绍

忽略2.1节的打印日志，反解析成功，则会打印日志：

```
############ object -> content ############
The object is successfully converted to content!
The content is : 
[OS]
name = OS
baseurl = https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/aarch64/
enabled = 0
gpgcheck = 0
```

