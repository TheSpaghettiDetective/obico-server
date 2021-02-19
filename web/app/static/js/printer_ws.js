// TODO: delete me after switching to Vue

"use strict";

function PrinterWebSocket() {
    var self = this;

    self.desiredWsList = new Map();
    self.wsList = new Map();
    self.passthruQueue = new Map();

    ifvisible.on("blur", function(){
        closeWebSockets();
    });
    ifvisible.on("focus", function(){
        self.desiredWsList.forEach( function(args, printerId) {
            self.openPrinterWebSockets(printerId, args[0], args[1]);
        });
    });

    self.openPrinterWebSockets = function(printerId, wsUri, onMessageReceived) {

        self.desiredWsList.set(printerId, [wsUri, onMessageReceived]);

        var printerSocket = new WebSocket( window.location.protocol.replace('http', 'ws') + '//' + window.location.host + wsUri);
        self.wsList.set(printerId, printerSocket);
        printerSocket.onmessage = function (e) {
            var msg = JSON.parse(e.data)
            if ('passthru' in msg) {
              printerSocket.on_passThruMessage(msg);
            } else {
              onMessageReceived(msg);
            }
        };

        printerSocket.on_passThruMessage = function (msg) {
          if ('passthru' in msg) {
              var refId = msg.passthru.ref;
              if (refId && self.passthruQueue.get(refId)) {
                  var callback = self.passthruQueue.get(refId);
                  self.passthruQueue.delete(refId);
                  callback(null, msg.passthru.ret);
              }
          }
        };

        ensureWebsocketClosed(printerSocket);
        setTimeout( function () { heartbeat(printerSocket); }, 30*1000);
    }


    self.passThruToPrinter = function(printerId, msg, callback) {
        var pSocket = self.wsList.get(printerId);
        let msgObj = {passthru: msg};
        if (pSocket) {
            if (callback) {
                var refId = Math.random().toString();
                self.passthruQueue.set(refId, callback);
                _.assign(msg, {ref: refId});
                setTimeout(function() {
                    if (self.passthruQueue.has(refId)) {
                        Toast.fire({
                            type: 'error',
                            title: 'Failed to contact OctoPrint, or you have NOT upgraded to the latest TSD plugin version.',
                        });
                    }
                }, 10*1000);
            }
            pSocket.send(JSON.stringify(msgObj));
            return msgObj;
        } else {
            if (callback){
                callback("Message not passed through. No suitable WebSocket.");
            }
        }
    }

    // Helper methods

    function ensureWebsocketClosed(ws) {
        ws.onclose = function (e) {
            self.wsList.forEach( function(v, k) {
                if (v == ws) {
                    self.wsList.delete(k);
                }
            });
        };
        ws.onerror = function (e) {
            ws.close();
        };
    }

    function closeWebSockets() {
        self.wsList.forEach( function(v) {
            v.close();
        });
    }

    // Heartbeat to maintain the presence of connection
    // Adapted from https://stackoverflow.com/questions/50876766/how-to-implement-ping-pong-request-for-websocket-connection-alive-in-javascript

    function heartbeat(printerSocket) {
        if (!printerSocket) return;
        if (printerSocket.readyState !== 1) return;
        printerSocket.send(JSON.stringify({}));
        setTimeout( function () { heartbeat(printerSocket); }, 30*1000);
    }
}
