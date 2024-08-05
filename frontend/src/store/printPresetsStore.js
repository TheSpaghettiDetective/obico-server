// store/modules/printPresets.js
import axios from 'axios'

const state = {
  presets: {},
}

const mutations = {
    SET_PRESETS(state, presets) {
        state.presets = { ...presets }
      },
      UPDATE_PRESET(state, { key, value }) {
        state.presets = {
          ...state.presets,
          [key]: value,
        }
      },
}

const actions = {
   addPrintPresets({ commit }, data) {
        commit('SET_PRESETS', data)
  },

  updatePrintPreset({ commit }, payload) {
    commit('UPDATE_PRESET', payload)
  },

}

const getters = {
  getPresetValue: (state) => (key) => {
    return state.presets[key] || ''
  },
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
