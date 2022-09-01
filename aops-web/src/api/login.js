import request from '@/vendor/ant-design-pro/utils/request'

const userApi = {
  Login: '/manage/account/login',
  Logout: '/manage/logout',
  changePassword: '/manage/account/change',
  certificateKey: '/manage/account/certificate'
}

export function login (parameter) {
  return request({
    url: userApi.Login,
    method: 'post',
    data: {
      username: parameter.username,
      password: parameter.password
    }
  })
}

export function changePassword (parameter) {
  return request({
    url: userApi.changePassword,
    method: 'post',
    data: {
      password: parameter.password
    }
  })
}

export function certificateKey (parameter) {
  return request({
    url: userApi.certificateKey,
    method: 'post',
    data: {
      key: parameter.key
    }
  })
}

export function logout (parameter) {
  return request({
    url: userApi.Logout,
    method: 'post',
    data: parameter
  })
}
