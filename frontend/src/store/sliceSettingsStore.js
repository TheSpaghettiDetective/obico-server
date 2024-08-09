const state = {

  //Component States
  RotationbottomSheetOpen: false,
  ScalebottomSheetOpen: false,
  TranslatebottomSheetOpen: false,
  PrintProfilebottomSheetOpen: false,
  MachineSelectionOpen: false,
  FilamentSelectionOpen: false,
  PrintProcessSelectionOpen: false,


  // Profile Presets
  profilePreset: {},   // Preset values for the selected print profile. Should not be modified.
  profileOverwrites: {}, // User-modified values for the selected print profile. Should be used to generate the final print profile.
  selectedMachine: null,
  selectedFilament: null,
  selectedPrintProcess: null,
  designName: null,


  //Multimesh setup

   // Meshs Array
   meshes: [], // Array to store mesh-specific data
   selectedMeshIndex: 0 // Index of the currently selected mesh
}

const mutations = {

  //ADD MODEL
  ADD_MODEL(state, mesh) {
    state.meshes.push(mesh);
  },
  SET_SELECTED_MESH_INDEX(state, index) {
    state.selectedMeshIndex = index;
  },
  UPDATE_MESH_ROTATION(state, { index, rotation }) {
    if (state.meshes[index]) {
      state.meshes[index].rotation = rotation;
    }
  },

  UPDATE_MESH_TRANSLATE(state, { index, translate }) {
    if (state.meshes[index]) {
      state.meshes[index].translate = translate;
    }
  },

  UPDATE_MESH_DIMENSIONS(state, { index, dimensions }) {

    state.meshes[index].currentDimensions = {
      x: parseFloat(dimensions.x),
      y: parseFloat(dimensions.y),
      z: parseFloat(dimensions.z),
    };
  },



  SET_ROTATION_BOTTOM_SHEET_OPEN(state, RotationbottomSheetOpen) {
    state.RotationbottomSheetOpen = RotationbottomSheetOpen
  },

  SET_SCALE_BOTTOM_SHEET_OPEN(state, ScalebottomSheetOpen) {
    state.ScalebottomSheetOpen = ScalebottomSheetOpen
  },
  SET_TRANSLATE_BOTTOM_SHEET_OPEN(state, TranslatebottomSheetOpen) {
    state.TranslatebottomSheetOpen = TranslatebottomSheetOpen
  },

  SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN(state, PrintProfilebottomSheetOpen) {
    state.PrintProfilebottomSheetOpen = PrintProfilebottomSheetOpen;
  },

  SET_MACHINE_SELECTION_OPEN(state, MachineSelectionOpen) {
    state.MachineSelectionOpen = MachineSelectionOpen;
  },


  SET_FILAMENT_SELECTION_OPEN(state, FilamentSelectionOpen) {
    state.FilamentSelectionOpen = FilamentSelectionOpen;
  },

  SET_PRINT_PROCESSESS_SELECTION_OPEN(state, PrintProcessSelectionOpen) {
    state.PrintProcessSelectionOpen = PrintProcessSelectionOpen;
  },

  SET_SELECTED_MACHINE(state, printerName) {
    state.selectedMachine = printerName;
  },


  SET_DESIGN_NAME(state, designName) {
    state.designName = designName;
  },

  SET_SELECTED_FILAMENT(state, filamentName) {
    state.selectedFilament = filamentName;
  },

  SET_SELECTED_PRINT_PROCESSESS(state, selectedPrintProcess) {
    state.selectedPrintProcess = selectedPrintProcess;
  },

  SET_PROFILE_PRESET(state, profilePreset) {
    state.profilePreset = { ...profilePreset };
  },

  UPDATE_PROFILE_PRESET_VALUE(state, { key, value }) {
    state.profilePreset = {
      ...state.profilePreset,
      [key]: value,
    };
  },
}

