Name:		A-Ops
Version:	v1.3.0
Release:	3
Summary:	The intelligent ops toolkit for openEuler
License:	MulanPSL2
URL:		https://gitee.com/openeuler/A-Ops
Source0:	%{name}-%{version}.tar.gz
%global debug_package %{nil}

# build for ragdoll & aops basic module
BuildRequires:  python3-setuptools python3-connexion python3-werkzeug python3-libyang
BuildRequires:	git python3-devel systemd

# build for aops basic module
BuildRequires:  python3-setuptools python3-kafka-python python3-connexion


%description
The intelligent ops toolkit for openEuler


%package -n gala-ragdoll
Summary:    Configuration traceability
Requires:   python3-gala-ragdoll = %{version}-%{release}

%description -n gala-ragdoll
Configuration traceability


%package -n python3-gala-ragdoll
Summary: python3 pakcage of gala-ragdoll
Requires: python3-flask-testing python3-libyang git
Requires: python3-werkzeug python3-connexion python3-swagger-ui-bundle

%description -n python3-gala-ragdoll
python3 pakcage of gala-ragdoll


%prep
%autosetup -n %{name}-%{version}


%build
#build for gala-ragdoll
pushd gala-ragdoll
%py3_build
popd


%install
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


%pre -n gala-ragdoll
if [ -f "%{systemd_dir}/gala-ragdoll.service" ] ; then
        systemctl enable gala-ragdoll.service || :
fi

%post -n gala-ragdoll
%systemd_post gala-ragdoll.service

%preun -n gala-ragdoll
%systemd_preun gala-ragdoll.service

%postun -n gala-ragdoll
%systemd_postun gala-ragdoll.service


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


%changelog
* Mon Apr 17 2023 wenxin<shusheng.wen@outlook.com> - v1.3.0-3
- update the host id validate method for ragdoll

* Tue Feb 28 2023 zhuyuncheng<zhuyuncheng@huawei.com> - v1.3.0-2
- remove packages which have moved to new repositories.

* Mon Sep 26 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.3.0-1
- update delete host return message
- update add domain return message

* Wed Sep 14 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.6-1
- move aops-basedatabase to aops-tools
- rename default scene from 'unknown' to 'normal'

* Tue Sep 13 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.5-4
- bug fix: start gala-ragdoll.service when install gala-ragdoll.

* Fri Sep 9 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.5-3
- bug fix: add create time attribute of workflow, fix assign model bug of aops-check default mode
- update agent get host info interface and some test cases
- fix gala-ragdoll return code issue
- web fine-tuning for workflow and agent info.

* Wed Sep 7 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.5-2
- bug fix: adjust dependent packages for gala-ragdoll.

* Tue Sep 6 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.5-1
- bug fix: bugfix of aops-web and aops-check's interaction

* Fri Sep 2 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.4-1
- add default mode of aops-check, which can run independently.

* Mon Aug 29 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.3-3
- bug fix: gala-spider adapt to abnormal event format change.

* Mon Aug 29 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.3-2
- bug fix: bugfix for gopher report metadata to kafka.

* Sat Aug 27 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.3-1
- Add requires of aops-check for new features.

* Tue Aug 23 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.2-2
- Set user modification of confs will not be overwrite for gala_spider.

* Wed Aug 10 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.2.2-1
- New release 1.2.2, bug fix and add new module.
- add missed requirement python3-PyMySQL
- add new module, check and web

* Wed Aug 10 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.1-1
- New release 1.2.1, bug fix.
- modify patch for gala-gopher and rm patch for gala-anteater.
- reduce the operating noise of gala-gopher.
- optimize the module of gala-anteater.

* Tue Aug 2 2022 zhaoyuxing<zhaoyuxing2@huawei.com> - v1.2.0-3
- 1. add patch to modify install_requires of gala-anteater.
- 2. delete redundant dependent packages for gala-spider.

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
