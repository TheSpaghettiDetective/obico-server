<template>
  <section class="personalization">
    <h2 class="section-title">General</h2>
    <div class="form-group row mt-3">
      <label class="col-md-2 col-sm-3 col-form-label">Printers</label>
      <div class="col-sm-9 col-md-10 col-form-label">
        <div class="custom-control custom-checkbox form-check-inline system-theme-control">
          <input
            id="id_theme_system"
            v-model="redirectEnabled"
            type="checkbox"
            class="custom-control-input"
          />
          <label class="custom-control-label" for="id_theme_system">
            Skip dashboard view, if only one printer is available
            <br />
            <span class="text-muted setting-description"
              >Even enabled it won't take effect, if you have any archived printer(s)</span
            >
          </label>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'GeneralPreferences',

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
      required: true,
    },
    user: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      redirectEnabled: this.user.single_printer_redirect_enabled,
    }
  },

  watch: {
    redirectEnabled: function (newVal, prevVal) {
      this.$emit('updateSetting', 'single_printer_redirect_enabled', newVal)
    },
  },
}
</script>
