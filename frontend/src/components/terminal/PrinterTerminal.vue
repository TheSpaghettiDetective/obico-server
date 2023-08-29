<template>
  <div class="fullHeight">
    <div class="actionWrap">
      <a :href="`/printers/${printer.id}/terminal/`">
        <b-button class="actionBtn">
          <i class="fas fa-expand actionIcon"></i>
        </b-button>
      </a>
      <b-button
        v-if="!isMoonraker && meetsPowerVersion"
        class="actionBtn"
        @click="toggleTerminalPower"
      >
        <b-spinner v-if="terminalPower === null" small />
        <i v-else class="fas fa-power-off actionIcon"></i>
      </b-button>
      <b-button class="actionBtn" @click="clearFeed">
        <i class="fas fa-trash actionIcon"></i>
      </b-button>
      <b-dropdown
        :disabled="!terminalPower"
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
            <b-dropdown-text class="small text-secondary">Filter</b-dropdown-text>
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
                  <div class="text">Suppress Temperature</div>
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
                  <div class="text">Suppress SD Status Messages</div>
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
                  <div class="text">Suppress Position Messages</div>
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
                  <div class="text">Suppress 'OK' Messages</div>
                </div>
              </div>
            </b-dropdown-item>
          </div>
        </div>
      </b-dropdown>
    </div>
    <div class="wrapper fullHeight">
      <terminal-feed-view
        class="feedWrap fullHeight"
        :terminal-feed-array="terminalFeedArray"
        :show-powered-off="!isMoonraker && meetsPowerVersion && terminalPower === false"
      />
      <div class="inputWrap">
        <input
          :disabled="!terminalPower"
          v-model="inputValue"
          type="text"
          class="textInput"
          placeholder="Enter code..."
          @keyup.enter="sendMessage"
        />
        <b-button
          :disabled="!terminalPower"
          variant="outline-primary"
          class="sendBtn"
          @click="sendMessage"
        >
          Send
        </b-button>
      </div>
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
      isMoonraker: null,
      terminalPower: null,
      meetsPowerVersion: false,
    }
  },

  watch: {
    printer: {
      handler(newValue, oldValue) {
        if (this.isMoonraker === null && newValue !== null) {
          this.terminalSetup()
        }
      },
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
      if (!this.isMoonraker && this.meetsPowerVersion && this.terminalPower === false) return
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
      this.isMoonraker = this.printer.isAgentMoonraker()
      this.meetsPowerVersion = this.printer.isAgentVersionGte('2.4.7', '0.0.0')
      if (this.isMoonraker) {
        this.terminalPower = true
      }

      if (!this.isMoonraker && this.meetsPowerVersion) {
        this.printerComm.passThruToPrinter(
          {
            func: 'toggle_terminal_feed',
            target: 'gcode_hooks',
            args: ['get'],
          },
          (err, ret) => {
            this.terminalPower = ret || false
          }
        )
      }
    },

    async toggleTerminalPower() {
      const str = this.terminalPower ? 'off' : 'on'
      this.terminalPower = null
      this.clearFeed()
      this.printerComm.passThruToPrinter(
        {
          func: 'toggle_terminal_feed',
          target: 'gcode_hooks',
          args: [str],
        },
        (err, ret) => {
          this.terminalPower = ret || false
        }
      )
    },
  },
}
</script>

<style lang="sass" scoped>

.fullHeight
  flex: 1
  display: flex
  flex-direction: column

.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem
  position: relative

.feedWrap
  padding: 10px
  width: 100%
  background-color: var(--color-background)
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
