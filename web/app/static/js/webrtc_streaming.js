$(document).ready(function () {
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

                var mjpegStreamDecoder = new Decoder(updateJpeg);
                var streaming;

                var janus = new Janus({
                    server: window.location.protocol.replace('http', 'ws') + '//' + window.location.host + '/ws/janus/' + printerId + '/',
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
                                    if (data.length < 50) {
                                        Janus.debug("We got data from the DataChannel! " + data);
                                    }
                                    mjpegStreamDecoder.onMessage(data);
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

                function updateJpeg(jpg, l) {
                    var jpgEle = printerCard.find(".remote-jpg");

                    try {
                        console.log("jpg length: " + atob(jpg).length + " expected length: " + l);
                        jpgEle.attr("src", 'data:image/jpg;base64, ' + jpg);
                    } catch (e) {
                        console.log(e);
                    }
                    showRemoteStream(jpgEle);
                }
            });

        }
    });

    function showRemoteStream(ele) {
        var parentView = ele.parent().parent();
        if (!ele.is(':visible')) {
            parentView.find('[class^=remote-]').addClass('hide').hide();
            ele.removeClass('hide').show();
        }
        var taggedJpgEle = parentView.find('.tagged-jpg');
        if (taggedJpgEle.attr('src').endsWith('img/3d_printer.png')) {
            taggedJpgEle.addClass('hide').hide();
            expandThumbnailToFull(ele);
        }
    }

    function Decoder(onFrame) {
        this.onFrame = onFrame;
        this.contentLength = NaN;
        this.imageBuffer = '';
        this.bytesRead = 0;
    }

    Decoder.prototype.onMessage = function (value) {

        if (this.contentLength) {
            this.imageBuffer += value;
            this.bytesRead += value.length;

            if (this.bytesRead >= this.contentLength) {
                var jpg = this.imageBuffer;
                var jpgLength = this.originalJpgLength;
                this.contentLength = NaN;
                this.imageBuffer = '';
                this.bytesRead = 0;
                this.onFrame(jpg, jpgLength);
            }
        } else {
            if (value.slice(0, 2) === '\r\n' && value.slice(value.length - 2) === '\r\n') {
                var lengthHeaders = value.slice(2, value.length - 2).split(':');
                this.contentLength = parseInt(lengthHeaders[0]);
                this.originalJpgLength = parseInt(lengthHeaders[1]);
            }
        }
    }

});
