import Mock from 'mockjs2'
import { builder, getBody } from '../util'
// 故障诊断列表
const faultDiagnosisMockData = [
  {
    task_id: 'task1',
    tree_name: '故障树1',
    time: '20210817 11:20:08-20210817 12:20:08',
    report_id: 'aa',
    progress: 0
  },
  {
    task_id: 'task2',
    tree_name: '故障树2',
    time: '20210817 11:20:08-20210817 12:20:08',
    report_id: 'bb',
    progress: 0
  },
  {
    task_id: 'task3',
    tree_name: '故障树3',
    time: '20210817 11:20:08-20210817 12:20:08',
    report_id: 'cc',
    progress: 0
  },
  {
    task_id: 'task4',
    tree_name: '故障树4',
    time: '20210817 11:20:08-20210817 12:20:08',
    report_id: 'dd',
    progress: 0
  },
  {
    task_id: 'task5',
    tree_name: '故障树5',
    time: '20210817 11:20:08-20210817 12:20:08',
    report_id: 'ee',
    progress: 0
  }
]
// 故障树
const diagTreeData = [
  {
    tree_name: '',
    avatar: '',
    content: ''
  },
  {
    tree_name: '故障树1',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情1'
  },
  {
    tree_name: '故障树2',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树3',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树4',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树5',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树6',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树7',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树8',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树9',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树10',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树11',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树12',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树13',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  },
  {
    tree_name: '故障树14',
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: '这里可以放一两项简单描述，仅可点击查看详情2'
  }
]
// 故障诊断的进度
const diagProgressData = [
    {
      task_id: 'task1',
      progress: 20
    },
    {
      task_id: 'task2',
      progress: 55
    },
    {
      task_id: 'task3',
      progress: 40
    },
    {
      task_id: 'task4',
      progress: 60
    },
    {
      task_id: 'task5',
      progress: 85
    }
]
const checkResultData = {
  'code': '',
  'msg': '',
  'total_count': 1,
  'total_page': 1,
  'check_result': [
    {
      'host_id': 'host1',
      'data_list': ['data1', 'data2'],
      'start': 11,
      'end': 25,
      'check_item': '',
      'check_condition': '',
      'check_value': '10'
    }
  ]
}
const getFaultDiagnosis = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 5,
    'total_page': 1,
    'host_infos': faultDiagnosisMockData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const getDiagTree = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'total_count': 5,
    'total_page': 1,
    'diagTree_infos': diagTreeData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const getDiagProgress = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'diagProgress_infos': diagProgressData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const delDiagReport = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const delDiagTree = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '删除成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const executeDiag = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '执行成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

const importDiagTree = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)
  diagTreeData.splice(1, 0, {
    tree_name: body.tree_name,
    avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
    content: body.description
  })
  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success')
  }, '执行成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const importCheckRule = (options) => {
  const body = getBody(options)
  console.log('----->mock: body', body)

  return builder({
    'msg': Mock.mock('success')
  }, '添加成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}
const getcheckresult = (options) => {
  const body = getBody(options)
  console.log('mock: body', body)

  if (body.uid !== '123') {
    return builder({ 'msg': '用户错误' }, '用户错误', 410)
  }

  return builder({
    'msg': Mock.mock('success'),
    'checkResultData': checkResultData
  }, '查询成功', 200, { 'Custom-Header': Mock.mock('@guid') })
}

Mock.mock(/\/diag\/report\/getreportlist/, 'get', getFaultDiagnosis)
Mock.mock(/\/diag\/tree\/getdiagtree/, 'get', getDiagTree)
Mock.mock(/\/diag\/getdiagprogress/, 'get', getDiagProgress)
Mock.mock(/\/diag\/report\/deletediagreport/, 'post', delDiagReport)
Mock.mock(/\/diag\/tree\/deletediagtree/, 'post', delDiagTree)
Mock.mock(/\/diag\/execute_diag/, 'post', executeDiag)
Mock.mock(/\/diag\/tree\/importdiagtree/, 'post', importDiagTree)
Mock.mock(/\/check\/rule\/importcheckrule/, 'post', importCheckRule)
Mock.mock(/\/check\/result\/getcheckresult/, 'get', getcheckresult)
