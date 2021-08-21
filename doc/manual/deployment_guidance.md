# 1 框架概述

部署管理主要是基于ansible来对组件进行安装。

```yaml
│  
├─ansible_handler
│  │  README.md
│  │  
│  ├─example 模板示例
│  │  │  example_playbooks.yml 示例playbook
│  │  │  example_vars.yml 示例变量文件
│  │  │  
│  │  └─example 示例角色任务
│  │      ├─files 组件需要的文件目录，可以是软件包或运行时所需要的其他文件。
│  │      │      readme.md
│  │      │      
│  │      ├─tasks 示例任务
│  │      │      config_example.yml 配置示例说明
│  │      │      install_example.yml 安装示例说明
│  │      │      main.yml 任务入口示例说明
│  │      │      start_example.yml 启动示例说明
│  │      │      
│  │      └─templates 模板文件
│  │              example.j2 模板配置示例说明
│  │              
│  ├─inventory 组件的主机列表
│  │      elasticsearch
│  │      fluentd
│  │      ...
│  │      
│  ├─playbooks 组件的playbook入口文件
│  │      elasticsearch.yml
│  │      fluentd.yml
│  │      ...
│  │      
│  ├─roles 组件角色任任务
│  │  ├─elasticsearch
│  │  │  ├─tasks 组件的playbook中的具体task步骤组件的playbook中的具体task步骤
│  │  │  │      config_elasticsearch.yml 定义配置具体步骤。
│  │  │  │      install_elasticsearch.yml 定义安装具体步骤。
│  │  │  │      main.yml 任务执行的主脚本，会包含install、config、start以及自定义的yml文件。
│  │  │  │      start_elasticsearch.yml 定义启动步骤。
│  │  │  │      
│  │  │  └─templates 组件安装过程中需要的模板文件。安装时会根据配置值生成实际的文件。
│  │  │          elasticsearch.j2
│  │  │          
│  │  └─...
│  │              
│  └─vars 组件的变量文件
│          elasticsearch_vars.yml
│          fluentd_vars.yml
│          ...
│          
├─ansible_runner 调用ansible来执行任务的python接口
│      ansible_runner.py
│      inventory_builder.py
│      vault_handler.py
│      __init__.py
│      
└─tasks 任务文件，由一系列有序的的组件安装步骤组成
        XXX_task.yml
```


# 2 添加组件步骤

## 2.1 自定义组件模板

### 2.1.1 修改示例文件，制作自定义模板

- #### 组件playbook剧本文件

  ```yaml
  ---
  - hosts: example_hosts # 此处需套填写所安装组件配置的主机名。（建议按照统一生成的名称来处理）
    gather_facts: no
    user: root
    vars_files: # 需要引用变量文件时，加入vars文件
      - "../vars/example_vars.yml"
    vars: # 定义安装步骤的变量，在安装过程中可以根据需要修改是否启用
      install_example: true # 安装 example
      config_example: true # 配置 example
      start_example: true # 启动 example service
      create_user: true # 创建新的用户和组
    roles: # playbook中需要完成的角色剧本，可自定义，与顺序相关
      - ../roles/user # （1）创建用户 playbook
      - ../roles/example # （2） 安装 exampl playbook
  
  ```

- #### 组件vars变量文件

  ```yaml
  ---
  # 根据组件安装的实际需要来确定需要使用哪些变量，在安装过程中yaml中key会被替换成实际值
  
  # example 软件版本值
  example_version: 1.1.1
  
  # example 需要的用户与用户组名
  user: "example"
  group: "example"
  
  # 日志目录
  log_path: "log"
  
  # 安装目录
  install_dir: "/opt/example"
  
  # 使用的主机列表
  example_hosts: example_hosts
  
  ```

