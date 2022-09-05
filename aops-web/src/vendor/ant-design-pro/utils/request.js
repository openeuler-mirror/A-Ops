/**
 * @file: 将axios对象封装为request对象供全局调用。同时配置拦截器功能
 */

import axios from 'axios';
import store from '@/store';
import cookie from 'js-cookie';
import notification from 'ant-design-vue/es/notification';
import {VueAxios} from './axios';

const errorMsgs = {
    noResponse: 'request failed, no response'
};

// 创建 axios 实例
const request = axios.create({
    // API 请求的默认前缀
    baseURL: process.env.VUE_APP_API_BASE_URL,
    timeout: 24000 // 请求超时时间
});

// 异常拦截处理器
const errorHandler = error => {
    if (error.response) {
        const data = error.response.data;
        // 从 localstorage 获取 token
        const token = cookie.get('aops_token');
        if (error.response.status === 403) {
            notification.error({
                message: 'Forbidden',
                description: data.message
            });
        }
        if (
            error.response.status === 401
            && !(data.result && data.result.isLogin)
        ) {
            notification.error({
                message: 'Unauthorized',
                description: 'Authorization verification failed'
            });
            if (token) {
                store.dispatch('Logout').then(() => {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                });
            }
        }
    } else {
        // 请求失败没有返回体时（如请求超时），添加默认错误信息
        error.response = {
            data: {
                msg: errorMsgs.noResponse
            }
        };
    }
    return Promise.reject(error);
};

// request interceptor
request.interceptors.request.use(config => {
    const token = cookie.get('aops_token');
    // 如果 token 存在
    // 让每个请求携带自定义 token 请根据实际情况自行修改
    if (token) {
        config.headers['Access-Token'] = token;

        // reset cookie expired time
        const in30Minutes = 1 / 48;
        cookie.set('aops_token', token, {expires: in30Minutes});
        const userName = cookie.get('user_name');
        userName && cookie.set('user_name', userName, {expires: in30Minutes});
    }
    return config;
}, errorHandler);

// response interceptor
request.interceptors.response.use(response => {
    // 这对业务域相关接口返回体做特殊处理，后续需要统一
    const code = response.data.code || response.status;
  // 不处理所有2xx的状态码
  if (!code.toString().match(/^2[0-9]{2,2}$/)) {
        let err = null;
        switch (code) {
            case 1201:
                notification.error({
                    message: '用户校验失败',
                    description: response.data.msg
                });
                store.dispatch('Logout').then(() => {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                });
                break;
            default:
                err = new Error(response.data.msg);
                err.data = response.data;
                err.response = response;
                throw err;
        }
    }
    if (response.headers['content-type'] === 'application/octet-stream') {
        const fileName = response.headers['content-disposition']
            .split(';')[1]
            .split('=')[1]
            .replace(/^'/, '')
            .replace(/'$/, '');
        const downloadResponse = {
            data: response.data,
            fileName
        };
        return downloadResponse;
    }
    return response.data;
}, errorHandler);

const installer = {
    vm: {},
    install(Vue) {
        Vue.use(VueAxios, request);
    }
};

export default request;

export {installer as VueAxios, request as axios};
