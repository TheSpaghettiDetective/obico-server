$(document).ready(function () {
    var wsList = [];
    var printerList = [];

    /*** Websocket messaging */

    function ensureWebsocketClosed(ws) {
        ws.onclose = function (e) {
            _.remove(wsList, function(ele) {
                return ele === ws;
            })
        };
        ws.onerror = function (e) {
            ws.close();
        };
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
                printerList[printerId] = printer;
                updatePrinterCard(printerCard);
            };

            ensureWebsocketClosed(printerSocket);
        });
    }

    function closeWebSockets() {
        _.forEach(wsList, function(ws) {
            ws.close();
        });
    }

    function shouldShowAlert(printer) {
        if (!printer.current_print || !printer.current_print.alerted_at) {
            return false;
        }
        return moment(printer.current_print.alerted_at).isAfter(moment(printer.current_print.alert_acknowledged_at || 0));

    }

    ifvisible.on("blur", function(){
        closeWebSockets();
    });
    ifvisible.on("focus", function(){
        openPrinterWebSockets();
    });
    openPrinterWebSockets();

    /*** End of websocket messaging */

    /** Printer cards */
    function printerGet(printerId, uri, callback) {
        $.ajax({
            url: '/api/v1/printers/' + printerId + uri,
            type: 'GET',
            dataType: 'json',
        }).done(function(result) { callback(result); });
    }

    function sendPrinterCommand(printerId, command) {
        printerGet(printerId, command, function (result) {
            var toastHtml = '<h6>Successfully sent command to OctoPrint!</h6>' +
            '<p>It may take a while to be executed by OctoPrint.</p>';
            if (result.user_credited) {
                toastHtml += '<p>BTW <a href="/ent/detective_hours/">You just earned ' +
                '<img class="dh-icon" src="/static/img/detective-hour-inverse.png" />.</a><p>';
            }
            Toast.fire({
                type: 'success',
                html: toastHtml,
            });
        });
    }

    $('.printer-card').each(function () {
        var printerCard = $(this);
        var printerId = printerCard.attr('id');

        printerCard.find("#print-pause-resume").click(function () {
            var btn = $(this);
            sendPrinterCommand(printerId, _.lowerCase(_.trim(btn.text())) === 'pause' ? '/pause_print/' : '/resume_print/');
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

        printerCard.find('input.update-printer').on('change', function (e) {
            var formInputs = {
                action_on_failure: printerCard.find('input[name="pause_on_failure"]').prop('checked') ? 'PAUSE': 'NONE',
                watching: printerCard.find('input[name="watching"]').prop('checked'),
            }
            $.ajax({
                url: '/api/v1/printers/' + printerId + '/',
                type: 'PATCH',
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify(formInputs),
            }).done(function(result) {
                printerList[printerId] = result.printer;
                updatePrinterCard(printerCard);
            });
        });

        printerCard.find('input.alert-toggle').on('change', function (e) {
            var muteAlert = $(this).is(':checked');
            printerGet(printerId, '/mute_current_print/?mute_alert=' + muteAlert, function(result) {
                printerList[printerId] = result.printer;
                updatePrinterCard(printerCard);
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
                    html: '<a href="/ent/detective_hours/">You just earned ' + '<img class="dh-icon" src="/static/img/detective-hour-inverse.png" />' + '.</a>' +
                    '<p /><p>What do you want to do now?</p>',
                    confirmButtonText: 'Resume print',
                    cancelButtonText: 'Resume, and don\'t alert again for this print',
                }).then(function (result) {
                    if (result.value) {
                        sendPrinterCommand(printerId, '/resume_print/');
                    } else if (result.dismiss == 'cancel') {
                        sendPrinterCommand(printerId, '/resume_print/?mute_alert=true');
                    }
                });
            } else {
                $.ajax({
                    url: '/api/v1/printers/' + printerId + '/acknowledge_alert/?alert_overwrite=NOT_FAILED',
                    type: 'GET',
                    dataType: 'json',
                });
                Confirm.fire({
                    title: 'Noted!',
                    html: '<p>Thank you for your feedback.</p><p><a href="/ent/detective_hours/">You just earned ' +
                    '<img class="dh-icon" src="/static/img/detective-hour-inverse.png" />' + '.</a></p><p>Do you want to turn off watching for this print?</p>',
                    confirmButtonText: 'No. Keep on watching',
                    cancelButtonText: 'Yes. Stop watching this print',
                }).then(function (result) {
                    if (!result.value) {
                        printerGet(printerId, '/mute_current_print/?mute_alert=true', function(result) {
                            printerList[printerId] = result.printer;
                            updatePrinterCard(printerCard);
                        });
                    }
                });
            }

            e.preventDefault();
        });

        printerCard.find('.tagged-jpg').on('click', function () {
            expandThumbnailToFull($(this));
        });

        printerCard.find('button.info-section-toggle').on('click', function() {
            var ele = $(this);
            setPrinterLocalPref(ele.data('target-div'), printerId, !ele.hasClass('pressed'));
            updatePrinterCard(printerCard);
        })

        updatePrinterCard(printerCard);
    });

    function updatePrinterCard(printerCard) {
        var printerId = printerCard.attr('id');
        updateUI();

        var printer = printerList[printerId];

        if (!printer) {
            return;
        }

        // Card title
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

        // Show and expand tagged jpg view to full view if it was previously hidden automatically by stream views
        var taggedJpgEle = printerCard.find("img.tagged-jpg");
        taggedJpgEle.attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));
        if (!taggedJpgEle.is(':visible') && !taggedJpgEle.attr('src').endsWith(printer_stock_img_src)) {
            taggedJpgEle.removeClass('hide').show();
        }
        showPicInPicExpandIfNeeded(taggedJpgEle);

        // Alert section
        var pauseResumeBtn = printerCard.find("#print-pause-resume");
        var cancelBtn = printerCard.find('#print-cancel');
        if (shouldShowAlert(printer)) {
            printerCard.find(".failure-alert").show();
            pauseResumeBtn.find("img").show();
            cancelBtn.find("img").show();
        } else {
            printerCard.find(".failure-alert").hide();
            pauseResumeBtn.find("img").hide();
            cancelBtn.find("img").hide();
        }

        // Gauge
        var gaugeDiv = printerCard.find('.gauge-container');
        updateGauge(gaugeDiv.find('.tangle-index'), _.get(printer, 'printerprediction.ewm_mean', 0));
        if (printer.should_watch && _.get(printer, 'status.state.flags.printing')) {
            gaugeDiv.removeClass('overlay');
            gaugeDiv.find('.overlay-top').hide();
        } else {
            gaugeDiv.addClass('overlay');
            gaugeDiv.find('.overlay-top').show();
        }


        // Pause/Resume/Cancel buttons
        if (printer.status && printer.current_print) {
            printerCard.find('.print-actions button').prop('disabled', false);
        } else {
            printerCard.find('.print-actions button').prop('disabled', true);
        }

        if (_.get(printer, 'status.state.text') === 'Paused') {
            pauseResumeBtn.addClass('btn-success').removeClass('btn-warning');
            pauseResumeBtn.find('span').text('Resume');
        } else {
            pauseResumeBtn.removeClass('btn-success').addClass('btn-warning');
            pauseResumeBtn.find('span').text('Pause ');
        }

        // Panel settings
        if (printer.current_print ) {
            printerCard.find(".alert-toggle-container").show();
        } else {
            printerCard.find(".alert-toggle-container").hide();
        }
        printerCard.find("input.alert-toggle").prop("checked", printer.current_print && printer.current_print.alert_muted_at);

        if (printer.watching) {
            printerCard.find('#detailed-controls').show();
        } else {
            printerCard.find('#detailed-controls').hide();
        }
        if (printer.action_on_failure == 'PAUSE') {
            printerCard.find('input[name=pause_on_failure]').prop('checked', true);
            printerCard.find('label[for^=pause-toggle-] .text-muted').hide();
        } else {
            printerCard.find('input[name=pause_on_failure]').prop('checked', false);
            printerCard.find('label[for^=pause-toggle-] .text-muted').show();
        }

        // Print status
        var secondsLeft = _.get(printer, 'status.progress.printTimeLeft');
        var secondsPrinted = _.get(printer, 'status.progress.printTime');
        if (isInfoSectionOn('print-time')) {
            printerCard.find("#print-time").show();
            printerCard.find("#print-time-remaining").html(toDurationBlock(secondsLeft));
            printerCard.find("#print-time-total").html(toDurationBlock(secondsPrinted + secondsLeft));
        } else {
            printerCard.find("#print-time").hide();
        }

        var progressPct = _.get(printer, 'status.progress.completion');
        if (progressPct) {
            printerCard.find('#print-progress').css('width', progressPct+'%').attr('aria-valuenow', progressPct);
            if (progressPct > 99.9) {
                printerCard.find('#print-progress').removeClass('progress-bar-striped progress-bar-animated');
            } else {
                printerCard.find('#print-progress').addClass('progress-bar-striped progress-bar-animated');
            }
        }

        // Temperatures
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
        printerCard.find("#status_temp_block").html(Mustache.template('status_temp').render({temperatures: temperatures, show: temperatures.length > 0}));
        if (isInfoSectionOn("status_temp_block")) {
            printerCard.find("#status_temp_block").show();
        } else {
            printerCard.find("#status_temp_block").hide();
        }

        function isInfoSectionOn(sectionId) {
            return getPrinterLocalPref(sectionId,
                printerId,
                printerCard.find('button[data-target-div="' + sectionId + '"]').hasClass('pressed')
                );
        }

        function updateUI() {

            // Section visibility controls
            printerCard.find('button.info-section-toggle').each( function(index, element) {
                var sectionId = $(element).data('target-div');
                if (isInfoSectionOn(sectionId)) {
                    $(element).addClass('pressed');
                } else {
                    $(element).removeClass('pressed');
                }
            });

            // Panel settings
            if (isInfoSectionOn("panel-settings")) {
                printerCard.find("#panel-settings").show();
            } else {
                printerCard.find("#panel-settings").hide();
            }
        }
    }

    function toDurationBlock(seconds) {
        var durationObj;
        if (seconds == null || seconds == 0) {
            durationObj = {valid: false};
        } else {
            var d = moment.duration(seconds, 'seconds')
            var h = Math.floor(d.asHours());
            var m = d.minutes();
            var s = d.seconds();
            durationObj = {valid: true, hours: h, showHours: (h>0), minutes: m, showMinutes: (h>0 || m>0), seconds: s, showSeconds: (h==0 && m==0)}
        }
        return Mustache.template('duration_block').render(durationObj);
    }

    /*** End of printer card */

    function showNotificationMsgIfExisted() {
        $.ajax({
            url: '/ent/api/messages/',
            type: 'GET',
            dataType: 'json',
        }).done(function(result) {
            if (result.length > 0) {
                msg = result[0];
                opt = {
                    position: 'top-end',
                    confirmButtonText: "Gotcha! Don't show this again.",
                };
                msg_obj = JSON.parse(msg.message);
                _.assign(opt, msg_obj);
                Swal.fire(opt)
                .then(function (result) {
                    if (result.value) {
                        $.ajax({
                            url: '/ent/api/messages/' + msg.id + '/dismiss/',
                            type: 'GET',
                            dataType: 'json',
                        });
                    }
                });
            }
         });
    }

    if (isEnt) {
        showNotificationMsgIfExisted();
    }

    $('.hint').popover({
        container: 'body'
    });

});
