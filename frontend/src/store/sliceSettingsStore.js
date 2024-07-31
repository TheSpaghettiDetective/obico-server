const state = {
  bottomSheetOpen: false,
  rotationAngles: [0, 0, 0],
}

const mutations = {
  SET_BOTTOM_SHEET_OPEN(state, bottomSheetOpen) {
    state.bottomSheetOpen = bottomSheetOpen
  },
  SET_ROTATION_ANGLE(state, {index, angle}) {
    state.rotationAngles.splice(index, 1, angle);
  }
}

const actions = {
  openModelRotationBottomSheet({ commit }) {
    commit('SET_BOTTOM_SHEET_OPEN', true)
  },
  closeModelRotationBottomSheet({ commit }) {
    commit('SET_BOTTOM_SHEET_OPEN', false)
  },
  updateRotationAngle({ commit }, payload) {
    commit('SET_ROTATION_ANGLE', payload)
  },
}

const getters = {
  bottomSheetOpen: (state) => state.bottomSheetOpen,
  rotationAngles: (state) => state.rotationAngles,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
