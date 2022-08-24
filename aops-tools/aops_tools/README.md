# 1. 介绍
    本工具当前主要用于安装aops_agent。
# 2. 安装
- 将aops_tools拷贝或解压在一台可以ssh登录其他agent节点的环境下即可使用,机器需要支持联网，建议配置22.09的yum源。
- 待部署的机器需要配置22.09 EPOL的yum源
- repo源路径：/etc/yum.repos.d/openEuler.repo
```ini
[openEuler22.09] # openEuler 22.09 官方发布源
name=openEuler22.09
baseurl=https://repo.openeuler.org/openEuler-22.09/everything/$basearch/ 
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/openEuler-22.09/everything/$basearch/RPM-GPG-KEY-openEuler

[Epol] # openEuler 22.09:Epol 官方发布源
name=Epol
baseurl=https://repo.openeuler.org/openEuler-22.09/EPOL/main/$basearch/ 
enabled=1
gpgcheck=1
gpgkey=https://repo.openeuler.org/openEuler-22.09/OS/$basearch/RPM-GPG-KEY-openEuler

```
# 3. 配置 

## 主机信息清单配置
    修改conf/import_host.xls文件。表格中为需要部署的每一台机器的agent信息。各字段的含义如下：

|字段名称|含义|
|----|----|
|host_name|目标机器的主机名，如localhost即为该主机的IP地址|
|ansible_host|目标机器的IP地址|
|ansible_user|ssh登录目标机器的用户名|	
|ansible_ssh_pass|ssh登录目标机器的密码|	
|ansible_become_user|目标主机可以切换提权的用户名|	
|ansible_become_method|目标主机切换用户方式|	
|ansible_become_password|标主机切换用户的密码|
|web_username|前端登录用户名|
|web_password|前端登录用户密码|	
|aops_host_name|用户为目标机器自定义的别名|
|host_group_name|目标机器需要加入的主机组，须确保主机组已存在，若不存在需要先去前端添加主机组|	
|manager_ip|管理节点restful接口的监听地址|	
|management|目标机器是否为管理节点|	
|manager_port|管理节点restful接口的监听端口|	
|agent_port|目标机器restful接口的监听端口|

    import_host.xls中需要用户填写的agent登录密码与前端登录密码，部署完成后主机及时清空或删除。


# 4. 执行
运行脚本：
```shell
dos2unix install_aops.sh
sh install_aops.sh

```