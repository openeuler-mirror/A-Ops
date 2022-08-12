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
// const recommendMetricList = ['warning', 'devlopprobe', 'systemprobe']

// const pluginModel = {
//   plugin_name: 'gitee',
//   is_installed: true,
//   status: true,
//   collect_items: [{
//     probe_name: 'probe1',
//     probe_status: true
//   },
//   {
//     probe_name: 'probe2',
//     probe_status: true
//   },
//   {
//     probe_name: 'probe3',
//     probe_status: false
//   },
//   {
//     probe_name: 'probe4',
//     probe_status: true
//   },
//   {
//     probe_name: 'probe5',
//     probe_status: false
//   }],
//   resource: [
//     {
//       name: 'cpu',
//       limit_value: '2G',
//       current_value: '4核'
//     },
//     {
//       name: 'mem',
//       limit_value: '2G',
//       current_value: '4核'
//     }
//   ]
// };
// const pluginModel2 = {
//   plugin_name: 'gihub',
//   is_installed: true,
//   status: true,
//   collect_items: [{
//     probe_name: 'probe1',
//     probe_status: false
//   },
//   {
//     probe_name: 'probe2',
//     probe_status: true
//   },
//   {
//     probe_name: 'probe3',
//     probe_status: false
//   }
// ],
//   resource: [
//     {
//       name: 'cpu',
//       limit_value: '2G',
//       current_value: '4核'
//     },
//     {
//       name: 'mem',
//       limit_value: '2G',
//       current_value: '4核'
//     }
//   ]
// };

const getHosts = (options) => {
  const body = getBody(options)
  console.log(body)

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

// host detail plugin control
// const sceneGet = (options) => {
//   return builder({
//     'msg': Mock.mock('success'),
//     'scene_name': '开发者模式',
//     'recommend_metric_list': recommendMetricList
//   }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

// const pluginInfoGet = (options) => {
//   const pluginData = []
//   for (let i = 0; i < 50; i++) {
//     pluginData.push(pluginModel)
//   }
//   for (let j = 0; j < 55; j++) {
//     pluginData.push(pluginModel2)
//   }
//   return builder({
//     'msg': Mock.mock('success'),
//     'info': pluginData
//   }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

// const metricSet = (options) => {
//   return builder({
//     'msg': Mock.mock('success')
//   }, 'probe修改成功', 200, { 'Custom-Header': Mock.mock('@guid') })
// }

// const pluginChange = (options) => {
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
// Mock.mock(/\/manage\/host\/scene\/get/, 'get', sceneGet)
// Mock.mock(/\/manage\/agent\/plugin\/info/, 'get', pluginInfoGet)
// Mock.mock(/\/manage\/agent\/plugin\/set/, 'post', pluginChange)
// Mock.mock(/\/manage\/agent\/metric\/set/, 'post', metricSet)