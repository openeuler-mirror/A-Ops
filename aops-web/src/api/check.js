import request from '@/appCore/utils/request'
import { hostBasicInfo } from '@/api/assest'

const api = {
  // 获取异常检测结果
  getResult: '/check/result/get',
  // 导出异常检测规则
  getRule: '/check/rule/get',
  // 导⼊异常检测规则
  importRule: '/check/rule/import',
  // 删除异常检测规则 DELETE
  deleteRule: '/check/rule/delete',
  // 获取异常检测规则数量
  getRuleCount: '/check/rule/count',
  // 获取检测结果统计
  getResultCount: '/check/result/count'
}

export default api

// 获取异常检测结果
export function getResult ({ timeRange, checkItems, hostList, value, sort, direction, page, perPage }) {
  return request({
    url: api.getResult,
    method: 'post',
    data: {
      ...(sort ? { sort: sort } : {}),
      // sort:⽬前可选start或end或check_item，为空表示不排序
      time_range: timeRange || [], // 检测的时间范围，为空表示所有
      check_items: checkItems || [], // 异常检测项列表，为空表示所有
      host_list: hostList || [], // 主机列表，为空表示所有主机
      value: value || 'Abnormal', // 此API默认获取异常结果。
      direction: direction || 'asc', // 升序(asc)，降序(desc)，默认:asc
      page: page || 1, // 当前的⻚码
      per_page: perPage || 10 // 每⻚的数量，最⼤为50
    }
  }).then(function (data) {
    return hostBasicInfo(data.check_result).then(function (hostMap) {
      setHostInfo(data.check_result, hostMap)
      return data
    })
  })
}
// 导出异常检测规则
export function getRule ({ checkItems, sort, direction, page, perPage }) {
  return request({
    url: api.getRule,
    method: 'post',
    data: {
      ...(sort ? { sort: sort } : {}),
      // sort:⽬前check_item，为空表示不排序
      check_items: checkItems || [], // 异常检测项列表，为空表示所有
      direction: direction || 'asc', // 升序(asc)，降序(desc)，默认:asc
      page: page || 1, // 当前的⻚码
      per_page: perPage || 10 // 每⻚的数量，最⼤为50
    }
  })
}
// 获取全量规则
export function getRuleAll () {
  return request({
    url: api.getRule,
    method: 'post',
    data: {
      check_items: []
    }
  })
}
// 导⼊异常检测规则
export function importRule (checkItems) {
  return request({
    url: api.importRule,
    method: 'post',
    data: { check_items: checkItems }
  })
}
// 删除异常检测规则 DELETE
export function deleteRule (checkItems) {
  return request({
    url: api.deleteRule,
    method: 'delete',
    data: { check_items: checkItems }
  })
}
// 获取异常检测规则数量
export function getRuleCount (data) {
  return request({
    url: api.getRuleCount,
    method: 'post',
    data: data || {}
  })
}
// 获取检测结果统计
export function getResultCount ({ hostList, sort, direction, page, perPage }) {
  return request({
    url: api.getResultCount,
    method: 'post',
    data: {
      ...(sort ? { sort: sort } : {}),
      // sort:⽬前可选count，为空表示不排序
      host_list: hostList || [], // 主机列表，为空表示所有主机
      direction: direction || 'asc', // 升序(asc)，降序(desc)，默认:asc
      page: page || 1, // 当前的⻚码
      per_page: perPage || 10 // 每⻚的数量，最⼤为50
    }
  }).then(function (data) {
    return hostBasicInfo(data.results).then(function (hostMap) {
      setHostInfo(data.results, hostMap)
      return data
    })
  })
}
// 获取检测结果统计
export function getResultCountTopTen () {
  return request({
    url: api.getResultCount,
    method: 'post',
    data: {
      host_list: [],
      sort: 'count',
      direction: 'desc',
      page: 1,
      per_page: 10
    }
  }).then(function (data) {
    return hostBasicInfo(data.results).then(function (hostMap) {
      setHostInfo(data.results, hostMap)
      return data
    })
  })
}
// 获取主机信息
export function setHostInfo (dataList, hostMap) {
  dataList.forEach(function (item, index) {
    var host = hostMap[item.host_id]
    if (host) {
      item.hostName = host.host_name
      item.ip = host.public_ip
    }
  })
}
