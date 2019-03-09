$(document).ready(function () {
    var wsList = [];

    function removeWebSocket(ws) {
        _.remove(wsList, function(ele) {
            return ele === ws;
        })
    }

    function openPrinterWebSockets() {
        $('.printer-card').each(function () {
            var printerCard = $(this);
            var printerId = printerCard.attr('id');
            var printerSocket = new WebSocket(
                window.location.protocol.replace('http', 'ws') + '//' + window.location.host +
                '/ws/web/' + printerId + '/');

            wsList.push(printerSocket);
            printerSocket.onmessage = function (e) {
                var printer = JSON.parse(e.data);
                updatePrinterCard(printer, printerCard);
            };

            printerSocket.onclose = function (e) {
                removeWebSocket(printerSocket);
            };
            printerSocket.onerror = function (e) {
                printerSocket.close();
            };
        });
    }

    function closePrinterWebSockets() {
        _.forEach(wsList, function(ws) {
            ws.close();
        });
    }

    ifvisible.on("blur", function(){
        closePrinterWebSockets();
    });
    ifvisible.on("focus", function(){
        openPrinterWebSockets();
    });
    openPrinterWebSockets();

    function sendPrinterCommand(printerId, command) {
        $.ajax({
            url: '/api/printers/' + printerId + command,
            type: 'GET',
            dataType: 'json',
        }).done(function () {
            Toast.fire({
                type: 'success',
                title: 'Successfully sent command to OctoPrint! It may take a while to be executed by OctoPrint.',
            });
        });
    }

    $('.printer-card').each(function () {
        var printerCard = $(this);
        var printerId = printerCard.attr('id');

        printerCard.find("#print-pause-resume").click(function () {
            var btn = $(this);
            sendPrinterCommand(printerId, btn.text() === 'Pause' ? '/pause_print/' : '/resume_print/');
        });

        printerCard.find('#print-cancel').click(function () {
            Confirm.fire({
                text: 'Once cancelled, the print can no longer be resumed.',
            }).then(function (result) {
                if (result.value) {  // When it is confirmed
                    sendPrinterCommand(printerId, '/cancel_print/');
                }
            });
        });

        printerCard.find('#delete-print').click(function () {
            Confirm.fire({
            }).then(function (result) {
                if (result.value) {  // When it is confirmed
                    window.location.href = "/printers/" + printerId + "/delete/";
                }
            });
        });

        printerCard.find('#not-a-failure').click(function (e) {
            if (printerCard.find("#print-pause-resume").text() == 'Resume') {
                Confirm.fire({
                    title: 'Noted!',
                    text: 'What do you want to do now?',
                    confirmButtonText: 'Resume print',
                    cancelButtonText: 'Resume, and don\'t alert again for this print',
                }).then(function (result) {
                    if (result.value) {
                        sendPrinterCommand(printerId, '/resume_print/?mute_alert=true');   // Currently we mute alert in case of any false alarm to avoid bounced false alarms
                    } else if (result.dismiss == 'cancel') {
                        sendPrinterCommand(printerId, '/resume_print/?mute_alert=true');
                    }
                });
            } else {
                $.ajax({
                    url: '/api/printers/' + printerId + '/acknowledge_alert/',
                    type: 'GET',
                    dataType: 'json',
                });
                Swal.fire({
                    title: 'Noted!',
                    text: 'Thank you for your feedback.',
                    timer: 2500
                })
            }

            e.preventDefault();
        })
    });

    function updatePrinterCard(printer, printerCard) {

        if (printer.status && printer.current_print_alerted_at && !printer.alert_acknowledged_at) {
            printerCard.find(".failure-alert").show();
        } else {
            printerCard.find(".failure-alert").hide();
        }

        printerCard.find("img.webcam_img").attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));

        updateGauge(printerCard.find('#tangle-index'), _.get(printer, 'printerprediction.ewm_mean', 0));

        if (printer.status && printer.current_print_filename) {
            printerCard.find("#print-file-name").text(printer.current_print_filename);
            printerCard.find('.print-status button').prop('disabled', false);
        } else {
            printerCard.find("#print-file-name").text('-');
            printerCard.find('.print-status button').prop('disabled', true);
        }

        if (_.get(printer, 'status.text') === 'Paused') {
            printerCard.find("#print-pause-resume").addClass('btn-success').removeClass('btn-warning').text('Resume');
        } else {
            printerCard.find("#print-pause-resume").removeClass('btn-success').addClass('btn-warning').text('Pause');
        }

        var secondsLeft = _.get(printer, 'status.seconds_left', -1);
        printerCard.find("#time-left").text((secondsLeft > 0) ? moment.duration(secondsLeft, 'seconds').humanize() : '-');
    }

    /*** Swal Mixins */

    var Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 5000,
    });

    var Confirm = Swal.mixin({
        title: 'Are you sure?',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
    });
});
