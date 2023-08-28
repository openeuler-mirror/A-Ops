# A-Ops

#### 介绍
the intelligent  ops toolkit for openEuler

#### 软件介绍

**随着该仓库中的各软件包内容不断丰富，该仓库日渐臃肿，因此弃用该仓库并将其拆分成多个子仓库，以便独立演进。以下是各个子仓库的介绍和地址：**

- gala-gopher

  gala-gopher是基于eBPF的低负载探针框架，致力于提供裸机/虚机/容器场景下的云原生观测引擎（cloud observation engine），帮助业务快速创新；详细介绍请[进入](https://gitee.com/openeuler/gala-gopher/blob/master/README.md)。

  该仓库已迁移至新仓库，迁移地址为：https://gitee.com/openeuler/gala-gopher

- gala-ragdoll

  gala-ragdoll是基于OS的配置托管服务，能够实现对OS配置的集群式管理，屏蔽不同OS类型的配置差异，实现统一的、可溯源的、预期配置可管理的可信的OS配置运维入口。

  该仓库已迁移至新仓库，迁移地址为：https://gitee.com/openeuler/gala-ragdoll

- aops-agent

  A-Ops智能运维工具的客户端，提供采集主机信息、响应服务端aops-zeus(原aops-manager)下发命令、管理aops插件等功能。

  该仓库已更名为aops-ceres迁移至新仓库，迁移地址为：https://gitee.com/openeuler/aops-ceres

- aops-manager

  A-Ops智能运维工具的基础服务层，提供主机管理功能与用户管理功能，以及与A-Ops其他服务模块交互的功能。A-Ops项目的整体[架构设计文档](https://gitee.com/openeuler/aops-zeus/blob/master/doc/design/aops%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3.md)也存放于该仓库，可以通过查阅这份文档理解A-Ops项目的整体理架构和设计理念，以及进一步理解该服务模块在其中起到的作用。

  该仓库已更名为aops-zeus迁移至新仓库，迁移地址为：https://gitee.com/openeuler/aops-zeus

- aops-utils

  A-Ops智能运维工具项目的开发工具包，内部封装一些公用函数方法。

  该仓库已更名为aops-vulcanus迁移至新仓库, 迁移地址为：https://gitee.com/openeuler/aops-vulcanus

- aops-check

  A-Ops智能运维工具智能工作流模块，用户依据现有各种指标处理模型，定制适合自己的异常检测模型(算法、训练、预测、诊断等)。

  该仓库已更名为aops-check迁移至新仓库, 迁移地址为：https://gitee.com/openeuler/aops-diana

- cve-manager

  A-Ops智能运维工具的漏洞管理模块，提供纳管机器的冷热补丁混合管理功能，包括漏洞巡检、漏洞修复、漏洞回滚等功能。

  该仓库已更名为aops-apollo迁移至新仓库, 迁移地址为：https://gitee.com/openeuler/aops-apollo

- aops-web

  A-Ops智能运维工具的web服务，为aops智能运维工具提供可视化操作界面以及数据可视化展示。

  该仓库已更名为aops-hermes迁移至新仓库, 迁移地址为：https://gitee.com/openeuler/aops-hermes

- aops-tools

  A-Ops智能运维工具辅助脚本存储仓，提供部分服务的一键化部署脚本，如mysql，elasticsearch等服务。

  该部分已纳入aops-vulcanus中，具体地址见：https://gitee.com/openeuler/aops-vulcanus/tree/master/scripts/deploy

#### 使用说明

该仓库下各服务基本完成迁移工作，关于模块的具体使用方法或部署方案请移步至新仓库查看。

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
