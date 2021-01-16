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
      <b-row class="text-center">
        <div class="helper col mx-auto pt-2">*Need help? Check out the step-by-step <a href="#">set up guide</a></div>
      </b-row>
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
      <b-row class="text-center">
        <div class="helper col mx-auto pt-2">*Need help? Check out the step-by-step <a href="#">set up guide</a></div>
      </b-row>
    </div>
    <div v-else class="container">
      <div class="col"></div>
      <div class="d-flex flex-column col">
        <b-row class="pt-3 text-center">
          <div class="mx-auto title pb-3">Printer Preferences</div>
        </b-row>
        <b-row class="pt-2">
          <b-button variant="primary" class="mx-auto py-3 btn">Let's Go!</b-button>
        </b-row>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import urls from '@lib/server_urls'

import { BButton } from 'bootstrap-vue'

export default {
  components: {
    BButton
  },
  data() {
    return {
      setupStage: 'install',
      verificationCode: '',
      currentTime: Date.now(),
      expiryMoment: null,
      url: urls.verificationCode(),
      counter: 0
    }
  },
  computed: {
    validityHours() {
      if (this.expiryMoment) {
        return `0${Math.floor((this.expiryMoment - this.currentTime) / 3600000)}`.slice(-2)
      } 
      return '-'
    },
    validityMins() {
      if (this.expiryMoment) {
        return `0${(Math.floor((this.expiryMoment - this.currentTime) / 60000) % 60)}`.slice(-2)
      }
      return '-'
    }
  },
  created() {
    setInterval(() => {
      this.currentTime = Date.now()
    }, 5000)
  },
  mounted() {
    this.getStage()
    this.getVerificationCode()
    this.codeInterval = setInterval(() => {
      this.getVerificationCode()
    }, 5000)  
  },
  methods: {
    getStage() {
      const params = new URLSearchParams(window.location.search)
      const stage = params.get('setup')
      if (stage) {
        this.setupStage = stage
      }
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
    },
    getVerificationCode() {
      if (this.setupStage === 'link') {
        axios
        .get(this.url)
        .then((resp) => {
          if (resp.data) {
            this.verificationCode = resp.data.code
            const expiryTime = resp.data.expired_at.replace(/-|:/g, '')
            this.expiryMoment = moment(expiryTime).format('x')
            console.log(resp.data)
            if (this.currentTime > this.expiryMoment) {
              this.url += `${resp.data.id}`
            }
            this.counter += 1
            if (this.counter === 5) {
              clearInterval(this.codeInterval)
              this.setupStage = 'preferences'
            }
            // if (resp.data.printer) {
            //   clearInterval(this.codeInterval)
            //   this.setupStage = 'preferences'
            // }
          }
        })
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
  font-size: 1rem
  line-height: 1.2rem
  font-weight: 400

.helper
  font-size: 0.8rem
  font-weight: 400
  max-width: 200px
</style>