const actions = {

  //Multi Mesh Setup
  addMesh({ commit }, mesh) {
    commit('ADD_MODEL', mesh);
  },
  setSelectedMeshIndex({ commit }, index) {
    commit('SET_SELECTED_MESH_INDEX', index);
  },
  updateMeshRotation({ commit, state }, rotation) {
    const index = state.selectedMeshIndex;
    commit('UPDATE_MESH_ROTATION', { index, rotation });
  },

  updateMeshTranslate({ commit, state }, translate) {
    const index = state.selectedMeshIndex;
    commit('UPDATE_MESH_TRANSLATE', { index, translate });
  },




  updateCurrentDimensions({ commit, state }, { index, dimensions }) {
    commit('UPDATE_MESH_DIMENSIONS', { index, dimensions });
  },

  //RotationBottomSheet
  openMeshRotationBottomSheet({ commit }) {
    commit('SET_ROTATION_BOTTOM_SHEET_OPEN', true)
  },
  closeMeshRotationBottomSheet({ commit }) {
    commit('SET_ROTATION_BOTTOM_SHEET_OPEN', false)
  },

  //Scale Bottom Sheet
  openMeshScaleBottomSheet({ commit }) {
    commit('SET_SCALE_BOTTOM_SHEET_OPEN', true)
  },
  closeMeshScaleBottomSheet({ commit }) {
    commit('SET_SCALE_BOTTOM_SHEET_OPEN', false)
  },

  //Translate Bottom Sheet
  openTranslateBottomSheet({ commit }) {
    commit('SET_TRANSLATE_BOTTOM_SHEET_OPEN', true)
  },
  closeTranslateBottomSheet({ commit }) {
    commit('SET_TRANSLATE_BOTTOM_SHEET_OPEN', false)
  },


  //Print Profile BottomSheet
  openPrintProfileBottomSheet({ commit }) {
    commit('SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN', true);
  },
  closePrintProfileBottomSheet({ commit }) {
    commit('SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN', false);
  },

  //Profile Presets

  setProfilePreset({ commit }, profilePreset) {
    commit('SET_PROFILE_PRESET', profilePreset);
  },

  updateProfilePresetValue({ commit }, { key, value }) {
    commit('UPDATE_PROFILE_PRESET_VALUE', { key, value });
  },

  openMachineSelection({ commit }) {
    commit('SET_MACHINE_SELECTION_OPEN', true);
  },
  closeMachineSelection({ commit }) {
    commit('SET_MACHINE_SELECTION_OPEN', false);
  },

  setSelectedMachine({ commit }, printerName) {
    commit('SET_SELECTED_MACHINE', printerName);
  },

  setSelectedFilament({ commit }, filamentName) {
    commit('SET_SELECTED_FILAMENT', filamentName);
  },

  setDesignName({ commit }, designName) {
    commit('SET_DESIGN_NAME', designName);
  },


  setSelectedPrintProcess({ commit }, selectedPrintProcess) {
    commit('SET_SELECTED_PRINT_PROCESSESS', selectedPrintProcess);
  },



  //FilamentSelection
  openFilamentSelection({ commit }) {
    commit('SET_FILAMENT_SELECTION_OPEN', true);
  },
  closeFilamentSelection({ commit }) {
    commit('SET_FILAMENT_SELECTION_OPEN', false);
  },


  //PrintProcess
  openPrintProcess({ commit }) {
    commit('SET_PRINT_PROCESSESS_SELECTION_OPEN', true);
  },
  closePrintProcess({ commit }) {
    commit('SET_PRINT_PROCESSESS_SELECTION_OPEN', false);
  },


}

const getters = {

  //Multi Mesh Setup
  selectedMeshRotation: (state) => state.meshes[state.selectedMeshIndex]?.rotation,
  selectedMeshTranslate: (state) => state.meshes[state.selectedMeshIndex]?.translate,

  selectedMeshDimensions: (state) => ({
    originalDimensions: state.meshes[state.selectedMeshIndex]?.originalDimensions,
    currentDimensions: state.meshes[state.selectedMeshIndex]?.currentDimensions,
  }),

  RotationbottomSheetOpen: (state) => state.RotationbottomSheetOpen,
  ScalebottomSheetOpen: (state) => state.ScalebottomSheetOpen,
  TranslatebottomSheetOpen: (state) => state.TranslatebottomSheetOpen,
  PrintProfilebottomSheetOpen: (state) => state.PrintProfilebottomSheetOpen,
  MachineSelectionOpen: (state) => state.MachineSelectionOpen,
  FilamentSelectionOpenn: (state) => state.FilamentSelectionOpen,
  PrintProcessSelectionOpen: (state) => state.PrintProcessSelectionOpen,

  selectedMachine: (state) => state.selectedMachine,
  selectedFilament: (state) => state.selectedFilament,
  selectedPrintProcess: (state) => state.selectedPrintProcess,
  designName: (state) => state.designName,
  getProfilePresetValue: (state) => (key) => {
    return state.profilePreset[key] || ''
  },

  getProfilePreset: (state) => state.profilePreset,
  getMeshes: (state) => state.meshes,


}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
