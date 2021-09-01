gala-ragdoll的使用指导
============================

本文基于当前已支持的yum源的配置文件/etc/yum.repos.d/openEuler.repo为例，讲解如何将该配置文件进行纳管。

### 配置文件介绍

```/etc/yum.repos.d/openEuler.repo```是用来规定yum源地址的配置文件，该配置文件内容为：

```
[root@openeuler-development-2-pafcm root]# cat /etc/yum.repos.d/openEuler.repo
[snn]
name = snn
baseurl = https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
enabled = 1
gpgcheck = 0
```

### yang模型介绍

`/etc/yum.repos.d/openEuler.repo`采用yang语言进行表示，参见`gala-ragdoll/yang_modules/openEuler-logos-openEuler.repo.yang`;
其中增加了三个拓展字段：

| 拓展字段名称 | 拓展字段格式           | 样例                                      |
| ------------ | ---------------------- | ----------------------------------------- |
| path         | OS类型：配置文件的路径 | openEuler:/etc/yum.repos.d/openEuler.repo |
| type         | 配置文件类型           | ini、key-value、json、text等              |
| spacer       | 配置项和配置值的中间键 | ” “、”=“、”：“等                          |

附：yang语言的学习地址：https://tonydeng.github.io/rfc7950-zh/

### 通过配置溯源创建域

#### 查看配置配文件

gala-ragdoll中存在配置溯源的配置文件

```
[root@openeuler-development-1-1drnd ~]# cat /etc/ragdoll/gala-ragdoll.conf
[git]                                       // 定义当前的git信息：包括git仓的目录和用户信息
git_dir = "/home/confTraceTestConf" 
user_name = "songnannan"
user_email = "songnannan2@huawei.com"

[collect]                                  // A-OPS 对外提供的collect接口
collect_address = "http://127.0.0.1:11111"
collect_api = "/manage/config/collect"

[ragdoll]
port = 11114

```

#### 创建配置域

调用```domain/createDomain```接口。

- input：

    ```
    POST /domain/createDomain
    
    [
        {
            "domain_name": "dnf",
            "priority": 0
        }
    ]
    ```

- output:

    ```
    {
      "code": 200,
      "msg": "All domain created successfully, 1 domain in total."
    }
    ```

    

