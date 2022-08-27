import Mock from 'mockjs2'
import { builder, getBody } from '../util'

const hostMockData = [
  {
    host_id: '101',
    host_name: 'host1',
    public_ip: '192.1.1.1',
    ssh_port: '1000',
    host_group_name: 'g1',
    management: 'true',
    status: 'online'
  },
  {
    host_id: '102',
    host_name: 'host2',
    public_ip: '192.1.1.2',
    ssh_port: '1000',
    host_group_name: 'g2',
    management: 'true',
    status: 'online'
  },
  {
    host_id: '103',
    host_name: 'host3',
    public_ip: '192.1.1.3',
    ssh_port: '1001',
    host_group_name: 'g2',
    management: 'true',
    status: 'online'
  }
]

const hostsInfo = [
  {
      host_id: '101',
      host_name: 'host1',
      public_ip: '192.1.1.1',
      host_group_name: 'host1',
      management: 'true',
      scene: '大数据',
      status: 'online'
  },
  {
      host_id: '102',
      host_name: 'host2',
      public_ip: '192.1.1.2',
      host_group_name: 'host2',
      management: 'true',
      scene: '大数据',
      status: 'online'
  },
  {
      host_id: '103',
      host_name: 'host3',
      public_ip: '192.1.1.3',
      host_group_name: 'host2',
      management: 'true',
      scene: '大数据',
      status: 'online'
  },
  {
      host_id: '113',
      host_name: 'host4',
      public_ip: '192.1.1.4',
      host_group_name: 'host1',
      management: 'true',
      scene: '大数据',
      status: 'online'
  }
]
const hostInfoList = [
  {
    'host_id': 'id1',
    'host_name': 'host1',
    'host_group_name': 'group1',
    'host_group_id': '1003',
    'public_ip': '1.1.1.1',
    'ssh_port': 2,
    'management': false,
    'status': 'online'
  }
]

