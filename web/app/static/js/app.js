$(document).ready(function () {
    var timer;

    function startPolling() {
        if (timer === undefined) {
            timer = setInterval(pollAllPrinters, 5 * 1000);
        }
    }

    function stopPolling() {
        if (timer) {
            clearInterval(timer);
            timer = undefined;
        }
    }

    function pollAllPrinters() {
        $('.printer-card').each(function () {
            var printerCard = $(this);
            var printerId = printerCard.attr('id');
            $.ajax({
                url: '/api/printers/' + printerId + '/',
                type: 'GET',
                dataType: 'json',
            })
                .done(function (printer) {
                    updatePrinterCard(printer, printerCard);
                })
        });
    }

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            stopPolling();
        } else {
            pollAllPrinters();
            startPolling();
        }
    });

    pollAllPrinters();
    startPolling();

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
            }).then( function(result) {
                if (result.value) {  // When it is confirmed
                    sendPrinterCommand(printerId, '/cancel_print/');
                }
            });
        });

        printerCard.find('#delete-print').click(function () {
            Confirm.fire({
            }).then( function(result) {
                if (result.value) {  // When it is confirmed
                    window.location.href = "/printers/" + printerId + "/delete/";
                }
            });
        });

        printerCard.find('#not-a-failure').click(function (e) {
            Confirm.fire({
                title: 'Noted!',
                text: 'What do you want to do now?',
                confirmButtonText: 'Resume print',
                cancelButtonText: 'Resume, and don\'t alert again for this print',
            }).then( function(result) {
                if (result.value) {
                    sendPrinterCommand(printerId, '/resume_print/');
                } else if (result.dismiss == 'cancel') {
                    sendPrinterCommand(printerId, '/resume_print/?mute_alert=true');
                }
            });
            e.preventDefault();
        })
    });

    function updatePrinterCard(printer, printerCard) {

        if (printer.current_print_alerted_at){
            printerCard.find(".failure-alert").show();
        } else {
            printerCard.find(".failure-alert").hide();
        }

        printerCard.find("img.webcam_img").attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));
        printerCard.find('#tangle-index').attr('data-value', _.get(printer, 'pic.score', 0) * 100);

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

    /** Printer form */
    $('#smartwizard').smartWizard();
    $("#smartwizard").on("leaveStep", function (e, anchorObject, stepNumber, stepDirection) {
        if (stepNumber === 0 && stepDirection === 'forward') {
            $("#printer_form").submit();
        }
        if (stepNumber === 1 && stepDirection === 'forward') {
            var printerId = $('.connection-step').data('printer-id');
            if (printerId) {
                checkPrinterEvent(printerId);
            }
        }
    });

    function setTooltip(btn, message) {
        $(btn).tooltip('hide')
            .attr('data-original-title', message)
            .tooltip('show');
    }

    function hideTooltip(btn) {
        setTimeout(function () {
            $(btn).tooltip('hide');
        }, 1000);
    }

    $('#copy-to-clipboard').tooltip({
        trigger: 'click',
        placement: 'bottom'
    });

    var clipboard = new ClipboardJS('#copy-to-clipboard');
    clipboard.on('success', function (e) {
        setTooltip(e.trigger, 'Copied!');
        hideTooltip(e.trigger);
    });

    clipboard.on('error', function (e) {
        setTooltip(e.trigger, 'Failed!');
        hideTooltip(e.trigger);
    });

    function checkPrinterEvent(printerId) {
        $.ajax({
            url: '/api/printers/' + printerId + '/',
            type: 'GET',
            dataType: 'json',
        })
            .done(function (printer) {
                if (!_.isEmpty(printer.status)) {
                    $('#connected').show();
                    $('#waiting').hide();
                } else {
                    setTimeout(function () {
                        checkPrinterEvent(printerId);
                    }, 2000);
                }
            });
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