import Vue from 'vue'
import Vuex from 'vuex'
import sliceSettingsStore from './sliceSettingsStore'
Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    sliceSettingsStore,
  }
});
