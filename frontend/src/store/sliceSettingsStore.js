const state = {

  //Component States
  RotationbottomSheetOpen: false,
  ScalebottomSheetOpen: false,
  TranslatebottomSheetOpen: false,
  PrintProfilebottomSheetOpen: false,
  PrinterSelectionOpen: false,
  FilamentSelectionOpen: false,
  PrintProcessessSelectionOpen: false,


  // Model Manipulation Parameter States
  rotationAngles: [0, 0, 0],
  initialDimensions: { x: 0, y: 0, z: 0 },
  currentDimensions: { x: 0, y: 0, z: 0 },
  translateMagnitudes: [0, 0],



  //printers
  selectedPrinter: null,
  selectedFilament: null,
  selectedPrintProcessess: null,
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

  SET_TRANSLATE_MAGNITUDE(state, {index, magnitude}) {
    state.translateMagnitudes.splice(index, 1, magnitude);
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

  SET_PRINTER_SELECTION_OPEN(state, PrinterSelectionOpen) {
    state.PrinterSelectionOpen = PrinterSelectionOpen;
  },


  SET_FILAMENT_SELECTION_OPEN(state, FilamentSelectionOpen) {
    state.FilamentSelectionOpen = FilamentSelectionOpen;
  },

  SET_PRINT_PROCESSESS_SELECTION_OPEN(state, PrintProcessessSelectionOpen) {
    state.PrintProcessessSelectionOpen = PrintProcessessSelectionOpen;
  },

  SET_SELECTED_PRINTER(state, printerName) {
    state.selectedPrinter = printerName;
  },
  
  SET_SELECTED_FILAMENT(state, filamentName) {
    state.selectedFilament = filamentName;
  },

  SET_SELECTED_PRINT_PROCESSESS(state, selectedPrintProcessess) {
    state.selectedPrintProcessess = selectedPrintProcessess;
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

  //PrinterSelection

  openPrinterSelection({ commit }) {
    commit('SET_PRINTER_SELECTION_OPEN', true);
  },
  closePrinterSelection({ commit }) {
    commit('SET_PRINTER_SELECTION_OPEN', false);
  },

  setSelectedPrinter({ commit }, printerName) {
    commit('SET_SELECTED_PRINTER', printerName);
  },

  setSelectedFilament({ commit }, filamentName) {
    commit('SET_SELECTED_FILAMENT', filamentName);
  },


  setSelectedPrintProcessess({ commit }, selectedPrintProcessess) {
    commit('SET_SELECTED_PRINT_PROCESSESS', selectedPrintProcessess);
  },



  //FilamentSelection
  openFilamentSelection({ commit }) {
    commit('SET_FILAMENT_SELECTION_OPEN', true);
  },
  closeFilamentSelection({ commit }) {
    commit('SET_FILAMENT_SELECTION_OPEN', false);
  },


  //PrintProcessess
  openPrintProcessess({ commit }) {
    commit('SET_PRINT_PROCESSESS_SELECTION_OPEN', true);
  },
  closePrintProcessess({ commit }) {
    commit('SET_PRINT_PROCESSESS_SELECTION_OPEN', false);
  },


  //Rotation Angle
  updateRotationAngle({ commit }, payload) {
    commit('SET_ROTATION_ANGLE', payload)
  },


  updateTranslateMagnitude({ commit }, payload) {
    commit('SET_TRANSLATE_MAGNITUDE', payload)
  },

}

const getters = {
  RotationbottomSheetOpen: (state) => state.RotationbottomSheetOpen,
  ScalebottomSheetOpen: (state) => state.ScalebottomSheetOpen,
  TranslatebottomSheetOpen: (state) => state.TranslatebottomSheetOpen,
  PrintProfilebottomSheetOpen: (state) => state.PrintProfilebottomSheetOpen,
  PrinterSelectionOpen: (state) => state.PrinterSelectionOpen,
  FilamentSelectionOpenn: (state) => state.FilamentSelectionOpen,
  PrintProcessessSelectionOpen: (state) => state.PrintProcessessSelectionOpen,

  initialDimensions: (state) => state.initialDimensions,
  currentDimensions: (state) => state.currentDimensions,
  rotationAngles: (state) => state.rotationAngles,
  translateMagnitudes: (state) => state.translateMagnitudes,
  selectedPrinter: (state) => state.selectedPrinter,
  selectedFilament: (state) => state.selectedFilament,
  selectedPrintProcessess: (state) => state.selectedPrintProcessess

}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
