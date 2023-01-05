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
    onPrinterStatusChanged
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
        args: [gcode]
      }
    } else {
      passThruProps = {
        func: 'select_file',
        target: '_printer',
        args: [ `${gcode.path}`, null ],
        kwargs: { printAfterSelect: 'true' }
      }
    }

    printerComm.passThruToPrinter(
      passThruProps,
      (err, ret) => {
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
      }
    )
  })
}

export const getPrinterPrintAvailability = (normalizedPrinter) => {
  if (!normalizedPrinter.isOffline() && !normalizedPrinter.isDisconnected() && !normalizedPrinter.isActive()) {
    return {
      key: 'ready',
      text: 'Ready',
    }
  } else {
    return {
      key: 'unavailable',
      text: 'Unavailable',
    }
  }
}
