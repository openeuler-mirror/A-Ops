Name:		A-Ops
Version:	v1.0.3
Release:	1
Summary:	The intelligent ops toolkit for openEuler
License:	MulanPSL2
URL:		https://gitee.com/openeuler/A-Ops
Source0:	%{name}-%{version}.tar.gz
Source1:	A-Ops-web-node-modules.tar.gz


# build for gopher
BuildRequires:	cmake gcc-c++ yum elfutils-devel clang >= 10.0.1 llvm libconfig-devel
BuildRequires:	librdkafka-devel libmicrohttpd-devel

# build for ragdoll & aops basic module
BuildRequires:  python3-setuptools python3-connexion python3-werkzeug python3-libyang
BuildRequires:	git python3-devel systemd

# build for spider & aops basic module
BuildRequires:  python3-setuptools python3-kafka-python python3-connexion

# build for web
BuildRequires: nodejs node-gyp nodejs-yarn

%description
The intelligent ops toolkit for openEuler


%package -n aops-utils
Summary:    utils for A-Ops
Requires:   python3-concurrent-log-handler python3-xmltodict python3-pyyaml python3-marshmallow >= 3.13.0
Requires:   python3-requests python3-xlrd python3-prettytable python3-pygments

%description -n aops-utils
utils for A-Ops


%package -n aops-cli
Summary:        cli of A-ops
Requires: 	aops-utils = %{version}-%{release}

%description -n aops-cli
commandline tool of aops, offer commands for account management, host management,
host group management, task and template management of ansible.


%package -n aops-manager
Summary:    manager of A-ops
Requires:   aops-utils = %{version}-%{release} ansible >= 2.9.0
Requires:   python3-pyyaml python3-marshmallow >= 3.13.0 python3-flask python3-flask-restful
Requires:   python3-requests sshpass python3-uWSGI

%description -n aops-manager
manager of A-ops, support software deployment and installation, account management, host management,
host group management, task and template management of ansible.


%package -n aops-database
Summary:    database center of A-ops
Requires:   aops-utils = %{version}-%{release} python3-pyyaml
Requires:   python3-elasticsearch >= 7 python3-requests python3-werkzeug python3-urllib3
Requires:   python3-flask python3-flask-restful python3-PyMySQL python3-sqlalchemy
Requires:   python3-prometheus-api-client python3-uWSGI

%description -n aops-database
database center of A-ops, offer database proxy of mysql, elasticsearch and prometheus time series database.


%package -n adoctor-check-scheduler
Summary:    scheduler of A-ops check module
Requires:   aops-utils = %{version}-%{release}
Requires:   python3-requests python3-flask python3-flask-restful python3-uWSGI python3-kafka-python
Requires:   python3-marshmallow >= 3.13.0 python3-Flask-APScheduler >= 1.11.0

%description -n adoctor-check-scheduler
Exception detection and scheduling service. Provides an exception detection interface to
manage exception detection tasks.


%package -n adoctor-check-executor
Summary:    executor of A-ops check module
Requires:   aops-utils = %{version}-%{release}
Requires:   python3-kafka-python python3-pyyaml python3-marshmallow >= 3.13.0 python3-requests
Requires:   python3-ply >= 3.11

%description -n adoctor-check-executor
Performs an exception task based on the configured exception detection rule.


%package -n adoctor-diag-scheduler
Summary:    scheduler of A-ops diag module
Requires:   aops-utils = %{version}-%{release}
Requires:   python3-requests python3-flask python3-flask-restful python3-uWSGI python3-kafka-python

%description -n adoctor-diag-scheduler
Scheduler for diagnose module, provides restful interfaces to reply to requests about
importing/exporting diagnose tree, executing diagnose and so on.


%package -n adoctor-diag-executor
Summary:    executor of A-ops check module
Requires:   aops-utils = %{version}-%{release}
Requires:   python3-kafka-python

%description -n adoctor-diag-executor
Executor of diagnose module. Get messages from kafka and do the diagnose tasks.


%package -n adoctor-cli
Summary:    command line tool of A-doctor
Requires:   aops-utils = %{version}-%{release}


%description -n adoctor-cli
commandline tool of adoctor, offer commands for executing diagnose, importing/exporting diagnose tree,
getting diagnose report, importing/exporting check rule, querying check result and so on.


