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

const getHosts = (options) => {
  const body = getBody(options)

  if (body.uid !== '123') {
      return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  let hostsData
  if (body.host_group_list && body.host_group_list.length > 0) {
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

Mock.mock(/\/manage\/host\/get_host_group/, 'post', getHostGroupList)
Mock.mock(/\/manage\/host\/add_host_group/, 'post', addHostGroup)
Mock.mock(/\/manage\/host\/delete_host_group/, 'delete', deleteHostGroup)
Mock.mock(/\/manage\/host\/get_host_information/, 'get', getHostInfo)
Mock.mock(/\/manage\/host\/get_host/, 'post', getHosts)
Mock.mock(/\/manage\/host\/add_host/, 'post', addHost)
Mock.mock(/\/manage\/host\/delete_host/, 'delete', deleteHost)
