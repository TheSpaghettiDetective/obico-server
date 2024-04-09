<template>
  <page-layout>
    <template #content>
      <div class="container">
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
          <div v-if="targetOctoPrint" class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>{{ $t("Open OctoPrint in another browser tab.") }}</li>
                  <li>
                    {{ $t("Select") }}
                    <em>"{{$t("OctoPrint settings menu → Plugin Manager → Get More...")}}"</em>.
                  </li>
                  <li>{{ $t("Enter '{brandName}' to locate the plugin. Click",{brandName:$syndicateText.brandName}) }} <em>"{{$t("Install")}}"</em>.</li>
                  <li>{{ $t("Restart OctoPrint when prompted.") }}</li>
                </ol>
              </div>
            </div>
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img
                  class="mx-auto screenshot"
                  :src="
                    require('@static/img/octoprint-plugin-guide/install_plugin.png')
                  "
                  @click="zoomIn($event)"
                />
              </div>
            </div>
          </div>
          <div v-if="targetKlipper"  class="container">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-8">
                <ol>
                  <li>{{ $t("SSH to the Raspberry Pi your Klipper runs on.") }}</li>
                  <li>
                    <div>{{ $t("Run:") }}</div>
<pre class="mt-2">
cd ~
git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
cd moonraker-obico
./install.sh
                  </pre
                    >
                  </li>
                  <li>{{ $t("Follow the installation steps.") }}</li>
                </ol>
              </div>
            </div>
          </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12 col-lg-6 p-4">
            <b-button
              variant="primary"
              @click="goForward"
            >
              {{ $t("Next") }}
            </b-button>
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
  computed: {
    targetOctoPrint() {
      return this.$route.params.targetPlatform === 'octoprint'
    },
    targetKlipper() {
      return this.$route.params.targetPlatform === 'moonraker'
    },
  },
  methods: {
    goForward() {
      this.$router.push({
        path: `/printers/wizard/link/${$route.params.targetPlatform}/`,
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
