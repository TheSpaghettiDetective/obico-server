import moment from 'moment'

export default {
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
