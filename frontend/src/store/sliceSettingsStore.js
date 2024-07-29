const state = {
  bottomSheetOpen: false,
  rotationAngle: 0,
}

const mutations = {
  SET_BOTTOM_SHEET_OPEN(state, bottomSheetOpen) {
    state.bottomSheetOpen = bottomSheetOpen
  },
  SET_ROTATION_ANGLE(state, rotationAngle) {
    state.rotationAngle = rotationAngle
  },
}

const actions = {
  updateBottomSheetOpen({ commit }, bottomSheetOpen) {
    commit('SET_BOTTOM_SHEET_OPEN', bottomSheetOpen)
  },
  updateRotationAngle({ commit }, rotationAngle) {
    commit('SET_ROTATION_ANGLE', rotationAngle)
  },
}

const getters = {
  bottomSheetOpen: (state) => state.bottomSheetOpen,
  rotationAngle: (state) => state.rotationAngle,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