- #### 组件roles角色人物定义

  - ##### files目录

    - 放置组件需要的文件目录，可以是软件包或运行时所需要的其他文件。
    - 在files目录下的文件，playbook中可以直接引用，用于后续的拷贝、解压、修改等动作
    - 修改变量尽量使用templates中的模板文件，而非files文件。

  - ##### templates目录

    放置需要根据主机或变量动态生成的配置文件、Service文件等。为j2文件，使用jinja生成。

    ```yaml
    ## 模板文件是有相对固定的框架，如配置文件可以以软件中定义的配置文件为框架进行修改，service文件以规范的框架进行修改。自定义的模板同理。
    
    # 固定项
    
    http.port: 9200
    path.logs: /var/log/example
    
    
    # 可变项-直接使用vars中的变量
    # 如 example_vars中的配置项为：
    #   example_cluster_name: mycluster
    # 最终生成的配置项如下：
    # cluster.name: mycluster
    
    cluster.name: {{example_cluster_name}}
    
    # 可变项-使用主机清单中的配置变量
    # 如 主机清单中配置如下：
    # example_hosts:
    # hosts:
    #  192.168.1.1:
    #    ansible_host: 192.168.1.1
    #    example_id: example_node1
    #  192.168.1.2:
    #    ansible_host: 192.168.1.2
    #    example_id: example_node1
    #  192.168.1.2:
    #    ansible_host: 192.168.1.2
    #    example_id: example_node1
    # 最终生成的配置项如下：
    # 192.168.1.1主机上的配置文件为：node.name: example1
    # 192.168.1.2主机上的配置文件为：node.name: example2
    # 192.168.1.3主机上的配置文件为：node.name: example3
    node.name: {{example_id}} 
    
    # 可变项-根据主机生成配置项
    # 如 主机清单中配置如下：
    # example_hosts:
    # hosts:
    #  192.168.1.1:
    #    ansible_host: 192.168.1.1
    #    example_id: example_node1
    #  192.168.1.2:
    #    ansible_host: 192.168.1.2
    #    example_id: example_node1
    #  192.168.1.2:
    #    ansible_host: 192.168.1.2
    #    example_id: example_node1
    # 最终生成的配置项如下：
    # discovery.seed_hosts: ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
      {% for host in groups.elasticsearch_hosts -%}
          {% set host_ip = hostvars[host].ansible_host -%}
      discovery.seed_hosts: ["{{host_ip}}"]
      {% endfor -%}
  
  - ##### task目录
    - ###### main.yml
  
    ```yaml
    ---
    
    ## 包含常规流程，如需要特出处理，可以自定义添加
    # step1 安装组件
    - name: Install example
    include: install_example.yml
    when: install_example
    
    # step2 修改配置
    - name: Config example
    include: config_example.yml
    when: config_example
    
    # step3 启动服务
    - name: Start example
    include: start_example.yml
    when: start_example
    ```
  
    
      - ###### install_example.yml
  
    ```yaml
    ---
    ##  本文件中主要实现软件包的安装步骤，将软件包部署到目的位置
    ##  新版本ansible中安装rpm包，建议使用dnf，而非yum
    
    ###############################自己上传rpm软件包###########################
    # 1. 拷贝example_rpm到/tmp目录下， example_rpm为具体的文件名，定义在example_vars文件中
    - name: Copy rpm file to server
      copy:
        src: "{{ example_rpm }}"
        dest: /tmp/{{example_rpm}}
        mode: 755
    
    # 2. 安装/tmp/{{example_rpm}}软件包
    - name: install packages
      become: true
      become_user: root
      dnf:
        state: present #选择状态为present
        disable_gpg_check: true # 本地包可关闭gpg检查
        name: /tmp/{{example_rpm}}
    
    ###############################直接使用dnf安装软件包###########################
    # 如果openEuler版本中已经发布了该软件包，配置repo源即可下载
    - name: install packages
      become: true
      become_user: root
      dnf:
        state: present
        name:
          - example
    
    ###############################自己上传源码包###########################
    # 创建安装目录
    - name: mkdir install_path
      file: path={{install_path}} state=directory mode=0755
    
    # 复制软件包到目标目录
    - name: copy example
      unarchive: src=example-{{version}}.tar.gz dest={{install_path}} copy=yes
    
    # 修改权限
    - name: chown
      file: path={{install_path}} state=directory mode=0755 owner={{user}} group={{group}} recurse=yes
    ```
  
      - ###### config_example.yml
  
    ```yaml
    ---
    # 在本文件中主要定义需要配置的一些操作，包括配置文件修改，Service文件修改等
    
    # 使用jinja直接匹配模板中的配置文件。j2文件中的变量会自动替换，生成真实的配置。
    - name: Deploy elastic.yml
      template: src=templates/example.j2 dest={{example_config}}/example.yml mode=0755
    
    
    # 直接使用shell命令修改配置，可以定义自己需要的修改命令或shell脚本，在此处调用执行
    - name: Modify config file
      shell: |
        echo "xxx" >> {{example_config}}/example.conf
        echo "elasticsearch hard memlock unlimited" >> /etc/security/limits.conf
    ```
  
      - ###### start_example.yml
  
    ```yaml
    ## 本文件中主要用于启动组件
    
    ## 1. 启动服务
    ##############################systemctl 启动服务###############################
    # 服务类的组件可以直接使用systemctl控制，使用如下方式，设置state、enable等项来来拉起服务
    - name: Start example
      become_user: "{{user}}"
      service:
        name: example
        state: started
    
    ##############################脚本启动服务###############################
    # 如果组件没有服务化，可以使用脚本拉起服务，并指定配置文件。
    - name: Start example
      shell: "cd {{install_dir}}/bin && ./example-start.sh -daemon ../config/example.conf"
      become: yes
      become_user: root
    
    
    ## 2. 启动状态检查
    ################################服务状态采集##########################
    - name: collect facts about system services
      service_facts:
      register: services_state
    
    - name: Debug
      debug:
        var: services_state
    
    
    ##################################自定义的检查##############################
    # 检查服务状态
    - name: verify example service
      command: /usr/sbin/service example status
      changed_when: false
    
    # 检查端口监听状态
    - name: verify example is listening on 1111
      wait_for: port=111 timeout=1
    ```

### 2.1.2 将自定义模板的文件添加至框架中

可以使用example中的实例文件进行修改， 然后

```
│  example_playbooks.yml  文件名为"组件名.yml"，移动至install_ansible/playbooks
│  example_vars.yml 文件名为"组件名_vars.yml", 移动至install_ansible/vars
│
└─example 目录名为"组件名", 移动至install_ansible/roles
    ├─files
    │      readme.md
    │
    ├─tasks
    │      config_example.yml
    │      install_example.yml
    │      main.yml
    │      start_example.yml
    │
    └─templates
            example.j2

