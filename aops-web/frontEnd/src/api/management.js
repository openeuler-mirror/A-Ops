import request from '@/utils/request'

const api = {
  addManagementConf: '/management/addManagementConf', // 新增业务域配置
  getManagementConf: '/management/getManagementConf', // 读取业务域配置信息
  queryManageConfChange: '/management/queryManageConfChange', // 读取业务域配置日志信息
  deleteManagementConf: '/management/deleteManagementConf' // 删除业务域配置
}

export default api

// 新增配置
export function addManagementConf ({ name, configList, ...parameter }) {
  return request({
    url: api.addManagementConf,
    method: 'post',
    data: {
      ...parameter,
      domainName: name,
      configList
    }
  })
}

// 配置管理
export function getManagementConf ({ tableInfo, ...parameter }) {
  console.log(parameter)
  return request({
    url: api.getManagementConf,
    method: 'get',
    data: {
      ...parameter,
      item: tableInfo.filters.item,
      href: tableInfo.filters.href
    }
  })
}

// 配置管理日志
export function queryManageConfChange ({ parameter }) {
  console.log(parameter)
  return request({
    url: api.queryManageConfChange,
    method: 'get',
    parameter
  })
}

// 删除配置
export function deleteManagementConf ({ managementConfList, parameter }) {
  return request({
    url: api.deleteManagementConf,
    method: 'delete',
    data: {
      management_conf_list: managementConfList,
      ...parameter
    }
  })
}
