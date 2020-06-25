function updateActionsSection(actionsDiv, printerMap, printerId, alertShowing, printerWs) {
    var printer = printerMap.get(printerId);
    actionsDiv.html(Mustache.template('printer_actions').render({
        printerId: printerId,
        status: printer.status,
        printerStateTxt: _.get(printer, 'status.state.text', ''),
        printerPaused: isPrinterPaused(_.get(printer, 'status.state')),
        idle: isPrinterIdle(_.get(printer, 'status.state')),
        error: printerHasError(_.get(printer, 'status.state')),
        disconnected: isPrinterDisconnected(_.get(printer, 'status.state')),
    }));

    actionsDiv.find("#print-pause-resume").click(pauseResumeBtnClicked);
    actionsDiv.find('#print-cancel').click(cancelBtnClicked);
    actionsDiv.find('#connect-printer').click(connectBtnClicked);
    actionsDiv.find('#start-print').click(startPrintBtnClicked);

    function pauseResumeBtnClicked() {
        var toResume = _.lowerCase(_.trim($(this).text())) === 'resume';
        if (alertShowing && toResume) {
            notFailedBtnClicked(event, printerId, true);
        } else {
            sendPrinterAction(printerId, toResume ? '/resume_print/' : '/pause_print/', true);
        }
    }

    function cancelBtnClicked() {
        Confirm.fire({
            text: 'Once cancelled, the print can no longer be resumed.',
        }).then(function (result) {
            if (result.value) {  // When it is confirmed
                sendPrinterAction(printerId, '/cancel_print/', true);
            }
        });
    }

    function connectBtnClicked() {
        actionsDiv.find('button#connect-printer').attr("disabled", true);
        actionsDiv.find('button#connect-printer i.fa-spin').show();

        printerWs.passThruToPrinter(printerId, { func: 'get_connection_options', target: '_printer' }, function (err, connectionOptions) {
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
                    html: Mustache.template('connect_printer').render({ connectionOptions: connectionOptions }),
                    confirmButtonText: 'Connect',
                    showCancelButton: true,
                    onOpen: function (e) {
                        $(e).find('select.selectpicker').selectpicker();
                    },
                }).then((result) => {
                    if (result.value) {
                        var args = [$('select#id-port').val(),];
                        if ($('select#id-baudrate').val()) {
                            args.push($('select#id-baudrate').val());
                        }
                        printerWs.passThruToPrinter(printerId, { func: 'connect', target: '_printer', args: args });
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
        }).done(function (gcodeFiles) {
            gcodeFiles.forEach(function (gcodeFile) {
                gcodeFile.created_at = moment(gcodeFile.created_at).fromNow();
                gcodeFile.num_bytes = filesize(gcodeFile.num_bytes);
            });

            Swal.fire({
                title: 'Print on ' + printer.name,
                html: Mustache.template('start_print').render({ gcodeFiles: gcodeFiles }),
                showConfirmButton: false,
                showCancelButton: true,
                onOpen: function (gcodeDiv) {
                    $(gcodeDiv).find("#myInput").on("keyup", function () {
                        var value = $(this).val().toLowerCase();
                        $(gcodeDiv).find(".card").filter(function () {
                            $(this).toggle($(this).find(".gcode-filename").text().toLowerCase().indexOf(value) > -1)
                        });
                    });
                    $(gcodeDiv).find('button.send-print').on('click', function () {
                        actionsDiv.find('button').attr("disabled", true);
                        $(this).find('i.fa-spin').show();

                        var gcodeFileId = $(this).data('gcode-file-id');
                        printerWs.passThruToPrinter(printerId,
                            { func: 'download', target: 'file_downloader', args: _.filter(gcodeFiles, { id: gcodeFileId }) },
                            function (err, ret) {
                                if (ret.error) {
                                    Toast.fire({
                                        type: 'error',
                                        title: ret.error,
                                    });
                                    return;
                                }

                                Swal.fire({
                                    html: Mustache.template('waiting_download').render({ gcodeFiles: gcodeFiles, targetPath: ret.target_path, printer: printer }),
                                    showConfirmButton: false
                                });

                                function checkPrinterStatus() {
                                    var updatedPrinter = printerMap.get(printerId);
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
