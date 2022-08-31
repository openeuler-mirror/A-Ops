import request from '@/vendor/ant-design-pro/utils/request'

const api = {
  // 获取架构感知列表
  getTopo: '/gala-spider/api/v1/get_entities'
}

export default api

export function getTopoData (parameter) {
  return request({
    url: api.getTopo,
    method: 'get',
    data: parameter
  })
}
