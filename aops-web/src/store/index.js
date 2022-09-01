import Vue from 'vue'
import Vuex from 'vuex'

import app from '@/vendor/ant-design-pro/store/modules/app'
import user from '@/vendor/ant-design-pro/store/modules/user'

// default router permission control
import permission from '@/vendor/ant-design-pro/store/modules/permission'

// dynamic router permission control (Experimental)
// import permission from './modules/async-router'

import host from './modules/host'

import getters from '@/vendor/ant-design-pro/store/getters'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    user,
    permission,
    host
  },
  state: {},
  mutations: {},
  actions: {},
  getters
})
