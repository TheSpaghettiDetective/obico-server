function updateActionsSection(actionsDiv, printerList, printerId, alertShowing, printerWs) {
    var printer = printerList[printerId];
    var printerState = _.get(printer, 'status.state.flags');
    var printerStateTxt = _.get(printer, 'status.state.text');

    actionsDiv.html(Mustache.template('printer_actions').render({
        dhInverseIconSrc: dhInverseIconSrc,
        alertShowing: alertShowing,
        status: printer.status,
        printerPaused: _.get(printerState, 'paused'),
        idle: printerStateTxt == 'Operational',
        error: _.get(printerState, 'error'),
        disconnected: _.get(printerState, 'closedOrError'),
    }));

    actionsDiv.find("#print-pause-resume").click(pauseResumeBtnClicked);
    actionsDiv.find('#print-cancel').click(cancelBtnClicked);
    actionsDiv.find('#connect-printer').click(connectBtnClicked);
    actionsDiv.find('#start-print').click(startPrintBtnClicked);

    function pauseResumeBtnClicked() {
        var btn = $(this);
        sendPrinterCommand(printerId, _.lowerCase(_.trim(btn.text())) === 'pause' ? '/pause_print/' : '/resume_print/');
    }

    function cancelBtnClicked() {
        Confirm.fire({
            text: 'Once cancelled, the print can no longer be resumed.',
        }).then(function (result) {
            if (result.value) {  // When it is confirmed
                sendPrinterCommand(printerId, '/cancel_print/');
            }
        });
    }

    function connectBtnClicked() {
        actionsDiv.find('button#connect-printer').attr("disabled", true);
        actionsDiv.find('button#connect-printer i.fa-spin').show();

        printerWs.passThruToPrinter(printerId, {func: 'get_connection_options'}, function(err, connectionOptions) {
            if (err) {
                Toast.fire({
                    type: 'error',
                    title: 'Failed to contact OctoPrint!',
                });
            } else {
                if (connectionOptions.ports.length < 1) {
                    Toast.fire({
                        type: 'error',
                        title: 'Uh-Oh. No printer is found on the serial port.',
                    });
                    return;
                }
                Swal.fire({
                    html: Mustache.template('connect_printer').render({connectionOptions: connectionOptions}),
                    confirmButtonText: 'Connect',
                    showCancelButton: true,
                    onOpen: function(e){
                        $(e).find('select.selectpicker').selectpicker();
                    },
                }).then((result) => {
                    if (result.value) {
                        printerWs.passThruToPrinter(printerId, {func: 'connect', args: [
                            $('select#id-port').val(),
                            $('select#id-baudrate').val(),
                        ]});
                    }
                });

                actionsDiv.find('button#connect-printer').attr("disabled", false);
                actionsDiv.find('button#connect-printer i.fa-spin').hide();
            }
        });
    }

    function startPrintBtnClicked() {
        if (!isProAccount) {
            Swal.fire({
                title: 'Wait!',
                html: '<h5 class="mb-3">You need to <a href="/ent/pricing/">upgrade to Pro plan</a> to start a remote print job. </h5>\
                <p>Remote G-Code upload and print start is a Pro feature.</p>\
                <p>With <a href="/ent/pricing/">little more than 1 Starbucks per month</a>, you can upgrade to a Pro account.</p>'
            });
            return;
        }

        $.ajax({
            url: '/api/v1/gcodes/',
            type: 'GET',
            dataType: 'json',
        }).done(function(gcodeFiles) {
            Swal.fire({
                html: Mustache.template('start_print').render({gcodeFiles: gcodeFiles}),
                showConfirmButton: false,
                showCancelButton: true,
                onOpen: function(gcodeDiv){
                    $(gcodeDiv).find("#myInput").on("keyup", function() {
                        var value = $(this).val().toLowerCase();
                        $(e).find(".card").filter(function() {
                            $(this).toggle($(this).find(".gcode-filename").text().toLowerCase().indexOf(value) > -1)
                        });
                    });
                    $(gcodeDiv).find('button.send-print').on('click', function() {
                        actionsDiv.find('button').attr("disabled", true);
                        $(this).find('i.fa-spin').show();

                        var gcodeFileId = $(this).data('gcode-file-id');
                        printerWs.passThruToPrinter(printerId,
                            {func: 'download', target: 'file_downloader', args: _.filter(gcodeFiles, {id: gcodeFileId})},
                            function(err, ret) {
                                if (err) {
                                    Toast.fire({
                                        type: 'error',
                                        title: 'Failed to contact OctoPrint!',
                                    });
                                    return;
                                }
                                Swal.fire({
                                    html: Mustache.template('waiting_download').render({gcodeFiles: gcodeFiles, targetPath: ret, printer: printer}),
                                    showConfirmButton: false
                                });

                                function checkPrinterStatus() {
                                    var updatedPrinter = printerList[printerId];
                                    if (_.get(updatedPrinter, 'status.state.text') == 'Operational') {
                                        setTimeout(checkPrinterStatus, 1000);
                                    } else {
                                        Swal.close();
                                    }
                                }
                                checkPrinterStatus();
                        });
                    });
                },
            });
        });
    }
}
