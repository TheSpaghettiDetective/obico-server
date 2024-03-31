<template>
  <page-layout>
    <template #content>
      <div class="container">
        <div class="row">
          <h3 class="col-sm-12 text-center p-3">{{ $t("Which platform are you using?") }}</h3>
        </div>
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <div class="wizard-card" @click="setTargetPlatform('octoprint')">
              <img :src="require('@static/img/octoprint_logo.png')" />
              <h3 class="mt-4">OctoPrint</h3>
              <div>{{ $t("Including OctoPrint for Klipper such as OctoKlipper.") }}</div>
            </div>
          </div>
          <div class="col-sm-12 col-lg-6 p-4">
            <div class="wizard-card" @click="setTargetPlatform('moonraker')">
              <div>
                <img :src="require('@static/img/klipper_logo.jpg')" />
                <img :src="require('@static/img/mainsail_logo.png')" />
                <img :src="require('@static/img/fluidd_logo.png')" />
              </div>
              <h3 class="mt-4">Klipper</h3>
              <h5>{{ $t("with Mainsail/Fluidd/Moonraker") }}</h5>
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
      targetPlatform: null,
    }
  },
  methods: {
    setTargetPlatform(platform) {
      this.targetPlatform = platform
      this.$router.push(`/printers/wizard/link/${platform}`);
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
