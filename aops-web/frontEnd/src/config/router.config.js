// eslint-disable-next-line
import { UserLayout, BasicLayout, BlankLayout } from '@/layouts'
// import { bxAnaalyse } from '@/core/icons'

const RouteView = {
  name: 'RouteView',
  render: h => h('router-view')
}

const routeMap = {
  index: {
    title: 'menu.home',
    path: '/'
  },
  assests: {
    title: 'menu.assests',
    path: '/assests',
    children: {
      HostsManagement: {
        title: 'menu.assests.hosts-management',
        path: '/assests/hosts-management'
      },
      CreateHost: {
        title: 'menu.assests.create-host',
        path: '/assests/hosts-management/host-create'
      }
    }
  },
  diagnosis: {
    title: 'menu.diagnosis',
    path: '/diagnosis',
    children: {
      AbnormalCheck: {
        title: 'menu.diagnosis.abnormal-check',
        path: '/diagnosis/abnormal-check/redirect',
        children: {
          MainView: {
            title: 'menu.diagnosis.abnormal-check',
            path: '/diagnosis/abnormal-check'
          },
          RuleManagement: {
            title: 'menu.diagnosis.abnormal-check.rule-management',
            path: '/diagnosis/abnormal-check/rule-management'
          }
        }
      },
      FaultDiagnosis: {
        title: 'menu.diagnosis.fault-diagnosis',
        path: '/diagnosis/fault-diagnosis/redirect',
        children: {
          MainView: {
            title: 'menu.diagnosis.fault-diagnosis',
            path: '/diagnosis/fault-diagnosis'
          },
          FaultTrees: {
            title: 'menu.diagnosis.fault-trees',
            path: '/diagnosis/fault-trees/:id'
          },
          DiagReport: {
            title: 'menu.diagnosis.diag-report',
            path: '/diagnosis/diag-report/:id'
          },
          NetworkTopoDiagram: {
            title: 'menu.diagnosis.network-topo-diagram',
            path: '/diagnosis/network-topo-diagram'
          }
        }
      }
    }
  },
  configuration: {
    title: 'menu.configuration',
    path: '/configuration',
    children: {
      TranscationDomainManagement: {
        title: 'menu.configuration.transcation-domain-management',
        path: '/configuration/transcation-domain-management'
      },
      TranscationDomainConfigurations: {
        title: 'menu.configuration.transcation-domain-configurations',
        path: '/configuration/transcation-domain-configurations'
      },
      hostConfigurations: {
        title: 'menu.configuration.host-configurations',
        path: '/configuration/host-configurations'
      },
      queryHostList: {
        title: 'menu.configuration.transcation-domain-management.query_host_list',
        path: '/configuration/query_host_list/:domainName'
      }
    }
  }
}

