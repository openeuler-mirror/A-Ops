# ebpf.probe开发指南

ebpf.probe是一个bpf探针程序的开发框架，定义了一些开发规范，方便bpf程序的开发集成；

## ebpf.probe目录结构

目录结构：

```sh
├── libbpf					# libbpf代码目录
├── src						# bpf程序源码目录
│   ├── include				# 公共头文件
│   │   ├── util.h				# 基础lib库
│   │   ├── linux_4.18.0-147.5.1.6.h425.h		# 内核版本的头文件（仅包含probe使用相关）
│   │   ├── linux_4.19.90-2003.4.0.0036.oe1.h	# 内核版本的头文件（仅包含probe使用相关）
│   │   └── vmlinux.h -> linux_4.19.90-2003.4.0.0036.oe1.h	# 根据编译环境生成的vmlinux.h
│   └── lib					# 基础库
│       ├── util.c				# 基础库文件
│   ├── Makefile				# makefile
│   └── tcpprobe				# tcpprobe探针源码
│       ├── tcp_link.meta		# 探针meta
│       ├── tcpprobe.bpf.c		# bpf内核态程序
│       ├── tcpprobe.c			# bpf用户态程序
│       └── tcpprobe.h			# 相关头文件
└── tools					# 工具目录
    ├── bpftool				# bpftool工具，用于生成vmlinux.h/BPF skeletons头文件
    └── gen_vmlinux_h.sh		# 自动生成vmlinux.h
```
## 如何编译

### 编译命令

```sh
# 编译bpf程序
[root@localhost ebpf.probe]# ./build.sh

# 安装bpf程序，安装到 /usr/bin/extends/ebpf.probe 目录下
[root@localhost ebpf.probe]# ./install.sh
/opt/A-Ops/gala-gopher/src/probes/extends/ebpf.probe/src/lib/util.c
.output .output/tcpprobe/ .output/killprobe/ .output/libbpf
tcpprobe/tcpprobe killprobe/killprobe  /usr/bin/extends/ebpf.probe
mkdir -p /usr/bin/extends/ebpf.probe
cp tcpprobe/tcpprobe killprobe/killprobe  /usr/bin/extends/ebpf.probe
[root@localhost ebpf.probe]#

# 清理编译过程
[root@localhost ebpf.probe]# ./build.sh clean
```

注：

1. bpf探针依赖libbpf开发库，./build.sh过程中会从git下载libbpf的稳定版本，编译环境要求能正常访问git；

2. bpf探针要求编译环境安装 elfutils-devel、clang、llvm等软件包，其中clang版本>=10.x.x，./build.sh中会检查安装；

### 编译流程介绍

todo

## 如何新增probe程序

### ebpf程序开发过程

1. 在src目录下创建一个独立目录， Makefile中增加新的探针；

   ```sh
   # 1 killprobe为新增的探针目录
   [root@localhost src]# ll
   total 20K
   drwxr-xr-x. 2 root root 4.0K Apr 24 02:09 include
   drwxr-xr-x. 2 root root 4.0K Apr 24 05:33 killprobe
   drwxr-xr-x. 2 root root 4.0K Apr 24 05:33 lib
   -rw-r--r--. 1 root root 2.7K Apr 24 03:57 Makefile
   drwxr-xr-x. 2 root root 4.0K Apr 24 05:33 tcpprobe
   [root@localhost src]#
   
   # 2 Makefile中增加killprobe探针, killprobe/killprobe /前为探针目录名，/后为探针可执行程序名，与*.bpf.c的*名称一致；
   [root@localhost src]# vim Makefile
   # add probe
   APPS := tcpprobe/tcpprobe killprobe/killprobe
   ```

2. 开发*.bpf.c bpf代码；

   ```sh
   [root@localhost killprobe]# ll
   total 1.6K
   -rw-r--r--. 1 root root 1.3K Apr 24 02:09 killprobe.bpf.c
   -rw-r--r--. 1 root root  294 Apr 24 02:09 killprobe.h
   [root@localhost killprobe]#
   ```

3. 生成*.skel.h 方便用户态程序开发；

   *.skel.h是通过bpftool gen skeleton根据bpf代码生成包含prog、map数据结构、bpf程序加载、卸载等API的头文件，方便bpf程序开发；

   ```sh
   # 通过执行make生成*.skel.h，因为还没有开发用户态程序，编译会报错，不用管，*.skel.h在.output/killprobe下；
   [root@localhost src]# make
   [root@localhost src]# cd .output/killprobe
   [root@localhost killprobe]# ll
   total 17.6K
   -rw-r--r--. 1 root root 3.6K Apr 24 05:41 killprobe.bpf.o
   -rw-r--r--. 1 root root  14K Apr 24 05:41 killprobe.skel.h
   [root@localhost killprobe]#
   ```

4. 开发用户态代码；

   用户态代码中，引用 *.skel.h 开发；开发完成后再次到src目录下make直到正常编译成功；（此时也可以在ebpf.probe目录下执行./build.sh编译）

5. 探针框架集成探针采集数据方法

   对于需要探针框架集成输出观测指标的探针，要在探针目录下增加meta元模型，定义探针输出的观测指标模型，具体方法参考探针框架开发指南；