```

### 2.1.3 任务列表中添加组件

```yaml
---
step_list: # 步骤列表
 kafka: # 第一步安装kafka，可以使用默认模板
  enable: # false 置为false则跳过安装步骤，true执行安装步骤
  continue: # false 置为false则安装失败时终止任务，true执行安装失败时继续下一个组件安装
 example: # 第二步安装example自定义组件,将组件添加在合适的位置，并设置配置项
  enable: false
  continue: false
```

## 2.2 默认组件模板

### 2.2.1 默认组件列表

当前提供的默认组件包括：

| 组件名称      | 安装方式 | 版本   | 部署位置 |
| ------------- | -------- | ------ | -------- |
| zookeeper     | dnf      | 3.6.2  | all      |
| kafka         | dnf      | 2.6.0  | all      |
| prometheus    | dnf      | 2.20.0 | 主节点   |
| node_exporter | dnf      | 1.0.1  | all      |
| mysql         | dnf      | 8.0.26 | 主节点   |
| elasticsearch | dnf(官网镜像) | 7.14.0（随官网更新） | 主节点   |
| fluentd | dnf      | 1.13.3 | all |
| fluent-plugin-elasticsearch | dnf      | 5.0.5 | all      |

### 2.2.2 默认任务配置

#### （1） zookeeper

zookeeper主要负责集群管理，并且是kafka运行的基础，需要配置在集群的每个节点中。

- 主机配置

主机清单中需要有对每个节点的配置IP，节点ID：

```yaml
zookeeper_hosts:
  hosts:
    192.168.1.1:
      ansible_host: 192.168.1.1
      ansible_python_interpreter: /usr/bin/python3
      myid: 2
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
      myid: 1
    192.168.1.3:
      ansible_host: 192.168.1.3
      ansible_python_interpreter: /usr/bin/python3
      myid: 3

