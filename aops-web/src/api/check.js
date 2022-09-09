import request from '@/vendor/ant-design-pro/utils/request';
import { hostBasicInfo } from '@/api/assest';
import qs from 'qs';

const api = {
// API for the first phase of Aops.
// haven't been used, may be deleted later.
  // 获取异常检测结果
  getResult: '/check/result/get',
  // 导出异常检测规则
  getRule: '/check/rule/get',
  // 导⼊异常检测规则
  importRule: '/check/rule/import',
  // 删除异常检测规则 DELETE
  deleteRule: '/check/rule/delete',
  // 获取异常检测规则数量, abandoned
  getRuleCount: '/check/rule/count',
  // 获取检测结果统计
  getResultCount: '/check/result/count',
  // 获取工作流列表
  getWorkflowList: '/check/workflow/list',
  // 获取工作流详情信息 /check/workflow/{workflow_id}
  getWorkflowDatail: '/check/workflow',
  // 创建工作流
  createWorkFlow: 'check/workflow/create',
  // 修改工作流模型
  updateWorkflow: '/check/workflow/update',
  // 执行工作流
  excuteWorkflow: '/check/workflow/execute',
  // 暂停工作流
  stopWorkflow: '/check/workflow/stop',
  // 删除工作流
  deleteWorkflow: '/check/workflow',
  // 获取应用列表
  getAppList: '/check/app/list',
  // 获取app信息
  getWorkflowAppExtraInfo: '/check/app',
  // 新增应用列表
  createApp: '/check/app/create',
  // 获取模型列表
  getModuleList: '/check/algo/model/list',
  // 获取告警数量
  getAlertCount: '/check/result/total/count',
  // 获取告警信息
  getAlertInfoResult: '/check/result/domain/count',
  // 获取告警记录
  getAlertRecordResult: '/check/result/list',
  // 确认告警信息
  confirmTheAlert: '/check/result/confirm',
  // 下载报告
  downloadReport: '/check/report/download',
  // 异常详情
  getAlertDetail: '/check/result/host'
};

export default api;

const directionMap = {
  'ascend': 'asc',
  'descend': 'desc'
};

// 获取异常检测结果
export function getResult({timeRange, checkItems, hostList, value, sort, direction, page, perPage}) {
  return request({
    url: api.getResult,
    method: 'post',
    data: {
      ...(sort ? {sort: sort} : {}),
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
      setHostInfo(data.check_result, hostMap);
      return data;
    });
  });
};
// 导出异常检测规则
export function getRule({checkItems, sort, direction, page, perPage}) {
  return request({
    url: api.getRule,
    method: 'post',
    data: {
      ...(sort ? {sort: sort} : {}),
      // sort:⽬前check_item，为空表示不排序
      check_items: checkItems || [], // 异常检测项列表，为空表示所有
      direction: direction || 'asc', // 升序(asc)，降序(desc)，默认:asc
      page: page || 1, // 当前的⻚码
      per_page: perPage || 10 // 每⻚的数量，最⼤为50
    }
  });
};
// 获取全量规则
export function getRuleAll() {
  return request({
    url: api.getRule,
    method: 'post',
    data: {
      check_items: []
    }
  });
};
// 导⼊异常检测规则
export function importRule(checkItems) {
  return request({
    url: api.importRule,
    method: 'post',
    data: {check_items: checkItems}
  });
};
// 删除异常检测规则 DELETE
export function deleteRule(checkItems) {
  return request({
    url: api.deleteRule,
    method: 'delete',
    data: {check_items: checkItems}
  });
};
// 获取异常检测规则数量, abandened
export function getRuleCount(data) {
  return request({
    url: api.getRuleCount,
    method: 'post',
    data: data || {}
  });
};
// 获取检测结果统计
export function getResultCount({hostList, sort, direction, page, perPage}) {
  return request({
    url: api.getResultCount,
    method: 'post',
    data: {
      ...(sort ? {sort: sort} : {}),
      // sort:⽬前可选count，为空表示不排序
      host_list: hostList || [], // 主机列表，为空表示所有主机
      direction: direction || 'asc', // 升序(asc)，降序(desc)，默认:asc
      page: page || 1, // 当前的⻚码
      per_page: perPage || 10 // 每⻚的数量，最⼤为50
    }
  }).then(function (data) {
    return hostBasicInfo(data.results).then(function (hostMap) {
      setHostInfo(data.results, hostMap);
      return data;
    });
  });
};
// 获取检测结果统计
export function getResultCountTopTen() {
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
      setHostInfo(data.results, hostMap);
      return data;
    });
  });
};
// 获取主机信息
export function setHostInfo(dataList, hostMap) {
  dataList.forEach(function (item, index) {
    var host = hostMap[item.host_id];
    if (host) {
      item.hostName = host.host_name;
      item.ip = host.public_ip;
    };
  });
};

