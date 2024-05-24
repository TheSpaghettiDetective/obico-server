<template>
  <div>
    <div v-if="!isPro && usageFetched" class="floating-panel">
      <div
        v-if="showDetails"
        @click="showDetails = false"
        @mouseover="showDetails = true"
        @mouseleave="showDetails = false"
      >
        <div class="text-muted">
          <i18next :translation="$t('Monthly data usage ({localizedDom})')">
            <template #localizedDom>
              <a :href="getDocUrl('/user-guides/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users')" target="_blank">{{$t("Resets in {daysUntilReset} days",{daysUntilReset})}}</a>
            </template>
          </i18next>
        </div>
        <div :class="usageClass">{{ $t("Used {usageMTD} of {humanizedUsageCap}.",{usageMTD,humanizedUsageCap}) }}</div>
        <div v-if="overage">
          {{$t("Your month-to-date tunnel data usage is over the Free plan limit.")}}
          <a type="button" class="btn btn-sm btn-primary" href="/ent_pub/pricing/"
            >{{ $t("Get Unlimited Tunnel Data") }}</a
          >
        </div>
      </div>
      <div
        v-else
        :class="usageClass"
        @click="showDetails = true"
        @mouseover="showDetails = true"
        @mouseleave="showDetails = false"
      >
        {{ percentage }}%
      </div>
    </div>
    <div>
      <iframe v-if="printerId" :src="iframeUrl() + '#temp'" class="tunnel-iframe"></iframe>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'
import split from 'lodash/split'
import filesize from 'filesize'
import urls from '@config/server-urls'
import { user } from '@src/lib/page-context'
import { isLocalStorageSupported } from '@static/js/utils'

export default {
  name: 'OctoPrintTunnelPage',

  components: {},

  props: {},
  data: function () {
    return {
      bytesMTD: null,
      usageCap: null,
      usageFetched: false,
      isPro: true,
      printerId: null,
      showDetails: false,
    }
  },

  computed: {
    usageClass() {
      return {
        'text-success': this.bytesMTD < this.usageCap * 0.8,
        'text-warning': this.bytesMTD >= this.usageCap * 0.8 && this.bytesMTD < this.usageCap,
        'text-danger': this.bytesMTD >= this.usageCap,
      }
    },
    usageMTD() {
      return filesize(this.bytesMTD)
    },
    humanizedUsageCap() {
      return filesize(this.usageCap)
    },
    overage() {
      return this.bytesMTD >= this.usageCap
    },
    percentage() {
      return Math.round((this.bytesMTD / this.usageCap) * 100)
    },
    daysUntilReset() {
      const endOfMonth = moment().endOf('month')
      return endOfMonth.diff(moment(), 'days') + 1
    },
  },

  created() {
    this.isPro = user().is_pro
    this.printerId = split(window.location.pathname, '/').slice(-2, -1).pop()
  },

  mounted() {
    const skipWarning = isLocalStorageSupported()
      ? localStorage.getItem('skip-tunneling-warning')
      : null
    if (skipWarning !== 'yes') {
      this.$swal.Prompt.fire(
        {
          html: `
          <h4 class="text-center p-2">
            <svg class="menu-icon" style="height: 1.1em; width: 1em; margin-right: 0.75em;">
              <use href="#svg-tunnel" />
            </svg>
            ${this.$i18next.t("OctoPrint/Klipper Secure Tunnel")}
          </h4>
          <div class="p-1">
            ${this.$i18next.t("It may take long time for OctoPrint/Mainsail/Fluidd page to load as it is securely tunneled via the {brandName} app server.",{brandName:this.$syndicateText.brandName})}
          </div>
          <div class="p-1">
            <a target="_blank" href="${getDocUrl('/user-guides/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users')}">
            ${this.$i18next.t("Learn more about OctoPrint/Klipper tunnel's security and page load speed.")}
            <i class="fas fa-external-link-alt"></i>
          </a>
        </div>
        `,
          input: 'checkbox',
          inputPlaceholder: `${this.$i18next.t("Don't show again")}`,
        },
        'octoprint-tunnel.warning'
      ).then((result) => {
        if (result.isConfirmed) {
          if (result.value && isLocalStorageSupported()) {
            localStorage.setItem('skip-tunneling-warning', 'yes')
          }
        }
      })

      // Scale up popup on mobiles, otherwise it's too small (because of disabled meta viewport tag)
      if (window.matchMedia('(pointer:none), (pointer:coarse)')) {
        document.querySelector('.swal2-popup').classList.add('x150')
      }
    }

    const self = this
    const fetchUsage = (firstFetch = false) => {
      axios.get(urls.tunnelUsage()).then((resp) => {
        self.bytesMTD = resp.data.total
        self.usageCap = resp.data.monthly_cap
        if (firstFetch) {
          self.usageFetched = true
        }
      })
    }
    setInterval(fetchUsage, 15 * 1000)
    setTimeout(() => {
      fetchUsage(true)
    }, 4000)
  },

  methods: {
    iframeUrl() {
      return `/octoprint/${this.printerId}/`
    },
  },
}
</script>

<style lang="sass" scoped>
.tunnel-iframe
    width: 100%
    height: 100vh
    background: var(--color-background)
    position: absolute
    top: 0
    left: 0

.floating-panel
  position: fixed
  bottom: 0px
  right: 0px
  box-shadow: 2px 2px 10px rgba(0,0,0,.3)
  background-color: var(--color-surface-primary)
  padding: 10px
  max-width: 300px
  z-index: 10
  display: flex
  align-items: center
</style>

<style lang="sass">
@media (pointer:none), (pointer:coarse)
  .swal2-popup.x150
    transform: scale(1.5)
  .floating-panel
    transform: scale(2)
    transform-origin: right bottom
</style>