```

- 变量配置

zookeeper的变量包括：

```yaml
---
# zookeeper user group 用户名、用户组
user: "zookeeper"
group: "zookeeper"

# zookeeper data path data路径
data_dir: "data"
# zookeeper log path 日志路径
zookeeper_log_path: "log"
# zookeeper install path 安装路径
install_dir: "/opt/zookeeper"

# zookeeper port config 端口配置
leader_port: 2888
vote_port: 3888
client_port: 2181
```

#### （2）kafka

- 主机配置

  kafka 需要在安装zookeeper之后再安装。主及清单中需要配置kafka的端口，ID。同时需要配置zookeeper的IP与ID。

```yaml
kafka_hosts:
  hosts:
    192.168.1.1:
      ansible_host: 192.168.1.1
      ansible_python_interpreter: /usr/bin/python3
      kafka_id: 2
      kafka_port: 9092
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
      kafka_id: 1
      kafka_port: 9092
    192.168.1.3:
      ansible_host: 192.168.1.3
      ansible_python_interpreter: /usr/bin/python3
      kafka_id: 3
      kafka_port: 9092
zookeeper_hosts:
  hosts:
    192.168.1.1:
      ansible_host: 192.168.1.1
      ansible_python_interpreter: /usr/bin/python3
      myid: 2
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
      myid: 1
    192.168.1.3:
      ansible_host: 192.168.1.3
      ansible_python_interpreter: /usr/bin/python3
      myid: 3
```

- 变量配置

```yaml
---
# zookeeper user group 用户、用户组
user: "kafka"
group: "kafka"

# Log Path 日志路径
kafka_log_path: "log"

# Install path 安装路径
install_dir: "/opt/kafka"

# zookeeper client port 客户端端口
zk_client_port: 2181

```



#### （3） prometheus

- 主机配置

  prometheus负责集中采集的kpi数据项。只需要安装在server 节点上。另外，Prometheus需要去node_exporter上抓取数据，需要配置可连接的node_exporterde 节点IP

```yaml
node_exporter_hosts:
  hosts:
    192.168.1.1:
      ansible_host: 192.168.1.1
      ansible_python_interpreter: /usr/bin/python3
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
    192.168.1.3:
      ansible_host: 192.168.1.3
      ansible_python_interpreter: /usr/bin/python3
prometheus_hosts:
  hosts:
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
```

- 变量配置

```yaml
---
# prometheus 用户 用户组
user: "prometheus"
group: "prometheus"

# prometheus 监听端口
prometheus_listen_port: 9090

# node_exporter 监听端口
node_exporter_listen_port: 9100

# prometheus 配置文件路径
prometheus_conf_dir: "/etc/prometheus"
```


#### （4）node_exporter

- 主机配置

node_exporter需要安装在所有需要采集数据的主机节点上，主要需要配置IP

```yaml
node_exporter_hosts:
  hosts:
    192.168.1.1:
      ansible_host: 192.168.1.1
      ansible_python_interpreter: /usr/bin/python3
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
    192.168.1.3:
      ansible_host: 192.168.1.3
      ansible_python_interpreter: /usr/bin/python3
```

- 变量配置

```yaml
---
# node_exporter user 用户 用户组
user: "node_exporter"
group: "node_exporter"

# Listening port 监听端口
node_exporter_listen_port: 9100

```

#### (5) MySQL

- 主机配置

MySQL数据库只需要安装在server 节点上。

```
mysql_hosts:
  hosts:
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3

