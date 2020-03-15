"use strict";

function notFailedBtnClicked(event, printerId, resumePrint) {
    Confirm.fire({
        title: 'Noted!',
        html: '<p>Do you want The Detective to keep watching this print?</p><small>If you select "No", The Detective will stop watching this print, but will automatically resume watching on your next print.</small>',
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
    }).then(function (result) {
        if (result.dismiss == 'cancel') {
            // Hack: So that 2 APIs are not called at the same time
            setTimeout(function() {
                sendPrinterAction(printerId, '/mute_current_print/?mute_alert=true', false);
            }, 1000);
        }
        if (resumePrint) {
            sendPrinterAction(printerId, '/resume_print/', true);
        } else {
            sendPrinterAction(printerId, '/acknowledge_alert/?alert_overwrite=NOT_FAILED', false);
        }
    });
    event.preventDefault();
}

$(document).ready(function () {
    var printerList = [];
    var printerWs = new PrinterWebSocket();

    /*** Establish websocket connections and callbacks */
    $('.printer-card').each(function () {
        var printerCard = $(this);
        var printerId = printerCard.attr('id');
        var wsUri = printerCard.data('share-token') ?
        '/ws/shared/web/' + printerCard.data('share-token') + '/' : '/ws/web/' + printerId + '/';

        printerWs.openPrinterWebSockets(printerId, wsUri, function(msg) {
            printerList[printerId] = msg;
            updatePrinterCard(printerCard);
        });
    });

    /** Printer cards */

    function shouldShowAlert(printer) {
        if (!printer.current_print || !printer.current_print.alerted_at) {
            return false;
        }
        return moment(printer.current_print.alerted_at).isAfter(moment(printer.current_print.alert_acknowledged_at || 0));

    }

    $('.printer-card').each(function () {
        var printerCard = $(this);
        var printerId = printerCard.attr('id');

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

        printerCard.find('#delete-print').click(function () {
            Confirm.fire({
            }).then(function (result) {
                if (result.value) {  // When it is confirmed
                    window.location.href = "/printers/" + printerId + "/delete/";
                }
            });
        });

        printerCard.find('#not-a-failure').click(function (e) { notFailedBtnClicked(e, printerId, false); });

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
        updateInfoSections();

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

        // Tagged jpg from webcam
        var imgUrl = _.get(printer, 'pic.img_url', printerStockImgSrc);
        var taggedJpgEle = printerCard.find('.tagged-jpg');
        taggedJpgEle.attr('src', imgUrl);

        // Nothing else needs to be done if it's a shared page. A bit hacky.
        if (typeof isOnSharedPage !== 'undefined' && isOnSharedPage)
            return;

        // Video streaming and tagged jpg display logics
        var videoEle = printerCard.find("video.remote-video");
        if (shouldShowAlert(printer)) {
            printerCard.find(".failure-alert").show();

            // Shrink video stream view to thumbnail to reveal tagged jpg if it's failing
            if (imgUrl !== printerStockImgSrc && taggedJpgEle.parent().hasClass("full")) {
                videoEle.parent().addClass("thumbnail").removeClass("full");
            }
        } else {
            printerCard.find(".failure-alert").hide();
            expandThumbnailToFull(videoEle);
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

        // Action section. Pause/Resume/Cancel and Connect buttons
        updateActionsSection(printerCard.find("#printer-actions"), printerList, printerId, shouldShowAlert(printer), printerWs);

        // Panel settings
        printerCard.find('input[name=watching]').prop('checked', printer.watching);
        if (printer.watching) {
            printerCard.find('label[for^=watching-toggle-] .text-muted').hide();
        } else {
            printerCard.find('label[for^=watching-toggle-] .text-muted').show();
        }
        printerCard.find('input[name=pause_on_failure]').prop('checked', printer.action_on_failure == 'PAUSE');
        if (printer.action_on_failure == 'PAUSE') {
            printerCard.find('label[for^=pause-toggle-] .text-muted').hide();
        } else {
            printerCard.find('label[for^=pause-toggle-] .text-muted').show();
        }

        // Print status
        var secondsLeft = _.get(printer, 'status.progress.printTimeLeft');
        var secondsPrinted = _.get(printer, 'status.progress.printTime');
        if (isInfoSectionOn('print-time')) {
            printerCard.find("#print-time").show();
            printerCard.find("#print-time-remaining").html(toDurationBlock(secondsLeft, _.get(printer, 'status.state.text')));
            printerCard.find("#print-time-total").html(toDurationBlock((secondsPrinted && secondsLeft) ? (secondsPrinted + secondsLeft) : null, _.get(printer, 'status.state.text')));
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
                temp.target = Math.round(temp.target);
                Object.assign(temp, {toolName: _.capitalize(tempKey)});
                temp.id = printerId + '-' + tempKey;
                temperatures.push(temp);
            }
        });
        var tempDiv = printerCard.find("#status_temp_block");
        var editable = _.get(printer, 'settings.temp_profiles') != undefined; //If temp_profiles is missing, it's a plugin version too old to change temps
        tempDiv.html(Mustache.template('status_temp').render({temperatures: temperatures, show: temperatures.length > 0, editable: editable}));
        if (isInfoSectionOn("status_temp_block")) {
            tempDiv.show();
        } else {
            tempDiv.hide();
        }
        if (editable) {
            initTempEditIcon(tempDiv, temperatures, _.get(printer, 'settings.temp_profiles', []), printerWs);
        }

        // Info Section helpers
        function isInfoSectionOn(sectionId) {
            return getPrinterLocalPref(sectionId,
                printerId,
                printerCard.find('button[data-target-div="' + sectionId + '"]').hasClass('pressed')
                );
        }

        function updateInfoSections() {

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

        // End of Info sections
    }

    function toDurationBlock(seconds, printerState) {
        var durationObj;
        if (seconds == null || seconds == 0) {
            durationObj = {valid: false, printing: printerState && printerState !== 'Operational',};
        } else {
            var d = moment.duration(seconds, 'seconds')
            var h = Math.floor(d.asHours());
            var m = d.minutes();
            var s = d.seconds();
            durationObj = {valid: true, printing: true, hours: h, showHours: (h>0), minutes: m, showMinutes: (h>0 || m>0), seconds: s, showSeconds: (h==0 && m==0)}
        }
        return Mustache.template('duration_block').render(durationObj);
    }

    /*** End of printer card */

    $('.hint').popover({
        container: 'body'
    });

});
