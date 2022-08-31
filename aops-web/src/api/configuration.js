import request from '@/vendor/ant-design-pro/utils/request'
import qs from 'qs'

const api = {
  domainList: '/domain/queryDomain', // 获取域信息列表
  createDomain: '/domain/createDomain', // 新建业务域
  deleteDomain: '/domain/deleteDomain', // 删除业务域
  domainHostList: '/host/getHost', // 获取业务域主机列表
  deleteHost: '/host/deleteHost', // 删除业务域主机
  addHost: '/host/addHost', // 添加业务域主机
  domainStatus: '/confs/getDomainStatus', // 获取业务域主机同步状态
  syncConf: '/confs/syncConf', // 获取业务域主机同步状态
  queryRealConfs: '/confs/queryRealConfs', // 获取主机当前配置
  queryExpectedConfs: '/confs/queryExpectedConfs' // 获取主机配置日志
}

export default api

// 主机管理
export function domainList (parameter) {
  return request({
    url: api.domainList,
    method: 'post',
    parameter
  })
}

// 业务域主机列表
export function domainHostList (domainName, ...parameter) {
  return request({
    url: api.domainHostList,
    method: 'post',
    data: {
      ...parameter,
      domainName: domainName
    }
  })
}
export function addHost (domainName, hostInfos, ...parameter) {
  return request({
    url: api.addHost,
    method: 'post',
    data: {
      ...parameter,
      domainName: domainName,
      hostInfos: hostInfos
    }
  })
}
// 获取业务域主机同步状态
export function domainStatus ({ domainName, ...parameter }) {
  return request({
    url: api.domainStatus,
    method: 'post',
    data: {
      domainName
    }
  })
}
// 新建业务域
// domainInfo = [
//   {
//     "domainName": "domainName",
//     "priority": 0
//   }
// ]
export function createDomain (domainInfo, ...parameter) {
  return request({
    url: api.createDomain,
    method: 'post',
    data: domainInfo
  })
}
// 删除业务域
export function deleteDomain (parameter) {
  const domainName = parameter.domainNameArray
  return request({
    url: api.deleteDomain,
    method: 'delete',
    params: {
      domainName
    },
    paramsSerializer: params => {
      return qs.stringify(params, { indices: false })
    }
  })
}
// 删除业务域主机
export function deleteHost ({ domainName, hostInfos, ...parameter }) {
  return request({
    url: api.deleteHost,
    method: 'delete',
    data: {
      domainName: domainName,
      hostInfos: hostInfos
    }
  })
}
// 同步
export function syncConf (domainName, hostIds, ...parameter) {
  return request({
    url: api.syncConf,
    method: 'post',
    data: {
      ...parameter,
      domainName: domainName,
      hostIds: hostIds
    }
  })
}
// 获取主机当前配置
export function queryRealConfs ({ domainName, hostIds, ...parameter }) {
  return request({
    url: api.queryRealConfs,
    method: 'post',
    data: {
      domainName: domainName,
      hostIds: hostIds
    }
  })
}
// 获取主机配置日志
export function queryExpectedConfs (domainName, hostIds, ...parameter) {
  return request({
    url: api.queryExpectedConfs,
    method: 'get',
    data: {
      ...parameter,
      domainName: domainName,
      hostIds: hostIds
    }
  })
}
