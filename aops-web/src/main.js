/**
 * @file: 入口js文件。加载框架模块并挂在Vue对象到html
 */

// with polyfills
import 'core-js/stable';
import 'regenerator-runtime/runtime';

import Vue from 'vue';
import App from '@/vendor/ant-design-pro/App.vue';
import router from '@/vendor/ant-design-pro/router';
import store from './store/';
import i18n from '@/vendor/ant-design-pro/locales';
import {VueAxios} from '@/vendor/ant-design-pro/utils/request';
import ProLayout, {PageHeaderWrapper} from '@ant-design-vue/pro-layout';
import themePluginConfig from '@/vendor/ant-design-pro/config/themePluginConfig';

// mock
// WARNING: `mockjs` NOT SUPPORT `IE` PLEASE DO NOT USE IN `production` ENV.
import './mock';

import bootstrap from '@/vendor/ant-design-pro/core/bootstrap';
import '@/vendor/ant-design-pro/core/lazy_use'; // use lazy load components
import '@/vendor/ant-design-pro/permission'; // permission control
import '@/vendor/ant-design-pro/utils/filter'; // global filter
import '@/vendor/ant-design-pro/global.less'; // global style

Vue.config.productionTip = false;

// mount axios to `Vue.$http` and `this.$http`
Vue.use(VueAxios);
// use pro-layout components
Vue.component('pro-layout', ProLayout);
Vue.component('page-container', PageHeaderWrapper);
Vue.component('page-header-wrapper', PageHeaderWrapper);

window.umi_plugin_ant_themeVar = themePluginConfig.theme;

new Vue({
    router,
    store,
    i18n,
    // init localstorage, vuex, Logo message
    created: bootstrap,
    render: h => h(App)
}).$mount('#app');
