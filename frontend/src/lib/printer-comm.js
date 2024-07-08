'use strict'
import assign from 'lodash/assign'
import Vue from 'vue'
import ifvisible from 'ifvisible'
import pako from 'pako'
import { toArrayBuffer } from '@src/lib/utils'
import { clearPrinterTransientState } from '@src/lib/printer-transient-state'
import i18n from '@src/i18n/i18n.js'

// PrinterCommManager is a singleton: https://www.sitepoint.com/javascript-design-patterns-singleton/
class PrinterCommManager {
  constructor() {
    if (!PrinterCommManager.instance) {
      this.printerCommMap = new Map()
      PrinterCommManager.instance = this
    }
    return PrinterCommManager.instance
  }

  setPrinterComm(printerId, printerComm) {
    this.printerCommMap.set(printerId, printerComm)
  }

  getPrinterComm(printerId) {
    return this.printerCommMap.get(printerId)
  }

  getOrCreatePrinterComm(...props) {
    const printerId = String(props[0]) // assuming same args as for PrinterComm function
    if (!this.getPrinterComm(printerId)) {
      this.setPrinterComm(printerId, PrinterComm(...props))
    }
    return this.getPrinterComm(printerId)
  }

  closeConnection(printerId) {
    const printerComm = this.getPrinterComm(printerId)
    if (printerComm) {
      printerComm.closeServerWebSocket()
      printerComm.webrtcConnections.forEach((webrtc) => {
        if (webrtc) webrtc.close();
      });
      this.printerCommMap.delete(printerId)
    }
  }

  closeAllConnections() {
    this.printerCommMap.forEach((_, token) => this.closeConnection(token))
  }
}

export const printerCommManager = new PrinterCommManager()
Object.freeze(printerCommManager)

export default function PrinterComm(printerId, wsUri, callbacks) {
  const self = { printerId, wsUri, ...callbacks }

  self.ws = null
  self.webrtcConnections = new Map(); // key: webcamName. Null if it's data channel-only WebRTC
  self.passthruQueue = new Map()

  ifvisible.on('blur', function () {
    self.closeWebSocket()
  })

  ifvisible.on('focus', function () {
    self.connect()
  })

  self.onPassThruReceived = function (msg) {
    const refId = msg.ref
    if (refId && self.passthruQueue.get(refId)) {
      const callback = self.passthruQueue.get(refId)
      self.passthruQueue.delete(refId)
      callback(msg.error, msg.ret)
    } else if ('terminal_feed' in msg) {
      self.onTerminalFeedReceived && self.onTerminalFeedReceived(msg.terminal_feed)
    } else if ('printer_event' in msg) {
      const printerEvent = msg.printer_event
      Vue.swal.Toast.fire({
        icon: printerEvent.event_class.toLowerCase(),
        title: printerEvent.event_title,
        html: printerEvent.event_text,
      }).then((result) => {
        if (result.isDismissed && result.dismiss === 'close') {
          // SWAL returns 'close' as the reason when user clicks on the toast
          window.location.href = '/printer_events/'
        }
      })
    }
  }

  self.connect = function (onOpenCallback = null) {
    if (self.ws && self.ws.readyState === WebSocket.OPEN) {
      onOpenCallback && onOpenCallback()
      return
    }

    self.ws = new WebSocket(
      window.location.protocol.replace('http', 'ws') + '//' + window.location.host + self.wsUri
    )
    self.ws.onmessage = function (e) {
      let msg = {}
      try {
        msg = JSON.parse(e.data)
      } catch (error) {
        console.log(e.data)
        throw error
      }
      if ('passthru' in msg) {
        self.onPassThruReceived(msg.passthru)
      } else {
        self.onPrinterUpdateReceived && self.onPrinterUpdateReceived(msg)
      }
    }

    if (onOpenCallback) {
      self.ws.onopen = onOpenCallback
    }

    self.ensureWebsocketClosed()
    setTimeout(function () {
      self.heartbeat()
    }, 30 * 1000)
  }

  self.setWebRTCConnection = function(webcamName, webrtc) {
    if (self.webrtcConnections.has(webcamName)) {
      console.log(`WARNING: Existing WebRTC connection for ${webcamName} in printerComm. Closing it.`);
      self.webrtcConnections.get(webcamName).close();
    }

    self.webrtcConnections.set(webcamName, webrtc);

    function parseJsonData(jsonData) {
      let msg = {}
      try {
        msg = JSON.parse(jsonData)
      } catch (error) {
        // Any garbage sent to the Janus UDP port will be forwarded here.
        return
      }

      if (msg && 'ref' in msg && 'ret' in msg) {
        self.onPassThruReceived(msg)
        return
      }

      self.onStatusReceived && self.onStatusReceived(msg)
    }


    const callbacksFuncs = {
      onDestroy: () => {
        if (self.webrtcConnections.get(webcamName) === webrtc) {  // only remove if it's the same object
          self.webrtcConnections.delete(webcamName);
        }
      },
    };

    if (webcamName === null) { // data channel-only WebRTC
      callbacksFuncs.onData = function (maybeBin) {
        if (typeof maybeBin === 'string' || maybeBin instanceof String) {
          parseJsonData(maybeBin)
        } else {
          toArrayBuffer(maybeBin, (arrayBuffer) => {
            parseJsonData(pako.ungzip(new Uint8Array(arrayBuffer), { to: 'string' }))
          })
        }
      }
    }

    self.webrtcConnections.get(webcamName).setCallbacks(callbacksFuncs);
  };

  self.passThruToPrinter = function (msg, callback) {
    if (self.canSend()) {
      var refId = Math.random().toString()
      assign(msg, { ref: refId })
      if (callback) {
        self.passthruQueue.set(refId, callback)
        setTimeout(function () {
          if (self.passthruQueue.has(refId)) {
            clearPrinterTransientState(self.printerId)
            Vue.swal.Toast.fire({
              icon: 'error',
              title: `${i18n.t('Failed to contact printer. Is it powered on and connected to Internet?')}`,
            })
          }
        }, 60 * 1000)
      }

      const dataChannelWebrtc = self.webrtcConnections.get(null); // key == null -> data channel-only WebRTC
      if (dataChannelWebrtc) {
        dataChannelWebrtc.sendData(JSON.stringify(msg))
      }

      self.ws.send(JSON.stringify({ passthru: msg }))
    } else {
      if (callback) {
        clearPrinterTransientState(self.printerId)
        callback('Message not passed through. No suitable WebSocket.')
      }
    }
  }

  // Helper methods

  self.ensureWebsocketClosed = function () {
    self.ws.onclose = function (ev) {
      if (self.ws === ev.target) {
        self.ws = null
      }
    }
    self.ws.onerror = function () {
      if (self.ws) {
        self.ws.close()
      }
    }
  }

  self.closeWebSocket = function () {
    if (self.ws) {
      self.ws.close()
    }
  }

  // Heartbeat to maintain the presence of connection
  // Adapted from https://stackoverflow.com/questions/50876766/how-to-implement-ping-pong-request-for-websocket-connection-alive-in-javascript

  self.heartbeat = function () {
    if (!self.canSend()) {
      return
    }
    self.ws.send(JSON.stringify({}))
    setTimeout(function () {
      self.heartbeat()
    }, 30 * 1000)
  }

  self.canSend = function () {
    return self.ws && self.ws.readyState === 1
  }

  return self
}
