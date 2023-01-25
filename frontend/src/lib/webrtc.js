import get from 'lodash/get'
import find from 'lodash/find'

import Janus from '@src/lib/janus'

let printerWebRTCUrl = (printerId) => `/ws/janus/${printerId}/`
let printerSharedWebRTCUrl = (token) => `/ws/share_token/janus/${token}/`

function iceServers(authToken) {
  const turnServer = window.location.hostname.replace('app', 'turn')

  return [
    {
      urls: ['stun:stun.l.google.com:19302'],
    },
    {
      urls: `turn:${turnServer}:80?transport=udp`,
      credential: authToken,
      username: authToken,
    },
    {
      urls: `turn:${turnServer}:80?transport=tcp`,
      credential: authToken,
      username: authToken,
    },
  ]
}

export default function WebRTCConnection() {
  let self = {
    callbacks: {},
    initialized: false,
    mainWebRTCConn: MainWebRTCConnection(),
    mjpegWebRTCConn: MJpegtWebRTCConnection(),

    openForShareToken(shareToken) {
      self.connect(printerSharedWebRTCUrl(shareToken), shareToken)
    },

    openForPrinter(printerId, authToken) {
      self.connect(printerWebRTCUrl(printerId), authToken)
    },
    connect(wsUri, token) {
      self.initialized = true
      self.mainWebRTCConn.connect(wsUri, token)
      self.mjpegWebRTCConn.connect(wsUri, token)
    },
    stopStream() {
      self.mainWebRTCConn.stopStream()
      self.mjpegWebRTCConn.stopStream()
    },
    sendData(data) {
      self.mainWebRTCConn.sendData(data) // Data channel in the default stream is used to pass data from client to agent
    },
    startStream() {
      self.mainWebRTCConn.startStream()
      self.mjpegWebRTCConn.startStream()
    },
    setCallbacks(callbacks) {
      self.callbacks = { ...self.callbacks, ...callbacks }
      self.mainWebRTCConn.callbacks = self.callbacks
      self.mjpegWebRTCConn.callbacks = self.callbacks
    },
  }
  return self
}

