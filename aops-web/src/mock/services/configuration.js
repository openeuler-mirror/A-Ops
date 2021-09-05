import Mock from 'mockjs2'
import { builder } from '../util'

const domainData = [
  {
    'domainName': 'domainName1',
    'priority': 0
  },
  {
    'domainName': 'domainName2',
    'priority': 0
  },
  {
    'domainName': 'domainName3',
    'priority': 0
  },
  {
    'domainName': 'domainName4',
    'priority': 0
  },
  {
    'domainName': 'domainName5',
    'priority': 0
  },
  {
    'domainName': 'domainName6',
    'priority': 0
  }
]
const domainHostData = [
  {
    'ipv6': 'ipv6',
    'ip': '202.193.49.1',
    'hostId': 'hostId1'
  },
  {
    'ipv6': 'ipv6',
    'ip': '202.193.49.2',
    'hostId': 'hostId2'
  },
  {
    'ipv6': 'ipv6',
    'ip': '202.193.49.3',
    'hostId': 'hostId3'
  },
  {
    'ipv6': 'ipv6',
    'ip': '202.193.49.4',
    'hostId': 'hostId4'
  },
  {
    'ipv6': 'ipv6',
    'ip': '202.193.49.5',
    'hostId': 'hostId5'
  }
]
const doMainStatusData = {
  'hostStatus': [
    {
      'hostId': 'hostId1',
      'syncStatus': [
        {
          'isSynced': 'FOUND',
          'filePath': 'filePath'
        },
        {
         'isSynced': 'FOUND',
          'filePath': 'filePath'
        }
      ]
    },
    {
      'hostId': 'hostId2',
      'syncStatus': [
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        },
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        }
      ]
    },
    {
      'hostId': 'hostId3',
      'syncStatus': [
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        },
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        }
      ]
    },
    {
      'hostId': 'hostId4',
      'syncStatus': [
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        },
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        }
      ]
    },
    {
      'hostId': 'hostId5',
      'syncStatus': [
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        },
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        }
      ]
    },
    {
      'hostId': 'hostId6',
      'syncStatus': [
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        },
        {
          'isSynced': 'NOT FOUND',
          'filePath': 'filePath'
        }
      ]
    }
  ],
  'domainName': 'domainName'
}
const syncConfData = [
  {
    'hostId': 'hostId1',
    'syncStatus': 'SUCCESS'
  },
  {
    'hostId': 'hostId2',
    'syncStatus': 'SUCCESS'
  },
  {
    'hostId': 'hostId3',
    'syncStatus': 'FAIL'
  }
]
const realConfsData = [
  {
    'domainName': 'domainName',
    'hostID': 'hostID',
    'confBaseInfos': [
      {
        'rpmName': 'rpmName',
        'path': '/ete/yum.repos.d/openEuler.repo',
        'filePath': 'filePath',
        'spacer': 'spacer',
        'rpmVersion': 'rpmVersion',
        'rpmRelease': 'rpmRelease',
        'fileOwner': 'fileOwner',
        'confType': 'key-value',
        'confContents': ' "OS": { "nam34e": "OS", "baseurl": "http://repo.open{ "OS": { "nam12e": "OS", "baseurl": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/", "enabled": "1", "gpgcheck": "1", "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler" }, "21.09": { "name": "21.09", "baseurl": "http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345", "enabled": "1", "gpgcheck": "0" }, "everything": { "name": "everything", "baseurl": "http://repo.openeuler.org/openEuler-21.03/everything/$basearch/", }\n',
        'fileAttr': 'fileAttr',
        'diff': '1'
      },
      {
        'rpmName': 'rpmName',
        'path': '/ete/yum.repos.d/openEuler.repo2',
        'filePath': 'filePath',
        'spacer': 'spacer',
        'rpmVersion': 'rpmVersion',
        'rpmRelease': 'rpmRelease',
        'fileOwner': 'fileOwner',
        'confType': 'key-value',
        'confContents': '{ "OS": { "nam34e": "OS", "baseurl": "http://repo.open{ "OS": { "nam12e": "OS", "baseurl": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/", "enabled": "1", "gpgcheck": "1", "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler" }, "21.09": { "name": "21.09", "baseurl": "http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345", "enabled": "1", "gpgcheck": "0" }, "everything": { "name": "everything", "baseurl": "http://repo.openeuler.org/openEuler-21.03/everything/$basearch/", }\n',
        'fileAttr': 'fileAttr',
        'diff': '2'
      },
      {
        'rpmName': 'rpmName',
        'path': '/ete/yum.repos.d/openEuler.repo3',
        'filePath': 'filePath',
        'spacer': 'spacer',
        'rpmVersion': 'rpmVersion',
        'rpmRelease': 'rpmRelease',
        'fileOwner': 'fileOwner',
        'confType': 'key-value',
        'confContents': '{ "OS": { "nam34e": "OS", "baseurl": "http://repo.open{ "OS": { "nam12e": "OS", "baseurl": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/", "enabled": "1", "gpgcheck": "1", "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler" }, "21.09": { "name": "21.09", "baseurl": "http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345", "enabled": "1", "gpgcheck": "0" }, "everything": { "name": "everything", "baseurl": "http://repo.openeuler.org/openEuler-21.03/everything/$basearch/", }\n',
        'fileAttr': 'fileAttr',
        'diff': '3'
      }
    ]
  }
]
const expectedConfsData = [
  {
    'domainName': 'domainName',
    'confBaseInfos': [
      {
        'expectedContents': '{ "OS": { "nam34e": "OS", "baseurl": "http://repo.open{ "OS": { "nam12e": "OS", "baseurl": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/", "enabled": "1", "gpgcheck": "1", "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler" }, "21.09": { "name": "21.09", "baseurl": "http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345", "enabled": "1", "gpgcheck": "0" }, "everything": { "name": "everything", "baseurl": "http://repo.openeuler.org/openEuler-21.03/everything/$basearch/", }\n',
        'filePath': '/ete/yum.repos.d/openEuler.repo',
        'changeLog': [
          {
            'date': '2000-01-23T04:56:07.000+00:00',
            'preValue': 'preValue',
            'changeReason': 'changeReason',
            'author': 'author',
            'postValue': 'postValue',
            'changeId': 'changeId'
          },
          {
            'date': '2000-01-23T04:56:07.000+00:00',
            'preValue': 'preValue',
            'changeReason': 'changeReason',
            'author': 'author',
            'postValue': 'postValue',
            'changeId': 'changeId'
          }
        ]
      },
      {
        'expectedContents': '{ "OS": { "nam34e": "OS", "baseurl": "http://repo.open{ "OS": { "nam12e": "OS", "baseurl": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/", "enabled": "1", "gpgcheck": "1", "gpgkey": "http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler" }, "21.09": { "name": "21.09", "baseurl": "http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345", "enabled": "1", "gpgcheck": "0" }, "everything": { "name": "everything", "baseurl": "http://repo.openeuler.org/openEuler-21.03/everything/$basearch/", }\n',
        'filePath': '/ete/yum.repos.d/openEuler.repo2',
       'changeLog': [
          {
            'date': '2000-01-23T04:56:07.000+00:00',
            'preValue': 'preValue',
            'changeReason': 'changeReason',
            'author': 'author',
            'postValue': 'postValue',
            'changeId': 'changeId'
          },
          {
            'date': '2000-01-23T04:56:07.000+00:00',
            'preValue': 'preValue',
            'changeReason': 'changeReason',
            'author': 'author',
            'postValue': 'postValue',
            'changeId': 'changeId'
          }
        ]
      }
    ]
  }
]
const createDomain = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 0, { 'Custom-Header': Mock.mock('@guid') })
}
const getDomainData = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'domainData': domainData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const deleteDomain = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'syncConfData': syncConfData
  }, '删除成功', 0, { 'Custom-Header': Mock.mock('@guid') })
}
const getDomainHostData = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'domainHostData': domainHostData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const getDomainStatus = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'doMainStatusData': doMainStatusData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const delHost = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const syncConf = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'syncConfData': syncConfData
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const queryRealConfs = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'realConfsData': realConfsData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const queryExpectedConfs = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'expectedConfsData': expectedConfsData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const addHost = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 0, { 'Custom-Header': Mock.mock('@guid') })
}

const addDomain = (options) => {
  console.log('添加主机域： ', options)

  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

Mock.mock(/\/domain\/createDomain/, 'post', addDomain)
Mock.mock(/\/domain\/deleteDomain/, 'delete', deleteDomain)
Mock.mock(/\/domain\/queryDomain/, 'get', getDomainData)
Mock.mock(/\/domain\/createDomain/, 'post', createDomain)
Mock.mock(/\/domain\/deleteDomain/, 'post', deleteDomain)
Mock.mock(/\/host\/getHost/, 'get', getDomainHostData)
Mock.mock(/\/host\/deleteHost/, 'post', delHost)
Mock.mock(/\/host\/addHost/, 'post', addHost)
Mock.mock(/\/confs\/getDomainStatus/, 'get', getDomainStatus)
Mock.mock(/\/confs\/syncConf/, 'post', syncConf)
Mock.mock(/\/confs\/queryRealConfs/, 'get', queryRealConfs)
Mock.mock(/\/confs\/queryExpectedConfs/, 'get', queryExpectedConfs)
