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

                janus = new Janus({
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
                                    $('#start').removeAttr('disabled').html("Stop")
                                        .click(function() {
                                            $(this).attr('disabled', true);
                                            clearInterval(bitrateTimer);
                                            janus.destroy();
                                            $('#streamslist').attr('disabled', true);
                                            $('#watch').attr('disabled', true).unbind('click');
                                            $('#start').attr('disabled', true).html("Bye").unbind('click');
                                        });
                                },
                                error: function(error) {
                                    Janus.error("  -- Error attaching plugin... ", error);


                                },
                                onmessage: onMessage,
                                onremotestream: onRemoteStream,
                                ondataopen: function(data) {
                                    Janus.log("The DataChannel is available!");
                                    $('#waitingvideo').remove();
                                    printerCard.find('#webrtc-stream').append(
                                        '<input class="form-control" type="text" id="datarecv" disabled></input>'
                                    );
                                    if(spinner !== null && spinner !== undefined)
                                        spinner.stop();
                                    spinner = null;
                                },
                                ondata: function(data) {
                                    Janus.debug("We got data from the DataChannel! " + data);
                                    $('#datarecv').val(data);
                                },
                                oncleanup: function() {
                                    Janus.log(" ::: Got a cleanup notification :::");
                                    $('#waitingvideo').remove();
                                    $('#remotevideo').remove();
                                    $('#datarecv').remove();
                                    $('.no-video-container').remove();
                                    $('#bitrate').attr('disabled', true);
                                    $('#bitrateset').html('Bandwidth<span class="caret"></span>');
                                    $('#curbitrate').hide();
                                    if(bitrateTimer !== null && bitrateTimer !== undefined)
                                        clearInterval(bitrateTimer);
                                    bitrateTimer = null;
                                    $('#curres').hide();
                                    $('#simulcast').remove();
                                    simulcastStarted = false;
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
                                $('#status').removeClass('hide').text("Started").show();
                            else if(status === 'stopped')
                                stopStream();
                        } else if(msg["streaming"] === "event") {
                            // Is simulcast in place?
                            var substream = result["substream"];
                            var temporal = result["temporal"];
                            if((substream !== null && substream !== undefined) || (temporal !== null && temporal !== undefined)) {
                                if(!simulcastStarted) {
                                    simulcastStarted = true;
                                    addSimulcastButtons(temporal !== null && temporal !== undefined);
                                }
                                // We just received notice that there's been a switch, update the buttons
                                updateSimulcastButtons(substream, temporal);
                            }
                            // Is VP9/SVC in place?
                            var spatial = result["spatial_layer"];
                            temporal = result["temporal_layer"];
                            if((spatial !== null && spatial !== undefined) || (temporal !== null && temporal !== undefined)) {
                                if(!svcStarted) {
                                    svcStarted = true;
                                    addSvcButtons();
                                }
                                // We just received notice that there's been a switch, update the buttons
                                updateSvcButtons(spatial, temporal);
                            }
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
                                    $('#watch').html("Stop").removeAttr('disabled').click(stopStream);
                                },
                                error: function(error) {
                                    Janus.error("WebRTC error:", error);
                                    bootbox.alert("WebRTC error... " + JSON.stringify(error));
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
                        printerCard.find('#webrtc-stream').append('<video class="rounded centered hide" id="remotevideo" width=960 height=540 autoplay playsinline/>');
                        // Show the stream and hide the spinner when we get a playing event
                        printerCard.find("#remotevideo").bind("playing", function () {
                            $('#waitingvideo').remove();
                            if(this.videoWidth)
                                printerCard.find('#remotevideo').removeClass('hide').show();
                            var videoTracks = stream.getVideoTracks();
                            if(videoTracks === null || videoTracks === undefined || videoTracks.length === 0)
                                return;
                        });
                    }
                    Janus.attachMediaStream($('#remotevideo').get(0), stream);
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

// Helpers to create Simulcast-related UI, if enabled
function addSimulcastButtons(temporal) {
	$('#curres').parent().append(
		'<div id="simulcast" class="btn-group-vertical btn-group-vertical-xs pull-right">' +
		'	<div class"row">' +
		'		<div class="btn-group btn-group-xs" style="width: 100%">' +
		'			<button id="sl-2" type="button" class="btn btn-primary" data-toggle="tooltip" title="Switch to higher quality" style="width: 33%">SL 2</button>' +
		'			<button id="sl-1" type="button" class="btn btn-primary" data-toggle="tooltip" title="Switch to normal quality" style="width: 33%">SL 1</button>' +
		'			<button id="sl-0" type="button" class="btn btn-primary" data-toggle="tooltip" title="Switch to lower quality" style="width: 34%">SL 0</button>' +
		'		</div>' +
		'	</div>' +
		'	<div class"row">' +
		'		<div class="btn-group btn-group-xs hide" style="width: 100%">' +
		'			<button id="tl-2" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 2" style="width: 34%">TL 2</button>' +
		'			<button id="tl-1" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 1" style="width: 33%">TL 1</button>' +
		'			<button id="tl-0" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 0" style="width: 33%">TL 0</button>' +
		'		</div>' +
		'	</div>' +
		'</div>');
	// Enable the simulcast selection buttons
	$('#sl-0').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Switching simulcast substream, wait for it... (lower quality)", null, {timeOut: 2000});
			if(!$('#sl-2').hasClass('btn-success'))
				$('#sl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#sl-1').hasClass('btn-success'))
				$('#sl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#sl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			streaming.send({message: { request: "configure", substream: 0 }});
		});
	$('#sl-1').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Switching simulcast substream, wait for it... (normal quality)", null, {timeOut: 2000});
			if(!$('#sl-2').hasClass('btn-success'))
				$('#sl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#sl-1').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			if(!$('#sl-0').hasClass('btn-success'))
				$('#sl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", substream: 1 }});
		});
	$('#sl-2').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Switching simulcast substream, wait for it... (higher quality)", null, {timeOut: 2000});
			$('#sl-2').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			if(!$('#sl-1').hasClass('btn-success'))
				$('#sl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#sl-0').hasClass('btn-success'))
				$('#sl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", substream: 2 }});
		});
	if(!temporal)	// No temporal layer support
		return;
	$('#tl-0').parent().removeClass('hide');
	$('#tl-0').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping simulcast temporal layer, wait for it... (lowest FPS)", null, {timeOut: 2000});
			if(!$('#tl-2').hasClass('btn-success'))
				$('#tl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#tl-1').hasClass('btn-success'))
				$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#tl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			streaming.send({message: { request: "configure", temporal: 0 }});
		});
	$('#tl-1').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping simulcast temporal layer, wait for it... (medium FPS)", null, {timeOut: 2000});
			if(!$('#tl-2').hasClass('btn-success'))
				$('#tl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-info');
			if(!$('#tl-0').hasClass('btn-success'))
				$('#tl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", temporal: 1 }});
		});
	$('#tl-2').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping simulcast temporal layer, wait for it... (highest FPS)", null, {timeOut: 2000});
			$('#tl-2').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			if(!$('#tl-1').hasClass('btn-success'))
				$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#tl-0').hasClass('btn-success'))
				$('#tl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", temporal: 2 }});
		});
}

