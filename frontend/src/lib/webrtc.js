import get from 'lodash/get'
import ifvisible from 'ifvisible'

import Janus from '@src/lib/janus'

let printerWebRTCUrl = printerId => `/ws/janus/${printerId}/`
let printerSharedWebRTCUrl = token => `/ws/share_token/janus/${token}/`

export default function WebRTCConnection(videoEnabled) {
  let self = {
    callbacks: {},
    initialized: false,
    streamId: undefined,
    streaming: undefined,
    videoEnabled: videoEnabled ?? false,
    bitrateInterval: null,

    openForShareToken(shareToken) {
      self.connect(
        printerSharedWebRTCUrl(shareToken),
        shareToken
      )
    },

    openForPrinter(printerId, authToken) {
      self.connect(
        printerWebRTCUrl(printerId),
        authToken
      )
    },

    connect(wsUri, token) {
      Janus.init({
        debug: 'all',
        callback: () => {
          self.initialized = true
          if (!Janus.isWebrtcSupported()) {
            return
          }
          self.connectJanusWebSocket(wsUri, token)
        }
      })

      ifvisible.on('blur', () => {
        self.stopStream()
      })

      ifvisible.on('focus', () => {
        self.startStream()
      })
    },

    connectJanusWebSocket(wsUri, token) {
      const opaqueId = 'streamingtest-' + Janus.randomString(12)

      var iceServers = [{urls:['stun:stun.l.google.com:19302']}]
      if (token) {
        var turnServer = window.location.hostname.replace('app', 'turn')
        iceServers.push(
          {
            urls:'turn:' + turnServer + ':80?transport=udp',
            credential: token,
            username: token
          })
        iceServers.push(
          {
            urls:'turn:' + turnServer + ':80?transport=tcp',
            credential: token,
            username: token
          })
      }

      var janus = new Janus({
        server: window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
        iceServers: iceServers,
        ipv6: true,
        success: () => {
          janus.attach(
            {
              plugin: 'janus.plugin.streaming',
              opaqueId: opaqueId,
              success: function (pluginHandle) {
                Janus.log('Plugin attached! (' + pluginHandle.getPlugin() + ', id=' + pluginHandle.getId() + ')')

                const body = { 'request': 'list' }
                Janus.debug('Sending message (' + JSON.stringify(body) + ')')
                pluginHandle.send({
                  'message': body, success: function (result) {
                    let stream = get(result, 'list[0]')
                    if (stream) {
                      self.streamId = stream.id
                      self.streaming = pluginHandle
                      self.startStream()
                    }
                  }
                })
              },
              error: function (error) {
                Janus.error('  -- Error attaching plugin... ', error)
                janus.destroy()
              },
              onmessage: function(msg, jsep) {
                self.onMessage(msg, jsep)
              },
              onremotestream: function(stream) {
                Janus.debug(' ::: Got a remote stream :::')
                Janus.debug(stream)
                if ('onRemoteStream' in self.callbacks) {
                  self.callbacks.onRemoteStream(stream)
                }
              },
              ontrackmuted: function() {
                if ('onTrackMuted' in self.callbacks) {
                  self.callbacks.onTrackMuted()
                }
              },
              ontrackunmuted: function() {
                if ('onTrackUnmuted' in self.callbacks) {
                  self.callbacks.onTrackUnmuted()
                }
              },
              slowLink: function(uplink, lost) {
                if ('onSlowLink' in self.callbacks) {
                  self.callbacks.onSlowLink(lost)
                }
              },
              ondataopen: function() {
              },
              ondata: function(rawData) {
                if ('onData' in self.callbacks) {
                  self.callbacks.onData(rawData)
                }
              },
              oncleanup: function() {
                if ('onCleanup' in self.callbacks) {
                  self.callbacks.onCleanup()
                }
              }
            })
        },
        error(e) {
          Janus.error('  -- Error -- ', e)
          janus.destroy()
        },
        destroyed() {
          self.streaming = undefined
          self.streamId = undefined
        }
      })
    },
    onMessage(msg, jsep) {
      let self = this
      Janus.debug(' ::: Got a message :::')
      Janus.debug(msg)
      let result = msg['result']
      if (result !== null && result !== undefined) {
        if (result['status'] !== undefined && result['status'] !== null) {
          var status = result['status']
          if (status === 'starting')
            console.log('Starting')
          else if (status === 'started')
            console.log('Started')
          else if (status === 'stopped') {
            self.stopStream()
          }
        }
      } else if (msg['error'] !== undefined && msg['error'] !== null) {
        Janus.error(msg)
        self.stopStream()
        return
      }
      if (jsep !== undefined && jsep !== null) {
        Janus.debug('Handling SDP as well...')
        Janus.debug(jsep)
        // Offer from the plugin, let's answer
        self.streaming?.createAnswer(
          {
            jsep: jsep,
            // We want recvonly audio/video and, if negotiated, datachannels
            media: { audioSend: false, videoSend: false, data: true },
            success: function (jsep) {
              Janus.debug('Got SDP!')
              Janus.debug(jsep)
              var body = { 'request': 'start' }
              self.streaming?.send({ 'message': body, 'jsep': jsep })
            },
            error: function (error) {
              Janus.error('WebRTC error:', error)
            }
          })
      }
    },
    channelOpen() {
      return !(self.streamId === undefined || self.streaming === undefined)
    },
    startStream() {
      if (!self.channelOpen()) {
        return
      }
      const body = { 'request': 'watch', offer_video: self.videoEnabled, id: parseInt(self.streamId) }
      self.streaming?.send({ 'message': body })

      if (self.bitrateInterval) {
        clearInterval(self.bitrateInterval)
        self.bitrateInterval = null
      }

      self.bitrateInterval = setInterval(function() {
        if (self.streaming) {
          console.log(self.streaming.getBitrate())
        }
      }, 5000)
    },
    stopStream() {
      if (self.bitrateInterval) {
        clearInterval(self.bitrateInterval)
        self.bitrateInterval = null
      }

      if (!self.channelOpen()) {
        return
      }
      const body = { 'request': 'stop' }
      self.streaming?.send({ 'message': body })
      self.streaming?.hangup()
    },

    sendData(data) {
      if (self.channelOpen()) {
        self.streaming?.data({text: data, success: () => {}})
      }
    }
  }

  return self
}
