$(document).ready(function () {
    if (!isProAccount) {
        return;
    }

    $('video.remote-video').on('loadstart', function (event) {
        $(this).attr("poster", loadingIcon);
    });
    $('video.remote-video').on('canplay', function (event) {
        $(this).removeAttr("poster");
    });

    var streamList = [];

    function removeFromList(janus) {
        _.remove(streamList, function (ele) {
            return ele === janus;
        })
    }

    function startStream(streamId, streaming) {
        var body = { "request": "watch", id: parseInt(streamId) };
        streaming.send({ "message": body });
    }

    function stopStream(streaming) {
        var body = { "request": "stop" };
        streaming.send({ "message": body });
        streaming.hangup();
    }

    function stopAllStreaming() {
        _.forEach(streamList, function (s) {
            stopStream(s.streaming);
        });
    }

    function resumeAllStreaming() {
        _.forEach(streamList, function (s) {
            startStream(s.id, s.streaming);
        });
    }

    ifvisible.on("blur", function () {
        stopAllStreaming();
    });
    ifvisible.on("focus", function () {
        resumeAllStreaming();
    });

    // Initialize the library (all console debuggers enabled)
    Janus.init({
        debug: "all", callback: function () {
            if (!Janus.isWebrtcSupported()) {
                return;
            }

            $('.printer-card').each(function () {
                var opaqueId = "streamingtest-" + Janus.randomString(12);

                var printerCard = $(this);
                var printerId = printerCard.attr('id');

                printerCard.on("playing", ".remote-video", function () {
                    if (this.videoWidth) {
                        showRemoteStream(printerCard.find('.remote-video'));
                    }
                    var videoTracks = stream.getVideoTracks();
                    if (videoTracks === null || videoTracks === undefined || videoTracks.length === 0)
                        return;
                });

                printerCard.on("click", "[class^=remote-]", function () {
                    expandThumbnailToFull($(this));
                });

                var streaming, wsUri, turnToken, turnId;

                printerCard.on('sendPassThruMessage', function (e, message) {
                  if (streaming) {
                    streaming.data({text: JSON.stringify(message), success: function() {}})
                  }
                });

                if (printerCard.data('share-token')) {
                    wsUri = '/ws/share_token/janus/' + printerCard.data('share-token') + '/';
                    turnToken = printerCard.data('share-token');
                } else {
                    wsUri = '/ws/janus/' + printerId + '/';
                    turnToken = printerCard.data('auth-token');
                }

                var iceServers = [{urls:["stun:stun.l.google.com:19302"]}];
                if (turnToken) {
                    var turnServer = window.location.hostname.replace('app', 'turn');
                    iceServers.push({urls:'turn:' + turnServer + ':80?transport=udp',credential: turnToken, username: turnToken});
                    iceServers.push({urls:'turn:' + turnServer + ':80?transport=tcp',credential: turnToken, username: turnToken});
                }

                var janus = new Janus({
                    server: window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri,
                    iceServers: iceServers,
                    success: function () {
                        janus.attach(
                            {
                                plugin: "janus.plugin.streaming",
                                opaqueId: opaqueId,
                                success: function (pluginHandle) {
                                    streaming = pluginHandle;
                                    Janus.log("Plugin attached! (" + streaming.getPlugin() + ", id=" + streaming.getId() + ")");
                                    // Setup streaming session
                                    updateStreamsList();
                                },
                                error: function (error) {
                                    Janus.error("  -- Error attaching plugin... ", error);
                                    janus.destroy();
                                },
                                onmessage: onMessage,
                                onremotestream: onRemoteStream,
                                ondataopen: function (data) {
                                },
                                ondata: function (data) {
                                  var msg = undefined;
                                  try {
                                    msg = JSON.parse(data);
                                  } catch {
                                    console.log('cannot parse datachannel message')
                                  }
                                  if (msg && 'passthru' in msg) {
                                    printerCard.trigger('gotPassthruMessage', [msg]);
                                  }
                                },
                                oncleanup: function () {
                                    printerCard.find('.remote-video').hide();
                                }
                            });
                    },
                    error: function (error) {
                        janus.destroy();
                    },
                    destroyed: function () {
                        removeFromList(janus);
                    }
                });

                function onMessage(msg, jsep) {
                    Janus.debug(" ::: Got a message :::");
                    Janus.debug(msg);
                    var result = msg["result"];
                    if (result !== null && result !== undefined) {
                        if (result["status"] !== undefined && result["status"] !== null) {
                            var status = result["status"];
                            if (status === 'starting')
                                console.log("Starting");
                            else if (status === 'started')
                                console.log("Started");
                            else if (status === 'stopped')
                                stopStream(streaming);
                        }
                    } else if (msg["error"] !== undefined && msg["error"] !== null) {
                        Janus.error(msg);
                        stopStream(streaming);
                        return;
                    }
                    if (jsep !== undefined && jsep !== null) {
                        Janus.debug("Handling SDP as well...");
                        Janus.debug(jsep);
                        // Offer from the plugin, let's answer
                        streaming.createAnswer(
                            {
                                jsep: jsep,
                                // We want recvonly audio/video and, if negotiated, datachannels
                                media: { audioSend: false, videoSend: false, data: true },
                                success: function (jsep) {
                                    Janus.debug("Got SDP!");
                                    Janus.debug(jsep);
                                    var body = { "request": "start" };
                                    streaming.send({ "message": body, "jsep": jsep });
                                },
                                error: function (error) {
                                    Janus.error("WebRTC error:", error);
                                }
                            });
                    }
                }

                function onRemoteStream(stream) {
                    Janus.debug(" ::: Got a remote stream :::");
                    Janus.debug(stream);
                    Janus.attachMediaStream(printerCard.find('.remote-video').get(0), stream);
                    var videoTracks = stream.getVideoTracks();
                    var videoEle = printerCard.find('.remote-video');
                    if (videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
                        // No remote video
                        videoEle.hide();
                    } else {
                        showRemoteStream(videoEle);
                    }
                }

                function updateStreamsList() {
                    var body = { "request": "list" };
                    Janus.debug("Sending message (" + JSON.stringify(body) + ")");
                    streaming.send({
                        "message": body, success: function (result) {
                            var stream = _.get(result, 'list[0]');
                            if (stream) {
                                startStream(stream.id, streaming);
                                streamList.push({ id: stream.id, streaming: streaming });
                            }
                        }
                    });
                }
            });

        }
    });

    function showRemoteStream(ele) {
        var parentView = ele.parent().parent();
        if (!ele.is(':visible')) {
            ele.removeClass('hide').show();
        }
    }
});
