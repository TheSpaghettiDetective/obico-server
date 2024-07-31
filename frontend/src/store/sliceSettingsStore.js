const state = {
  RotationbottomSheetOpen: false,
  ScalebottomSheetOpen: false,
  MovebottomSheetOpen: false,
  PrintProfilebottomSheetOpen: false,
  rotationAngles: [0, 0, 0],
  initialDimensions: { x: 0, y: 0, z: 0 },
  currentDimensions: { x: 0, y: 0, z: 0 },
  moveMagnitudes: [0, 0],
}

const mutations = {

  SET_INITIAL_DIMENSIONS(state, dimensions) {
    Object.assign(state.initialDimensions, dimensions);
  },
  SET_CURRENT_DIMENSIONS(state, dimensions) {
    Object.assign(state.currentDimensions, dimensions);
  },



  SET_ROTATION_BOTTOM_SHEET_OPEN(state, RotationbottomSheetOpen) {
    state.RotationbottomSheetOpen = RotationbottomSheetOpen
  },
  SET_ROTATION_ANGLE(state, {index, angle}) {
    state.rotationAngles.splice(index, 1, angle);
  },

  SET_MOVE_MAGNITUDE(state, {index, magnitude}) {
    state.moveMagnitudes.splice(index, 1, magnitude);
  },

  SET_SCALE_BOTTOM_SHEET_OPEN(state, ScalebottomSheetOpen) {
    state.ScalebottomSheetOpen = ScalebottomSheetOpen
  },
  SET_MOVE_BOTTOM_SHEET_OPEN(state, MovebottomSheetOpen) { 
    state.MovebottomSheetOpen = MovebottomSheetOpen
  },

  SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN(state, PrintProfilebottomSheetOpen) {
    state.PrintProfilebottomSheetOpen = PrintProfilebottomSheetOpen;
  },

}

const actions = {

  setInitialDimensions({ commit }, dimensions) {
    commit('SET_INITIAL_DIMENSIONS', dimensions);
    commit('SET_CURRENT_DIMENSIONS', dimensions); // Initialize current dimensions without triggering watchers
  },
  updateCurrentDimensions({ commit }, dimensions) {
    commit('SET_CURRENT_DIMENSIONS', dimensions);
  },



  //RotationBottomSheet
  openModelRotationBottomSheet({ commit }) {
    commit('SET_ROTATION_BOTTOM_SHEET_OPEN', true)
  },
  closeModelRotationBottomSheet({ commit }) {
    commit('SET_ROTATION_BOTTOM_SHEET_OPEN', false)
  },

  //Scale Bottom Sheet
  openModelScaleBottomSheet({ commit }) {
    commit('SET_SCALE_BOTTOM_SHEET_OPEN', true)
  },
  closeModelScaleBottomSheet({ commit }) {
    commit('SET_SCALE_BOTTOM_SHEET_OPEN', false)
  },

  //Move Bottom Sheet
  openMoveBottomSheet({ commit }) { 
    commit('SET_MOVE_BOTTOM_SHEET_OPEN', true)
  },
  closeMoveBottomSheet({ commit }) { 
    commit('SET_MOVE_BOTTOM_SHEET_OPEN', false)
  },


  //Print Profile BottomSheet
  openPrintProfileBottomSheet({ commit }) {
    commit('SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN', true);
  },
  closePrintProfileBottomSheet({ commit }) {
    commit('SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN', false);
  },


  //Rotation Angle
  updateRotationAngle({ commit }, payload) {
    commit('SET_ROTATION_ANGLE', payload)
  },


  updateMoveMagnitude({ commit }, payload) {
    commit('SET_MOVE_MAGNITUDE', payload)
  },

}

const getters = {
  RotationbottomSheetOpen: (state) => state.RotationbottomSheetOpen,
  ScalebottomSheetOpen: (state) => state.ScalebottomSheetOpen,
  MovebottomSheetOpen: (state) => state.MovebottomSheetOpen,
  PrintProfilebottomSheetOpen: (state) => state.PrintProfilebottomSheetOpen,
  initialDimensions: (state) => state.initialDimensions,
  currentDimensions: (state) => state.currentDimensions,
  rotationAngles: (state) => state.rotationAngles,
  moveMagnitudes: (state) => state.moveMagnitudes,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
