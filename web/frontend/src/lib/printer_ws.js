'use strict'
import assign from 'lodash/assign'
import Vue from 'vue'
import ifvisible from 'ifvisible'
import EventBus from '@lib/event_bus'


export default function PrinterWebSocket(printerId, wsUri, onMessageReceived) {
  var self = {}

  self.printerId = printerId
  self.wsUri = wsUri
  self.onMessageReceived = onMessageReceived
  self.ws = null
  self.passthruQueue = new Map()

  ifvisible.on('blur', function(){
    self.closeWebSocket()
  })

  ifvisible.on('focus', function(){
    self.openPrinterWebSocket()
  })

  self.on_passThruReceived = function(msg) {
    var refId = msg.passthru.ref
    if (refId && self.passthruQueue.get(refId)) {
      var callback = self.passthruQueue.get(refId)
      self.passthruQueue.delete(refId)
      callback(null, msg.passthru.ret)
    }
  }

  EventBus.$on('gotPassthruOverDatachannel', self.on_passThruReceived)

  self.openPrinterWebSocket = function() {
    self.ws = new WebSocket( window.location.protocol.replace('http', 'ws') + '//' + window.location.host + self.wsUri)
    self.ws.onmessage = function (e) {
      var msg = JSON.parse(e.data)
      if ('passthru' in msg) {
        self.on_passThruReceived(msg)
      } else {
        onMessageReceived(msg)
      }
    }

    self.ensureWebsocketClosed()
    setTimeout( function () { self.heartbeat() }, 30*1000)
  }


  self.passThruToPrinter = function(msg, callback) {
    if (self.canSend()) {
      if (callback) {
        var refId = Math.random().toString()
        self.passthruQueue.set(refId, callback)
        assign(msg, {ref: refId})
        setTimeout(function() {
          if (self.passthruQueue.has(refId)) {
            Vue.swal.Toast.fire({
              type: 'error',
              title: 'Failed to contact OctoPrint, or the TSD plugin version is older than 1.2.0.',
            })
          }
        }, 10*1000)
      }
      let msgObj = {passthru: msg}
      self.ws.send(JSON.stringify(msgObj))
      EventBus.$emit('sendOverDatachannel', self.printerId, msgObj)
      return msgObj
    } else {
      if (callback){
        callback('Message not passed through. No suitable WebSocket.')
      }
    }
  }

  // Helper methods

  self.ensureWebsocketClosed = function() {
    self.ws.onclose = function () {
      self.ws = null
    }
    self.ws.onerror = function () {
      self.ws.close()
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
