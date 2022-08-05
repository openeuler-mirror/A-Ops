Name:		A-Ops
Version:	v1.2.0
Release:	2
Summary:	The intelligent ops toolkit for openEuler
License:	MulanPSL2
URL:		https://gitee.com/openeuler/A-Ops
Source0:	%{name}-%{version}.tar.gz
%ifarch x86_64
patch0001: 0001-gen-vmlinx-oe2209-x86.patch
%endif
%ifarch aarch64
patch0001: 0001-gen-vmlinx-oe2209-arm.patch
%endif


# build for gopher
BuildRequires:	cmake gcc-c++ yum elfutils-devel clang >= 10.0.1 llvm libconfig-devel
BuildRequires:	librdkafka-devel libmicrohttpd-devel uthash-devel libbpf libbpf-devel
BuildRequires:  log4cplus-devel

# build for ragdoll & aops basic module
BuildRequires:  python3-setuptools python3-connexion python3-werkzeug python3-libyang
BuildRequires:	git python3-devel systemd

# build for aops basic module
BuildRequires:  python3-setuptools python3-kafka-python python3-connexion

# build for spider & anteater
BuildRequires:  python3-setuptools


%description
The intelligent ops toolkit for openEuler


%package -n aops-agent
Summary:    agent for A-Ops
Requires:   python3-requests python3-flask python3-connexion python3-configparser python3-jsonschema
Requires:   python3-flask-testing python3-libconf python3-swagger-ui-bundle
Requires:   python3-concurrent-log-handler dmidecode

%description -n aops-agent
agent for A-Ops


%package -n aops-utils
Summary:    utils for A-Ops
Requires:   python3-concurrent-log-handler python3-xmltodict python3-pyyaml python3-marshmallow >= 3.13.0
Requires:   python3-requests python3-xlrd python3-prettytable python3-pygments python3-sqlalchemy
Requires:   python3-elasticsearch >= 7 python3-prometheus-api-client python3-urllib3 python3-werkzeug
Requires:   python3-flask python3-flask-restful

%description -n aops-utils
utils for A-Ops


%package -n aops-manager
Summary:    manager of A-ops
Requires:   aops-utils = %{version}-%{release} ansible >= 2.9.0
Requires:   python3-pyyaml python3-marshmallow >= 3.13.0 python3-flask python3-flask-restful
Requires:   python3-requests sshpass python3-uWSGI python3-sqlalchemy python3-werkzeug

%description -n aops-manager
manager of A-ops, support software deployment and installation, account management, host management,
host group management, task and template management of ansible.


%package -n gala-gopher
Summary:	Intelligent ops toolkit for openEuler
Requires:	bash glibc elfutils zlib elfutils-devel

%description -n gala-gopher
Intelligent ops toolkit for openEuler


%package -n gala-ragdoll
Summary:	Configuration traceability

%description -n gala-ragdoll
Configuration traceability


%package -n python3-gala-ragdoll
Summary: python3 pakcage of gala-ragdoll
Requires: gala-ragdoll = %{version}-%{release} python3-flask-testing python3-libyang git
Requires: python3-werkzeug python3-connexion python3-swagger-ui-bundle

%description -n python3-gala-ragdoll
python3 pakcage of gala-ragdoll

%package -n gala-spider
Summary:    Configuration traceability
Requires:   python3-gala-spider = %{version}-%{release}

%description -n gala-spider
Configuration traceability


%package -n python3-gala-spider
Summary:    Python3 package of gala-spider
Requires:   python3-kafka-python python3-pyyaml python3-pyarango python3-requests

%description -n python3-gala-spider
Python3 package of gala-spider


%package -n gala-inference
Summary:    Cause inference module for A-Ops project
Requires:   python3-gala-inference = %{version}-%{release}

%description -n gala-inference
Cause inference module for A-Ops project


%package -n python3-gala-inference
Summary:    Python3 package of gala-inference
Requires:   python3-gala-spider python3-kafka-python python3-pyyaml python3-pyarango
Requires:   python3-requests python3-networkx python3-scipy

%description -n python3-gala-inference
Python3 package of gala-inference


%package -n gala-anteater
Summary:    abnormal detection
Requires:   python3-gala-anteater = %{version}-%{release}

%description -n gala-anteater
Abnormal detection module for A-Ops project


%package -n python3-gala-anteater
Summary:    abnormal detection
Requires:   python3-APScheduler python3-kafka-python python3-joblib python3-numpy
Requires:   python3-pandas python3-requests python3-scikit-learn python3-pytorch

%description -n python3-gala-anteater
Python3 package of python3-gala-anteater


%prep
%setup
# %setup -T -D -a 1
%patch0001 -p1

%build
# build for aops-agent
pushd aops-agent
%py3_build
popd

# build for aops-utils
pushd aops-utils
%py3_build
popd

#build for aops-manager
pushd aops-manager
%py3_build
popd

#build for gala-gopher
pushd gala-gopher/build
sh build.sh --release
popd

#build for gala-ragdoll
pushd gala-ragdoll
%py3_build
popd

