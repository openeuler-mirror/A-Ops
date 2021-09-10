import Mock from 'mockjs2'
import { builder, getBody } from '../util'

const managementConfInfos = [
  {
    id: 1,
    name: 'configuration 202108121234',
    filePath: 'vim /user/local/nginx/conf/nginx.comf',
    contents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} '
  },
  {
    id: 2,
    name: 'configuration 15',
    filePath: 'vim /etc/firewalld/firewalld.conf',
    contents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} '
  },
  {
    id: 3,
    name: 'configuration 01',
    filePath: '/etc/hostname',
    contents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} '
  },
  {
    id: 4,
    name: 'configuration 03',
    filePath: 'vim /user/local/nagios/etc/nrpe.cfg',
    contents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} '
  },
  {
    id: 5,
    name: 'configuration 12',
    filePath: 'vim /etc/sysconfig/network-scripts/ifcfg-eth0',
    contents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} '
  }
]

const managementConfChangeList = [
  {
    managemengConfId: 1,
    managementConfname: 'configuration 202108121234',
    expectedContents: '{\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.open{\n    "OS": {\n        "nam12e": "OS",\n        "baseurl": "http://repo.openeuler.org/OS/$basearch/",\n        "enabled": "1",\n        "gpgcheck": "1",\n        "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler"\n    },\n    "21.09": {\n} ',
    filePath: 'vim /user/local/nginx/conf/nginx.comf',
    changeLog: [
      {
        changeId: '32498492',
        date: '2000-01-23T04:56:07.000+00:00',
        author: 'admin123',
        changeReason: 'upgrade',
        preValue: '\n "OS": {\n        "nam12e": "OS",\n        "baseurl":',
        postValue: '\n        "enabled": "1",\n        "gpgcheck": "1"'
      },
      {
        changeId: 'dfkvnns33',
        date: '2000-01-23T04:56:07.000+00:00',
        author: 'administrator',
        changeReason: 'operation',
        preValue: '\n "OS": {\n        "nam12e": "OS",\n        "baseurl":',
        postValue: '\n        "enabled": "1",\n        "gpgcheck": "1"'
      },
      {
        changeId: 'c8ignasdas',
        date: '2000-01-23T04:56:07.000+00:00',
        author: 'user1',
        changeReason: 'test',
        preValue: '\n "OS": {\n        "nam12e": "OS",\n        "baseurl":',
        postValue: '\n        "enabled": "1",\n        "gpgcheck": "1"'
      },
      {
        changeId: 'casohaoisd',
        date: '2000-01-23T04:56:07.000+00:00',
        author: 'user2',
        changeReason: 'upgrade',
        preValue: '\n "OS": {\n        "nam12e": "OS",\n        "baseurl":',
        postValue: '\n        "enabled": "1",\n        "gpgcheck": "1"'
      }
    ]
  }
]

// const addManagementConf = (options) => {
//   console.log('模拟')
//   const body = getBody(options)
//
//   if (!body.domainName || !body.configList) {
//     return builder({ 'msg': '缺少必要参数' }, '缺少参数', 410)
//   }
//
//   return builder({
//     'msg': Mock.mock('success')
//   }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

const getManagementConf = (options) => {
  const body = getBody(options)
  console.log('option: ', options)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 3,
    'total_page': 2,
    'manageConf_infos': managementConfInfos
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const queryManageConfChange = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'manageConfChange': managementConfChangeList
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const deleteManagementConf = (options) => {
  console.log(options)

  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

// Mock.mock(/\/management\/addManagementConf/, 'post', addManagementConf)
Mock.mock(/\/management\/getManagementConf/, 'get', getManagementConf)
Mock.mock(/\/management\/queryManageConfChange/, 'get', queryManageConfChange)
Mock.mock(/\/management\/deleteManagementConf/, 'delete', deleteManagementConf)
