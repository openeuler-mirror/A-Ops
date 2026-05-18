# A-Ops

## Overview

Intelligent operations toolkit for openEuler

## Software Introduction

**As the repository contains an increasing number of software packages, it has become too bloated to maintain effectively. Therefore, this repository has been deprecated and split into several sub-repositories for independent evolution. The following are the descriptions and addresses for each sub-repository:**

- gala-gopher

  A low-overhead observation framework based on eBPF. It is dedicated to providing a cloud-native observation engine for bare metal, virtual machine, and container scenarios to accelerate service innovation.

  Repository: https://gitcode.com/openeuler/gala-gopher

- gala-ragdoll

  An OS-based configuration management service. It enables cluster-level management of OS configurations, masks differences between OS types, and provides a unified, traceable, and trusted O&M entry for managing desired configurations.

  Repository: https://gitcode.com/openeuler/gala-ragdoll

- aops-agent (renamed to aops-ceres)

  The client-side agent for A-Ops. It is responsible for collecting host information, executing commands issued by `aops-zeus` (formerly `aops-manager`), and managing A-Ops plugins.

  Repository: https://gitcode.com/openeuler/aops-ceres

- aops-manager (renamed to aops-zeus)

  The infrastructure service layer of A-Ops. It provides host and user management functionalities and handles interactions with other A-Ops modules. The A-Ops architectural design documents are also hosted here, providing insights into the project's overall design philosophy.

  Repository: https://gitcode.com/openeuler/aops-zeus

- aops-utils (renamed to aops-vulcanus)

  The development toolkit for the A-Ops project, containing encapsulated common utility functions and methods.

  Repository: https://gitcode.com/openeuler/aops-vulcanus

- aops-check (renamed to aops-diana)

  The intelligent workflow module of A-Ops. It allows users to customize anomaly detection models (including algorithms, training, prediction, and diagnosis) based on existing metric processing models.

  Repository: https://gitcode.com/openeuler/aops-diana

- cve-managercve-manager (renamed to aops-apollo)

  The vulnerability management module of A-Ops. It provides hybrid management of hot and cold patches for managed machines, covering vulnerability inspection, remediation, and rollback.

  Repository: https://gitcode.com/openeuler/aops-apollo

- aops-web (renamed to aops-hermes)

  The web service for A-Ops, providing a graphical user interface (GUI) for operations and data visualization.

  Repository: https://gitcode.com/openeuler/aops-hermes

- aops-tools (merged into aops-vulcanus)

  A collection of auxiliary scripts for A-Ops, providing one-click deployment for services such as MySQL and Elasticsearch.

  This part has been merged into `aops-vulcanus`. For details, visit https://gitcode.com/openeuler/aops-vulcanus/tree/master/scripts/deploy.

## Contribution

1. Fork this repository.
2. Create a Feat_*xxx* branch.
3. Commit code.
4. Create a pull request (PR).

## Notes

Use the file naming pattern `README_xx.md` to indicate a supported language (for example, `README_EN.md`).
