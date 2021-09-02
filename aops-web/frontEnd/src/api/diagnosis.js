import request from '@/utils/request'

const api = {
  // 获取故障诊断报告列表
  reportlist: '/diag/report/getreportlist',
  // 获取故障诊断报告
  getdiagreport: '/diag/report/getdiagreport',
  // 删除故障诊断报告
  deletediagreport: '/diag/report/deletediagreport',
  // 获取故障诊断进度
  getdiagprogress: '/diag/getdiagprogress',
  // 导出故障树
  getdiagtree: '/diag/tree/getdiagtree',
  // 删除故障树
  deletediagtree: '/diag/tree/deletediagtree',
  // 执行故障诊断
  execute_diag: '/diag/execute_diag',
  // 导⼊故障树
  import_diagtree: '/diag/tree/importdiagtree',
  // 导入异常检测规则
  importcheckrule: '/check/rule/importcheckrule',
  // 获取异常检测的结果
  getcheckresult: '/check/result/getcheckresult'
}

export default api
// 获取故障诊断报告列表
export function getReportList ({ tableInfo, ...parameter }) {
  return request({
    url: api.reportlist,
    method: 'get',
    data: {
      ...parameter,
      time_range: tableInfo.filters.time_range,
      host_list: tableInfo.filters.host_list,
      task_id: tableInfo.filters.task_id,
      sort: tableInfo.sorter.field,
      direction: tableInfo.sorter.order,
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize,
      access_token: ''
    }
  })
}
// 获取故障诊断报告
export function getdiagreport ({ reportList, ...parameter }) {
  return request({
    url: api.getdiagreport,
    method: 'get',
    data: {
      ...parameter,
      report_list: reportList,
      access_token: ''
    }
  })
}
export function getDiagTree ({ tableInfo, ...parameter }) {
  return request({
    url: api.getdiagtree,
    method: 'get',
    data: {
      ...parameter,
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize,
      access_token: ''
    }
  })
}
export function getDiagProgress ({ taskList, ...parameter }) {
  return request({
    url: api.getdiagprogress,
    method: 'get',
    data: {
      ...parameter,
      task_list: taskList,
      access_token: ''
    }
  })
}
export function delDiagReport ({ reportList, ...parameter }) {
  return request({
    url: api.deletediagreport,
    method: 'post',
    data: {
      ...parameter,
      report_list: reportList,
      access_token: ''
    }
  })
}
export function delDiagTree ({ treeList, ...parameter }) {
  return request({
    url: api.deletediagtree,
    method: 'post',
    data: {
      ...parameter,
      tree_list: treeList,
      access_token: ''
    }
  })
}
export function executeDiag ({ data, ...parameter }) {
  return request({
    url: api.execute_diag,
    method: 'post',
    data: {
      ...parameter,
      host_list: data.host_list,
      time_range: data.time_range,
      tree_list: data.tree_list,
      access_token: ''
    }
  })
}
// 导⼊故障树
export function importDiagTree (data) {
  return request({
    url: api.import_diagtree,
    method: 'post',
    data: data
  })
}
// 获取故障诊断报告
export function importCheckRule (checkItems) {
  return request({
    url: api.importcheckrule,
    method: 'post',
    data: {
      check_items: checkItems,
      access_token: ''
    }
  })
}
// 获取异常检测的结果
export function getcheckresult ({ tableInfo, ...parameter }) {
  return request({
    url: api.getcheckresult,
    method: 'get',
    data: {
      ...parameter,
      time_range: tableInfo.filters.time_range,
      check_items: tableInfo.filters.check_items,
      host_list: tableInfo.filters.host_list,
      sort: tableInfo.sorter.field,
      direction: tableInfo.sorter.order,
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize,
      access_token: ''
    }
  })
}