%package -n gala-gopher
Summary:	Intelligent ops toolkit for openEuler
Requires:	bash glibc elfutils zlib iproute kernel >= 4.18.0-147.5.1.6 elfutils-devel

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
Summary:	Configuration traceability

%description -n gala-spider
Configuration traceability


%package -n python3-gala-spider
Summary: python3 pakcage of gala-spider
Requires: gala-spider = %{version}-%{release} python3-kafka-python python3-connexion

%description -n python3-gala-spider
python3 pakcage of gala-spider


%package -n aops-web
Summary:    website for A-Ops
Requires:   nginx

%description -n aops-web
website for A-Ops, deployed by Nginx


%define debug_package %{nil}

%prep
%setup
%setup -T -D -a 1
cp -r A-Ops-web-node-modules/node_modules aops-web/

%build
# build for aops-utils
pushd aops-utils
%py3_build
popd

#build for aops-cli
pushd aops-cli
%py3_build
popd

#build for aops-manager
pushd aops-manager
%py3_build
popd

#build for aops-database
pushd aops-database
%py3_build
popd

#build for adoctor-check-scheduler
pushd adoctor-check-scheduler
%py3_build
popd

#build for adoctor-check-executor
pushd adoctor-check-executor
%py3_build
popd

#build for adoctor-diag-scheduler
pushd adoctor-diag-scheduler
%py3_build
popd

#build for adoctor-diag-executor
pushd adoctor-diag-executor
%py3_build
popd

#build for adoctor-cli
pushd adoctor-cli
%py3_build
popd


#build for gala-gopher
pushd gala-gopher
sh build.sh build
popd

#build for gala-ragdoll
pushd gala-ragdoll
%py3_build
popd

#build for gala-spider
pushd gala-spider
%py3_build
popd

#build for aops-web
pushd aops-web
yarn build
popd


%install
# install for utils
pushd aops-utils
%py3_install
popd

# install for cli
pushd aops-cli
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

# install for database
pushd aops-database
%py3_install
popd

# install for adoctor-check-scheduler
pushd adoctor-check-scheduler
%py3_install
popd

# install for adoctor-check-executor
pushd adoctor-check-executor
%py3_install
popd

# install for adoctor-diag-scheduler
pushd adoctor-diag-scheduler
%py3_install
popd

# install for adoctor-diag-executor
pushd adoctor-diag-executor
%py3_install
popd

# install for adoctor-cli
pushd adoctor-cli
%py3_install
popd


# install for web
pushd aops-web
mkdir -p %{buildroot}/opt/aops_web
cp -r dist %{buildroot}/opt/aops_web/
mkdir -p %{buildroot}/%{_sysconfdir}/nginx
cp -r deploy/aops-nginx.conf %{buildroot}/%{_sysconfdir}/nginx/
mkdir -p %{buildroot}/usr/lib/systemd/system
cp -r deploy/aops-web.service %{buildroot}/usr/lib/systemd/system/
popd

