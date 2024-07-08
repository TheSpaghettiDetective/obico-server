import get from 'lodash/get'
import find from 'lodash/find'

import Janus from '@src/lib/janus'
import { syndicate } from '@src/lib/page-context'

let printerWebRTCUrl = (printerId) => `/ws/janus/${printerId}/`
let printerSharedWebRTCUrl = (token) => `/ws/share_token/janus/${token}/`

function iceServers(authToken) {
  const turnServer = syndicate()?.turn_server
  const servers = [
    {
      urls: ['stun:stun.l.google.com:19302'],
    }
  ]

  if (turnServer) {
    servers.push(
      {
        urls: `turn:${turnServer}:80?transport=udp`,
        credential: authToken,
        username: authToken,
      },
      {
        urls: `turn:${turnServer}:80?transport=tcp`,
        credential: authToken,
        username: authToken,
      }
    );
  }

  return servers
}

export default function WebRTCConnection(streamMode, streamIdToTest) {
  let h264Webrtc, mjpegWebrtc
  if (streamMode === undefined && streamIdToTest === undefined) {
    // The agent is an old version that doesn't support dynamic streaming
    h264Webrtc = H264WebRTCConnection([0, 1])
    mjpegWebrtc = MJpegWebRTCConnection([2])
  } else if (streamMode.includes('h264')) {
    h264Webrtc = H264WebRTCConnection([streamIdToTest])
  } else if (streamMode.includes('mjpeg')) {
    mjpegWebrtc = MJpegWebRTCConnection([streamIdToTest])
  }

  let self = {
    callbacks: {},
    initialized: false,
    h264WebRTCConn: h264Webrtc,
    mjpegWebRTCConn: mjpegWebrtc,

    openForShareToken(shareToken) {
      self.connect(printerSharedWebRTCUrl(shareToken), shareToken)
    },

    openForPrinter(printerId, authToken) {
      self.connect(printerWebRTCUrl(printerId), authToken)
    },
    connect(wsUri, token) {
      self.initialized = true
      if (self.h264WebRTCConn) self.h264WebRTCConn.connect(wsUri, token)
      if (self.mjpegWebRTCConn) self.mjpegWebRTCConn.connect(wsUri, token)
    },
    disconnect() {
      if (self.h264WebRTCConn) self.h264WebRTCConn.janus.destroy()
      if (self.mjpegWebRTCConn) self.mjpegWebRTCConn.janus.destroy()
    },
    stopStream() {
      if (self.h264WebRTCConn) self.h264WebRTCConn.stopStream()
      if (self.mjpegWebRTCConn) self.mjpegWebRTCConn.stopStream()
    },
    sendData(data) {
      if (self.h264WebRTCConn) self.h264WebRTCConn.sendData(data) // Data channel in the default stream is used to pass data from client to agent
    },
    startStream() {
      if (self.h264WebRTCConn) self.h264WebRTCConn.startStream()
      if (self.mjpegWebRTCConn) self.mjpegWebRTCConn.startStream()
    },
    setCallbacks(callbacks) {
        if (self.h264WebRTCConn) self.h264WebRTCConn.setCallbacks(callbacks)
        if (self.mjpegWebRTCConn) self.mjpegWebRTCConn.setCallbacks(callbacks)
    },
  }
  return self
}

function MJpegWebRTCConnection(streamIdsToTest) {
  let baseConnection = BaseWebRTCConnection(streamIdsToTest);

  baseConnection.infoSuccessCallback = function (result, pluginHandle) {
    let stream = get(result, 'info')
    if (stream) {
      baseConnection.streamId = stream.id
      baseConnection.streaming = pluginHandle

      const mjpegStreamExisting =
        get(stream, 'data') || // Janus 0.x format
        find(get(stream, 'media', []), { type: 'data' }) // Janus 1.x format

      if (mjpegStreamExisting) {
        baseConnection.callbacks.onStreamAvailable(baseConnection)
      }
    } else {
      baseConnection.janus.destroy()
    }
  };

  baseConnection.onRawData = function (rawData) {
    if ('onMJpegData' in baseConnection.callbacks) {
      baseConnection.callbacks.onMJpegData(rawData)
    }
  };

  baseConnection.startStream = function () {
    if (!baseConnection.channelOpen()) {
      return
    }
    const body = { request: 'watch', offer_video: false, id: parseInt(baseConnection.streamId) }
    baseConnection.streaming?.send({ message: body })
  };
  return baseConnection;
}