```

- 变量配置

```yaml
---
# mysql 用户、用户组
user: "mysql"
group: "mysql"

```



#### (6) elasticsearch

- 主机配置

elasticsearch数据库只需要安装在server 节点上。需要配置server节点删，并指定节点ID。如果需要配置分布式集群，需要修改主机清单和配置文件elasticsearch.j2

```yaml
elasticsearch_hosts:
  hosts:
    192.168.1.2:
      ansible_host: 192.168.1.2
      ansible_python_interpreter: /usr/bin/python3
      elasticsearch_id: elasticsearch_node1
```

- 变量配置

```yaml
---
# elasticsearch User Group 用户 用户组
user: elasticsearch
group: elasticsearch

# elasticsearch repo config  官方repo源配置
repo_name: "Elasticsearch"
repo_description: "Elasticsearch repository for 7.x packages"
repo_base_url: "https://artifacts.elastic.co/packages/7.x/yum"
repo_gpgkey: "https://artifacts.elastic.co/GPG-KEY-elasticsearch"
repo_file: "elasticsearch"

# elasticsearch Install dir 安装目录
install_dir: /etc/elasticsearch/

# elasticsearch cluster name 集群名称
elasticsearch_cluster_name: myApp

# elasticsearch init master ip address 默认的集群主节点IP
elasticsearch_cluster_init_master: 192.168.1.2

# elasticsearch listen port 监听端口
elasticsearch_listen_port: 9200

# elasticsearch data path 数据目录
elasticsearch_data_path: "/var/lib/elasticsearch"

# elasticsearch log path 日志目录
elasticsearch_log_path: "/var/log/elasticsearch"

# elasticsearch network host 网络IP
elasticsearch_network_host: "{{elasticsearch_cluster_init_master}}"

```

（7）fluentd

- 主机配置

fluentd 负责日志采集，部署在所有需要采集的节点上，最终将日志汇总在elasticsearch上。

```yaml
fluentd_hosts:
  hosts:
    192.168.1.1:
      ansible_python_interpreter: /usr/bin/python3
      elasticsearch_host: 192.168.1.1
    192.168.1.2:
      ansible_python_interpreter: /usr/bin/python3
      elasticsearch_host: 192.168.1.2
    192.168.1.3:
      ansible_python_interpreter: /usr/bin/python3
      elasticsearch_host: 192.168.1.3
```

- 变量配置

```yaml
---
# fluentd 用户 用户组
user: fluentd
group: fluentd

# fluentd 配置文件路径
fluentd_config_dir: /etc/fluentd/
```


- 采集项配置

fluentd 采集项的配置放待开发，目前需要修改具体的配置文件。



# 3 执行任务

## 3.1 任务配置

### 3.1.1 任务组件步骤配置

一个任务由多个步骤组成，基本可以认为每个步骤会安装一个组件，按照步骤组合的先后顺序，可以最终完成一次任务。

修改任务的步骤，需要修改tasks/任务名.xml

```yaml
---
step_list: # 步骤列表
 step_component: # 第一步安装kafka，可以使用默认模板
  enable: # false 置为false则跳过安装步骤，true执行安装步骤
  continue: # false 置为false则安装失败时终止任务，true执行安装失败时继续下一个组件安装
```

### 3.1.2 组件部署选项配置

组件的playbook中会定义几个关键选项的配置

```yaml
---
- hosts: example_hosts # 此处需套填写所安装组件配置的主机名。（建议按照统一生成的名称来处理）
  gather_facts: no
  user: root
  vars_files: # 需要引用变量文件时，加入vars文件
    - "../vars/example_vars.yml"
  vars: # 定义安装步骤的变量，在安装过程中可以根据需要修改是否启用
    install_example: true # 安装 example
    config_example: true # 配置 example
    start_example: true # 启动 example service
    create_user: true # 创建新的用户和组
  roles: # playbook中需要完成的角色剧本，可自定义，与顺序相关
    - ../roles/user # （1）创建用户 playbook
    - ../roles/example # （2） 安装 exampl playbook
```

