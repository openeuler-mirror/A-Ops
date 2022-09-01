import request from '@/vendor/ant-design-pro/utils/request'

const api = {
  addManagementConf: '/management/addManagementConf', // 新增业务域配置
  getManagementConf: '/management/getManagementConf', // 读取业务域配置信息
  queryManageConfChange: '/management/queryManageConfChange', // 读取业务域配置日志信息
  deleteManagementConf: '/management/deleteManagementConf' // 删除业务域配置
}

export default api

// 新增配置
export function addManagementConf (data) {
  return request({
    url: api.addManagementConf,
    method: 'post',
    data: data
  })
}

// 配置管理
export function getManagementConf (data) {
  return request({
    url: api.getManagementConf,
    method: 'post',
    data: data
  })
}

// 配置管理日志
export function queryManageConfChange (data) {
  return request({
    url: api.queryManageConfChange,
    method: 'post',
    data: data
  })
}

// 删除配置
export function deleteManagementConf (parameter) {
  return request({
    url: api.deleteManagementConf,
    method: 'delete',
    data: {
      domainName: parameter.domainName,
      confFiles: parameter.confFiles
    }
  })
}
