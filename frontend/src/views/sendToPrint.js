import PrinterComm from '@src/lib/printer_comm'
import urls from '@config/server-urls'
import axios from 'axios'
import get from 'lodash/get'

export const sendToPrint = (printerId, printerName, gcode, Swal, {onCommandSent, onPrinterStatusChanged}) => {
  const printerComm = PrinterComm(
    printerId,
    urls.printerWebSocket(printerId),
    (data) => {},
    (printerStatus) => {}
  )

  printerComm.connect(() => {
    printerComm.passThruToPrinter(
      {
        func: 'download',
        target: 'file_downloader',
        args: [gcode]
      },
      (err, ret) => {
        if (err || ret.error) {
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
              <h5 class="py-3">
                Uploading G-Code to ${printerName} ...
              </h5>
              <p>
                ${ret.target_path}
              </p>
            </div>
          `,
          showConfirmButton: false,
        })

        let checkPrinterStatus = async () => {
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