const hostGroupInfos = [
  {
    host_group_id: '1001',
    host_group_name: 'hos.1',
    description: '华北-可用区',
    host_count: '21',
    status: 'OK'
  },
  {
    host_group_id: '1002',
    host_group_name: 'host2',
    description: '无',
    host_count: '1',
    status: 'OK'
  },
  {
    host_group_id: '1003',
    host_group_name: 'host3',
    description: '华南可用区G',
    host_count: '0',
    status: 'OK'
  }
]
// const hostGroupInfo = [
//   {
//       host_group_name: '主机组1',
//       description: '华北-可用区',
//       host_count: '21'
//   },
//   {
//       host_group_name: 'g2',
//       description: '无',
//       host_count: '1'
//   },
//   {
//       host_group_name: 'g1',
//       description: '华南可用区G',
//       host_count: '3'
//   }
// ]
const filterByName = a => b => {
  return b.host_group_name.indexOf(a) > -1
}
const getHostList = (options) => {
  const body = getBody(options)
  let hosts
  if (body.host_group_list && body.host_group_list.length > 0) {
    hosts = hostsInfo.filter(filterByName(body.host_group_list))
  } else {
      hosts = hostsInfo
  }
  return builder({
    'msg': Mock.mock('success'),
    'total_count': 3,
    'total_page': options,
    'host_infos': hosts
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const hostInfos = [
    {
      'host_id': '192.168.1.1',
      'infos': {
        'os': {
          'kernel_version': '2.6.32-642.el6.x86_64',
          'bios_version': 'LENOVOCKCN11WW(V1.1)',
          'name': 'HarmonyOS系统'
        },
        'cpu': {
          'architecture': 'X86架构',
          'core_count': '4核',
          'model_name': 'Intel Core2 Duo P9xxx',
          'vendor_id': '1234',
          'l1d_cache': '32K',
          'l1i_cache': '32K',
          'l2_cache': '256K',
          'l3_cache': '8192K'
        },
        'memory': {
          'size': '128GB',
          'total': 0,
          'info': [
            {
              'size': '128GB',
              'type': 'SDRAM',
              'speed': '5ns',
              'manufacturer': '金士顿科技'
            }
          ]
        }
      }
    }
]

// host detail plugin control
const recommendMetricList = {
  gopher: [
    'probe1',
    'probe2',
    'probe3'
  ],
  plugin1: [
    'probe4',
    'probe5'
  ],
  plugin2: [
    'probe6',
    'probe7'
  ]
}

const pluginModel = {
  plugin_name: 'gropher',
  is_installed: true,
  status: 'active',
  collect_items: [{
    probe_name: '1ewwe',
    probe_status: 'off',
    support_auto: false
  },
  {
    probe_name: '1sfa',
    probe_status: 'on',
    support_auto: true
  },
  {
    probe_name: '1sfssa',
    probe_status: 'on',
    support_auto: false
  }],
  resource: [
    {
      name: 'cpu',
      limit_value: '2G',
      current_value: '4核'
    },
    {
      name: 'mem',
      limit_value: '2G',
      current_value: '4核'
    }
  ]
};

const pluginMode2 = {
  plugin_name: 'gsdr',
  is_installed: true,
  status: 'inactive',
  collect_items: [{
    probe_name: '2tdrd',
    probe_status: 'auto',
    support_auto: true
  },
  {
    probe_name: '2hfghg',
    probe_status: 'on',
    support_auto: true
  },
  {
    probe_name: '2sfssa',
    probe_status: 'on',
    support_auto: false
  }],
  resource: [
    {
      name: 'cpu',
      limit_value: '2G',
      current_value: '4核'
    },
    {
      name: 'mem',
      limit_value: '2G',
      current_value: '4核'
    }
  ]
};
const pluginMode3 = {
  plugin_name: 'ser',
  is_installed: true,
  status: 'active',
  collect_items: [{
    probe_name: '3pwe',
    probe_status: 'off',
    support_auto: true
  },
  {
    probe_name: '3preee',
    probe_status: 'auto',
    support_auto: true
  },
  {
    probe_name: '3sfssa',
    probe_status: 'off',
    support_auto: false
  }],
  resource: [
    {
      name: 'cpu',
      limit_value: '2G',
      current_value: '4核'
    },
    {
      name: 'mem',
      limit_value: '2G',
      current_value: '4核'
    }
  ]
};
const getHosts = (options) => {
  const body = getBody(options)

  let hostsData
  if (body.host_group_list && body.host_group_list.length > 0) {
    // 测试有主机组筛选的情况
    hostsData = [hostMockData[body.host_group_list[0] - 1001]]
  } else {
    hostsData = hostMockData
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 3,
    'total_page': 2,
    'host_infos': hostsData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostInfo = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'total_count': 3,
    'total_page': 2,
    'host_infos': hostInfoList
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const addHost = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const deleteHost = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const getHostGroupList = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'total_count': 3,
    'total_page': 2,
    'host_group_infos': hostGroupInfos
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const addHostGroup = (options) => {
  const body = getBody(options)

  if (!body.host_group_name || !body.description) {
    return builder({ 'msg': '缺少必要参数' }, '缺少参数', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const deleteHostGroup = (options) => {
  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

// const getHostGroup = (options) => {
//   return builder({
//     'msg': Mock.mock('success'),
//     'total_count': 3,
//     'total_page': 1,
//     'host_group_infos': hostGroupInfo
//   }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }
Mock.mock(/\/manage\/host\/get_host_group/, 'post', getHostGroupList)
// host detail plugin control
const sceneGet = (options) => {
  return builder({
    'msg': Mock.mock('success'),
    'scene_name': 'web',
    'collect_items': recommendMetricList
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const pluginInfoGet = (options) => {
  const pluginData = []
  pluginData.push(pluginModel)
  pluginData.push(pluginMode2)
  pluginData.push(pluginMode3)
  return builder({
    'msg': Mock.mock('success'),
    'info': pluginData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

// const metricSet = (options) => {
//   return builder({
//     'msg': Mock.mock('success')
//   }, 'probe修改成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

// const pluginSet = (options) => {
//   return builder({
//     'msg': Mock.mock('success')
//   }, 'plugin修改成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

const getHostInfoQuery = (options) => {
  return builder({
    'msg': Mock.mock('OperateSuccess'),
    'host_infos': hostInfos
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

Mock.mock(/\/manage\/host\/group\/get/, 'post', getHostGroupList)
Mock.mock(/\/manage\/host\/add_host_group/, 'post', addHostGroup)
Mock.mock(/\/manage\/host\/delete_host_group/, 'delete', deleteHostGroup)
Mock.mock(/\/manage\/host\/get_host_information/, 'get', getHostInfo)
Mock.mock(/\/manage\/host\/get/, 'post', getHosts)
Mock.mock(/\/manage\/host\/add_host/, 'post', addHost)
Mock.mock(/\/manage\/host\/delete_host/, 'delete', deleteHost)
Mock.mock(/\/manage\/host\/info\/query/, 'post', getHostInfoQuery)
// host detail plugin control
Mock.mock(/\/manage\/host\/scene\/get/, 'get', sceneGet)
Mock.mock(/\/manage\/agent\/plugin\/info/, 'get', pluginInfoGet)
// 获取主机列表
Mock.mock(/\/manage\/host\/get/, 'post', getHostList)
