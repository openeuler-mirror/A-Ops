import Vue from 'vue';
import Vuex from 'vuex';

import app from '@/vendor/ant-design-pro/store/modules/app';
import user from '@/vendor/ant-design-pro/store/modules/user';

// default router permission control
import permission from '@/vendor/ant-design-pro/store/modules/permission';

// dynamic router permission control (Experimental)
// import permission from './modules/async-router'

import host from './modules/host';
// abnormal alert count
import abnormalAlert from './modules/abnormalAlert';

import getters from '@/vendor/ant-design-pro/store/getters';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    app,
    user,
    permission,
    host,
    abnormalAlert
  },
  state: {},
  mutations: {},
  actions: {},
  getters
});
