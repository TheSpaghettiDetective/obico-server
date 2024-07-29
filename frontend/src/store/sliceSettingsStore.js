const state = {
  bottomSheetOpen: false,
}

const mutations = {
  SET_BOTTOM_SHEET_OPEN(state, bottomSheetOpen) {
    state.bottomSheetOpen = bottomSheetOpen
  },
}

const actions = {
  updateBottomSheetOpen({ commit }, bottomSheetOpen) {
    commit('SET_BOTTOM_SHEET_OPEN', bottomSheetOpen)
  },
}

const getters = {
  bottomSheetOpen: (state) => state.bottomSheetOpen,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
