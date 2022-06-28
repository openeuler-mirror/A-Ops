# 如何生成gala-gopher容器镜像

本目录提供生成gala-gopher容器镜像的Dockerfile文件，用以生成容器镜像。请按照如下步骤进行配置、生成、运行等。

### 创建容器镜像

在[build目录](../build)有用于生成容器镜像的Dockerfile文件，由于gala-gopher强依赖内核版本，此处针对不同内核版本分别提供Dockerfile文件。将编译生成的gala-gopher-xxx.rpm包，以及[OBS路径](https://117.78.1.88/package/binaries/home:z00451245:branches:openEuler:20.03:LTS:SP1/libbpf/standard_x86_64)下libbpf-0.3-1.h0.oe1.x86_64.rpm 和libbpf-devel-0.3-1.h0.oe1.x86_64.rpm 文件下载保存到该目录：

```shell
[root@localhost build]# ll
-rw-r--r--. 1 root root 1.9K Jun 27 21:59 Dockerfile_2003_sp1
-rw-r--r--. 1 root root 227K Jun 28 09:02 gala-gopher-v1.1.0-52.x86_64.rpm
-rw-r--r--. 1 root root 102K Jun 27 21:19 libbpf-0.3-1.h0.oe1.x86_64.rpm
-rw-r--r--. 1 root root  62K Jun 27 21:19 libbpf-devel-0.3-1.h0.oe1.x86_64.rpm
```

执行Dockerfile前要确保宿主机能够访问openEuler repo源，先下载openEuler镜像源：

```shell
[root@localhost build]# docker image pull openeuler/openeule:20.03-lts-sp1
[root@localhost build]# docker images
REPOSITORY            TAG                 IMAGE ID            CREATED             SIZE
openeuler/openeuler   20.03-lts-sp1       60402ce20dab        2 months ago        512MB
```

最后使用Dockerfile创建镜像：

```shell
[root@localhost build]# docker build -f Dockerfile_2003_sp1 -t gala-gopher:0.0.1 .
```

成功生成容器镜像：

```shell
[root@localhost build]# docker images
REPOSITORY            TAG                 IMAGE ID            CREATED             SIZE
gala-gopher           0.0.1               211913592b58        22 minutes ago      614MB
```

### 创建并运行容器

gala-gopher涉及两个配置文件：gala-gopher.conf和task_whitelist.conf。gala-gopher.conf主要用于配置探针的数据上报开关、探针参数、探针是否开启等；task_whitelist.conf是观测白名单，可以把用户感兴趣的进程名加入白名单，gala-gopher就会观测这个进程了。

容器启动前需要用户自定义配置这两个配置文件，请创建配置文件目录，并将[config目录](../config)下两个配置文件保存到该目录，示例如下：

```shell
[root@localhost ~]# mkdir gopher_user_conf
[root@localhost gopher_user_conf]# ll
total 8.0K
-rw-r--r--. 1 root root 3.2K Jun 28 09:43 gala-gopher.conf
-rw-r--r--. 1 root root  108 Jun 27 21:45 task_whitelist.conf
```

请按照[配置文件介绍](conf_introduction.md)自定义修改配置文件。

最后按照如下示例命令启动容器：

```shell
docker run -d --name xxx -p 8888:8888 --privileged -v /etc/machine-id:/etc/machine-id -v /lib/modules:/lib/modules:ro -v /usr/src:/usr/src:ro -v /boot:/boot:ro -v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf -v /root/gopher_user_conf:/gala-gopher/user_conf/ -v /etc/localtime:/etc/localtime:ro --pid=host gala-gopher:0.0.1
```

成功启动容器后，通过docker ps可以看到正在运行的容器：

```shell
[root@localhost build]# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                    NAMES
eaxxxxxxxx02        gala-gopher:0.0.1   "/bin/sh -c 'cp -f /…"   About a minute ago   Up About a minute   0.0.0.0:8888->8888/tcp   xxx
```

### 获取数据

如上步骤docker run命令中所示，我们映射了宿主机8888端口和容器的8888端口，因而可以通过8888端口获取数据来验证gala-gopher是否运行成功：

```shell
[root@localhost build]# curl http://localhost:8888
...
gala_gopher_udp_que_rcv_drops{tgid="1234",s_addr="192.168.12.34",machine_id="xxxxx",hostname="eaxxxxxxxx02"} 0 1656383357000
...
```

如上有指标数据输出则证明gala-gopher运行成功。

### 保存容器镜像

生成容器镜像后可以将镜像保存为tar文件，其他宿主机可以通过load命令导入容器镜像：

```shell
[root@localhost build]# docker save -o gala-gopher_sp1_v0.0.1.tar 211913592b58
```

```shell
[root@localhost build]# docker load gala-gopher_sp1_v0.0.1.tar
```
