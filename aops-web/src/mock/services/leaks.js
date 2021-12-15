// import Mock from 'mockjs2'
// import { builder, getBody } from '../util'
/*
const cvesMockData = [
  {
    cve_id: 'CEV-2021-29534',
    public_time: '30 AUG 2020',
    level: '高危',
    cvss: '7.2',
    hosts: ['1', '2', '3'],
    status: 'true',
    description: 'Around advice is the most general kind of advice. Since Spring AOP, like AspectJ, provides a full range of advice types, we recommend that you use the least powerful advice type that can implement the required behavior. For example, if you need only to update a cache with the return value of a method, you are better off implementing an after returning advice than an around advice, although an around advice can accomplish the same thing. Using the most specific advice type provides a simpler programming model with less potential for errors. For example, you do not need to invoke the proceed() method on the JoinPoint used for around advice, and, hence, you cannot fail to invoke it.'
  },
  {
    cve_id: 'CEV-2021-29535',
    public_time: '30 AUG 2020',
    level: '高危',
    cvss: '7.2',
    hosts: ['1', '2', '3', '5'],
    status: 'true',
    description: 'Around advice is the most general kind of advice. Since Spring AOP, like AspectJ, provides a full range of advice types, we recommend that you use the least powerful advice type that can implement the required behavior. For example, if you need only to update a cache with the return value of a method, you are better off implementing an after returning advice than an around advice, although an around advice can accomplish the same thing. Using the most specific advice type provides a simpler programming model with less potential for errors. For example, you do not need to invoke the proceed() method on the JoinPoint used for around advice, and, hence, you cannot fail to invoke it.'
  }
]
*/

