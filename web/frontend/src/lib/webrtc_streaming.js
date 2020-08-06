import get from 'lodash/get'
import Janus from '@lib/janus'


function getWebRTCManager(callbacks) {
  let manager = {
    callbacks: callbacks,
    streamList: new Map(),
    startStream(streamId, streaming) {
      const body = { 'request': 'watch', id: parseInt(streamId) }
      streaming.send({ 'message': body })
    },
    stopStream(streaming) {
      const body = { 'request': 'stop' }
      streaming.send({ 'message': body })
      streaming.hangup()
    },
    stopAllStreaming() {
      this.streamList.forEach((s, /* printerId */) => {
        this.stopStream(s.streaming)
      })
    },
    resumeAllStreaming() {
      this.streamList.forEach((s, /* printerId */) => {
        this.startStream(s.id, s.streaming)
      })
    },

    connect(printerId, wsUri, token) {
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
                let streaming = pluginHandle
                Janus.log('Plugin attached! (' + streaming.getPlugin() + ', id=' + streaming.getId() + ')')

                const body = { 'request': 'list' }
                Janus.debug('Sending message (' + JSON.stringify(body) + ')')
                streaming.send({
                  'message': body, success: function (result) {
                    let stream = get(result, 'list[0]')
                    if (stream) {
                      self.startStream(stream.id, streaming)
                      self.streamList.set(
                        printerId, { id: stream.id, streaming: streaming })
                    }
                  }
                })
              },
              error: function (error) {
                Janus.error('  -- Error attaching plugin... ', error)
                janus.destroy()
              },
              onmessage: function(msg, jsep) {
                self.onMessage(printerId, msg, jsep)
              },
              onremotestream: function(stream) {
                self.onRemoteStream(printerId, stream)
              },
              ondataopen: function () {
              },
              ondata: function () {
              },
              oncleanup: function() {
                self.onCleanup(printerId)
              }
            })
        },
        error(e) {
          Janus.error('  -- Error -- ', e)
          janus.destroy()
        },
        destroyed() {
          // TODO bug here? janus never ever matched that
          // remove(self.streamList, ([printerId, item]) => {
          //  return item === janus
          // })
          self.streamList.delete(printerId)
        }
      })
    },
    onMessage(printerId, msg, jsep) {
      Janus.debug(' ::: Got a message :::')
      Janus.debug(msg)
      let result = msg['result']
      let s = this.streamList.get(printerId)
      if (result !== null && result !== undefined) {
        if (result['status'] !== undefined && result['status'] !== null) {
          var status = result['status']
          if (status === 'starting')
            console.log('Starting')
          else if (status === 'started')
            console.log('Started')
          else if (status === 'stopped') {
            this.stopStream(s.streaming)
          }
        }
      } else if (msg['error'] !== undefined && msg['error'] !== null) {
        Janus.error(msg)
        this.stopStream(s.streaming)
        return
      }
      if (jsep !== undefined && jsep !== null) {
        Janus.debug('Handling SDP as well...')
        Janus.debug(jsep)
        // Offer from the plugin, let's answer
        s.streaming.createAnswer(
          {
            jsep: jsep,
            // We want recvonly audio/video and, if negotiated, datachannels
            media: { audioSend: false, videoSend: false, data: true },
            success: function (jsep) {
              Janus.debug('Got SDP!')
              Janus.debug(jsep)
              var body = { 'request': 'start' }
              s.streaming.send({ 'message': body, 'jsep': jsep })
            },
            error: function (error) {
              Janus.error('WebRTC error:', error)
            }
          })
      }
    },
    onRemoteStream(printerId, stream) {
      Janus.debug(' ::: Got a remote stream :::')
      Janus.debug(stream)
      this.callbacks.onRemoteStream(printerId, stream)
    },
    onCleanup(printerId) {
      this.callbacks.onCleanup(printerId)
    }
  }

  return manager
}


export default {
  getWebRTCManager,
}
