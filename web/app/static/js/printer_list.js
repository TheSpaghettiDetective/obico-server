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

    function printerGet(printerId, uri, callback) {
        $.ajax({
            url: '/api/printers/' + printerId + uri,
            type: 'GET',
            dataType: 'json',
        }).done(function(result) { callback(result); });
    }

    function sendPrinterCommand(printerId, command) {
        printerGet(printerId, command, function () {
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

        printerCard.find('input.alert-toggle').on('change', function (e) {
            var muteAlert = $(this).is(':checked');
            printerGet(printerId, '/mute_current_print/?mute_alert=' + muteAlert, function(printer) {
                updatePrinterCard(printer, printerCard);
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

        var printFilenameDiv = printerCard.find(".print-filename");
        var printerNameDiv = printerCard.find(".printer-name");

        if (printer.current_print && printer.current_print.filename) {
            printFilenameDiv.text(printer.current_print.filename);
            printFilenameDiv.show();
            printerNameDiv.addClass("secondary-title");
        } else {
            printFilenameDiv.hide();
            printerNameDiv.removeClass("secondary-title");
        }

        if (printer.current_print && printer.current_print.alerted_at && !printer.current_print.alert_acknowledged_at) {
            printerCard.find(".failure-alert").show();
        } else {
            printerCard.find(".failure-alert").hide();
        }

        if (printer.current_print) {
            printerCard.find(".mute-toggle").show();
        } else {
            printerCard.find(".mute-toggle").hide();
        }

        printerCard.find("img.webcam_img").attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));

        updateGauge(printerCard.find('.tangle-index'), _.get(printer, 'printerprediction.ewm_mean', 0));

        if (printer.status && printer.current_print) {
            printerCard.find('.print-status button').prop('disabled', false);
        } else {
            printerCard.find('.print-status button').prop('disabled', true);
        }

        if (_.get(printer, 'status.text') === 'Paused') {
            printerCard.find("#print-pause-resume").addClass('btn-success').removeClass('btn-warning').text('Resume');
        } else {
            printerCard.find("#print-pause-resume").removeClass('btn-success').addClass('btn-warning').text('Pause');
        }

        printerCard.find(".alert-toggle").prop("checked", printer.current_print && printer.current_print.alert_muted_at);

        var secondsLeft = _.get(printer, 'status.progress.printTimeLeft');
        var secondsTotal = _.get(printer, 'status.progress.printTime');
        if (secondsLeft || secondsTotal ) {
            printerCard.find("#print-time").show();
            $("#print-time-remaining").html(toDurationBlock(secondsLeft));
            $("#print-time-total").html(toDurationBlock(secondsTotal));
        } else {
            printerCard.find("#print-time").hide();
        }

        var temperatures = [];
        ['bed', 'tool0', 'tool1'].forEach( function(tempKey) {
            var temp = _.get(printer, 'status.temperatures.' + tempKey);
            if (temp) {
                temp.actual = parseFloat(temp.actual).toFixed(1);
                temp.target = parseFloat(temp.target).toFixed();
                Object.assign(temp, {toolName: _.capitalize(tempKey)});
                temperatures.push(temp);
            }
        });

        $("#status_temp_block").html(Mustache.template('status_temp').render({temperatures: temperatures, show: temperatures.length > 0}));
    }

    function toDurationBlock(seconds) {
        var durationObj;
        if (!seconds) {
            durationObj = {valid: false};
        } else {
            var d = moment.duration(seconds, 'seconds')
            var h = Math.floor(d.asHours());
            var m = d.minutes();
            var s = d.seconds();
            durationObj = {valid: true, hours: h, showHours: (h>0), minutes: m, showMinutes: (m>0), seconds: s, showSeconds: (m==0)}
        }
        return Mustache.template('duration_block').render(durationObj);
    }
});
