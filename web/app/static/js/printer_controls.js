"use strict";


$(document).ready(function () {
    var printerCard = $('.printer-card');
    var printerId = printerCard.attr('id');
    var wsUri = printerCard.data('share-token') ?
    '/ws/shared/web/' + printerCard.data('share-token') + '/' : '/ws/web/' + printerId + '/';
    var printerWs = new PrinterWebSocket();

    printerWs.openPrinterWebSockets(printerId, wsUri, function(msg) {
        printerList[printerId] = msg;
    });

    $('.printer-controls button').on('click', function() {
        var ele = $(this);
        var axes = ele.data('axis');

        if (ele.data('dir') == 'home') {
            if (axes == 'xy') {
                axes = ['x', 'y'];
            }
            printerWs.passThruToPrinter(printerId, {func: 'home', target: '_printer', args: [axes]});
        } else {
            var a = ele.data('dir') == 'up' ? 1 : -1;
            var distance = parseFloat(printerCard.find('.btn-group-toggle input:checked').val());
            var jogArgs = {}
            jogArgs[axes] = a*distance;
            printerWs.passThruToPrinter(printerId, {func: 'jog', target: '_printer', args: [jogArgs]});
        }
    });
});
