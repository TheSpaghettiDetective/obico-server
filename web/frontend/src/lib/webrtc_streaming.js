import get from 'lodash/get'
import Janus from '@lib/janus'


function getWebRTCManager(callbacks) {
  let manager = {
    callbacks: callbacks,
    streamId: undefined,
    streaming: undefined,

    connect(wsUri, token) {
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

      let self = this
      var janus = new Janus({
        server: window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
        iceServers: iceServers,
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
                setInterval(function() {
                    console.log(pluginHandle.getBitrate())
                }, 5000)
              },
              error: function (error) {
                Janus.error('  -- Error attaching plugin... ', error)
                janus.destroy()
              },
              onmessage: function(msg, jsep) {
                self.onMessage(msg, jsep)
              },
              onremotestream: function(stream) {
                self.onRemoteStream(stream)
              },
              ontrackmuted: function() {
                  self.onTrackMuted()
              },
              ontrackunmuted: function() {
                self.onTrackUnmuted()
              },
              slowLink: function(uplink, lost) {
                self.onSlowLink(lost)
              },
              ondataopen: function() {
              },
              ondata: function(rawData) {
                self.onData(rawData)

              },
              oncleanup: function() {
                self.onCleanup()
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
        self.streaming.createAnswer(
          {
            jsep: jsep,
            // We want recvonly audio/video and, if negotiated, datachannels
            media: { audioSend: false, videoSend: false, data: true },
            success: function (jsep) {
              Janus.debug('Got SDP!')
              Janus.debug(jsep)
              var body = { 'request': 'start' }
              self.streaming.send({ 'message': body, 'jsep': jsep })
            },
            error: function (error) {
              Janus.error('WebRTC error:', error)
            }
          })
      }
    },
    onRemoteStream(stream) {
      Janus.debug(' ::: Got a remote stream :::')
      Janus.debug(stream)
      this.callbacks.onRemoteStream(stream)
    },
    onTrackMuted() {
      this.callbacks.onTrackMuted()
    },
    onTrackUnmuted() {
      this.callbacks.onTrackUnmuted()
    },
    onSlowLink(lost) {
      this.callbacks.onSlowLink(lost)
    },
    onCleanup() {
      this.callbacks.onCleanup()
    },
    onData(rawData) {
      this.callbacks.onData(rawData)
    },
    startStream() {
      if (this.streamId === undefined || this.streaming === undefined) {
        return
      }
      const body = { 'request': 'watch', id: parseInt(this.streamId) }
      this.streaming.send({ 'message': body })
    },
    stopStream() {
      if (this.streamId === undefined || this.streaming === undefined) {
        return
      }
      const body = { 'request': 'stop' }
      this.streaming.send({ 'message': body })
      this.streaming.hangup()
    },
  }

  return manager
}


export default {
  getWebRTCManager,
}
