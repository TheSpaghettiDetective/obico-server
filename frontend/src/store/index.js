import Vue from 'vue'
import Vuex from 'vuex'
import sliceSettingsStore from './sliceSettingsStore'
import printPresetsStore from './printPresetsStore'
Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    sliceSettingsStore,
    printPresetsStore,
  }
});
