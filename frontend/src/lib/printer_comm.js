'use strict'
import assign from 'lodash/assign'
import Vue from 'vue'
import ifvisible from 'ifvisible'
import pako from 'pako'

export default function PrinterComm(printerId, wsUri, onPrinterUpdateReceived, onStatusReceived=null) {
  var self = {}

  self.printerId = printerId
  self.wsUri = wsUri
  self.onPrinterUpdateReceived = onPrinterUpdateReceived
  self.onStatusReceived = onStatusReceived

  self.ws = null
  self.webrtc = null
  self.passthruQueue = new Map()

  ifvisible.on('blur', function(){
    self.closeWebSocket()
  })

  ifvisible.on('focus', function(){
    self.connect()
  })

  self.onPassThruReceived = function(msg) {
    const refId = msg.ref
    if (refId && self.passthruQueue.get(refId)) {
      const callback = self.passthruQueue.get(refId)
      self.passthruQueue.delete(refId)
      callback(null, msg.ret)
    }
  }

  self.connect = function() {
    self.ws = new WebSocket( window.location.protocol.replace('http', 'ws') + '//' + window.location.host + self.wsUri)
    self.ws.onmessage = function (e) {
      let msg = {}
      try {
        msg = JSON.parse(e.data)
      } catch (error) {
        console.log(e.data)
        throw(error)
      }
      if ('passthru' in msg) {
        self.onPassThruReceived(msg.passthru)
      } else {
        onPrinterUpdateReceived(msg)
      }
    }

    self.ensureWebsocketClosed()
    setTimeout( function () { self.heartbeat() }, 30*1000)
  }

  self.setWebRTC = function(webrtc) {
    self.webrtc = webrtc

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

      if (self.onStatusReceived) {
        self.onStatusReceived(msg)
      }
    }

    self.webrtc.callbacks.onData = (maybeBin) => {
      if (!maybeBin) {
        return
      }

      if (maybeBin instanceof ArrayBuffer) {
        try {
          const jsonData = pako.ungzip(new Uint8Array(maybeBin), {'to': 'string'})
          parseJsonData(jsonData)
        } catch {
          console.error('could not decompress datachannel arraybuffer')
        }

      } else if (maybeBin instanceof Blob) {
        const reader = new FileReader()
        reader.addEventListener('loadend', (e) => {
          if (!e.srcElement) {
            return
          }

          const arrayBuffer = e.srcElement.result

          try {
            const jsonData = pako.ungzip(new Uint8Array(arrayBuffer), {'to': 'string'})
            parseJsonData(jsonData)
          } catch {
            console.error('could not decompress datachannel blob')
          }
        })
        reader.readAsArrayBuffer(maybeBin)
      } else {
        parseJsonData(maybeBin)
      }
    }
  }

  self.passThruToPrinter = function(msg, callback) {
    if (self.canSend()) {
      var refId = Math.random().toString()
      assign(msg, {ref: refId})
      if (callback) {
        self.passthruQueue.set(refId, callback)
        setTimeout(function() {
          if (self.passthruQueue.has(refId)) {
            Vue.swal.Toast.fire({
              type: 'error',
              title: 'Failed to contact OctoPrint, or the Obico plugin version is older than 1.2.0.',
            })
          }
        }, 10*1000)
      }
      if (self.webrtc) {
        self.webrtc.sendData(JSON.stringify(msg))
      }
      self.ws.send(JSON.stringify({passthru: msg}))
    } else {
      if (callback){
        callback('Message not passed through. No suitable WebSocket.')
      }
    }
  }

  // Helper methods

  self.ensureWebsocketClosed = function() {
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

  self.closeWebSocket = function() {
    if (self.ws) {
      self.ws.close()
    }
  }

  // Heartbeat to maintain the presence of connection
  // Adapted from https://stackoverflow.com/questions/50876766/how-to-implement-ping-pong-request-for-websocket-connection-alive-in-javascript

  self.heartbeat = function() {
    if (!self.canSend()) {
      return
    }
    self.ws.send(JSON.stringify({}))
    setTimeout( function () { self.heartbeat() }, 30*1000)
  }

  self.canSend = function() {
    return self.ws && self.ws.readyState === 1
  }

  return self
}
