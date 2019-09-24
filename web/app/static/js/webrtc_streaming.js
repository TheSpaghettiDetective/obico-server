$(document).ready(function() {
    var streamList = [];

    function removeFromList(janus) {
        _.remove(streamList, function(ele) {
            return ele === janus;
        })
    }

    function startStream(streamId, streaming) {
        var body = { "request": "watch", id: parseInt(streamId) };
        streaming.send({"message": body});
    }

    function stopStream(streaming) {
        var body = { "request": "stop" };
        streaming.send({"message": body});
        streaming.hangup();
    }

    function stopAllStreaming() {
        _.forEach(streamList, function(s) {
            stopStream(s.streaming);
        });
    }

    function resumeAllStreaming() {
        _.forEach(streamList, function(s) {
            startStream(s.id, s.streaming);
        });
    }

    ifvisible.on("blur", function(){
        stopAllStreaming();
    });
    ifvisible.on("focus", function(){
        resumeAllStreaming();
    });

	// Initialize the library (all console debuggers enabled)
	Janus.init({debug: "all", callback: function() {
        if(!Janus.isWebrtcSupported()) {
            return;
        }

        $('.printer-card').each(function () {
            var opaqueId = "streamingtest-"+Janus.randomString(12);

            var printerCard = $(this);
            var printerId = printerCard.attr('id');

            printerCard.on("playing", ".remotevideo", function () {
                if(this.videoWidth)
                    printerCard.find('.remotevideo').removeClass('hide').show();
                var videoTracks = stream.getVideoTracks();
                if(videoTracks === null || videoTracks === undefined || videoTracks.length === 0)
                    return;
            });

            printerCard.on("click", ".remotevideo", function() {
                swapthumbnailAndFull($(this));
            });

            var streaming;

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
                                printerCard.find('.remotevideo').hide();
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
                            console.log("Started");
                        else if(status === 'stopped')
                            stopStream(streaming);
                    }
                } else if(msg["error"] !== undefined && msg["error"] !== null) {
                    Janus.error(msg);
                    stopStream(streaming);
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
                Janus.attachMediaStream(printerCard.find('.remotevideo').get(0), stream);
                var videoTracks = stream.getVideoTracks();
                if(videoTracks === null || videoTracks === undefined || videoTracks.length === 0) {
                    // No remote video
                    printerCard.find('.remotevideo').hide();
                } else {
                    printerCard.find('.remotevideo').removeClass('hide').show();
                }
            }

            function updateStreamsList() {
                var body = { "request": "list" };
                Janus.debug("Sending message (" + JSON.stringify(body) + ")");
                streaming.send({"message": body, success: function(result) {
                    var stream = _.get(result, 'list[0]');
                    if (stream) {
                        startStream(stream.id, streaming);
                        streamList.push({id: stream.id, streaming: streaming});
                    }
                }});
            }

        });

    }});

    		/*
            const SOI = new Uint8Array(2);
            SOI[0] = 0xFF;
            SOI[1] = 0xD8;
*/
const SOI = String.fromCharCode(0xFF) + String.fromCharCode(0xD8);
var lengthRegex = /Content-Length:\s*(\d+)/i;
    const CONTENT_LENGTH = 'Content-Length';
    const TYPE_JPEG = 'image/jpeg';

function Decoder(onFrame) {
        this.onFrame = onFrame;
        this.headers = '';
        this.contentLength = -1;
        this.imageBuffer = null;
this.residue = '';
        this.bytesRead = 0;
        this.lll = 0;

/*
this.buffer = null;
this.reading = false;
this.contentLength = null;
this.bytesWritten = 0;
*/
}

