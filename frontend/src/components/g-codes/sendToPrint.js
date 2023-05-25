import Vue from 'vue'
import axios from 'axios'
import get from 'lodash/get'
import { clearTransientState } from '@src/lib/printer-transient-state'

import { printerCommManager } from '@src/lib/printer-comm'
import {
  printPrinterLocalGCodeOctoPrint,
  printPrinterLocalGCodeMoonraker,
} from '@src/lib/printer-local-comm'
import urls from '@config/server-urls'

export const confirmPrint = (gcode, printer) => {
  return new Promise((resolve, reject) => {
    Vue.swal
      .fire({
        html: `<h5 style="text-align: center; line-height: 1.5;">Print "${gcode.filename}" on <b>${printer.name}</b>?</h5>`,
        imageUrl: gcode.getBigThumbnailUrl && gcode.getBigThumbnailUrl(),
        showCancelButton: true,
        confirmButtonText: 'Print!',
        cancelButtonText: 'Cancel',
        reverseButtons: true,
      })
      .then((result) => {
        if (result.value) {
          resolve()
        }
      })
  })
}

export function printCloudGCode(printerComm, gcode) {
  return new Promise((resolve, reject) => {
    printerComm.passThruToPrinter(
      {
        func: 'download',
        target: 'file_downloader',
        args: [gcode],
      },
      (err, ret) => {
        if (err || ret?.error) {
          reject(ret?.error || 'Something went wrong!')
        } else {
          resolve()
        }
      }
    )
  })
}

export const sendToPrint = (args) => {
  const {
    printerId,
    gcode,
    isCloud,
    Swal,
    onCommandSent,
    onPrinterStatusChanged,
    isAgentMoonraker = false,
  } = args

  const printerComm = printerCommManager.getOrCreatePrinterComm(
    printerId,
    urls.printerWebSocket(printerId),
    (data) => {},
    (printerStatus) => {}
  )

  printerComm.connect(() => {
    const printGCode = isCloud
      ? printCloudGCode
      : isAgentMoonraker
      ? printPrinterLocalGCodeMoonraker
      : printPrinterLocalGCodeOctoPrint

    printGCode(printerComm, gcode).catch((err) => {
      clearTransientState(printerId)
      Swal.Toast.fire({
        icon: 'error',
        title: err,
      })
    })
  })

  onCommandSent && onCommandSent()

  const checkPrinterStatus = async () => {
    let printer
    try {
      printer = await axios.get(urls.printer(printerId))
      printer = printer.data
    } catch (e) {
      console.error(e)
      return
    }

    if (
      get(printer, 'status.state.text') === 'Operational' ||
      get(printer, 'status.state.text') === 'Downloading G-Code'
    ) {
      setTimeout(checkPrinterStatus, 1000)
    } else {
      onPrinterStatusChanged && onPrinterStatusChanged()
    }
  }

  checkPrinterStatus()
}

const REDIRECT_TIMER = 3000
export const showRedirectModal = (Swal, onClose, printerId) => {
  let timerInterval
  Swal.Prompt.fire({
    html: `
      <div class="text-center">
        <h5 class="py-3">
          You'll be redirected to printers page in <strong>${Math.round(
            REDIRECT_TIMER / 1000
          )}</strong> seconds
        </h5>
      </div>
    `,
    timer: REDIRECT_TIMER,
    showConfirmButton: true,
    showCancelButton: true,
    confirmButtonText: 'Redirect now',
    onOpen: () => {
      timerInterval = setInterval(() => {
        Swal.getHtmlContainer().querySelector('strong').textContent = (
          Swal.getTimerLeft() / 1000
        ).toFixed(0)
      }, 1000)
    },
    onClose: () => {
      clearInterval(timerInterval)
      timerInterval = null
    },
  }).then((result) => {
    if (result.isConfirmed || result.dismiss === 'timer') {
      window.location.assign(`/printers/${printerId}/control/`)
    } else {
      onClose && onClose()
    }
  })
}
