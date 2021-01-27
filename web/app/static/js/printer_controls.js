// TODO: Delete me after switching to Vue

"use strict";


$(document).ready(function () {
    var MM_PER_STEP_PREF = 'mm-per-step';

    var printerCard = $('.printer-card');
    var printerId = printerCard.attr('id');
    var wsUri = printerCard.data('share-token') ?
    '/ws/share_token/web/' + printerCard.data('share-token') + '/' : '/ws/web/' + printerId + '/';
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

    printerCard.on('gotPassThruMessage', function (e, msg) {
      printerWs.on_passThruMessage(msg)
    })

    $('.printer-controls button').on('click', function() {
        var ele = $(this);
        var axes = ele.data('axis');

        if (ele.data('dir') == 'home') {
            if (axes == 'xy') {
                axes = ['x', 'y'];
            }
            var payload = {func: 'home', target: '_printer', args: [axes]};
            var msgObj = printerWs.passThruToPrinter(printerId, payload);
            if (msgObj) {
              printerCard.trigger('sendPassThruMessage', [msgObj]);
            }
        } else {
            var distance = parseFloat(printerCard.find('.btn-group-toggle input:checked').val());
            var jogArgs = {}
            jogArgs[axes] = distance * (ele.data('dir') == 'up' ? 1 : -1);
            var payload = {func: 'jog', target: '_printer', args: [jogArgs]};
            var msgObj = printerWs.passThruToPrinter(printerId, payload);
            if (msgObj) {
              printerCard.trigger('sendPassThruMessage', [msgObj]);
            }
        }
    });


    $(".control-options :input").change(function() {
        setPrinterLocalPref(MM_PER_STEP_PREF, printerId, $(this).val());
    });

    var mmPerStep = getPrinterLocalPref(MM_PER_STEP_PREF, printerId, "10");
    var toToggleOn = printerCard.find('.btn-group-toggle input[value="' + mmPerStep + '"]')
    toToggleOn.prop('checked', true);
    toToggleOn.parent().addClass('active').siblings().removeClass('active');
});
