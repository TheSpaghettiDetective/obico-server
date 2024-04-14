<template>
  <section class="personalization">
    <h2 class="section-title">{{ $t("General") }}</h2>
    <div class="form-group row mt-3">
      <label class="col-md-2 col-sm-3 col-form-label">{{ $t("Printers") }}</label>
      <div class="col-sm-9 col-md-10 col-form-label">
        <div class="custom-control custom-checkbox form-check-inline system-theme-control">
          <input
            id="id_theme_system"
            v-model="redirectEnabled"
            type="checkbox"
            class="custom-control-input"
          />
          <label class="custom-control-label" for="id_theme_system">
            {{$t("Land directly on the printer control page if I have only 1 printer")}}
            <br />
            <span class="text-muted setting-description"
              >{{$t("This option will be ignored if you have multiple printers. In this case, you will always land on the printer overview page.")}}</span
            >
          </label>
        </div>
      </div>
      <a class="col-sm-9 col-md-10 col-form-label" href="/ent/printers/archived/"
        >{{ $t("View Archived Printers") }}</a
      >
    </div>
  </section>
</template>

<script>
import { getLocalPref, setLocalPref } from '@src/lib/pref'

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
      redirectEnabled: true,
    }
  },

  watch: {
    redirectEnabled: function (newVal, prevVal) {
      setLocalPref('single-printer-redirect-enabled', newVal)
    },
  },

  created() {
    this.redirectEnabled = getLocalPref('single-printer-redirect-enabled', true)
  },
}
</script>