function H264WebRTCConnection(streamIdsToTest) {
  let baseConnection = BaseWebRTCConnection(streamIdsToTest);

  baseConnection.infoSuccessCallback = function (result, pluginHandle) {
    let stream = get(result, 'info')
    if (stream) {
      baseConnection.streamId = stream.id
      baseConnection.streaming = pluginHandle

      const videoStreamExisting =
        get(stream, 'video') || // Janus 0.x format
        find(get(stream, 'media', []), { type: 'video' }) // Janus 1.x format

      if (videoStreamExisting) {
        baseConnection.callbacks.onStreamAvailable(baseConnection)
      }
    }
  };
  baseConnection.onRawData = function (rawData) {
    if ('onData' in baseConnection.callbacks) {
      baseConnection.callbacks.onData(rawData)
    }
  };

  baseConnection.startStream = function () {
    if (!baseConnection.channelOpen()) {
      return
    }
    const body = { request: 'watch', offer_video: true, id: parseInt(baseConnection.streamId) }
    baseConnection.streaming?.send({ message: body })

    baseConnection.clearBitrateInterval()
    baseConnection.bitrateInterval = setInterval(function () {
      if (baseConnection.streaming) {
        const bitrate = baseConnection.streaming.getBitrate()
        if (bitrate && bitrate.value) {
          baseConnection.callbacks.onBitrateUpdated(baseConnection.streaming.getBitrate())
        } else {
          baseConnection.callbacks.onBitrateUpdated({ value: null })
        }
      } else {
        baseConnection.callbacks.onBitrateUpdated({ value: null })
      }
    }, 5000)
  };
  return baseConnection;
}

export function DataChannelOnlyWebRTCConnection(streamIdsToTest) {

  let baseConnection = BaseWebRTCConnection(streamIdsToTest); // webcamName is null for data channel-only WebRTC

  baseConnection.openForPrinter = function (printerId, authToken) {
    baseConnection.connect(printerWebRTCUrl(printerId), authToken)
  };

  baseConnection.infoSuccessCallback = function (result, pluginHandle) {
    let stream = get(result, 'info')
    if (stream) {
      baseConnection.streamId = stream.id
      baseConnection.streaming = pluginHandle

      const dataStreamExisting =
        get(stream, 'data') || // Janus 0.x format
        find(get(stream, 'media', []), { type: 'data' }) // Janus 1.x format

      if (dataStreamExisting) {
        baseConnection.startStream();
      } else {
        baseConnection.close();
      }
    }
  };

  baseConnection.onRawData = function (rawData) {
    baseConnection.callbacks.onData(rawData);
  };

  return baseConnection;
}

function BaseWebRTCConnection(streamIdsToTest) {
  let self = {
    callbacks: {},
    streamId: undefined,
    streaming: undefined,
    bitrateInterval: null,

    setCallbacks(callbacks) {
      self.callbacks = {...self.callbacks, ...callbacks};
    },

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
      self.janus = new Janus({
        server:
          window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
        iceServers: iceServers(token),
        ipv6: true,
        success: () => {
          self.janus.attach({
            plugin: 'janus.plugin.streaming',
            opaqueId: 'streamingtest-' + Janus.randomString(12),
            success: function (pluginHandle) {
              streamIdsToTest.forEach((streamIdToTest) => {
                const body = { request: 'info', id: streamIdToTest }
                Janus.debug('Sending message (' + JSON.stringify(body) + ')')
                pluginHandle.send({
                  message: body,
                  success: function(result) { self.infoSuccessCallback(result, pluginHandle) },
                })
              })
            },
            error: function (error) {
              Janus.error('  -- Error attaching plugin... ', error)
              self.janus.destroy()
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
            ondata: self.onRawData,
            oncleanup: function () {
              if ('onDefaultStreamCleanup' in self.callbacks) {
                self.callbacks.onDefaultStreamCleanup()
              }
            },
          })
        },
        error(e) {
          Janus.error('  -- Error -- ', e)
          self.janus.destroy()
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
      const body = { request: 'watch', offer_video: false, id: parseInt(self.streamId) }
      self.streaming?.send({ message: body })
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
