import { createStore } from 'vuex';
import createPersistedState from 'vuex-persistedstate';

import { SET_AUTHENTICATION, SET_USERNAME } from './store/storeconstants';

const createEmptyUser = () => ({
  nombre: '',
  appat: '',
  apmat: '',
  correo: '',
  telefono: '',
  area: '',
  departamento: '',
  rol: '',
  notif: false,
});

export default createStore({
  state: {
    auth: {
      isAuthenticated: false,
      username: '',
    },
    user: createEmptyUser(),
  },
  mutations: {
    setUser(state, userData) {
      state.user = userData;
    },
    [SET_AUTHENTICATION](state, status) {
      state.auth.isAuthenticated = status;
    },
    [SET_USERNAME](state, username) {
      state.auth.username = username;
    },
  },
  actions: {
    updateUser({ commit }, userData) {
      commit('setUser', userData);
    },
    setAuthentication({ commit }, status) {
      commit(SET_AUTHENTICATION, status);
    },
    setUsername({ commit }, username) {
      commit(SET_USERNAME, username);
    },
  },
  getters: {
    isAuthenticated: (state) => state.auth.isAuthenticated,
    user: (state) => state.user,
    username: (state) => state.auth.username,
  },
  plugins: [createPersistedState()],
});