function updateSimulcastButtons(substream, temporal) {
	// Check the substream
	if(substream === 0) {
		toastr.success("Switched simulcast substream! (lower quality)", null, {timeOut: 2000});
		$('#sl-2').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#sl-1').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#sl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
	} else if(substream === 1) {
		toastr.success("Switched simulcast substream! (normal quality)", null, {timeOut: 2000});
		$('#sl-2').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#sl-1').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
		$('#sl-0').removeClass('btn-primary btn-success').addClass('btn-primary');
	} else if(substream === 2) {
		toastr.success("Switched simulcast substream! (higher quality)", null, {timeOut: 2000});
		$('#sl-2').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
		$('#sl-1').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#sl-0').removeClass('btn-primary btn-success').addClass('btn-primary');
	}
	// Check the temporal layer
	if(temporal === 0) {
		toastr.success("Capped simulcast temporal layer! (lowest FPS)", null, {timeOut: 2000});
		$('#tl-2').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#tl-1').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#tl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
	} else if(temporal === 1) {
		toastr.success("Capped simulcast temporal layer! (medium FPS)", null, {timeOut: 2000});
		$('#tl-2').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#tl-1').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
		$('#tl-0').removeClass('btn-primary btn-success').addClass('btn-primary');
	} else if(temporal === 2) {
		toastr.success("Capped simulcast temporal layer! (highest FPS)", null, {timeOut: 2000});
		$('#tl-2').removeClass('btn-primary btn-info btn-success').addClass('btn-success');
		$('#tl-1').removeClass('btn-primary btn-success').addClass('btn-primary');
		$('#tl-0').removeClass('btn-primary btn-success').addClass('btn-primary');
	}
}

