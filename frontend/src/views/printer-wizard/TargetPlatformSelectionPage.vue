<template>
  <page-layout>
    <template #content>
      <div class="container">
        <div class="row">
          <h3 class="col-sm-12 text-center p-3">{{ $t("Which platform are you using?") }}</h3>
        </div>
        <div v-if="devicesWithObicoPreInstalled.length > 0" class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <h4 class="col-sm-12 p-3">{{ $t("Devices with Obico Pre-installed") }}</h4>
            <div v-for="item in devicesWithObicoPreInstalled" :key="item.id" @click="targetPlatformClicked('klipper-obico-enabled')">
              <div>{{ item.model }}</div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <div class="wizard-card" @click="targetPlatformClicked('klipper-preinstalled')">
              <div>
                <img :src="require('@static/img/klipper_logo.jpg')" />
              </div>
              <h3 class="mt-4">{{ $t("Pre-Installed Klipper Printer") }}</h3>
              <h5>{{ $t("Creality K1, Sonic Pad, Sovol SV07, Kingroon KLP1, Elegoo Neptune 4, etc...") }}</h5>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <div class="wizard-card" @click="targetPlatformClicked('klipper-generic')">
              <div>
                <img :src="require('@static/img/klipper_logo.jpg')" />
                <img :src="require('@static/img/mainsail_logo.png')" />
                <img :src="require('@static/img/fluidd_logo.png')" />
              </div>
              <h3 class="mt-4">{{ $t("Generic Klipper - Self Installed") }}</h3>
              <h5>{{ $t("If you installed Klipper yourself on a Raspberry Pi or other linux device. E.g., Voron, RatRig") }}</h5>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <div class="wizard-card" @click="targetPlatformClicked('octoprint')">
              <img :src="require('@static/img/octoprint_logo.png')" />
              <h3 class="mt-4">OctoPrint</h3>
              <div>{{ $t("Including OctoPrint for Klipper such as OctoKlipper.") }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'

export default {
  components: {
    PageLayout,
  },
  data() {
    return {
      devicesWithObicoPreInstalled: [],
    }
  },
  async created() {
    const response = await fetch(`https://storage.googleapis.com/public-versioned/devices_with_obico_preinstalled.json?ts=${Date.now()}`);
    this.devicesWithObicoPreInstalled = await response.json();
  },
  methods: {
    targetPlatformClicked(platform) {
      this.$router.push({
        path: `/printers/wizard/guide/${platform}/`,
        query: {
          ...this.$route.query,
        }
      });
    },
  },
}
</script>

<style lang="sass" scoped>
.wizard-card
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-lg)
  padding: 1em
  display: flex
  flex-direction: column
  align-items: center
  min-height: 24em
  justify-content: center
  text-align: center
  &:hover
    cursor: pointer
    color: var(--color-primary)
    background-color: var(--color-hover)
.wizard-card img
  height: 3em
  margin: 1em
</style>