export const asyncRouterMap = [
  {
    path: routeMap.index.path,
    name: 'index',
    component: BasicLayout,
    meta: { title: routeMap.index.title },
    redirect: '/dashboard',
    children: [
      // dashboard
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard'),
        meta: { title: 'menu.dashboard.workplace', icon: 'dashboard', permission: ['dashboard'] }
      },
      {
        path: routeMap.assests.path,
        name: 'assests',
        redirect: '/assests/hosts-management',
        component: RouteView,
        meta: { title: routeMap.assests.title, icon: 'form', permission: ['assests'] },
        children: [
          {
            path: routeMap.assests.children.HostsManagement.path,
            name: 'HostsManagement',
            component: () => import('@/views/assests/HostManagement'),
            meta: { title: routeMap.assests.children.HostsManagement.title, permission: ['assests'] }
          },
          {
            path: routeMap.assests.children.CreateHost.path,
            name: 'CreateHost',
            hidden: true,
            component: () => import('@/views/assests/HostEdition'),
            meta: {
              title: routeMap.assests.children.CreateHost.title,
              permission: ['assests'],
              diyBreadcrumb: [
                { breadcrumbName: routeMap.index.title, path: routeMap.index.path },
                { breadcrumbName: routeMap.assests.title, path: routeMap.assests.path },
                { breadcrumbName: routeMap.assests.children.HostsManagement.title, path: routeMap.assests.children.HostsManagement.path },
                { breadcrumbName: routeMap.assests.children.CreateHost.title, path: routeMap.assests.children.CreateHost.path }
              ]
            }
          },
          {
            path: '/assests/host/edit/:hostId',
            name: 'EditHost',
            hidden: true,
            component: () => import('@/views/assests/HostEdition'),
            meta: { title: 'menu.assests.edit-host', permission: ['assests'] }
          },
          {
            path: '/assests/host-group-management',
            name: 'HostGroupManagement',
            component: () => import('@/views/assests/HostGroupManagement'),
            meta: { title: 'menu.assests.host-group-management', permission: ['assests'] }
          }
        ]
      }
      /* 关闭智能诊断页面路由
      {
        path: routeMap.diagnosis.path,
        name: 'diagnosis',
        redirect: '/diagnosis/abnormal-check',
        component: RouteView,
        meta: { title: routeMap.diagnosis.title, icon: 'form', permission: ['diagnosis'] },
        children: [{
          path: routeMap.diagnosis.children.AbnormalCheck.path,
          name: 'AbnormalCheck',
          component: RouteView,
          redirect: routeMap.diagnosis.children.AbnormalCheck.children.MainView.path,
          meta: { title: routeMap.diagnosis.children.AbnormalCheck.title, permission: ['diagnosis'] },
          hideChildrenInMenu: true,
          children: [{
            path: routeMap.diagnosis.children.AbnormalCheck.children.MainView.path,
            name: 'AbnormalCheckMainView',
            component: () => import('@/views/diagnosis/AbnormalCheck'),
            meta: {
              title: routeMap.diagnosis.children.AbnormalCheck.children.MainView.title,
              permission: ['diagnosis'],
              diyBreadcrumb: [
                { breadcrumbName: routeMap.index.title, path: routeMap.index.path },
                { breadcrumbName: routeMap.diagnosis.title, path: routeMap.diagnosis.path },
                { breadcrumbName: routeMap.diagnosis.children.AbnormalCheck.title, path: routeMap.diagnosis.children.AbnormalCheck.path }
              ]
            }
          }, {
            path: routeMap.diagnosis.children.AbnormalCheck.children.RuleManagement.path,
            name: 'RuleManagement',
            component: () => import('@/views/diagnosis/RuleManagement'),
            meta: { title: routeMap.diagnosis.children.AbnormalCheck.children.RuleManagement.title, permission: ['diagnosis'] }
          }]
        }, {
          path: routeMap.diagnosis.children.FaultDiagnosis.path,
          name: 'FaultDiagnosis',
          component: RouteView,
          redirect: routeMap.diagnosis.children.FaultDiagnosis.children.MainView.path,
          meta: { title: routeMap.diagnosis.children.FaultDiagnosis.title, permission: ['diagnosis'] },
          hideChildrenInMenu: true,
          children: [{
            path: routeMap.diagnosis.children.FaultDiagnosis.children.MainView.path,
            name: 'MainView',
            component: () => import('@/views/diagnosis/FaultDiagnosis'),
            meta: {
              title: routeMap.diagnosis.children.FaultDiagnosis.children.MainView.title,
              permission: ['diagnosis'],
              diyBreadcrumb: [
                { breadcrumbName: routeMap.index.title, path: routeMap.index.path },
                { breadcrumbName: routeMap.diagnosis.title, path: routeMap.diagnosis.path },
                { breadcrumbName: routeMap.diagnosis.children.FaultDiagnosis.title, path: routeMap.diagnosis.children.FaultDiagnosis.path }
              ]
            }
          }, {
            path: routeMap.diagnosis.children.FaultDiagnosis.children.FaultTrees.path,
            name: 'FaultTrees',
            component: () => import('@/views/diagnosis/FaultTrees'),
            meta: { title: routeMap.diagnosis.children.FaultDiagnosis.children.FaultTrees.title, permission: ['diagnosis'] }
          }, {
            path: routeMap.diagnosis.children.FaultDiagnosis.children.DiagReport.path,
            name: 'DiagReport',
            component: () => import('@/views/diagnosis/DiagReport'),
            meta: { title: routeMap.diagnosis.children.FaultDiagnosis.children.DiagReport.title, permission: ['diagnosis'] }
          }, {
            path: routeMap.diagnosis.children.FaultDiagnosis.children.NetworkTopoDiagram.path,
            name: 'NetworkTopoDiagram',
            component: () => import('@/views/diagnosis/NetworkTopoDiagram'),
            meta: { title: routeMap.diagnosis.children.FaultDiagnosis.children.NetworkTopoDiagram.title, permission: ['diagnosis'] }
          }]
        }]
      },
      */
      /* 关闭配置管理页面
      {
        path: routeMap.configuration.path,
        name: 'configuration',
        redirect: routeMap.configuration.children.TranscationDomainManagement.path,
        component: RouteView,
        meta: { title: routeMap.configuration.title, icon: 'form', permission: ['configuration'] },
        children: [
          {
            path: routeMap.configuration.children.TranscationDomainManagement.path,
            name: 'transcationDomainManagement',
            component: () => import('@/views/configuration/TranscationDomainManagement'),
            meta: { title: routeMap.configuration.children.TranscationDomainManagement.title, permission: ['configuration'] }
          },
          {
            path: routeMap.configuration.children.TranscationDomainConfigurations.path,
            name: 'transcationDomainConfigurations',
            component: () => import('@/views/configuration/TranscationDomainConfigurations'),
            meta: { title: routeMap.configuration.children.TranscationDomainConfigurations.title, permission: ['configuration'] }
          },
          {
            // 主机管理页面开发完成后从menu中隐藏掉，同时配置自定义面包屑
            path: routeMap.configuration.children.hostConfigurations.path,
            name: 'hostConfigurations',
            component: () => import('@/views/configuration/TranscationDomainManagement'),
            meta: { title: routeMap.configuration.children.hostConfigurations.title, permission: ['configuration'] }
          },
          {
            path: '/configuration/diff-test',
            name: 'DiffTest',
            component: () => import('@/views/configuration/DiffTest'),
            meta: { title: 'diff test', permission: ['configuration'] }
          },
          {
            path: routeMap.configuration.children.queryHostList.path,
            name: 'QueryHostList',
            hidden: true,
            component: () => import('@/views/configuration/QueryHostList'),
            meta: {
              title: routeMap.configuration.children.queryHostList.title,
              permission: ['configuration'],
              diyBreadcrumb: [
                { breadcrumbName: routeMap.index.title, path: routeMap.index.path },
                { breadcrumbName: routeMap.configuration.title, path: routeMap.configuration.path },
                { breadcrumbName: routeMap.configuration.children.TranscationDomainManagement.title, path: routeMap.configuration.children.TranscationDomainConfigurations.path },
                { breadcrumbName: routeMap.configuration.children.queryHostList.title, path: routeMap.configuration.children.queryHostList.path }
              ] }
          }
        ]
      }
      */
    ]
  },
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

/**
 * 基础路由
 * @type { *[] }
 */
export const constantRouterMap = [
  {
    path: '/user',
    component: UserLayout,
    redirect: '/user/login',
    hidden: true,
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Login')
      },
      {
        path: 'register',
        name: 'register',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Register')
      },
      {
        path: 'register-result',
        name: 'registerResult',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/RegisterResult')
      },
      {
        path: 'recover',
        name: 'recover',
        component: undefined
      }
    ]
  },

  {
    path: '/404',
    component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404')
  }
]