// Helpers to create SVC-related UI for a new viewer
function addSvcButtons() {
	if($('#svc').length > 0)
		return;
	$('#curres').parent().append(
		'<div id="svc" class="btn-group-vertical btn-group-vertical-xs pull-right">' +
		'	<div class"row">' +
		'		<div class="btn-group btn-group-xs" style="width: 100%">' +
		'			<button id="sl-1" type="button" class="btn btn-primary" data-toggle="tooltip" title="Switch to normal resolution" style="width: 50%">SL 1</button>' +
		'			<button id="sl-0" type="button" class="btn btn-primary" data-toggle="tooltip" title="Switch to low resolution" style="width: 50%">SL 0</button>' +
		'		</div>' +
		'	</div>' +
		'	<div class"row">' +
		'		<div class="btn-group btn-group-xs" style="width: 100%">' +
		'			<button id="tl-2" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 2 (high FPS)" style="width: 34%">TL 2</button>' +
		'			<button id="tl-1" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 1 (medium FPS)" style="width: 33%">TL 1</button>' +
		'			<button id="tl-0" type="button" class="btn btn-primary" data-toggle="tooltip" title="Cap to temporal layer 0 (low FPS)" style="width: 33%">TL 0</button>' +
		'		</div>' +
		'	</div>' +
		'</div>'
	);
	// Enable the VP8 simulcast selection buttons
	$('#sl-0').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Switching SVC spatial layer, wait for it... (low resolution)", null, {timeOut: 2000});
			if(!$('#sl-1').hasClass('btn-success'))
				$('#sl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#sl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			streaming.send({message: { request: "configure", spatial_layer: 0 }});
		});
	$('#sl-1').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Switching SVC spatial layer, wait for it... (normal resolution)", null, {timeOut: 2000});
			$('#sl-1').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			if(!$('#sl-0').hasClass('btn-success'))
				$('#sl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", spatial_layer: 1 }});
		});
	$('#tl-0').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping SVC temporal layer, wait for it... (lowest FPS)", null, {timeOut: 2000});
			if(!$('#tl-2').hasClass('btn-success'))
				$('#tl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#tl-1').hasClass('btn-success'))
				$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#tl-0').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			streaming.send({message: { request: "configure", temporal_layer: 0 }});
		});
	$('#tl-1').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping SVC temporal layer, wait for it... (medium FPS)", null, {timeOut: 2000});
			if(!$('#tl-2').hasClass('btn-success'))
				$('#tl-2').removeClass('btn-primary btn-info').addClass('btn-primary');
			$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-info');
			if(!$('#tl-0').hasClass('btn-success'))
				$('#tl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", temporal_layer: 1 }});
		});
	$('#tl-2').removeClass('btn-primary btn-success').addClass('btn-primary')
		.unbind('click').click(function() {
			toastr.info("Capping SVC temporal layer, wait for it... (highest FPS)", null, {timeOut: 2000});
			$('#tl-2').removeClass('btn-primary btn-info btn-success').addClass('btn-info');
			if(!$('#tl-1').hasClass('btn-success'))
				$('#tl-1').removeClass('btn-primary btn-info').addClass('btn-primary');
			if(!$('#tl-0').hasClass('btn-success'))
				$('#tl-0').removeClass('btn-primary btn-info').addClass('btn-primary');
			streaming.send({message: { request: "configure", temporal_layer: 2 }});
		});
}
