<template>
  <widget-template v-if="isPluginCompatible">
    <template #title>Printer Terminal</template>
    <template #content>
      <div class="actionWrap">
        <a :href="`/printers/${printer.id}/terminal/`">
          <div class="actionBtn">
            <i class="fas fa-expand actionIcon"></i>
          </div>
        </a>
        <div class="actionBtn" @click="clearFeed">
          <i class="fas fa-trash actionIcon"></i>
        </div>
        <b-dropdown
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
                @click.native.capture.stop.prevent="hideTempMessages = !hideTempMessages"
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
                @click.native.capture.stop.prevent="hideSDMessages = !hideSDMessages"
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
            </div>
          </div>
        </b-dropdown>
      </div>
      <div class="wrapper">
        <div class="feedWrap" colorScheme="background">
          <div v-for="(feed, index) in terminalFeedArray" :key="index" class="itemWrap">
            <div v-if="feed?.msg" class="terminalText">
              <p class="messageTimeStamp messageText">
                {{ feed.normalTimeStamp }}
              </p>
              <p class="messageText">
                {{ feed.msg }}
              </p>
            </div>
            <div class="divider"></div>
          </div>
        </div>
        <div class="inputWrap">
          <input v-model="inputValue" type="text" class="textInput" placeholder="Enter code..." />
          <b-button variant="outline-primary" class="sendBtn" @click="sendMessage"> Send </b-button>
        </div>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import moment from 'moment'

export default {
  name: 'TerminalWidget',

  components: {
    WidgetTemplate,
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
      terminalFeedArray: [],
      inputValue: '',
      hideTempMessages: false,
      hideSDMessages: false,
    }
  },

  computed: {
    isPluginCompatible() {
      return this.printer.isTerminalCompatible() && !this.printer.isAgentMoonraker()
    },
  },

  watch: {
    'printer.terminal_feed': {
      handler(newTerminalFeed, oldTerminalFeed) {
        const sameMsg = newTerminalFeed?.msg === oldTerminalFeed?.msg
        const same_ts = newTerminalFeed?._ts === oldTerminalFeed?._ts
        const newMsg = newTerminalFeed?.msg

        const temperatureRegex =
          /.*[TB]:\d+(\.\d+)?\/\s*\d+(\.\d+)?\s*[TB]:\d+(\.\d+)?\/\s*\d+(\.\d+)?\s*@:\d+.*/g
        const SDRegex = /Not SD printing/
        const bRegex = /^B:\d+(\.\d+)?$/
        const tRegex = /^T:\d+(\.\d+)?$/

        if (this.hideSDMessages && SDRegex.test(newMsg)) return
        if (
          this.hideTempMessages &&
          (temperatureRegex.test(newMsg) || bRegex.test(newMsg) || tRegex.test(newMsg))
        ) {
          return
        }

        if (!sameMsg && !same_ts) {
          newTerminalFeed.normalTimeStamp = moment().format('h:mma')
          this.terminalFeedArray.unshift(newTerminalFeed)
        }
      },
      immediate: true, // Trigger the watcher immediately when the component is created
    },
  },

  updated() {},

  methods: {
    sendMessage() {
      if (!this.inputValue.length) return
      const newString = this.inputValue.toUpperCase()

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
        if (err || ret?.error) {
          this.$swal.Toast.fire({
            icon: 'error',
            title: ret.error,
          })
        }
      })
      this.inputValue = ''
    },
    clearFeed() {
      this.terminalFeedArray = []
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem
  height: 300px
  position: relative

.feedWrap
  display: flex
  flex-direction: column
  align-items: flex-start
  width: 100%
  height: 250px
  overflow-y: auto
  background-color: var(--color-background)
  border-radius: var(--border-radius-md)
  padding: 10px

.feedWrap::-webkit-scrollbar
  background-color: var(--color-background)
  border-radius: var(--border-radius-md)

.feedWrap::-webkit-scrollbar-thumb
  background-color: var(--color-surface-primary)
  border-radius:  var(--border-radius-md)

.terminalText
  display: flex
  align-items: center
  flex-direction: row

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
  position: absolute
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

.messageTimeStamp
  opacity: 0.8
  margin-right: 10px
  font-size: 0.7rem
.divider
  width: 100%
  background-color: var(--color-divider)
  height: 1px

.itemWrap
  display: flex
  flex-direction: column
  width: 100%
.messageText
  margin-top: 7px
  margin-bottom: 7px
</style>
