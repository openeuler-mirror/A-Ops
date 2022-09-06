import { getAlertCount } from '@/api/check';

const abnormalAlert = {
  state: {
    alertCount: 0,
    alertCountLoading: false
  },

  mutations: {
    SET_COUNT: (state, count) => {
      state.alertCount = count;
    },
    SET_COUNT_LOADING: (state, isLoading) => {
      state.alertCountLoading = isLoading;
    }
  },

  actions: {
    updateCount({commit}) {
      return new Promise((resolve, reject) => {
        commit('SET_COUNT_LOADING', true);
        getAlertCount().then(res => {
          commit('SET_COUNT', res.count);
          resolve();
        }).catch(err => {
          reject(err);
        }).finally(() => {
          commit('SET_COUNT_LOADING', false);
        });
      });
    }
  }
};

export default abnormalAlert;
