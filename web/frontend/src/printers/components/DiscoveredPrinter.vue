<template>
<div class="discovered-printers mt-4">
  <div class="flex-grow-0 pt-1 mr-2">
    <img v-if="discoveredPrinter.rpi_model" class="logo-img"
      :src="require('@static/img/raspberry_pi.png')" />
    <img v-else class="logo-img"
      :src="require('@static/img/octoprint_logo.png')" />
  </div>
  <div class="row flex-grow-1 ml-1 link-action">
    <div class="col-sm-12 col-md-10 pb-2">
      <div v-if="discoveredPrinter.rpi_model">
        {{discoveredPrinter.rpi_model}}
      </div>
      <div v-if="discoveredPrinter.machine_type">
        {{discoveredPrinter.machine_type}}
      </div>
      <div v-if="discoveredPrinter.host_or_ip" class="text-muted small">
        IP address: {{discoveredPrinter.host_or_ip}}<span v-if="discoveredPrinter.port">:{{ discoveredPrinter.port }}</span>
      </div>
      <div v-if="discoveredPrinter.hostname" class="text-muted small">
        Hostname: {{discoveredPrinter.hostname}}
      </div>
      <div v-if="discoveredPrinter.octopi_version" class="text-muted small">
        OctoPi: {{discoveredPrinter.octopi_version}}
      </div>
      <div v-if="!discoveredPrinter.octopi_version && discoveredPrinter.os" class="text-muted small">
        OS: {{discoveredPrinter.os}}
      </div>
      <div v-if="!satisfyVersionForAutoLink" class="text-danger small">Auto-linking is not available as the version of The Spaghetti Detective plugin is lower than 1.8.0. Please upgrade the plugin to the latest version, or switch to <a class="link" @click="discoveryEnabled=false">Manual Setup</a>.</div>
    </div>
    <div v-if="satisfyVersionForAutoLink" class="col-sm-12 col-md-2 center px-3">
      <button class="btn btn-block btn-primary" @click="$emit('auto-link-printer', {...discoveredPrinter})">Link</button>
    </div>
    <div v-else class="col-sm-12 col-md-2 center px-3">
      <button class="btn btn-block btn-primary" disabled>Link</button>
    </div>
  </div>

</div>
</template>

<script>
import semverSatisfies from 'semver/functions/satisfies'

export default {
  name: 'DiscoveredPrinter',
  props: {
    discoveredPrinter: {
      type: Object,
      required: true
    },
  },
  computed: {
    satisfyVersionForAutoLink() {
      return this.discoveredPrinter.plugin_version && semverSatisfies(this.discoveredPrinter.plugin_version, '>=1.8.0')
    },
  }
}
</script>

<style lang="sass">
@use "~main/theme"

.discovered-printers
  display: flex
  flex-direction: columns

  .logo-img
    height: 3.5rem

  .link-action
    border-left: solid thin

.center
  display: flex
  justify-content: center
  align-items: center
</style>