/*
    var getLength = function(headers) {
        var contentLength = -1;
        var headerArray = headers.split('\n');
for (var i = 0; i < headerArray.length; i++) {
            const pair = headerArray[i].split(':');
            if (pair[0] === CONTENT_LENGTH) {
            contentLength = pair[1];
            }
}
        return contentLength;
    };
*/
Decoder.prototype.onMessage = function(value) {

    //value = Uint8Array.from(atob(value), function(c) { return c.charCodeAt(0) });
    value = atob(value);
                this.lll += value.length;
    //console.log(this.lll);
    if (this.residue.length > 0) {
        value = this.residue + value;
        this.residue = '';
    }

    //still looking for header
                if (this.contentLength < 0) {
        var jpgStart = value.indexOf(SOI);
        if (jpgStart >= 0) {
            this.contentLength = parseInt((lengthRegex.exec(value.slice(0, jpgStart)) || [])[1]);
                        this.imageBuffer = value.slice(jpgStart);
        this.bytesRead += this.imageBuffer.length;
        return;
        }
/*
                for ( var index =0; index < value.length; index++) {

                    // we've found start of the frame. Everything we've read till now is the header.
                    if (value[index] === SOI[0] && value[index+1] === SOI[1]) {
                        // console.log('header found : ' + newHeader);
                        this.contentLength = parseInt(getLength(this.headers));
                        // console.log("Content Length : " + newContentLength);
                        //this.imageBuffer = new Uint8Array(new ArrayBuffer(this.contentLength));
                        this.imageBuffer = '';
                    }
                    // we're still reading the header.
                    if (this.contentLength < 0) {
                        this.headers += value[index];
                    }
                    // we're now reading the jpeg.
                    else {
        var jpgdata = value.slice(index);
        //this.imageBuffer.set(jpgdata);
        this.imageBuffer += jpgdata;
        this.bytesRead += jpgdata.length;
        return;
                    }
                }
*/
    }
                // We are in the middle of the jpg data
    else if ((this.bytesRead + value.length) <= this.contentLength) {
        //this.imageBuffer.set(value, this.bytesRead);
        this.imageBuffer += value;
        this.bytesRead += value.length;
        //console.log(this.bytesRead);
    }
    // We are reading the last chunk of jpg data
    else {
        var remainingLength = this.contentLength - this.bytesRead;
        var jpgdata = value.slice(0, remainingLength)
        //this.imageBuffer.set(jpgdata, this.bytesRead);
        this.imageBuffer += jpgdata;
        this.bytesRead += remainingLength;
                        console.log("jpeg read with bytes : " + this.bytesRead);
        this.residue = value.slice(remainingLength)
                        this.onFrame(this.imageBuffer);
                        this.contentLength = -1;
                        this.bytesRead = 0;
                        this.headers = '';
                this.imageBuffer = null;
    }

}

/*
Decoder.prototype.onMessage = function(chunk) {
chunk = Uint8Array.from(atob(chunk), function(c) { return c.charCodeAt(0) });
var start = chunk.indexOf(SOI);
var end = chunk.indexOf(EOI);
var len = getLength(this.headers);

if (this.buffer && (this.reading || start > -1)) {
this._readFrame(chunk, start, end);
}

if (len) {
this._initFrame(+len, chunk, start, end);
}
}

Decoder.prototype._initFrame = function(len, chunk, start, end) {
this.contentLength = len;
this.buffer = Buffer.alloc(len);
this.bytesWritten = 0;

var hasStart = typeof start !== 'undefined' && start > -1;
var hasEnd = typeof end !== 'undefined' && end > -1 && end > start;

if (hasStart) {
var bufEnd = chunk.length;

if (hasEnd) {
bufEnd = end + eoi.length;
}

chunk.copy(this.buffer, 0, start, bufEnd);

this.bytesWritten = chunk.length - start;
// If we have the eoi bytes, send the frame
if (hasEnd) {
this._sendFrame();
} else {
this.reading = true;
}
}
};

Decoder.prototype._readFrame = function(chunk, start, end) {
var bufStart = start > -1 && start < end ? start : 0;
var bufEnd = end > -1 ? end + eoi.length : chunk.length;

chunk.copy(this.buffer, this.bytesWritten, bufStart, bufEnd);

this.bytesWritten += bufEnd - bufStart;

if (end > -1 || this.bytesWritten === this.contentLength) {
this._sendFrame();
} else {
this.reading = true;
}
};

Decoder.prototype._sendFrame = function() {
this.reading = false;
this.push(this.buffer);
};
*/

});
