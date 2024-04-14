<template>
  <div class="discovered-printers mt-4">
    <div class="flex-grow-0 pt-1 mr-2">
      <img v-if="discoveredPrinter.agent.toLowerCase().includes('octoprint')" class="logo-img" :src="require('@static/img/octoprint_logo.png')" />
      <img v-else-if="discoveredPrinter.agent.toLowerCase().includes('klipper')" class="logo-img" :src="require('@static/img/klipper_logo.jpg')" />
      <img
        v-else
        class="logo-img"
        :src="require('@static/img/raspberry_pi.png')"
      />
    </div>
    <div class="row flex-grow-1 ml-1 link-action">
      <div class="col-sm-12 col-md-10 pb-2">
        <div v-if="discoveredPrinter.rpi_model">
          {{ discoveredPrinter.rpi_model }}
        </div>
        <div v-if="discoveredPrinter.machine_type">
          {{ discoveredPrinter.machine_type }}
        </div>
        <div v-if="discoveredPrinter.agent" class="text-muted small">
          {{$t("Platform")}}: {{ discoveredPrinter.agent }}
        </div>
        <div v-if="discoveredPrinter.host_or_ip" class="text-muted small">
          {{$t("IP address")}}: {{ discoveredPrinter.host_or_ip }}
        </div>
        <div v-if="discoveredPrinter.hostname" class="text-muted small">
          {{$t("Hostname")}}: {{ discoveredPrinter.hostname }}
        </div>
        <div v-if="discoveredPrinter.octopi_version" class="text-muted small">
          {{$t("OctoPi")}}: {{ discoveredPrinter.octopi_version }}
        </div>
        <div
          v-if="!discoveredPrinter.octopi_version && discoveredPrinter.os"
          class="text-muted small"
        >
          {{$t("OS")}}: {{ discoveredPrinter.os }}
        </div>
      </div>
      <div class="col-sm-12 col-md-2 center px-3">
        <button
          class="btn btn-block btn-primary"
          @click="$emit('auto-link-printer', { ...discoveredPrinter })"
        >
          {{$t("Link")}}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiscoveredPrinter',
  props: {
    discoveredPrinter: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="sass">
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