#install for gala-gopher
pushd gala-gopher
install -d %{buildroot}/opt/gala-gopher
install -d %{buildroot}%{_bindir}
mkdir -p  %{buildroot}/usr/lib/systemd/system
install -m 0600 service/gala-gopher.service %{buildroot}/usr/lib/systemd/system/gala-gopher.service
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
mkdir -p %{buildroot}/%{_sysconfdir}/spider
install config/*.conf %{buildroot}/%{_sysconfdir}/spider/
install anomaly_detection/*.yaml %{buildroot}/%{_sysconfdir}/spider/
mkdir %{buildroot}/%{python3_sitelib}/spider/config
install config/*.conf %{buildroot}/%{python3_sitelib}/spider/config
install anomaly_detection/*.yaml %{buildroot}/%{python3_sitelib}/spider/config
mkdir -p %{buildroot}/%{_prefix}/lib/systemd/system
install service/gala-spider.service %{buildroot}/%{_prefix}/lib/systemd/system
mkdir -p %{buildroot}/%{_tmppath}/spider
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

%pre -n python3-gala-spider
if [ -f "%{systemd_dir}/gala-spider.service" ] ; then
        systemctl enable gala-spider.service || :
fi

%post -n python3-gala-spider
%systemd_post gala-spider.service

%preun -n python3-gala-spider
%systemd_preun gala-spider.service

%postun -n python3-gala-spider
%systemd_postun gala-spider.service

%files -n aops-utils
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/system.ini
%{python3_sitelib}/aops_utils*.egg-info
%{python3_sitelib}/aops_utils/*
%attr(0755,root,root) %{_bindir}/aops-utils


%files -n aops-cli
%attr(0755,root,root) %{_bindir}/aops
%{python3_sitelib}/aops_cli*.egg-info
%{python3_sitelib}/aops_cli/*


%files -n aops-manager
%attr(0644,root,root) %{_sysconfdir}/aops/manager.ini
%attr(0755,root,root) %{_bindir}/aops-manager
%attr(0755,root,root) %{_unitdir}/aops-manager.service
%{python3_sitelib}/aops_manager*.egg-info
%{python3_sitelib}/aops_manager/*


%files -n aops-database
%attr(0644,root,root) %{_sysconfdir}/aops/database.ini
%attr(0644,root,root) %{_sysconfdir}/aops/default.json
%attr(0755,root,root) %{_unitdir}/aops-database.service
%attr(0755,root,root) %{_bindir}/aops-database
%attr(0755,root,root) %{_bindir}/aops-basedatabase
%{python3_sitelib}/aops_database*.egg-info
%{python3_sitelib}/aops_database/*


%files -n adoctor-check-scheduler
%attr(0644,root,root) %{_sysconfdir}/aops/check_scheduler.ini
%attr(0755,root,root) %{_unitdir}/adoctor-check-scheduler.service
%attr(0755,root,root) %{_bindir}/adoctor-check-scheduler
%{python3_sitelib}/adoctor_check_scheduler*.egg-info
%{python3_sitelib}/adoctor_check_scheduler/*


%files -n adoctor-check-executor
%attr(0644,root,root) %{_sysconfdir}/aops/check_executor.ini
%attr(0644,root,root) %{_sysconfdir}/aops/check_rule_plugin.yml
%attr(0755,root,root) %{_unitdir}/adoctor-check-executor.service
%attr(0755,root,root) %{_bindir}/adoctor-check-executor
%{python3_sitelib}/adoctor_check_executor*.egg-info
%{python3_sitelib}/adoctor_check_executor/*


%files -n adoctor-diag-scheduler
%attr(0644,root,root) %{_sysconfdir}/aops/diag_scheduler.ini
%attr(0755,root,root) %{_unitdir}/adoctor-diag-scheduler.service
%attr(0755,root,root) %{_bindir}/adoctor-diag-scheduler
%{python3_sitelib}/adoctor_diag_scheduler*.egg-info
%{python3_sitelib}/adoctor_diag_scheduler/*


%files -n adoctor-diag-executor
%attr(0644,root,root) %{_sysconfdir}/aops/diag_executor.ini
%attr(0755,root,root) %{_unitdir}/adoctor-diag-executor.service
%attr(0755,root,root) %{_bindir}/adoctor-diag-executor
%{python3_sitelib}/adoctor_diag_executor*.egg-info
%{python3_sitelib}/adoctor_diag_executor/*


%files -n adoctor-cli
%attr(0755,root,root) %{_bindir}/adoctor
%{python3_sitelib}/adoctor_cli*.egg-info
%{python3_sitelib}/adoctor_cli/*


%files -n gala-gopher
%defattr(-,root,root)
%dir /opt/gala-gopher
%dir /opt/gala-gopher/extend_probes
%dir /opt/gala-gopher/meta
%{_bindir}/gala-gopher
%config(noreplace) /opt/gala-gopher/gala-gopher.conf
/opt/gala-gopher/extend_probes/*
/opt/gala-gopher/meta/*
/usr/lib/systemd/system/gala-gopher.service


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
%doc gala-spider/doc/*
%license gala-spider/LICENSE
/%{_sysconfdir}/spider/gala-spider.conf
%{_bindir}/spider
%{_prefix}/lib/systemd/system/gala-spider.service
%dir %{_tmppath}/spider


%files -n python3-gala-spider
%{python3_sitelib}/spider/*
%{python3_sitelib}/spider-*.egg-info


%files -n aops-web
%attr(0755, root, root) /opt/aops_web/dist/*
%attr(0755, root, root) %{_sysconfdir}/nginx/aops-nginx.conf
%attr(0755, root, root) %{_unitdir}/aops-web.service


%changelog
* Fri Nov 12 2021 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.0.3-2
- gala-spider add anormaly_detection conf

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
