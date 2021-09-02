import storage from 'store'
import cookie from 'js-cookie'
import { login, /* getInfo, */ logout } from '@/api/login'
import { ACCESS_TOKEN } from '@/store/mutation-types'
// import { welcome } from '@/utils/util'

const user = {
  state: {
    token: '',
    name: '',
    welcome: '',
    avatar: '',
    roles: [],
    info: {}
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_NAME: (state, { name, welcome }) => {
      state.name = name
      state.welcome = welcome
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar
    },
    SET_ROLES: (state, roles) => {
      state.roles = roles
    },
    SET_INFO: (state, info) => {
      state.info = info
    }
  },

  actions: {
    // 登录
    Login ({ commit }, userInfo) {
      return new Promise((resolve, reject) => {
        login(userInfo).then(response => {
          if (response.code !== 200) {
            reject(response.msg)
          }
          const result = response
          storage.set(ACCESS_TOKEN, result.access_token, 7 * 24 * 60 * 60 * 1000)
          const in15Minutes = 1 / 96
          cookie.set('aops_token', result.access_token, { expires: in15Minutes })
          cookie.set('user_name', userInfo.username, { expires: in15Minutes })
          commit('SET_TOKEN', result.access_token)
          commit('SET_NAME', { name: userInfo.username })
          resolve()
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 获取用户信息
    GetInfo ({ commit }) {
      return new Promise((resolve, reject) => {
        // 暂时还没有userInfo的接口，跳过，使用空数据
        const userInfo = {}
        // role
        const roleObj = {}

        userInfo.role = roleObj
        const response = { result: userInfo }
        const result = response.result

        commit('SET_ROLES', [1])
        commit('SET_INFO', result)

        resolve(response)

        /* 启用获取userInfo后，删除上方代码
        getInfo().then(response => {
          const result = response.result

          if (result.role && result.role.permissions.length > 0) {
            const role = result.role
            role.permissions = result.role.permissions
            role.permissions.map(per => {
              if (per.actionEntitySet != null && per.actionEntitySet.length > 0) {
                const action = per.actionEntitySet.map(action => { return action.action })
                per.actionList = action
              }
            })
            role.permissionList = role.permissions.map(permission => { return permission.permissionId })
            commit('SET_ROLES', [1])
            commit('SET_INFO', result)
          } else {
            reject(new Error('getInfo: roles must be a non-null array !'))
          }

          commit('SET_NAME', { name: result.name, welcome: welcome() })
          commit('SET_AVATAR', result.avatar)
          resolve(response)
        }).catch(error => {
          reject(error)
        })
        */
      })
    },

    // 应为getInfo被跳过了，通过本action设置登录返回的用户名
    setUserName ({ commit }, userName) {
      console.log()
      commit('SET_NAME', { name: userName })
    },

    // 登出
    Logout ({ commit, state }) {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      storage.remove(ACCESS_TOKEN)
      cookie.remove('aops_token')
      cookie.remove('user_name')

      return new Promise((resolve) => {
        logout(state.token).then(() => {
          resolve()
        }).catch(() => {
          resolve()
        }).finally(() => {
        })
      })
    }
  }
}

export default user