#build for gala-spider
pushd gala-spider
%py3_build
popd

#build for gala-anteater
pushd gala-anteater
%py3_build
popd


%install
# install for agent
pushd aops-agent
%py3_install
popd

# install for utils
pushd aops-utils
%py3_install
popd

# install for manager
pushd aops-manager
%py3_install
mkdir -p %{buildroot}/%{python3_sitelib}/aops_manager/deploy_manager/ansible_handler
cp -r aops_manager/deploy_manager/ansible_handler/* %{buildroot}/%{python3_sitelib}/aops_manager/deploy_manager/ansible_handler
mkdir -p %{buildroot}/%{python3_sitelib}/aops_manager/deploy_manager/tasks
cp -r aops_manager/deploy_manager/tasks/* %{buildroot}/%{python3_sitelib}/aops_manager/deploy_manager/tasks
popd

#install for gala-gopher
pushd gala-gopher/build
install -d %{buildroot}/opt/gala-gopher
install -d %{buildroot}%{_bindir}
mkdir -p  %{buildroot}/usr/lib/systemd/system
install -m 0600 ../service/gala-gopher.service %{buildroot}/usr/lib/systemd/system/gala-gopher.service
sh install.sh %{buildroot}%{_bindir} %{buildroot}/opt/gala-gopher
popd

#install for gala-ragdoll
pushd gala-ragdoll
%py3_install
install yang_modules/*.yang %{buildroot}/%{python3_sitelib}/yang_modules/
mkdir -p %{buildroot}/%{_sysconfdir}/ragdoll
install config/*.conf %{buildroot}/%{_sysconfdir}/ragdoll/
mkdir %{buildroot}/%{python3_sitelib}/ragdoll/config
install config/*.conf %{buildroot}/%{python3_sitelib}/ragdoll/config
mkdir -p %{buildroot}/%{_prefix}/lib/systemd/system
install service/gala-ragdoll.service %{buildroot}/%{_prefix}/lib/systemd/system
popd

#install for gala-spider
pushd gala-spider
%py3_install
popd

#install for gala-anteater
pushd gala-anteater
%py3_install
popd


%post -n gala-gopher
%systemd_post gala-gopher.service

%preun -n gala-gopher
%systemd_preun gala-gopher.service

%postun -n gala-gopher
%systemd_postun_with_restart gala-gopher.service


%pre -n python3-gala-ragdoll
if [ -f "%{systemd_dir}/gala-ragdoll.service" ] ; then
        systemctl enable gala-ragdoll.service || :
fi

%post -n python3-gala-ragdoll
%systemd_post gala-ragdoll.service

%preun -n python3-gala-ragdoll
%systemd_preun gala-ragdoll.service

%postun -n python3-gala-ragdoll
%systemd_postun gala-ragdoll.service

%pre -n gala-spider
if [ -f "%{_unitdir}/gala-spider.service" ] ; then
        systemctl enable gala-spider.service || :
fi

%post -n gala-spider
%systemd_post gala-spider.service

%preun -n gala-spider
%systemd_preun gala-spider.service

%postun -n gala-spider
%systemd_postun gala-spider.service


%pre -n gala-inference
if [ -f "%{_unitdir}/gala-inference.service" ] ; then
        systemctl enable gala-inference.service || :
fi

%post -n gala-inference
%systemd_post gala-inference.service

%preun -n gala-inference
%systemd_preun gala-inference.service

%postun -n gala-inference
%systemd_postun gala-inference.service


%pre -n gala-anteater
if [ -f "%{_unitdir}/gala-anteater.service" ] ; then
        systemctl enable gala-anteater.service || :
fi

%post -n gala-anteater
%systemd_post gala-anteater.service

%preun -n gala-anteater
%systemd_preun gala-anteater.service

%postun -n gala-anteater
%systemd_postun gala-anteater.service


%files -n aops-agent
%attr(0644,root,root) %{_sysconfdir}/aops/agent.conf
%attr(0644,root,root) %{_sysconfdir}/aops/agent_token.json
%attr(0755,root,root) %{_unitdir}/aops-agent.service
%{python3_sitelib}/aops_agent*.egg-info
%{python3_sitelib}/aops_agent/*
%{_bindir}/aops_agent


%files -n aops-utils
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/system.ini
%{python3_sitelib}/aops_utils*.egg-info
%{python3_sitelib}/aops_utils/*
%attr(0755,root,root) %{_bindir}/aops-utils


%files -n aops-manager
%attr(0644,root,root) %{_sysconfdir}/aops/manager.ini
%attr(0644,root,root) %{_sysconfdir}/aops/default.json
%attr(0755,root,root) %{_bindir}/aops-manager
%attr(0755,root,root) %{_bindir}/aops-basedatabase
%attr(0755,root,root) %{_unitdir}/aops-manager.service
%{python3_sitelib}/aops_manager*.egg-info
%{python3_sitelib}/aops_manager/*


%files -n gala-gopher
%defattr(-,root,root)
%dir /opt/gala-gopher
%dir /opt/gala-gopher/extend_probes
%dir /opt/gala-gopher/meta
%dir /opt/gala-gopher/lib
%{_bindir}/*
%config(noreplace) /opt/gala-gopher/gala-gopher.conf
%config(noreplace) /opt/gala-gopher/task_whitelist.conf
/opt/gala-gopher/extend_probes/*
/opt/gala-gopher/meta/*
/opt/gala-gopher/lib/*
%{_unitdir}/gala-gopher.service


%files -n gala-ragdoll
%doc gala-ragdoll/doc/*
%license gala-ragdoll/LICENSE
/%{_sysconfdir}/ragdoll/gala-ragdoll.conf
%{_bindir}/ragdoll
%{_prefix}/lib/systemd/system/gala-ragdoll.service


%files -n python3-gala-ragdoll
%{python3_sitelib}/ragdoll/*
%{python3_sitelib}/yang_modules
%{python3_sitelib}/ragdoll-*.egg-info


%files -n gala-spider
%doc gala-spider/README.md gala-spider/docs/*
%license gala-spider/LICENSE
%{_sysconfdir}/gala-spider/*
%{_bindir}/spider-storage
%{_unitdir}/gala-spider.service


%files -n python3-gala-spider
%{python3_sitelib}/spider/*
%{python3_sitelib}/*.egg-info


%files -n gala-inference
%doc gala-spider/README.md gala-spider/docs/*
%license LICENSE
%{_sysconfdir}/gala-inference/*
%{_bindir}/gala-inference
%{_unitdir}/gala-inference.service


%files -n python3-gala-inference
%{python3_sitelib}/cause_inference/*


%files -n gala-anteater
%doc README.md
%license LICENSE
%{_bindir}/gala-anteater
%{_unitdir}/gala-anteater.service


%files -n python3-gala-anteater
%{python3_sitelib}/anteater/*
%{python3_sitelib}/*.egg-info


%changelog
* Mon Aug 1 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.0-2
- add base-database executable file into aops-manager to downlaod database.

* Sun Jul 31 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.0-1
- modify spec for gala-gopher&gala-spider and add new features.
- 1. gala-gopher & gala-spider adapt to the latest code.
- 2. add new feature gala-anteater.
- add aops-agent module, delete aops-database, aops-cli, aops-web,
  and four adoctor modules for new architecture.

* Thu Sep 30 2021 chemingdao<chemingdao@huawei.com> - v1.1.1-5
- Using image source overwrite instead of patching image binaries.

* Wed Sep 29 2021 chemingdao<chemingdao@huawei.com> - v1.1.1-4
- switch logo images and modify logo size.

* Wed Sep 29 2021 orange-snn<songnannan2@huawei.com> - v1.1.1-3
- add permission control in ragdoll.

* Wed Sep 29 2021 chemingdao<chemingdao@huawei.com> - v1.1.1-2
- fix log info of the task execution.

* Sun Sep 26 2021 chemingdao<chemingdao@huawei.com> - v1.1.1-1
- New release 1.1.1, bug fix and new features.
- 1. Web issues fix: display fix and domain management modification.
- 2. Fix cli display issues and add loading bar of diag.
- 3. Fix return of gala-ragdoll.
- 4. Fix log level.
- 5. haproxy probe with vport info.

* Sat Sep 18 2021 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.0-2
- add missed file and better cli output

* Fri Sep 17 2021 chemingdao<chemingdao@huawei.com> - v1.1.0-1
- New release 1.1.0, bug fix and UI beautify.
- 1. Simplify gala-spider UI display.
- 2. Beautify cli print with table and highlight json.
- 3. Bug fix: now support check with management host.
- 4. Modify elasticsearch and fluentd default config.

* Thu Sep 16 2021 chemingdao<chemingdao@huawei.com> - v1.0.3-1
- NEW release 1.0.3.

* Mon Sep 13 2021 chemingdao<chemingdao@huawei.com> - v1.0.2-3
- modify spec for aops-web build and fix some issues.

* Sat Sep 11 2021 yangyunyi<yangyunyi2@huawei.com> - v1.0.2-2
- modify ansible playbook

* Tue Sep 7 2021 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.0.2-1
- add gala-spider in spec

* Mon Sep 6 2021 Yiru Wang<wangyiru1@huawei.com> - v1.0.1-2
- add web build modle of the aops

* Mon Sep 6 2021 Lostwayzxc<luoshengwei@huawei.com> - v1.0.1-1
- update src, add intelligent check and diagnosis module

* Thu Sep 2 2021 zhaoyuxing<zhaoyuxsing2@huawei.com> - 1.0.0-4
- add service file in gala-spider

* Wed Sep 1 2021 orange-snn<songnannan2@huawei.com> - 1.0.0-3
- add service file in gala-ragdoll

* Tue Aug 24 2021 zhu-yuncheng<zhuyuncheng@huawei.com> - 1.0.0-2
- Update spec

* Sat Jul 31 2021 orange-snn<songnannan2@huawei.com> - 1.0.0-1
- Package init
