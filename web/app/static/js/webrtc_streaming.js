$(document).ready(function() {
    var streamList = [];

    function removeFromList(janus) {
        _.remove(streamList, function(ele) {
            return ele === janus;
        })
    }

	// Initialize the library (all console debuggers enabled)
	Janus.init({debug: "all", callback: function() {
        if(!Janus.isWebrtcSupported()) {
            return;
        }
        function openWebRTCStreaming() {
			$('.printer-card').each(function () {
                var opaqueId = "streamingtest-"+Janus.randomString(12);

                var printerCard = $(this);
                var printerId = printerCard.attr('id');

                var streaming;

                printerCard.find("#start").click(startStream);
                printerCard.find("#stop").click(stopStream);

                var janus = new Janus({
                    server: window.location.protocol.replace('http', 'ws') + '//' + window.location.host + '/ws/janus/' + printerId + '/',
                    success: function() {
                        janus.attach(
                            {
                                plugin: "janus.plugin.streaming",
                                opaqueId: opaqueId,
                                success: function(pluginHandle) {
                                    streaming = pluginHandle;
                                    Janus.log("Plugin attached! (" + streaming.getPlugin() + ", id=" + streaming.getId() + ")");
                                    // Setup streaming session
                                    updateStreamsList();
                                },
                                error: function(error) {
                                    Janus.error("  -- Error attaching plugin... ", error);
                                    janus.destroy();
                                },
                                onmessage: onMessage,
                                onremotestream: onRemoteStream,
                                ondataopen: function(data) {
                                },
                                ondata: function(data) {
                                    Janus.debug("We got data from the DataChannel! " + data);
                                    $('#datarecv').val(data);
                                },
                                oncleanup: function() {
                                    printerCard.find('#webrtc-stream').empty();
                                }
                            });
                    },
                    error: function(error) {
                        janus.destroy();
                    },
                    destroyed: function() {
                        removeFromList(janus);
                    }
                });

                streamList.push(janus);

                function onMessage(msg, jsep) {
                    Janus.debug(" ::: Got a message :::");
                    Janus.debug(msg);
                    var result = msg["result"];
                    if(result !== null && result !== undefined) {
                        if(result["status"] !== undefined && result["status"] !== null) {
                            var status = result["status"];
                            if(status === 'starting')
                                console.log("Starting");
                            else if(status === 'started')
                                console.log("Started");
                            else if(status === 'stopped')
                                stopStream();
                        }
                    } else if(msg["error"] !== undefined && msg["error"] !== null) {
                        Janus.error(msg);
                        stopStream();
                        return;
                    }
                    if(jsep !== undefined && jsep !== null) {
                        Janus.debug("Handling SDP as well...");
                        Janus.debug(jsep);
                        // Offer from the plugin, let's answer
                        streaming.createAnswer(
                            {
                                jsep: jsep,
                                // We want recvonly audio/video and, if negotiated, datachannels
                                media: { audioSend: false, videoSend: false, data: true },
                                success: function(jsep) {
                                    Janus.debug("Got SDP!");
                                    Janus.debug(jsep);
                                    var body = { "request": "start" };
                                    streaming.send({"message": body, "jsep": jsep});
                                },
                                error: function(error) {
                                    Janus.error("WebRTC error:", error);
                                }
                            });
                    }
                }

                function onRemoteStream(stream) {
                    Janus.debug(" ::: Got a remote stream :::");
                    Janus.debug(stream);
                    var addButtons = false;
                    if(printerCard.find('#remotevideo').length === 0) {
                        addButtons = true;
                        printerCard.find('#webrtc-stream').html('<video id="remotevideo" width=960 height=540 autoplay playsinline class="hide" style="width: 25%; height: 25%; float: right;"/>');
                        printerCard.on("playing", "#remotevideo", function () {
                            if(this.videoWidth)
                                printerCard.find('#remotevideo').removeClass('hide').show();
                            var videoTracks = stream.getVideoTracks();
                            if(videoTracks === null || videoTracks === undefined || videoTracks.length === 0)
                                return;
                        });
                        printerCard.on("click", "#remotevideo", function (e) {
                            console.log(e);
                        });
                    }
                    Janus.attachMediaStream(printerCard.find('#remotevideo').get(0), stream);
                    var videoTracks = stream.getVideoTracks();
                    if(videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
                        // No remote video
                        printerCard.find('#remotevideo').hide();
                    } else {
                        printerCard.find('#remotevideo').removeClass('hide').show();
                    }
                }

                function updateStreamsList() {
                    var body = { "request": "list" };
                    Janus.debug("Sending message (" + JSON.stringify(body) + ")");
                    streaming.send({"message": body, success: function(result) {
                        var stream = _.get(result, 'list[0]');
                        if (stream) {
                            startStream(stream.id);
                        }
                    }});
                }

                function startStream(streamId) {
                    Janus.log("Selected video id #" + streamId);
                    var body = { "request": "watch", id: parseInt(streamId) };
                    streaming.send({"message": body});
                }

                function stopStream() {
                    var body = { "request": "stop" };
                    streaming.send({"message": body});
                    streaming.hangup();
                }

            });
        }

        function closeWebRTCStreaming() {
            _.forEach(streamList, function(janus) {
                janus.destroy();
            });
        }

        ifvisible.on("blur", function(){
            closeWebRTCStreaming();
        });
        ifvisible.on("focus", function(){
            openWebRTCStreaming();
        });
        openWebRTCStreaming();
	}});
});
