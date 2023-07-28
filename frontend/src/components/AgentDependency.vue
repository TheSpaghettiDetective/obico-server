<template>
  <div>
    <h3>The following packages are required:</h3>
    <ol>
      <li>Janus (>=0.8.2)</li>
    </ol>
    <h3>Enter your sudo password to install the required packages:</h3>
    <input v-model="sudoPassword" type="password" @keyup.enter="install" />
    <br />
    <b-button :disabled="running" @click="install">{{
      hasRunIntoError ? 'Retry' : 'Install'
    }}</b-button>
    <div v-if="running">
      <b-spinner label="Installing..."></b-spinner>
      <div>Installing...</div>
    </div>
    <div v-if="hasRunIntoError">
      <h3 class="text-danger">Failed to install the required packages.</h3>
      <pre>{{ error }}</pre>
    </div>
    <div v-if="result">
      <pre v-if="result.stdout">{{ result.stdout }}</pre>
      <pre v-if="result.stderr">{{ result.stderr }}</pre>
    </div>
    <div v-if="result && !hasRunIntoError">
      <b-button @click="done">Continue To Webcam Setup</b-button>
    </div>
  </div>
</template>

<script>
import { installSystemDependency } from '@src/lib/printer-passthru'

export default {
  name: 'AgentDependency',

  props: {
    printerComm: {
      type: Object,
      required: true,
    },
  },

  data: function () {
    return {
      sudoPassword: null,
      running: false,
      error: null,
      result: null,
    }
  },

  computed: {
    hasRunIntoError() {
      return this.error !== null || (this.result !== null && this.result?.returncode !== 0)
    },
  },

  methods: {
    install() {
      this.running = true
      installSystemDependency(this.printerComm, this.sudoPassword, ['janus'])
        .then((ret) => (this.result = ret))
        .catch((e) => (this.error = e))
        .finally(() => (this.running = false))
    },
    done() {
      this.$emit('done')
    },
  },
}
</script>

<style lang="sass" scoped>
.card-img-overlay
  display: flex
  align-items: center
  justify-content: center
</style>
