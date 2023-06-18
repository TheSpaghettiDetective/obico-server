import moment from 'moment'

export default {
  data() {
    return {
      oldTerminalFeed: null,
      terminalFeedArray: [],
      inputValue: '',
      hideTempMessages: false,
      hideSDMessages: false,
    }
  },

  methods: {
    onNextTerminalFeed(newTerminalFeed) {
      const sameMsg = newTerminalFeed?.msg === this.oldTerminalFeed?.msg
      const same_ts = newTerminalFeed?._ts === this.oldTerminalFeed?._ts
      const newMsg = newTerminalFeed?.msg

      this.oldTerminalFeed = newTerminalFeed

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
  },
}
