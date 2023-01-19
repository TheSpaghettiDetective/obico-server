import PrinterComm from '@src/lib/printer_comm'
import urls from '@config/server-urls'
import axios from 'axios'
import get from 'lodash/get'

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

  const printerComm = PrinterComm(
    printerId,
    urls.printerWebSocket(printerId),
    (data) => {},
    (printerStatus) => {}
  )

  printerComm.connect(() => {
    let passThruProps
    if (isCloud) {
      passThruProps = {
        func: 'download',
        target: 'file_downloader',
        args: [gcode],
      }
    } else if (isAgentMoonraker) {
      passThruProps = {
        func: 'printer/print/start',
        target: 'moonraker_api',
        kwargs: {
          verb: 'post',
          filename: gcode.path,
        },
      }
    } else {
      passThruProps = {
        func: 'select_file',
        target: '_printer',
        args: [`${gcode.path}`, null],
        kwargs: { printAfterSelect: 'true' },
      }
    }

    printerComm.passThruToPrinter(passThruProps, (err, ret) => {
      if (err || ret?.error) {
        Swal.Toast.fire({
          icon: 'error',
          title: err ? err : ret.error,
        })
        return
      }

      onCommandSent && onCommandSent()

      Swal.Prompt.fire({
        html: `
            <div class="text-center">
              <i class="fas fa-spinner fa-spin fa-lg py-3"></i>
              <h5 class="pt-3">
                Starting the print...
              </h5>
            </div>
          `,
        showConfirmButton: false,
      })

      const checkPrinterStatus = async () => {
        let printer
        try {
          printer = await axios.get(urls.printer(printerId))
          printer = printer.data
        } catch (e) {
          console.error(e)
          return
        }

        if (get(printer, 'status.state.text') === 'Operational') {
          setTimeout(checkPrinterStatus, 1000)
        } else {
          Swal.close()
          onPrinterStatusChanged && onPrinterStatusChanged()
        }
      }

      checkPrinterStatus()
    })
  })
}

const REDIRECT_TIMER = 3000
export const showRedirectModal = (Swal, onClose) => {
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
      window.location.assign('/printers/')
    } else {
      onClose && onClose()
    }
  })
}
