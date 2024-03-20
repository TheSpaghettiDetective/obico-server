<template>
  <div :class="['wrapper', { 'full-screen-height': fullScreenHeight }]">
    <div class="actionWrap">
      <a v-if="showFullScreenOpt" :href="`/printers/${printer.id}/terminal/`">
        <b-button :disabled="!feedIsOn" class="actionBtn">
          <i class="fas fa-expand actionIcon"></i>
        </b-button>
      </a>
      <b-button v-if="canToggleFeed" class="actionBtn" @click="toggleTerminalPower">
        <b-spinner v-if="feedIsOn === null" small />
        <i v-else :class="['fas', 'fa-power-off', 'actionIcon', { 'text-primary': !feedIsOn }]"></i>
      </b-button>
      <b-button :disabled="!feedIsOn" class="actionBtn" @click="clearFeed">
        <i class="fas fa-trash actionIcon"></i>
      </b-button>
      <b-dropdown
        :disabled="!feedIsOn"
        right
        no-caret
        class="actionBtnNoP"
        toggle-class="action-btn icon-btn"
        menu-class="scrollable"
        title="Filter"
      >
        <template #button-content>
          <i class="fas fa-filter"></i>
        </template>
        <div>
          <div>
            <b-dropdown-text class="small text-secondary">{{ $t("Filter") }}</b-dropdown-text>
            <b-dropdown-item
              @click.native.capture.stop.prevent="
                updateFilterPrefs('temperature', !hideTempMessages)
              "
            >
              <div class="dropdown-text-group">
                <i
                  class="fas fa-check text-primary"
                  :style="{ visibility: hideTempMessages ? 'visible' : 'hidden' }"
                ></i>
                <div class="filterItemH">
                  <i class="fas fa-fire"></i>
                  <div class="text">{{ $t("Suppress Temperature") }}</div>
                </div>
              </div>
            </b-dropdown-item>
            <b-dropdown-item
              @click.native.capture.stop.prevent="updateFilterPrefs('sd', !hideSDMessages)"
            >
              <div class="dropdown-text-group">
                <i
                  class="fas fa-check text-primary"
                  :style="{ visibility: hideSDMessages ? 'visible' : 'hidden' }"
                ></i>
                <div class="filterItemH">
                  <i class="fas fa-sd-card"></i>
                  <div class="text">{{ $t("Suppress SD Status Messages") }}</div>
                </div>
              </div>
            </b-dropdown-item>
            <b-dropdown-item
              @click.native.capture.stop.prevent="updateFilterPrefs('gcode', !hideGCodeMessages)"
            >
              <div class="dropdown-text-group">
                <i
                  class="fas fa-check text-primary"
                  :style="{ visibility: hideGCodeMessages ? 'visible' : 'hidden' }"
                ></i>
                <div class="filterItemH">
                  <i class="fas fa-code"></i>
                  <div class="text">{{ $t("Suppress Position Messages") }}</div>
                </div>
              </div>
            </b-dropdown-item>
            <b-dropdown-item
              @click.native.capture.stop.prevent="updateFilterPrefs('ok', !hideOKMessages)"
            >
              <div class="dropdown-text-group">
                <i
                  class="fas fa-check text-primary"
                  :style="{ visibility: hideOKMessages ? 'visible' : 'hidden' }"
                ></i>
                <div class="filterItemH">
                  <i class="fas fa-thumbs-up"></i>
                  <div class="text">{{ $t("Suppress 'OK' Messages") }}</div>
                </div>
              </div>
            </b-dropdown-item>
          </div>
        </div>
      </b-dropdown>
    </div>
    <terminal-feed-view
      class="feedWrap"
      :terminal-feed-array="terminalFeedArray"
      :feed-is-on="feedIsOn"
    />
    <div class="inputWrap">
      <input
        :disabled="!feedIsOn"
        v-model="inputValue"
        type="text"
        class="textInput"
        :placeholder="$t('Enter code...')"
        @keyup.enter="sendMessage"
      />
      <b-button
        :disabled="!feedIsOn"
        variant="outline-primary"
        class="sendBtn"
        @click="sendMessage"
      >
        <i class="fas fa-chevron-right text-primary-icon"></i>
      </b-button>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import TerminalFeedView from '@src/components/terminal/TerminalFeedView'

