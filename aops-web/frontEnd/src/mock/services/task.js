import Mock from 'mockjs2'
import { builder, getBody } from '../util'
// 部署任务列表
const taskMockData = [
  {
    task_id: 'task1',
    task_name: '部署任务1',
    description: '这个描述很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长',
    playbook_name: 'playbook1'
  },
  {
    task_id: 'task2',
    task_name: '部署任务2',
    description: '这个描述很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长',
    playbook_name: 'playbook2'
  },
  {
    task_id: 'task3',
    task_name: '部署任务3',
    description: '这个描述很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长',
    playbook_name: 'playbook3'
  },
  {
    task_id: 'task4',
    task_name: '部署任务4',
    description: '这个描述很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长',
    playbook_name: 'playbook4'
  },
  {
    task_id: 'task5',
    task_name: '部署任务5',
    description: '这个描述很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长',
    playbook_name: 'playbook5'
  }
]
// playbook列表
const templateMockData = [
  {
    template_name: '',
    template_content: '{}',
    description: ''
  },
  {
    template_name: 'templateName1',
    template_content: '{}',
    description: '这是template1'
  },
  {
    template_name: 'templateName2',
    template_content: '{}',
    description: '这是template2'
  },
  {
    template_name: 'templateName3',
    template_content: '{}',
    description: '这是template4'
  },
  {
    template_name: 'templateName4',
    template_content: '{}',
    description: '这是template4'
  },
  {
    template_name: 'templateName5',
    template_content: '{}',
    description: '这是template5'
  },
  {
    template_name: 'templateName6',
    template_content: '{}',
    description: '这是template6'
  },
  {
    template_name: 'templateName7',
    template_content: '{}',
    description: '这是template7'
  },
  {
    template_name: 'templateName8',
    template_content: '{}',
    description: '这是template8'
  },
  {
    template_name: 'templateName9',
    template_content: '{}',
    description: '这是template9'
  },
  {
    template_name: 'templateName10',
    template_content: '{}',
    description: '这是template10'
  }
]

const getTask = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 5,
    'total_page': 1,
    'task_infos': taskMockData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const generateTask = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '执行成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const deleteTask = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const executeTask = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '执行成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const imporTemplate = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '执行成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const getTemplate = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 5,
    'total_page': 1,
    'template_infos': templateMockData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const deleteTemplate = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

Mock.mock(/\/task\/getTask/, 'get', getTask)
Mock.mock(/\/task\/generateTask/, 'post', generateTask)
Mock.mock(/\/task\/deleteTask/, 'delete', deleteTask)
Mock.mock(/\/task\/executeTask/, 'post', executeTask)
Mock.mock(/\/template\/imporTemplate/, 'post', imporTemplate)
Mock.mock(/\/template\/getTemplate/, 'get', getTemplate)
Mock.mock(/\/template\/deleteTemplate/, 'delete', deleteTemplate)
