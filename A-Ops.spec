Name:		A-Ops
Version:	1.0.0
Release:	1
Summary:	The intelligent ops toolkit for openEuler
License:	MulanPSL2
URL:		https://gitee.com/openeuler/A-Ops
Source0:	%{name}-%{version}.tar.gz


# build for gopher
BuildRequires:	cmake gcc-c++ yum elfutils-devel clang >= 10.0.1 llvm libconfig-devel
BuildRequires:	librdkafka-devel libmicrohttpd-devel

# build for ragdoll & aops basic module
BuildRequires:  python3-setuptools python3-connexion python3-werkzeug python3-libyang
BuildRequires:	git python3-devel


%description
The intelligent ops toolkit for openEuler


%package -n aops-utils
Summary:	utils for A-Ops
Requires:   python3-concurrent-log-handler python3-xmltodict python3-pyyaml python3-marshmallow >= 3.13.0
Requires:   python3-requests python3-xlrd

%description -n aops-utils
utils for A-Ops


%package -n aops-cli
Summary:        cli of A-ops
Requires: 	aops-utils = %{version}-%{release}

%description -n aops-cli
commandline tool of aops, offer commands for account management, host management,
host group management, task and template management of ansible.


%package -n aops-manager
Summary:	manager of A-ops
Requires:	aops-utils = %{version}-%{release} ansible >= 2.9.0
Requires:   python3-pyyaml python3-marshmallow >= 3.13.0 python3-flask python3-flask-restful
Requires:   python3-requests sshpass

%description -n aops-manager
manager of A-ops, support software deployment and installation, account management, host management,
host group management, task and template management of ansible.


%package -n aops-database
Summary:	database center of A-ops
Requires:   aops-utils = %{version}-%{release} python3-pyyaml
Requires:   python3-elasticsearch >= 7 python3-requests python3-werkzeug python3-urllib3
Requires:   python3-flask python3-flask-restful python3-PyMySQL python3-sqlalchemy
Requires:   python3-prometheus-api-client

%description -n aops-database
database center of A-ops, offer database proxy of mysql, elasticsearch and prometheus time series database.


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
Requires: gala-ragdoll = %{version}-%{release} python3-flask-testing python3-libyang git python3-werkzeug

%description -n python3-gala-ragdoll
python3 pakcage of gala-ragdoll


%define debug_package %{nil}

%prep
%autosetup -n %{name}-%{version}


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

#build for gala-gopher
pushd gala-gopher
sh build.sh package
popd

#build for gala-ragdoll
pushd gala-ragdoll
%py3_build
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

#install for gala-gopher
pushd gala-gopher
install -d %{buildroot}/opt/gala-gopher
install -d %{buildroot}%{_bindir}
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
popd


%files -n aops-utils
%doc README.*
%{python3_sitelib}/aops_utils*.egg-info
%{python3_sitelib}/aops_utils/*
%attr(0755,root,root) %{_bindir}/aops-utils
%attr(0755,root,root) %{_bindir}/aops-convert-check-rule
%attr(0755,root,root) %{_bindir}/aops-convert-diag-tree


%files -n aops-cli
%attr(0755,root,root) %{_bindir}/aops
%attr(0644,root,root) %{_sysconfdir}/aops/system.ini
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
%attr(0644,root,root) %{_sysconfdir}/aops/collector.yml
%attr(0755,root,root) %{_unitdir}/aops-database.service
%attr(0755,root,root) %{_bindir}/aops-database
%attr(0755,root,root) %{_bindir}/aops-basedatabase
%{python3_sitelib}/aops_database*.egg-info
%{python3_sitelib}/aops_database/*


%files -n gala-gopher
%defattr(-,root,root)
%dir /opt/gala-gopher
%dir /opt/gala-gopher/extend_probes
%dir /opt/gala-gopher/meta
%{_bindir}/gala-gopher
%config(noreplace) /opt/gala-gopher/gala-gopher.conf
/opt/gala-gopher/extend_probes/*
/opt/gala-gopher/meta/*


%files -n gala-ragdoll
%doc gala-ragdoll/doc/*
%license gala-ragdoll/LICENSE
/%{_sysconfdir}/ragdoll/gala-ragdoll.conf
%{_bindir}/ragdoll


%files -n python3-gala-ragdoll
%{python3_sitelib}/ragdoll/*
%{python3_sitelib}/yang_modules/*
%{python3_sitelib}/ragdoll-*.egg-info


%changelog
* Sat 31 Jul 2021 orange-snn<songnannan2@huawei.com> - 1.0.0-1
- Package init

* Tue 24 Aug 2021 zhu-yuncheng<zhuyuncheng@huawei.com> - 1.0.0-2
- Update spec
