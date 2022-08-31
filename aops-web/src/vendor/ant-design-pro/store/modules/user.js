/**
 * @file vuex仓库，用户信息模块
 */

import storage from 'store';
import cookie from 'js-cookie';
import {login, logout} from '@/api/login';
import {ACCESS_TOKEN} from '@/vendor/ant-design-pro/store/mutation-types';

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
            state.token = token;
        },
        SET_NAME: (state, {name, welcome}) => {
            state.name = name;
            state.welcome = welcome;
        },
        SET_AVATAR: (state, avatar) => {
            state.avatar = avatar;
        },
        SET_ROLES: (state, roles) => {
            state.roles = roles;
        },
        SET_INFO: (state, info) => {
            state.info = info;
        }
    },

    actions: {
        // 登录
        Login({commit}, userInfo) {
            return new Promise((resolve, reject) => {
                login(userInfo)
                    .then(response => {
                        if (response.code !== 200) {
                            reject(response.msg);
                        }
                        const result = response;
                        storage.set(
                            ACCESS_TOKEN,
                            result.access_token,
                            7 * 24 * 60 * 60 * 1000
                        );
                        const in30Minutes = 1 / 48;
                        cookie.set('aops_token', result.access_token, {
                            expires: in30Minutes
                        });
                        cookie.set('user_name', userInfo.username, {
                            expires: in30Minutes
                        });
                        commit('SET_TOKEN', result.access_token);
                        commit('SET_NAME', {name: userInfo.username});
                        resolve();
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        },

        // 获取用户信息
        GetInfo({commit}) {
            return new Promise((resolve, reject) => {
                try {
                    // 暂时还没有userInfo的接口，跳过，使用空数据
                    const userInfo = {};
                    // role
                    const roleObj = {};

                    userInfo.role = roleObj;
                    const response = {result: userInfo};
                    const result = response.result;

                    commit('SET_ROLES', [1]);
                    commit('SET_INFO', result);

                    resolve(response);
                } catch (err) {
                    reject(err);
                }
            });
        },

        // 此action设置登录返回的用户名
        setUserName({commit}, userName) {
            commit('SET_NAME', {name: userName});
        },

        // 登出
        Logout({commit, state}) {
            commit('SET_TOKEN', '');
            commit('SET_ROLES', []);
            storage.remove(ACCESS_TOKEN);
            cookie.remove('aops_token');
            cookie.remove('user_name');

            return new Promise(resolve => {
                logout(state.token)
                    .then(() => {
                        resolve();
                    })
                    .catch(() => {
                        resolve();
                    })
                    .finally(() => {});
            });
        }
    }
};

export default user;
