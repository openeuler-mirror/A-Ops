import request from '@/vendor/ant-design-pro/utils/request';

const api = {
  // 获取诊断任务列表
  getTaskList: '/diag/task/get',
  // 获取故障诊断的进度
  getProgress: '/diag/progress/get',
  // 获取故障诊断报告列表
  // reportlist: '/diag/report/getreportlist',
  reportlist: '/diag/report/get_list',
  // 获取故障诊断报告
  // getdiagreport: '/diag/report/getdiagreport',
  getdiagreport: '/diag/report/get',
  // 删除故障诊断报告
  deletediagreport: '/diag/report/delete',
  // 获取故障诊断进度
  // getdiagprogress: '/diag/getdiagprogress',
  getdiagprogress: '/diag/progress/get',
  // 导出故障树
  // getdiagtree: '/diag/tree/getdiagtree',
  getdiagtree: '/diag/tree/get',
  // 删除故障树
  deletediagtree: '/diag/tree/delete',
  // 执行故障诊断
  execute_diag: '/diag/execute',
  // 导⼊故障树
  import_diagtree: '/diag/tree/import',
  // 导入异常检测规则
  importcheckrule: '/check/rule/importcheckrule',
  // 获取异常检测的结果
  getcheckresult: '/check/result/getcheckresult'
};

export default api;
// 获取诊断任务列表
export function getTaskList(data) {
  return request({
    url: api.getTaskList,
    method: 'post',
    data: {
      status: data.status,
      sort: data.sort,
      direction: data.direction,
      page: data.pagination.current,
      per_page: data.pagination.pageSize,
      time_range: data.time_range
    }
  });
};
// 获取诊断任务进度
export function getProgress(taskList) {
  return request({
    url: api.getProgress,
    method: 'post',
    data: {
      task_list: taskList
    }
  });
};
// 获取故障诊断报告列表
export function getReportList(parameter) {
  return request({
    url: api.reportlist,
    method: 'post',
    data: {
      task_id: parameter.taskId,
      page: parameter.pagination.current,
      per_page: parameter.pagination.pageSize
    }
  });
};
// 获取故障诊断报告
export function getdiagreport(reportList) {
  return request({
    url: api.getdiagreport,
    method: 'post',
    data: {
      report_list: reportList
    }
  });
};
export function getDiagTree({treeList}) {
  return request({
    url: api.getdiagtree,
    method: 'post',
    data: {
      tree_list: treeList
    }
    // data: {
    //   ...parameter,
    //   page: tableInfo.pagination.current,
    //   per_page: tableInfo.pagination.pageSize,
    //   access_token: ''
    // }
  });
};
export function delDiagReport(reportList) {
  return request({
    url: api.deletediagreport,
    method: 'delete',
    data: {
      report_list: reportList
    }
  });
};
export function delDiagTree({treeList}) {
  return request({
    url: api.deletediagtree,
    method: 'delete',
    data: {
      tree_list: treeList
    }
  });
};
export function executeDiag(data) {
  return request({
    url: api.execute_diag,
    method: 'post',
    data: {
      host_list: data.host_list,
      time_range: data.time_range,
      tree_list: data.tree_list,
      interval: data.interval
    }
  });
};
// 导⼊故障树
export function importDiagTree(data) {
  return request({
    url: api.import_diagtree,
    method: 'post',
    data: {
      trees: [data]
    }
  });
};
// 获取故障诊断报告
export function importCheckRule(checkItems) {
  return request({
    url: api.importcheckrule,
    method: 'post',
    data: {
      check_items: checkItems,
      access_token: ''
    }
  });
};
// 获取异常检测的结果
export function getcheckresult({tableInfo, ...parameter}) {
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
  });
};
