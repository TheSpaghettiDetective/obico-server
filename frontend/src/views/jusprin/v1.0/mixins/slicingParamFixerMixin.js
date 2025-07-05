export default {
  methods: {
    fixFilamentParamOverrides(param_overrides) {
      // FIXME: No idea how these temps are used in Orca. But for most printers this hack seems to be good enough.

      // Filament params now have an array of values but apply_config still expects a single value
      Object.keys(param_overrides).forEach((key) => {
        if (Array.isArray(param_overrides[key]) && param_overrides[key].length > 0) {
          param_overrides[key] = param_overrides[key][0]; // Unpack to the first value
        }
      });

      const plateTemps = [
        'cool_plate_temp',
        'eng_plate_temp',
        'hot_plate_temp',
        'textured_cool_plate_temp',
        'textured_plate_temp',
      ]

      // Check if any plate temp parameter exists
      const existingTemp = plateTemps.find((key) => key in param_overrides)

      if (existingTemp) {
        const tempValue = param_overrides[existingTemp]
        // Set the same temperature for all plate types
        plateTemps.forEach((key) => {
          param_overrides[key] = tempValue
        })
      }

      const plateTempsInitialLayer = [
        'cool_plate_temp_initial_layer',
        'eng_plate_temp_initial_layer',
        'hot_plate_temp_initial_layer',
        'textured_cool_plate_temp_initial_layer',
        'textured_plate_temp_initial_layer',
      ]

      // Check if any plate temp parameter exists
      const existingTempInitialLayer = plateTempsInitialLayer.find((key) => key in param_overrides)

      if (existingTempInitialLayer) {
        const tempValue = param_overrides[existingTempInitialLayer]
        // Set the same temperature for all plate types
        plateTempsInitialLayer.forEach((key) => {
          param_overrides[key] = tempValue
        })
      }

      return param_overrides
    },
  },
}