- result：

        ```
        [root@openeuler-development-2-pafcm test]# tree /home/confTrace/
        /home/confTrace/
        └── dnf
        
        2 directories, 0 files

#### 添加配置域纳管node

- input:

    ```
    POST /host/addHost
    
    {
      "domainName": "dnf",
      "hostInfos": [
        {
          "ipv6": "",
          "ip": "210.22.22.155",
          "hostId": "551d02da-7d8c-4357-b88d-15dc55ee22ss"
        }
      ]
    }
    ```

- output：

    ```
    {
      "code": 200,
      "msg": "All host add hosts successfully, 1 host in total.                  \"
    }
    ```

    

- result

    ```
    [root@openeuler-development-2-pafcm test]# ll /home/confTrace/dnf
    total 4.0K
    -rw-r--r--. 1 root root 190 Jul 30 10:14 hostRecord.txt
    [root@openeuler-development-2-pafcm test]# cat /home/confTrace/dnf/hostRecord.txt
    "{'host_id': '551d02da-7d8c-4357-b88d-15dc55ee22ss',\n 'ip': '210.22.22.155',\n 'ipv6': None}"
    ```

    

#### 添加配置域配置

- input

  ```
  POST /management/addManagementConf
  
  {
    "domainName": "string",
    "confFiles": [
      {
        "filePath": "/etc/yum.repos.d/openEuler.repo",
        "contents": "
          			[OS]
                          name=OS
                          baseurl=https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
                          enabled=1
                          gpgcheck=0
                          gpgkey=http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler
          		  "
      }
    ]
  }
  ```

  

- output：

  ```
  {
    "code": 200,
    "msg": "All confs add management conf successfully, 1 confs in total.\                   \"
  }
  ```

  

- result

  ```
  [root@openeuler-development-2-pafcm test]# tree /home/confTrace/dnf
  /home/confTrace/dnf
  ├── hostRecord.txt
  └── yum
      └── openEuler.repo
  
  1 directory, 2 files
  [root@openeuler-development-2-pafcm test]# cat /home/confTrace/dnf/yum/openEuler.repo
  {
      "OS": {
          "name": "OS",
          "baseurl": "https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/",
          "enabled": "1",
          "gpgcheck": "0",
          "gpgkey": "http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler"
      }
  }
  ```

#### 查询预期配置

- input

  ```
  POST /management/getManagementConf
  
  {
    "domainName": "string"
  }
  ```

  

- output

  ```
  {
    "domainName": 'dnf',
    "confFiles": [
      { 
    	  "filePath": "openEuler:/etc/yum.repos.d/openEuler.repo",
    	  "contents": "
                      "OS": {
                          "name": "OS",
                          "baseurl": "https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/",
                          "enabled": "1",
                          "gpgcheck": "0",
                          "gpgkey": "http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler"
                       }
    	  			 "
    	 }]
  }
  ```

  

- result

 查询动作，不会产生result

#### 删除配置

- input

  ```
  {
    "domainName": "ll",
    "confFiles": [
      {
        "filePath": "/etc/yum.repo.d/openEuler.repo"
      }
    ]
  }
  ```

  

- output

  ```
  {
    "code": 200,
    "msg": "delete the conf in ll domian, the path including : /etc/yum.repos.d/openEuler.repo                  \"
  }
  ```

  

- result

  ```
  [root@openeuler-development-2-pafcm test]# cat /home/confTrace/ll/yum/openEuler.repo
  cat: /home/confTrace/ll/yum/openEuler.repo: No such file or directory
  ```

#### 查询实际配置

- input

  ```
  {
    "domainName": "dnf",
    "hostIds": [
      {
        "hostId": "551d02da-7d8c-4357-b88d-15dc55ee22ss"
      }
    ]
  }
  ```

  

- output

  ```
  [
    {
      "domainName": "dnf",
      "hostID": "551d02da-7d8c-4357-b88d-15dc55ee22ss",
      "confBaseInfos": [
        {
          "rpmName": "openEuler-repos",
          "filePath": "/etc/yum.repos.d/openEuler.repo",
          "spacer": None,
          "rpmVersion": "1.0",
          "rpmRelease": "3.0.oe1.aarch64",
          "fileOwner": "(root root)",
          "confType": None,
          "confContents": "
          				'snn': {
                              'name': 'snn',
                              'baseurl': 'https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/',
                              'enabled': '1',
                              'gpgcheck': '0',
                              'gpgkey': 'http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler'
                       	}",
          "fileAttr": "0644"
        }
      ]
    }
  ]
  ```

  

- result

 查询动作，不会产生result

#### 配置校验

- input

  ```
  {
    "domainName": "dnf"
  }
  ```

  

- output

  ```
  {
    "domainName": "dnf",
    "hostStatus": [
      {
        "hostId": "551d02da-7d8c-4357-b88d-15dc55ee22ss",
        "syncStatus": [
          {
            "file_path": "/etc/yum.repos.d/openEuler.repo",
            "isSynced": "NOT SYNCHRONIZE"
          }
        ]
      }
    ]
  }
  ```

  

- result

  校验动作，不产生结果

#### 配置同步

- input

  ```
  {
    "domainName": "dnf",
    "hostIds": [
      {
        "hostId": "551d02da-7d8c-4357-b88d-15dc55ee22ss"
      }
    ]
  }
  ```

  

- output

  ```
  [
    {
      "hostId": {
        "hostId": "551d02da-7d8c-4357-b88d-15dc55ee22ss"
      },
      "syncResult": [
        {
          "filePath": "/etc/yum.repos.d/openEuler.repo",
          "result": "SUCCESS"
        }
      ]
    }
  ]
  ```

  

- result

  - 同步前：

    ```
    [root@openeuler-development-2-pafcm test]# cat /etc/yum.repos.d/openEuler.repo
    [snn]
    name = snn
    baseurl = https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
    enabled = 1
    ```

    

  - 同步后：

    ```
    [root@openeuler-development-2-pafcm test]# cat /etc/yum.repos.d/openEuler.repo
    [OS]
    name = OS
    baseurl = https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
    enabled = 1
    gpgcheck = 0
    gpgkey = http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler"
    ```

  