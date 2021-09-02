import request from '@/utils/request'

const api = {
  hostList: '/manage/host/get', // 全量接口待确认
  hostInfo: '/manage/host/info/query',
  addHost: '/manage/host/add',
  editHost: '/manage/host/edit_host', // 未提供
  deleteHost: '/manage/host/delete',
  hostGroupList: '/manage/host/group/get',
  addHostGroup: '/manage/host/group/add',
  deleteHostGroup: '/manage/host/group/delete',
  transcationDomainConfigList: '/manage/config/get_transcation_domain_config',
  deleteTranscationDomainConfig: '/manage/config/delete_transcation_domain_config'
}

export default api

const directionMap = {
  'ascend': 'asc',
  'descend': 'desc'
}
const managementMap = {
  'true': true,
  'false': false
}

// 主机管理
export function hostList ({ tableInfo, ...parameter }) {
  console.log('主机列表： ', tableInfo, parameter)
  const management = tableInfo.filters.management
  ? managementMap[tableInfo.filters.management[0]] // 将字符串true false转换成boolean
  : undefined
  return request({
    url: api.hostList,
    method: 'post',
    data: {
      ...parameter,
      host_group_list: tableInfo.filters.host_group_name || [],
      management,
      sort: tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  })
}

export function hostInfo (parameter) {
  console.log(parameter)
  return request({
    url: api.hostInfo,
    method: 'post',
    data: {
      ...parameter,
      host_list: parameter.host_list
    }
  })
}

export function addHost (parameter) {
  return request({
    url: api.addHost,
    method: 'post',
    data: {
      host_list: [{
        host_name: parameter.host_name,
        host_group_name: parameter.host_group_name,
        public_ip: parameter.public_ip,
        ssh_port: parameter.ssh_port,
        management: parameter.management,
        username: parameter.username,
        password: parameter.password,
        sudo_password: parameter.sudo_password
      }],
      key: parameter.key
    }
  })
}

export function deleteHost ({ hostList, parameter }) {
  return request({
    url: api.deleteHost,
    method: 'delete',
    data: {
      host_list: hostList,
      ...parameter
    }
  })
}

// 主机组管理
export function hostGroupList ({ tableInfo, ...parameter }) {
  return request({
    url: api.hostGroupList,
    method: 'post',
    data: {
      ...parameter,
      sort: tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  })
}

export function addHostGroup ({ name, description, ...parameter }) {
  return request({
    url: api.addHostGroup,
    method: 'post',
    data: {
      ...parameter,
      host_group_name: name,
      description
    }
  })
}

export function deleteHostGroup ({ hostGroupList, parameter }) {
  return request({
    url: api.deleteHostGroup,
    method: 'delete',
    data: {
      host_group_list: hostGroupList,
      ...parameter
    }
  })
}
