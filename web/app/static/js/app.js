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
        })
            .done(function () {
                $.notify("Successfully sent command to OctoPrint! It may take a while to be executed by OctoPrint.");
            });
    }

    $('.printer-card').each(function () {
        var printerCard = $(this);
        var printerId = printerCard.attr('id');

        printerCard.find("#print-pause-resume").click(function () {
            var btn = $(this);
            sendPrinterCommand(printerId, btn.text() === 'Pause' ? '/pause_print/' : '/resume_print/');
        });

        printerCard.find('#print-cancel').click( function() {
            $.confirm({
                theme: 'dark',
                title: 'Are you sure?',
                content: 'Once cancelled, the print can no longer be resumed!',
                buttons: {
                    yes: {
                        action: function () {
                            sendPrinterCommand(printerId, '/cancel_print/');
                        },
                    },
                    no: {}
                }
            });
        });

        printerCard.find('#delete-print').click( function() {
            $.confirm({
                theme: 'dark',
                title: 'Are you sure?',
                content: '',
                buttons: {
                    yes: {
                        action: function() {
                            window.location.href = "/printers/" + printerId + "/delete/";
                        },
                    },
                    no: {},
                }
            })
        });

        printerCard.find('#not-a-failure').click( function(e) {
            $.confirm({
                theme: 'dark',
                columnClass: 'medium',
                title: 'Noted!',
                content: 'What do you want to do now?',
                buttons: {
                    resume: {
                        text: 'Resume print',
                        action: function() {
                            sendPrinterCommand(printerId, '/resume_print/');
                        }
                    },
                    resumeAll: {
                        text: 'Resume, and do not alert me again',
                        action: function() {
                            sendPrinterCommand(printerId, '/resume_print/');
                        }
                    },
                }
            });
            e.preventDefault();
        })
    });

    function updatePrinterCard(printer, printerCard) {

        if (_.get(printer, 'status.alert_outstanding') === 't') {
            printerCard.find(".failure-alert").show();
        } else {
            printerCard.find(".failure-alert").hide();
        }

        printerCard.find("img.webcam_img").attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));
        printerCard.find('#tangle-index').attr('data-value', _.get(printer, 'pic.score', 0) * 100);

        if (_.get(printer, 'status.print_file_name')) {
            printerCard.find("#print-file-name").text(_.get(printer, 'status.print_file_name'));
            $('.print-status button').prop('disabled', false);
        } else {
            printerCard.find("#print-file-name").text('-');
            $('.print-status button').prop('disabled', true);
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
});