// 获取工作流列表
export function getWorkFlowList({tableInfo}) {
  const domain = (tableInfo.filters.domain && tableInfo.filters.domain[0]) ? tableInfo.filters.domain : undefined;
  const app = (tableInfo.filters.app_name && tableInfo.filters.app_name[0]) ? tableInfo.filters.app_name : undefined;
  const status = (tableInfo.filters.status && tableInfo.filters.status[0]) ? tableInfo.filters.status : undefined;
  const sort = tableInfo.sorter.order && tableInfo.sorter.field;
  const direction = directionMap[tableInfo.sorter.order];
  return request({
    url: api.getWorkflowList,
    method: 'post',
    data: {
      filter: {
        domain,
        app,
        status
      },
      sort,
      direction,
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  });
};
// 获取工作流详情信息
export function getWorkflowDatail(id) {
  return request({
    url: api.getWorkflowDatail,
    method: 'get',
    params: {workflow_id: id}
  });
};
// 创建工作流
export function createWorkFlow(data) {
  return request({
    url: api.createWorkFlow,
    method: 'post',
    data: {
      workflow_name: data.workflow_name,
      description: data.description,
      app_name: data.app_name,
      app_id: data.app_id,
      input: data.input
    }
  });
};
// 修改工作流
export function updateWorkflow(workflowDetail, workflowId) {
  return request({
    url: api.updateWorkflow,
    method: 'post',
    data: {
      detail: workflowDetail,
      workflow_id: workflowId
    }
  });
};
// 执行工作流
export function executeWorkflow({workflowId}) {
  return request({
    url: api.excuteWorkflow,
    method: 'post',
    data: {workflow_id: workflowId}
  });
};
// 暂停工作流
export function stopWorkflow({workflowId}) {
  return request({
    url: api.stopWorkflow,
    method: 'post',
    data: {workflow_id: workflowId}
  });
};
// 删除工作流
export function deleteWorkflow({workflowId}) {
  return request({
    url: api.deleteWorkflow,
    method: 'delete',
    data: {workflow_id: workflowId}
  });
};
// 获取应用列表
export function getAppList({page, perPage}) {
  return request({
    url: api.getAppList,
    method: 'get',
    params: {
      page,
      per_page: perPage
    }
  });
};
// 获取app信息
export function getWorkflowAppExtraInfo(id) {
  return request({
    url: api.getWorkflowAppExtraInfo,
    method: 'get',
    params: {app_id: id}
  });
};
// 新增应用（暂未开发）
export function createApp(appInfo) {
  return request({
    url: api.createApp,
    method: 'post',
    data: appInfo
  });
};

// 获取模型列表
export function moduleList({tableInfo, ...parameter}) {
  return request({
    url: api.getModuleList,
    method: 'post',
    data: {
      ...parameter,
      filter: {
        tag: tableInfo.filters.tag || undefined,
        field: tableInfo.filters.field,
        model_name: tableInfo.filters.model_name || undefined,
        algo_name: tableInfo.filters.algo_name // 该接口未实现，暂无参数
      },
      sort: tableInfo.sorter.order && tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  });
};

export function getAlertCount() {
  return request({
    url: api.getAlertCount,
    method: 'get'
  });
};
export function getAlertInfoResult(parameter) {
  return request({
    url: api.getAlertInfoResult,
    method: 'get',
    params: {
      sort: 'count',
      direction: parameter.direction || 'desc',
      page: parameter.page || 1,
      per_page: parameter.per_page || 10
    }
  });
};
export function getAlertRecordResult(parameter) {
  return request({
    url: api.getAlertRecordResult,
    method: 'get',
    params: {
      page: parameter.page || 1,
      per_page: parameter.per_page || 10,
      domain: parameter.domain || [],
      sort: 'time',
      direction: directionMap[parameter.direction] || 'asc'
    },
    paramsSerializer: params => {
      return qs.stringify(params, {indices: false});
    }
  });
};
export function confirmTheAlert(parameter) {
  return request({
    url: api.confirmTheAlert,
    method: 'post',
    data: {
      alert_id: parameter.alert_id
    }
  });
};
export function downloadReport(parameter) {
  return request({
    url: api.downloadReport,
    method: 'get',
    params: {
      alert_id: parameter.alert_id
    }
  });
};
export function getAlertDetail(parameter) {
  return request({
    url: api.getAlertDetail,
    method: 'get',
    params: {
      alert_id: parameter.alert_id
    }
  });
};
