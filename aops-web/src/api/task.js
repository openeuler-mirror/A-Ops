import request from '@/vendor/ant-design-pro/utils/request'

const api = {
  // 获取部署任务列表
  tasklist: '/manage/task/get',
  // 生成部署任务列表
  generateTask: '/manage/task/generate',
  // 删除部署任务
  deleteTask: '/manage/task/delete',
  // 执行部署任务
  executeTask: '/manage/task/execute',
  // 导入playbook模板
  imporTemplate: '/manage/template/import',
  // 获取playbook模板
  templateList: '/manage/template/get',
  // 删除playbook模板
  deleteTemplate: '/manage/template/delete'
}

export default api

const directionMap = {
  'ascend': 'asc',
  'descend': 'desc'
}

// 获取部署任务列表
export function getTaskList ({ tableInfo, ...parameter }) {
  return request({
    url: api.tasklist,
    method: 'post',
    data: {
      ...parameter,
      task_list: tableInfo.filters.task_list || [],
      sort: tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  })
}
// 生成部署任务
export function generateTask (data) {
  return request({
    url: api.generateTask,
    method: 'post',
    data: data
  })
}
// 删除部署任务
export function deleteTask ({ taskList, ...parameter }) {
  return request({
    url: api.deleteTask,
    method: 'delete',
    data: {
      task_list: taskList,
      ...parameter
    }
  })
}
// 执行部署任务
export function executeTask ({ taskList, ...parameter }) {
  return request({
    url: api.executeTask,
    method: 'post',
    data: {
      task_list: taskList,
      ...parameter
    }
  })
}
// 生成playbook模板
export function imporTemplate (data) {
  return request({
    url: api.imporTemplate,
    method: 'post',
    data: data
  })
}
// 获取playbook模板列表
export function getTemplateList ({ tableInfo, ...parameter }) {
  return request({
    url: api.templateList,
    method: 'post',
    data: {
      ...parameter,
      template_list: []
      // sort: tableInfo.sorter.field,
      // direction: directionMap[tableInfo.sorter.order],
      // page: tableInfo.pagination.current,
      // per_page: tableInfo.pagination.pageSize
    }
  })
}
// 删除playbook模板
export function deleteTemplate ({ templateList, ...parameter }) {
  return request({
    url: api.deleteTemplate,
    method: 'delete',
    data: {
      template_list: templateList,
      ...parameter
    }
  })
}
