import Mock from 'mockjs2'
import { builder } from '../util'

const info = options => {
  console.log('options', options)
  const userInfo = {
    id: '4291d7da9005377ec9aec4a71ea837f',
    name: '天野远子',
    username: 'admin',
    password: '',
    avatar: '/avatar2.jpg',
    status: 1,
    telephone: '',
    lastLoginIp: '27.154.74.117',
    lastLoginTime: 1534837621348,
    creatorId: 'admin',
    createTime: 1497160610259,
    merchantCode: 'TLif2btpzg079h15bk',
    deleted: 0,
    roleId: 'admin',
    role: {}
  }
  // role
  const roleObj = {
    id: 'admin',
    name: '管理员',
    describe: '拥有所有权限',
    status: 1,
    creatorId: 'system',
    createTime: 1497160610259,
    deleted: 0,
    permissions: [
      // 开启权限验收后，通过permissions这个数组提供页面的权限控制，通过permissionId匹配
      {
        permissionId: 'dashboard',
        permissionName: '仪表盘'
      },
      {
        permissionId: 'assests',
        permissionName: '资产管理'
      },
      {
        permissionId: 'diagnosis',
        permissionName: '智能诊断'
      }
    ]
  }

  userInfo.role = roleObj
  return builder(userInfo)
}

/* for async-router, where router list are send by back-end
const userNav = options => {
  const nav = [
    // dashboard
    {
      name: 'dashboard',
      parentId: 0,
      id: 1,
      meta: {
        icon: 'dashboard',
        title: '仪表盘',
        show: true
      },
      component: 'Dashboard'
    },

    // assests
    {
      name: 'assests',
      parentId: 0,
      id: 2,
      meta: {
        icon: 'form',
        title: '资产管理'
      },
      redirect: '/assests/hosts-management',
      component: 'RouteView'
    },
    {
      name: 'hosts-management',
      parentId: 2,
      id: 21,
      meta: {
        title: '主机管理'
      },
      component: 'Dashboard'
    }
  ]
  const json = builder(nav)
  console.log('json', json)
  return json
}
*/

Mock.mock(/\/api\/user\/info/, 'get', info)
// Mock.mock(/\/api\/user\/nav/, 'get', userNav)
