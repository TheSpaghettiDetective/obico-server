import Vue from 'vue'
import axios from 'axios'
import get from 'lodash/get'
import { clearPrinterTransientState } from '@src/lib/printer-transient-state'

import { printerCommManager } from '@src/lib/printer-comm'
import {
  printPrinterLocalGCodeOctoPrint,
  printPrinterLocalGCodeMoonraker,
} from '@src/lib/printer-local-comm'
import urls from '@config/server-urls'
import { repeatPrinterLocalGCode } from '../../lib/printer-local-comm'
import i18n from "@src/i18n/i18n.js"

export const confirmPrint = (gcode, printer) => {
  return new Promise((resolve, reject) => {
    Vue.swal
      .fire({
        html: `<h5 style="text-align: center; line-height: 1.5;">${i18n.t("Print")} "${gcode.filename}" on <b>${printer.name}</b>?</h5>`,
        imageUrl: gcode.getBigThumbnailUrl && gcode.getBigThumbnailUrl(),
        showCancelButton: true,
        confirmButtonText: `${i18n.t('Print!')}`,
        cancelButtonText: `${i18n.t('Cancel')}`,
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
        args: [
          {
            id: gcode.id,
            url: gcode.url,
            filename: gcode.filename,
            safe_filename: gcode.safe_filename,
          },
        ],
      },
      (err, ret) => {
        if (err) {
          reject(err)
        } else {
          resolve()
        }
      }
    )
  })
}

export const sendToPrint = (args) => {
  const { printer, gcode, isCloud, Swal, onCommandSent, onPrinterStatusChanged } = args

  const printerId = printer.id
  const isAgentMoonraker = printer.isAgentMoonraker()

  const printerComm = printerCommManager.getOrCreatePrinterComm(
    printerId,
    urls.printerWebSocket(printerId)
  )

  printerComm.connect(() => {
    const printGCode = isCloud
      ? printCloudGCode
      : !gcode.path
      ? repeatPrinterLocalGCode
      : isAgentMoonraker
      ? printPrinterLocalGCodeMoonraker
      : printPrinterLocalGCodeOctoPrint

    printer.setTransientState(isCloud ? 'G-Code Downloading' : 'Starting')
    printGCode(printerComm, gcode).catch((err) => {
      clearPrinterTransientState(printerId)
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
      get(printer, 'status.state.text') === 'G-Code Downloading' ||
      get(printer, 'status.state.text') === 'Downloading G-Code' // Backward compatibility with OctoPrint-Obico 2.3.7 - 2.3.9
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
          ${i18n.t("You'll be redirected to printers page in")} <strong>${Math.round(
            REDIRECT_TIMER / 1000
          )}</strong> ${i18n.t("seconds")}
        </h5>
      </div>
    `,
    timer: REDIRECT_TIMER,
    showConfirmButton: true,
    showCancelButton: true,
    confirmButtonText: 'Redirect now',
    onOpen: () => {
      timerInterval = setInterval(() => {
        const htmlContainer = Swal.getHtmlContainer()
        const timerElement = htmlContainer?.querySelector('strong')
        if (!htmlContainer || !timerElement) return
        timerElement.textContent = (Swal.getTimerLeft() / 1000).toFixed(0)
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
