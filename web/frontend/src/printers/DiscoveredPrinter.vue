<template>
<div class="list-group-item list-group-item-action discovered-printers">
  <div>
    <img class="logo-img"
      :src="require('@static/img/octoprint_logo.png')" />
    <img v-if="discoveredPrinter.rpi_model" class="logo-img"
      :src="require('@static/img/raspberry_pi.png')" />
  </div>
  <div>
    <div v-if="discoveredPrinter.rpi_model">
      {{discoveredPrinter.rpi_model}}
    </div>
    <div v-if="discoveredPrinter.machine_type">
      {{discoveredPrinter.machine_type}}
    </div>
    <div v-if="octoPrintUrl">
      <a :href="octoPrintUrl">{{octoPrintUrl}}</a>
    </div>
  </div>
  <button class="btn btn-primary" @click="$emit('auto-link-printer', discoveredPrinter.device_id)">Link</button>
</div>
</template>

<script>
export default {
  name: 'DiscoveredPrinter',
  props: {
    discoveredPrinter: {
      type: Object,
      required: true
    },
  },
  computed: {
    octoPrintUrl() {
      if (this.discoveredPrinter.host_or_ip && this.discoveredPrinter.port) {
        return `http://${this.discoveredPrinter.host_or_ip}:${this.discoveredPrinter.port}`
      }
      return null
    },
  }
}
</script>

<style lang="sass">
@use "~main/theme"

.discovered-printers
  display: flex
  align-items: center
  justify-content: space-between
  .logo-img
    height: 2.5rem
</style>
