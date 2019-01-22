$(document).ready(function () {
    var timers = [];
    $('.printer-card').each(function () {
        var printer_card = $(this);
        var printer_id = printer_card.attr('id');
        timers += setInterval(function () {
            $.ajax({
                url: '/api/printers/' + printer_id + '/',
                type: 'GET',
                dataType: 'json',
            })
                .done(function (printer) {
                    updatePrinterCard(printer, printer_card);
                })
        }, 5 * 1000);
    });

    function updatePrinterCard(printer, printer_card) {

        if (_.get(printer, 'status.alert_outstanding') === 't') {
            printer_card.find(".failure-alert").show();
        } else {
            printer_card.find(".failure-alert").hide();
        }

        printer_card.find("img.webcam_img").attr('src', _.get(printer, 'pic.img_url', printer_stock_img_src));
        printer_card.find('#tangle-index').attr('data-value', _.get(printer, 'pic.score', 0)*100);

        printer_card.find("#print-file-name").text(_.get(printer, 'status.print_file_name', '-'));

        var secondsLeft = _.get(printer, 'status.seconds_left', -1);
        printer_card.find("#time-left").text( (secondsLeft > 0) ? moment.duration(secondsLeft, 'seconds').humanize() : '-');
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
                if (printer.last_contacted) {
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