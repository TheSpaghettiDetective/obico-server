import axios from 'axios'

const state = {

  //Component States
  RotationbottomSheetOpen: false,
  ScalebottomSheetOpen: false,
  TranslatebottomSheetOpen: false,
  PrintProfilebottomSheetOpen: false,
  MachineSelectionOpen: false,
  PatternSelectionOpen: false,
  GeneralTypeSelectionOpen: false,
  PatternSelectionType: null,
  GeneralTypeSelectionType: null,
  FilamentSelectionOpen: false,
  PrintProcessSelectionOpen: false,
  isInitialLoad: true,


  // Profile Presets
  profilePreset: {},   // Preset values for the selected print profile. Should not be modified.
  profileOverwrites: {}, // User-modified values for the selected print profile. Should be used to generate the final print profile.
  selectedMachine: null,
  selectedFilament: null,
  selectedPrintProcess: null,
  designName: null,

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
  UPDATE_MESH_ROTATION(state, { meshIndex, rotation }) {
    state.meshes[meshIndex].rotation = rotation;
  },

  UPDATE_MESH_TRANSLATE(state, { meshIndex, translate }) {
    state.meshes[meshIndex].translate = translate;
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

  SET_PATTERN_SELECTION_OPEN(state, PatternSelectionOpen) {
    state.PatternSelectionOpen = PatternSelectionOpen;
  },

  SET_PATTERN_SELECTION_TYPE(state, PatternSelectionType) {
    state.PatternSelectionType = PatternSelectionType;
  },

  SET_GENERAL_TYPE_SELECTION_OPEN(state, GeneralTypeSelectionOpen) {
    state.GeneralTypeSelectionOpen = GeneralTypeSelectionOpen;
  },

  SET_GENERAL_TYPE_SELECTION_TYPE(state, GeneralTypeSelectionType) {
    state.GeneralTypeSelectionType = GeneralTypeSelectionType;
  },

  SET_FILAMENT_SELECTION_OPEN(state, FilamentSelectionOpen) {
    state.FilamentSelectionOpen = FilamentSelectionOpen;
  },

  SET_PRINT_PROCESS_SELECTION_OPEN(state, PrintProcessSelectionOpen) {
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

  SET_SELECTED_PRINT_PROCESS(state, selectedPrintProcess) {
    state.selectedPrintProcess = selectedPrintProcess;
  },

  SET_PROFILE_PRESET(state, profilePreset) {
    state.profilePreset = { ...profilePreset,
      fuzzy_skin: 'none',
      internal_solid_infill_pattern: 'monotonic',
      brim_type: 'auto_brim',
     };
  },

  UPDATE_PROFILE_PRESET_VALUE(state, { key, value }) {
    state.profilePreset = {
      ...state.profilePreset,
      [key]: value,
    };
  },

  UPDATE_PROFILE_OVERWRITE_VALUE(state, { key, value }) {
    state.profileOverwrites = {
      ...state.profileOverwrites,
      [key]: value,
    };
  },

  SET_INITIAL_LOAD(state, value) {
    state.isInitialLoad = value;
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

  updateMeshTranslate({ commit, state }, {meshIndex, translate}) {
    commit('UPDATE_MESH_TRANSLATE', { meshIndex, translate });
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

  updateProfileValue({ commit }, { key, value }) {
    commit('UPDATE_PROFILE_OVERWRITE_VALUE', { key, value });
  },

  openMachineSelection({ commit }) {
    commit('SET_MACHINE_SELECTION_OPEN', true);
  },

  closeMachineSelectionAndClearInitialLoad({ commit }) {
    commit('SET_INITIAL_LOAD', false);
    commit('SET_MACHINE_SELECTION_OPEN', false);
  },

  openPatternSelection({ commit }) {
    commit('SET_PATTERN_SELECTION_OPEN', true);
  },
  closePatternSelection({ commit }) {
    commit('SET_PATTERN_SELECTION_OPEN', false);
  },
  setPatternSelectionType({ commit }, type) {
    commit('SET_PATTERN_SELECTION_TYPE', type);
  },


  openGeneralTypeSelection({ commit }) {
    commit('SET_GENERAL_TYPE_SELECTION_OPEN', true);
  },
  closeGeneralTypeSelection({ commit }) {
    commit('SET_GENERAL_TYPE_SELECTION_OPEN', false);
  },
  setGeneralTypeSelectionType({ commit }, type) {
    commit('SET_GENERAL_TYPE_SELECTION_TYPE', type);
  },

  changeMachineAndRelatedPresets({ commit, state, dispatch }, machine) {
    commit('SET_SELECTED_MACHINE', machine);
    commit('SET_SELECTED_FILAMENT', machine?.default_filament);
    dispatch('changePrintProcessAndLoadPreset', machine?.default_print_process);

    if (state.isInitialLoad) {
      setTimeout(() => {
        // A short delay to allow animation to complete for better UX
        if (!state.selectedFilament || !state.selectedPrintProcess) {
          commit('SET_PRINT_PROFILE_BOTTOM_SHEET_OPEN', true);
        }
      }, 300)
    }

    dispatch('closeMachineSelectionAndClearInitialLoad');
  },

  setDesignName({ commit }, designName) {
    commit('SET_DESIGN_NAME', designName);
  },


  changePrintProcessAndLoadPreset({ commit }, selectedPrintProcess) {
    commit('SET_SELECTED_PRINT_PROCESS', selectedPrintProcess);
    commit('SET_PRINT_PROCESS_SELECTION_OPEN', false);

    if (selectedPrintProcess?.slicer_profile_url) {
      axios
        .get(selectedPrintProcess?.slicer_profile_url)
        .then((response) => {
          commit('SET_PROFILE_PRESET', response.data)
        })
      }
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
    commit('SET_PRINT_PROCESS_SELECTION_OPEN', true);
  },
  closePrintProcess({ commit }) {
    commit('SET_PRINT_PROCESS_SELECTION_OPEN', false);
  },

  setInitialLoadDone({ commit }) {
    commit('SET_INITIAL_LOAD', false);
  }

}

const getters = {

  //Multi Mesh Setup
  selectedMeshRotation: (state) => state.meshes[state.selectedMeshIndex]?.rotation,
  selectedMeshTranslate: (state) => state.meshes[state.selectedMeshIndex]?.translate,
  selectedMeshCenter: (state) => state.meshes[state.selectedMeshIndex]?.center,

  selectedMeshDimensions: (state) => ({
    originalDimensions: state.meshes[state.selectedMeshIndex]?.originalDimensions,
    currentDimensions: state.meshes[state.selectedMeshIndex]?.currentDimensions,
  }),

  RotationbottomSheetOpen: (state) => state.RotationbottomSheetOpen,
  ScalebottomSheetOpen: (state) => state.ScalebottomSheetOpen,
  TranslatebottomSheetOpen: (state) => state.TranslatebottomSheetOpen,
  PrintProfilebottomSheetOpen: (state) => state.PrintProfilebottomSheetOpen,
  MachineSelectionOpen: (state) => state.MachineSelectionOpen,
  PatternSelectionOpen: (state) => state.PatternSelectionOpen,
  FilamentSelectionOpenn: (state) => state.FilamentSelectionOpen,
  PrintProcessSelectionOpen: (state) => state.PrintProcessSelectionOpen,

  selectedMachine: (state) => state.selectedMachine,
  selectedFilament: (state) => state.selectedFilament,
  selectedPrintProcess: (state) => state.selectedPrintProcess,
  profileOverwrites: (state) => state.profileOverwrites,
  designName: (state) => state.designName,
  getProfileValue: (state) => (key) => {
    if (state.profileOverwrites[key]) {
      return state.profileOverwrites[key];
    }
    return state.profilePreset[key] || ''
  },
  meshes: (state) => state.meshes,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
