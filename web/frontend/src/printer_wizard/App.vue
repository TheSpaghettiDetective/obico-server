<template>
  <div>
    <div v-if="setupStage === 'install'" class="container">
      <div class="col"></div>
      <div class="d-flex flex-column col">
        <b-row class="pt-3 text-center">
          <div class="mx-auto title pb-3">Install TSD Plugin in the Octoprint Store</div>
        </b-row>
        <b-row class="pb-3 d-flex justify-content-center">
          <img :src="require('@static/img/TSDInstallScreenshot.png')">
        </b-row>
        <b-row class="text-center">
          <div class="mx-auto content">Octoprint Settings menu > Plugin Manager > Install new Plugins</div>
        </b-row>
        <b-row class="pb-3 text-center">
          <div class="mx-auto content">After installing, Octoprint will restart (this may take a few minutes)</div>
        </b-row>
        <b-row class="pt-2">
          <b-button @click="toLinkStage" variant="primary" class="mx-auto py-3 btn">Next</b-button>
        </b-row>
      </div>
      <div class="helper col ml-auto">*Need help? Check out the step by step <a href="#">set up guide</a></div>
    </div>
    <div v-else-if="setupStage === 'link'" class="container">
      <div class="col"></div>
      <div class="d-flex flex-column col">
        <b-row class="pt-3 text-center">
          <div class="mx-auto title pb-2">Link Your Printer</div>
        </b-row>
        <b-row class="pt-1 text-center">
          <div class="mx-auto subtitle pb-3">Copy the 6-Digit verification Code</div>
        </b-row>
        <b-row class="d-flex justify-content-center">
          <div class="px-1">
            <input disabled ref="code" class="special-btn code-btn" :value="`${verificationCode}`"/>
          </div>
          <div class="px-1">
            <b-button class="special-btn copy-btn" @click="copy" variant="primary">Copy</b-button>
          </div>
        </b-row>
        <b-row class="pt-1 text-center">
          <div class="mx-auto pb-3">{{ `*This code will expire in ${validityHours} hrs ${validityMins} mins` }}</div>
        </b-row>
        <b-row class="pt-1 d-flex flex-column">
          <div class="mx-auto subtitle">Enter the 6-Digit verification Code in the Plugin</div>
          <div class="helper mx-auto pb-1" style="max-width: 220px;">Can't find where to enter the code?<span class="px-1" v-b-tooltip.hover.right="{ variant: 'primary' }" title="You need the latest version of TSD plugin">ⓘ</span></div>
        </b-row>
        <b-row class="pb-3 d-flex justify-content-center">
          <img :src="require('@static/img/TSDVerificationScreenshot.png')">
        </b-row>
      </div>
      <div class="helper col ml-auto">*Need help? Check out the step by step <a href="#">set up guide</a></div>
    </div>
  </div>
</template>

<script>
import { BButton } from 'bootstrap-vue'

export default {
  components: {
    BButton
  },
  data() {
    return {
      setupStage: 'install',
      verificationCode: 313894,
      validityTime: 3600000
    }
  },
  computed: {
    validityHours() {
      return `0${Math.floor(this.validityTime / 3600000)}`.slice(-2)
    },
    validityMins() {
      return `0${(Math.floor(this.validityTime / 60000) % 60)}`.slice(-2)
    }
  },
  created() {
    setInterval(() => {
      this.validityTime -= 5000
      console.log(this.validityTime)
    }, 5000)
  },
  mounted() {
    this.getStage()
  },
  methods: {
    getStage() {
      const params = new URLSearchParams(window.location.search)
      const stage = params.get('setup') 
      this.setupStage = stage
      console.log('Stage Set!')
    },
    toLinkStage() {
      this.setupStage = 'link'
    },
    copy() {
      const codeButton = this.$refs.code
      console.log(codeButton.value)
      codeButton.focus()
      codeButton.select()
      try {
        const successful = document.execCommand('copy')
        const msg = successful ? 'successful' : 'unsuccessful'
        console.log('Fallback: Copying text command was ' + msg)
      } catch (err) {
        console.error('Fallback: Oops, unable to copy', err)
      }
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

img
  width: 30vw
  min-width: 360px

.spacer
 width: 200px

.title
  font-size: 2.5rem
  font-weight: 800

.subtitle
  font-size: 1.5rem
  font-weight: 500

.btn
  width: 220px
  height: 60px
  font-size: 1.3rem
  line-height: 1.3rem

.special-btn
  border-radius: 10px

.code-btn
  text-align: center
  width: 220px
  height: 60px
  background-color: black
  border: black
  color: white
  font-size: 2rem
  font-weight: 500
  letter-spacing: 2px

.copy-btn
  width: 90px

.content
  font-size: 1.2rem
  font-weight: 400

.helper
  font-size: 0.8rem
  font-weight: 400
  max-width: 200px
</style>
