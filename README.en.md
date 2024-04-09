# A-Ops

#### introduce

the intelligent  ops toolkit for openEuler

#### software introduction

**As the packages in the repository grew richer, the repository became bloated, so it was deprecated and split into sub-repositories to evolve independently. Here are the descriptions and addresses of each sub-warehouse:**

- gala-gopher

  gala-gopher is a low-load probe framework based on eBPF, dedicated to providing cloud native observation engine in bare metal/virtual machine/container scenarios to help businesses innovate rapidly. For details, please go to.

  The warehouse has been migrated to a new warehouse at https://gitee.com/openeuler/gala-gopher

- gala-ragdoll

  gala-ragdoll is an OS-based configuration hosting service that enables cluster management of OS configurations, masks configuration differences of different OS types, and implements a unified, traceable, and trusted OS configuration O & M portal that is expected to be manageable. 

  The warehouse has been migrated to a new warehouse at https://gitee.com/openeuler/gala-ragdoll

- aops-agent

  The client of A-Ops intelligent operation and maintenance tool provides functions such as collecting host information, responding to commands issued by server aops-zeus(original aops-manager), and managing aops plug-ins. 

  The repository has been renamed aops-ceres and migrated to a new repository at https://gitee.com/openeuler/aops-ceres

- aops-manager

  The basic service layer of A-Ops intelligent operation and maintenance tool provides host management function and user management function, as well as the function of interacting with other service modules of A-Ops. The overall architecture design document of the A-Ops project is also stored in this repository, which can be consulted to understand the overall architecture and design philosophy of the A-Ops project and further understand the role played by the service module.

  The repository has been renamed aops-zeus and migrated to a new repository at https://gitee.com/openeuler/aops-zeus

- aops-utils

  A-Ops is a development kit for intelligent operation and maintenance tools, which encapsulates some common function methods. 

  The repository has been renamed aops-vulcanus and migrated to a new repository at https://gitee.com/openeuler/aops-vulcanus

- aops-check

  A-Ops intelligent operation and maintenance tool intelligent workflow module, users according to the existing various index processing models, customize their own anomaly detection model (algorithm, training, prediction, diagnosis, etc.). 

  The repository has been renamed aops-check and migrated to a new repository. The migration address is https://gitee.com/openeuler/aops-diana

- cve-manager

  The vulnerability management module of A-Ops intelligent operation and maintenance tool provides mixed hot and cold patch management functions of managed machines, including vulnerability inspection, vulnerability repair, vulnerability rollback and other functions. 

  The repository has been renamed aops-apollo and migrated to a new repository. The migration address is https://gitee.com/openeuler/aops-apollo

- aops-web

  Web service of A-Ops intelligent operation and maintenance tool, providing visual operation interface and data visualization display for aops intelligent operation and maintenance tool. 

  The repository has been renamed aops-hermes and migrated to a new repository at https://gitee.com/openeuler/aops-hermes

- aops-tools

  A-Ops intelligent operation and maintenance tool auxiliary script storage warehouse, providing one-click deployment scripts for some services, such as mysql, elasticsearch and other services. 

  This section is included in AOPS-Vulcanus, with a specific address：https://gitee.com/openeuler/aops-vulcanus/tree/master/scripts/deploy

#### instructions for use

The migration of services under this warehouse has been basically completed. For the specific usage method or deployment scheme of modules, please move to the new warehouse to view. 

#### to contribute

1. Fork this warehouse 
2. New Feat_xxx branch 
3. submit code 
4. create new Pull Request

#### special skills

1. Use Readme_XXX.md to support different languages such as Readme_en.md, Readme_zh.md 
2. Gitee official blog [blog.gitee.com](https://blog.gitee.com)
3. You can learn about the great open source projects on Gitee at https://gitee.com/explore
4.  GVP full name is Gitee most valuable open source project, is a comprehensive evaluation of excellent open source projects
5. Gitee official manual https://gitee.com/help 
6. Gitee cover character is a column used to showcase Gitee members https://gitee.com/gitee-stars/ 