/*
const hostListMockData = [
  {
    host_id: '192.168.1.1',
    public_ip: '192.168.1.1',
    repo_name: '20.03 update',
    status: 'true',
    scan_date: '6 hours ago',
    cveList: ['CEV-2021-29535', 'CEV-2021-29536']
  },
  {
    host_id: '192.168.1.2',
    public_ip: '192.168.1.2',
    repo_name: '20.10 update',
    status: 'true',
    scan_date: '12 hours ago',
    cveList: []
  }
]

const hostInCveMockData = [
  {
    host_id: '192.168.1.1',
    host_name: '192.168.1.1',
    host_ip: '192.168.1.1',
    host_group: 'group1',
    repo: '20.03-update',
    status: 'not reviewed',
    last_scan: 1111
  },
  {
    host_id: '192.168.1.2',
    host_name: '192.168.1.2',
    host_ip: '192.168.1.2',
    host_group: 'group1',
    repo: '20.03-update',
    status: 'not reviewed',
    last_scan: 1111
  }
]

const repoMockData = [
  {
    repo_name: '20.03-update',
    repo_data: '',
    repo_attr: 'openEuler-20.03'
  },
  {
    repo_name: '20.04-update',
    repo_data: '',
    repo_attr: 'ope'
  },
  {
    repo_name: '20.05-update',
    repo_data: '',
    repo_attr: 'openEuler-20.03'
  },
  {
    repo_name: '20.06-update',
    repo_data: '',
    repo_attr: 'ope'
  },
  {
    repo_name: '20.07-update',
    repo_data: '',
    repo_attr: 'openEuler-20.03'
  },
  {
    repo_name: '20.08-update',
    repo_data: '',
    repo_attr: 'ope'
  }
]
/*
const getCVES = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 2,
    'total_page': 1,
    'cvesList': cvesMockData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getCVEInfo = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    info: {
      cve_id: 'CEV-2021-29535',
      public_time: '30 AUG 2020',
      level: '高危',
      cvss: '7.2',
      hosts: [
        'h1', 'h2', 'h3'
      ],
      status: 'true',
      description: 'Around advice is the most general kind of advice. Since Spring AOP, like AspectJ, provides a full range of advice types, we recommend that you use the least powerful advice type that can implement the required behavior. For example, if you need only to update a cache with the return value of a method, you are better off implementing an after returning advice than an around advice, although an around advice can accomplish the same thing. Using the most specific advice type provides a simpler programming model with less potential for errors. For example, you do not need to invoke the proceed() method on the JoinPoint used for around advice, and, hence, you cannot fail to invoke it.'
    }
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostUnderCVE = (options) => {
  let result = {}
  const body = getBody(options)
  if (body.cve_list.length === 1) {
    result = {
      'CEV-2021-29534': [hostInCveMockData[0]]
    }
  } else {
    result = {
      'CEV-2021-29534': [hostInCveMockData[0]],
      'CEV-2021-29535': hostInCveMockData
    }
  }
  return builder({
    'msg': Mock.mock('success'),
    result
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostList = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    list: hostListMockData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostInfo = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    info: {
      host_id: '192.168.1.1',
      public_ip: '192.168.1.1',
      repo_name: '20.03 update',
      status: 'true',
      scan_date: '6 hours ago',
      cveList: ['CEV-2021-29535', 'CEV-2021-29536']
    }
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const addRepo = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success')
  }, '新建repo', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getRepo = (options) => {
  const body = getBody(options)
  console.log(body)
  let result = []

  if (body.repo_name_list.length < 1) {
    result = repoMockData
  } else {
    result = [repoMockData[0]]
  }

  return builder({
    'msg': Mock.mock('success'),
    result
  }, '新建repo', 200, { 'Custom-Header': Mock.mock('@guid') })
}
*/
/*
const getTaskList = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 2,
    'total_page': 1,
    'result': [
      {
        'task_id': 'id2',
        'task_name': 'task2',
        'task_type': 'cve',
        'description': 'fix cve CVE-2021-29535',
        'host_num': 2,
        'create_time': 11111
      }
    ]
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getTaskProgress = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 2,
    'total_page': 1,
    'result': {
      task1: {
          'succeed': 1,
          'fail': 0,
          'running': 11,
          'on standby': 0
      },
      task2: {
          'succeed': 5,
          'fail': 0,
          'running': 13,
          'on standby': 0
      }
   }
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
*/
/*
const getCveInfoUnderTask = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 2,
    'total_page': 1,
    'result': [
      {
          'cve_id': 'cve1',
          'package': 'test-p',
          'reboot': true,
          'host_num': 3,
          'status': 'running'
      }
  ]
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostOfCveInCveTask = (options) => {
  const body = getBody(options)
  console.log(body)

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 2,
    'total_page': 1,
    'result': {
      'cve1': [
        {
          'host_id': 'id1',
          'host_name': 'name1',
          'host_ip': 'ip1',
          'status': 'running' // 可选fixed unfixed running
        },
        {
          'host_id': 'id2',
          'host_name': 'name2',
          'host_ip': 'ip2',
          'status': 'fixed'
        }
      ]
  }
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
*/

// Mock.mock(/\/vulnerability\/cve\/host\/get/, 'post', getHostUnderCVE)
// Mock.mock(/\/leaks\/get_cves_info/, 'post', getCVEInfo)
// Mock.mock(/\/leaks\/get_cves/, 'post', getCVES)
// Mock.mock(/\/leaks\/get_host_leak_info/, 'post', getHostInfo)
// Mock.mock(/\/leaks\/get_host_leak_list/, 'post', getHostList)
// Mock.mock(/\/vulnerability\/repo\/import/, 'post', addRepo)
// Mock.mock(/\/vulnerability\/repo\/get/, 'post', getRepo)
// Mock.mock(/\/vulnerability\/task\/list\/get/, 'post', getTaskList)
// Mock.mock(/\/vulnerability\/task\/progress\/get/, 'post', getTaskProgress)
// Mock.mock(/\/vulnerability\/task\/cve\/info\/get/, 'post', getCveInfoUnderTask)
// Mock.mock(/\/vulnerability\/task\/cve\/status\/get/, 'post', getHostOfCveInCveTask)
