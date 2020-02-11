"use strict";


$(document).ready(function () {
    var printerCard = $('.printer-card');
    var printerId = printerCard.attr('id');
    var wsUri = printerCard.data('share-token') ?
    '/ws/shared/web/' + printerCard.data('share-token') + '/' : '/ws/web/' + printerId + '/';
    var printerWs = new PrinterWebSocket();

    printerWs.openPrinterWebSockets(printerId, wsUri, function(printer) {
        var controlsDiv = printerCard.find('.card-body');
        var idle = _.get(printer, 'status.state.text') == "Operational";
        if (idle) {
            controlsDiv.removeClass('overlay');
            controlsDiv.find('.overlay-top').hide();
        } else {
            controlsDiv.addClass('overlay');
            controlsDiv.find('.overlay-top').show();
        }

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
            var distance = parseFloat(printerCard.find('.btn-group-toggle input:checked').val());
            var jogArgs = {}
            jogArgs[axes] = distance * (ele.data('dir') == 'up' ? 1 : -1);
            printerWs.passThruToPrinter(printerId, {func: 'jog', target: '_printer', args: [jogArgs]});
        }
    });
});