function MJpegtWebRTCConnection() {
  let self = {
    callbacks: {},
    streamId: undefined,
    streaming: undefined,
    bitrateInterval: null,

    connect(wsUri, token) {
      Janus.init({
        debug: 'all',
        callback: () => {
          if (!Janus.isWebrtcSupported()) {
            return
          }
          self.connectJanusWebSocket(wsUri, token)
        },
      })
    },

    connectJanusWebSocket(wsUri, token) {
      var janus = new Janus({
        server:
          window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
        iceServers: iceServers(token),
        ipv6: true,
        success: () => {
          janus.attach({
            plugin: 'janus.plugin.streaming',
            opaqueId: 'streamingtest-' + Janus.randomString(12),
            success: function (pluginHandle) {
              Janus.log(
                'Plugin attached! (' +
                  pluginHandle.getPlugin() +
                  ', id=' +
                  pluginHandle.getId() +
                  ')'
              )
              const body = { request: 'info', id: 2 } // id=2 is for mjpeg stream. This stream may not exist in the agent.
              Janus.debug('Sending message (' + JSON.stringify(body) + ')')
              pluginHandle.send({
                message: body,
                success: function (result) {
                  let stream = get(result, 'info')
                  if (stream) {
                    self.streamId = stream.id
                    self.streaming = pluginHandle
                    if (get(stream, 'media[0].type') === 'data') {
                      self.callbacks.onStreamAvailable()
                    }
                  } else {
                    janus.destroy()
                  }
                },
              })
            },
            error: function (error) {
              Janus.error('  -- Error attaching plugin... ', error)
              janus.destroy()
            },
            onmessage: function (msg, jsep) {
              self.onMessage(msg, jsep)
            },
            onremotestream: function (stream) {},
            ondataopen: function () {},
            ondata: function (rawData) {
              if ('onMJpegData' in self.callbacks) {
                self.callbacks.onMJpegData(rawData)
              }
            },
            oncleanup: function () {},
          })
        },
        error(e) {
          Janus.error('  -- Error -- ', e)
          janus.destroy()
        },
        destroyed() {
          self.streaming = undefined
          self.streamId = undefined
        },
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
          if (status === 'starting') console.log('Starting')
          else if (status === 'started') console.log('Started')
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
        // Offer from the plugin, let's answer
        self.streaming?.createAnswer({
          jsep: jsep,
          // We want recvonly audio/video and, if negotiated, datachannels
          media: { audioSend: false, videoSend: false, data: true },
          success: function (jsep) {
            Janus.debug('Got SDP!')
            Janus.debug(jsep)
            var body = { request: 'start' }
            self.streaming?.send({ message: body, jsep: jsep })
          },
          error: function (error) {
            Janus.error('WebRTC error:', error)
          },
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
      const body = { request: 'watch', offer_video: false, id: parseInt(self.streamId) }
      self.streaming?.send({ message: body })
    },
    stopStream() {
      const body = { request: 'stop' }
      self.streaming?.send({ message: body })
      self.streaming?.hangup()
    },
  }

  return self
}

function MainWebRTCConnection() {
  let self = {
    callbacks: {},
    streamId: undefined,
    streaming: undefined,
    bitrateInterval: null,

    connect(wsUri, token) {
      Janus.init({
        debug: 'all',
        callback: () => {
          if (!Janus.isWebrtcSupported()) {
            return
          }
          self.connectJanusWebSocket(wsUri, token)
        },
      })
    },

    connectJanusWebSocket(wsUri, token) {
      var janus = new Janus({
        server:
          window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
        iceServers: iceServers(token),
        ipv6: true,
        success: () => {
          janus.attach({
            plugin: 'janus.plugin.streaming',
            opaqueId: 'streamingtest-' + Janus.randomString(12),
            success: function (pluginHandle) {
              // Janus.log('Plugin attached! (' + pluginHandle.getPlugin() + ', id=' + pluginHandle.getId() + ')')

              // Old plugin versions use stream_id=0, which is no longer valid in Janus 1.x so plugin 2.2.x switched to stream_id=1
              // Both ides are tried. The invalid one will return a failure and ignored.
              ;[0, 1].forEach((streamIdToTest) => {
                const body = { request: 'info', id: streamIdToTest }
                Janus.debug('Sending message (' + JSON.stringify(body) + ')')
                pluginHandle.send({
                  message: body,
                  success: function (result) {
                    let stream = get(result, 'info')
                    if (stream) {
                      self.streamId = stream.id
                      self.streaming = pluginHandle

                      const videoStreamExisting =
                        get(stream, 'video') || // Janus 0.x format
                        find(get(stream, 'media', []), { type: 'video' }) // Janus 1.x format

                      if (videoStreamExisting) {
                        self.callbacks.onStreamAvailable()
                      }
                    }
                  },
                })
              })
            },
            error: function (error) {
              Janus.error('  -- Error attaching plugin... ', error)
              janus.destroy()
            },
            onmessage: function (msg, jsep) {
              self.onMessage(msg, jsep)
            },
            onremotestream: function (stream) {
              Janus.debug(' ::: Got a remote stream :::')
              Janus.debug(stream)
              if ('onRemoteStream' in self.callbacks) {
                self.callbacks.onRemoteStream(stream)
              }
            },
            ontrackmuted: function () {
              if ('onTrackMuted' in self.callbacks) {
                self.callbacks.onTrackMuted()
              }
            },
            ontrackunmuted: function () {
              if ('onTrackUnmuted' in self.callbacks) {
                self.callbacks.onTrackUnmuted()
              }
            },
            slowLink: function (uplink, lost) {
              if ('onSlowLink' in self.callbacks) {
                self.callbacks.onSlowLink(lost)
              }
            },
            ondataopen: function () {},
            ondata: function (rawData) {
              if ('onData' in self.callbacks) {
                self.callbacks.onData(rawData)
              }
            },
            oncleanup: function () {
              if ('onDefaultStreamCleanup' in self.callbacks) {
                self.callbacks.onDefaultStreamCleanup()
              }
            },
          })
        },
        error(e) {
          Janus.error('  -- Error -- ', e)
          janus.destroy()
        },
        destroyed() {
          self.streaming = undefined
          self.streamId = undefined
          self.clearBitrateInterval()
        },
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
          if (status === 'starting') console.log('Starting')
          else if (status === 'started') console.log('Started')
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
        // Offer from the plugin, let's answer
        self.streaming?.createAnswer({
          jsep: jsep,
          // We want recvonly audio/video and, if negotiated, datachannels
          media: { audioSend: false, videoSend: false, data: true },
          success: function (jsep) {
            Janus.debug('Got SDP!')
            Janus.debug(jsep)
            var body = { request: 'start' }
            self.streaming?.send({ message: body, jsep: jsep })
          },
          error: function (error) {
            Janus.error('WebRTC error:', error)
          },
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
      const body = { request: 'watch', offer_video: true, id: parseInt(self.streamId) }
      self.streaming?.send({ message: body })

      self.clearBitrateInterval()
      self.bitrateInterval = setInterval(function () {
        if (self.streaming) {
          const bitrate = self.streaming.getBitrate()
          if (bitrate && bitrate.value) {
            self.callbacks.onBitrateUpdated(self.streaming.getBitrate())
          } else {
            self.callbacks.onBitrateUpdated({ value: null })
          }
        } else {
          self.callbacks.onBitrateUpdated({ value: null })
        }
      }, 5000)
    },
    stopStream() {
      self.clearBitrateInterval()
      if (!self.channelOpen()) {
        return
      }
      const body = { request: 'stop' }
      self.streaming?.send({ message: body })
      self.streaming?.hangup()
    },

    sendData(data) {
      if (self.channelOpen()) {
        self.streaming?.data({ text: data, success: () => {} })
      }
    },

    clearBitrateInterval() {
      if (self.bitrateInterval) {
        clearInterval(self.bitrateInterval)
        self.bitrateInterval = null
        self.callbacks.onBitrateUpdated({ value: null })
      }
    },
  }

  return self
}
