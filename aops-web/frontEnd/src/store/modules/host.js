const host = {
  state: {
    hostInfo: {}
  },

  mutations: {
    SET_HOSTINFO: (state, hostInfo) => {
      state.hostInfo = hostInfo
    },
    RESET_HOSTINFO: (state) => {
      state.hostInfo = {}
    }
  },

  actions: {
    setHostInfo ({ commit }, hostInfo) {
      commit('SET_HOSTINFO', hostInfo)
    },
    resetHostInfo ({ commit }) {
      commit('RESET_HOSTINFO')
    }
  }
}

export default host
