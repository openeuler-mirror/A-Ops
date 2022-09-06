import { getAlertCount, getAlertInfoResult } from '@/api/check';

const abnormalAlert = {
  state: {
    alertCount: 0,
    alertCountLoading: false,
    alertInfoResult: [],
    alertInfoResultLoading: false
  },

  mutations: {
    SET_COUNT: (state, count) => {
      state.alertCount = count;
    },
    SET_COUNT_LOADING: (state, isLoading) => {
      state.alertCountLoading = isLoading;
    },
    SET_ALERT_INFO_RESULT: (state, resultList) => {
      state.alertInfoResult = resultList;
    },
    SET_ALERT_INFO_RESULT_LOADING: (state, isLoading) => {
      state.alertInfoResultLoading = isLoading;
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
    },
    getAlertInfoResult({commit}) {
      return new Promise((resolve, reject) => {
        commit('SET_ALERT_INFO_RESULT_LOADING', true);
        getAlertInfoResult({})
        .then(res => {
          let tempArr = [];
          tempArr = res.results && res.results.map((item, idx) => {
            item.key = idx;
            item.order = idx;
            return item;
          });
          commit('SET_ALERT_INFO_RESULT', tempArr);
          resolve();
        }).catch(err => {
          reject(err);
        }).finally(() => {
          commit('SET_ALERT_INFO_RESULT_LOADING', false);
        });
      });
    }
  }
};

export default abnormalAlert;
