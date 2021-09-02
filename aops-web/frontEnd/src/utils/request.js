import axios from 'axios'
import store from '@/store'
// import storage from 'store'
import cookie from 'js-cookie'
import notification from 'ant-design-vue/es/notification'
import { VueAxios } from './axios'
// import { ACCESS_TOKEN } from '@/store/mutation-types'

// 创建 axios 实例
const request = axios.create({
  // API 请求的默认前缀
  baseURL: process.env.VUE_APP_API_BASE_URL,
  timeout: 6000 // 请求超时时间
})

// 异常拦截处理器
const errorHandler = (error) => {
  console.log('errHandler: ', error)
  if (error.response) {
    const data = error.response.data
    // 从 localstorage 获取 token
    const token = cookie.get('aops_token')
    if (error.response.status === 403) {
      notification.error({
        message: 'Forbidden',
        description: data.message
      })
    }
    if (error.response.status === 401 && !(data.result && data.result.isLogin)) {
      notification.error({
        message: 'Unauthorized',
        description: 'Authorization verification failed'
      })
      if (token) {
        store.dispatch('Logout').then(() => {
          setTimeout(() => {
            window.location.reload()
          }, 1500)
        })
      }
    }
  }
  return Promise.reject(error)
}

// request interceptor
request.interceptors.request.use(config => {
  // const token = storage.get(ACCESS_TOKEN)
  const token = cookie.get('aops_token')
  // 如果 token 存在
  // 让每个请求携带自定义 token 请根据实际情况自行修改
  if (token) {
    config.headers['Access-Token'] = token
  }
  return config
}, errorHandler)

// response interceptor
request.interceptors.response.use((response) => {
  // 这对业务域相关接口返回体做特殊处理，后续需要统一
  const config = response.config
  let code
  if (config.url.match('^/domain/')) {
    code = response.status
  } else {
    code = response.data.code
  }

  // 特殊处理结束
  if (code !== 200) {
    switch (code) {
      case 1201:
        notification.error({
          message: '用户校验失败',
          description: response.data.msg
        })
        store.dispatch('Logout').then(() => {
          setTimeout(() => {
            window.location.reload()
          }, 1000)
        })
        break
      default:
        const err = new Error(response.data.msg)
        err.data = response.data
        err.response = response
        throw err
    }
  }
  return response.data
}, errorHandler)

const installer = {
  vm: {},
  install (Vue) {
    Vue.use(VueAxios, request)
  }
}

export default request

export {
  installer as VueAxios,
  request as axios
}