export default {
  name: 'PrinterTerminal',

  components: {
    TerminalFeedView,
  },

  props: {
    printer: {
      type: Object,
      required: true,
    },
    printerComm: {
      type: Object,
      required: true,
    },
    fullScreenHeight: {
      type: Boolean,
      required: false,
      default: false,
    },
    showFullScreenOpt: {
      type: Boolean,
      required: true,
      default: true,
    },
  },

  data() {
    return {
      oldTerminalFeed: null,
      terminalFeedArray: [],
      inputValue: '',
      hideTempMessages: true,
      hideSDMessages: true,
      hideOKMessages: true,
      hideGCodeMessages: true,
      feedIsOn: true,
    }
  },

  computed: {
    canToggleFeed() {
      if (this.printer.isAgentMoonraker()) {
        return false
      }
      return this.printer.isAgentVersionGte('2.4.7', '0.0.0')
    },
  },

  created() {
    this.printerComm.onTerminalFeedReceived = this.onNextTerminalFeed
    this.terminalSetup()
  },

  mounted() {
    const hideTempPref = localStorage.getItem(`printer-terminal-filter-prefs-temperature`)
    const hideSDPref = localStorage.getItem(`printer-terminal-filter-prefs-sd`)
    const hideOKPref = localStorage.getItem(`printer-terminal-filter-prefs-ok`)
    const hideGCodePref = localStorage.getItem(`printer-terminal-filter-prefs-gcode`)
    if (hideTempPref) {
      this.hideTempMessages = JSON.parse(hideTempPref)
    }
    if (hideSDPref) {
      this.hideSDMessages = JSON.parse(hideSDPref)
    }
    if (hideGCodePref) {
      this.hideGCodeMessages = JSON.parse(hideGCodePref)
    }
    if (hideOKPref) {
      this.hideOKMessages = JSON.parse(hideOKPref)
    }
  },

  methods: {
    onNextTerminalFeed(newTerminalFeed) {
      const sameMsg = newTerminalFeed?.msg === this.oldTerminalFeed?.msg
      const same_ts = newTerminalFeed?._ts === this.oldTerminalFeed?._ts
      const newMsg = newTerminalFeed?.msg

      this.oldTerminalFeed = newTerminalFeed
      const tempRegex = /((N\d+\s+)?M105)|((ok\s+([PBN]\d+\s+)*)?([BCLPR]|T\d*):-?\d+)/g
      const SDRegex = /((N\d+\s+)?M27)|(SD printing byte)|(Not SD printing)/g
      const gCodeRegex = /^G[0-3].*$/g

      if (this.hideSDMessages && SDRegex.test(newMsg)) return
      if (this.hideTempMessages && tempRegex.test(newMsg)) return
      if (this.hideGCodeMessages && gCodeRegex.test(newMsg)) return
      if (this.hideOKMessages && newMsg.toLowerCase().trim() === 'ok') return
      if (!sameMsg && !same_ts) {
        newTerminalFeed.normalTimeStamp = moment().format('h:mm:ssa')
        newTerminalFeed.msg = newMsg.trim() // remove unnecessary whitespace
        this.terminalFeedArray.unshift(newTerminalFeed)
      }
    },

    sendMessage() {
      if (!this.inputValue.length) return
      if (!this.feedIsOn) return
      const newString = this.inputValue.toUpperCase()

      if (this.printer.isAgentMoonraker()) {
        this.onNextTerminalFeed({ msg: newString, _ts: new Date() }) // Moonraker doesn't echo the gcodes user enters. Hence we need to insert them to the terminal
      }

      const moonrakerPayload = {
        func: 'printer/gcode/script',
        target: 'moonraker_api',
        kwargs: { script: `${newString}` },
      }
      const octoPayload = {
        func: 'commands',
        target: '_printer',
        args: [`${newString}`],
        force: true,
      }

      const payload = this.printer.isAgentMoonraker() ? moonrakerPayload : octoPayload
      this.printerComm.passThruToPrinter(payload, (err, ret) => {
        if (err) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: err,
          })
        }
      })
      this.inputValue = ''
    },
    clearFeed() {
      this.terminalFeedArray = []
    },
    updateFilterPrefs(str, val) {
      localStorage.setItem(`printer-terminal-filter-prefs-${str}`, JSON.stringify(val))
      if (str === 'temperature') {
        this.hideTempMessages = val
      } else if (str === 'gcode') {
        this.hideGCodeMessages = val
      } else if (str === 'ok') {
        this.hideOKMessages = val
      } else {
        this.hideSDMessages = val
      }
    },
    async terminalSetup() {
      if (!this.canToggleFeed) {
        this.feedIsOn = true
        return
      }

      this.printerComm.passThruToPrinter(
        {
          func: 'toggle_terminal_feed',
          target: 'gcode_hooks',
          args: ['get'],
        },
        (err, ret) => {
          this.feedIsOn = ret || false
        }
      )
    },

    async toggleTerminalPower() {
      const str = this.feedIsOn ? 'off' : 'on'
      this.feedIsOn = null
      this.clearFeed()
      this.printerComm.passThruToPrinter(
        {
          func: 'toggle_terminal_feed',
          target: 'gcode_hooks',
          args: [str],
        },
        (err, ret) => {
          this.feedIsOn = ret || false
        }
      )
    },
  },
}
</script>

<style lang="sass" scoped>

.full-screen-height
  height: calc(100vh - 50px - var(--gap-between-blocks))
  margin-bottom: -120px

.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem
  position: relative
  width: 100%

.feedWrap
  display: flex
  flex-direction: column
  flex: 1
  padding: 10px
  width: 100%
  background-color: var(--color-background)
  border: solid var(--color-surface-primary) 1px
.feedWrap::-webkit-scrollbar
  background-color: var(--color-background)
.feedWrap::-webkit-scrollbar-thumb
  background-color: var(--color-surface-primary)

.inputWrap
  display: flex
  flex-direction: row
  justify-content: space-between
  height: 50px
  width: 100%
  gap: 1rem

.textInput
  height: 100%
  flex: 1
  padding: 10px

.sendBtn
  height: 100%
  width: auto
  min-width: 60px
  border-radius: var(--border-radius-sm)
  background-color: var(--color-surface-primary)
  border: none

.actionBtn
  margin-left: 5px
  margin-right: 5px
  padding: 10px 16px
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-sm)
  border: none
  &:hover
    cursor: pointer

.actionBtnNoP
  margin-left: 5px
  margin-right: 5px
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-sm)
  z-index: 1
  &:hover
    cursor: pointer

.actionIcon
  width: 16px
  height: 16px
  color: var(--color-text-primary)

.text-primary-icon
  color: var(--color-text-primary)

.actionWrap
  display: flex
  flex-direction: row
  top: 0px
  right: 15px
  align-items: center
  justify-content: flex-end
  width: 100%
  padding: 10px 15px

.filterItemH
  display: flex
  flex-direction: row
  align-items: center
</style>
