$(document).ready(function () {

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

    // A very hacky way to make sure the wizard goes back to step 0 when there is validation error with the form.
    if (formHasErrors) {
        window.setTimeout(function () {
            window.location.hash = '#step-1';
        }, 100);
    }

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

    $('#sensitivity').slider({
        formatter: function(value) {
            if (value < 0.95) {
                return 'Low';
            }
            if (value > 1.05) {
                return 'High';
            }
            return 'Medium';
        }
    });

    function updateSensitivityHint() {
        $('.sensitivity div[class^=hint]').hide();
        var value = parseFloat($('#sensitivity').val());
        if (value < 0.95) {
            $('.sensitivity .hint-low').show();
        } else if (value > 1.05) {
            $('.sensitivity .hint-high').show();
        } else {
            $('.sensitivity .hint-medium').show();
        }
    }

    $('#sensitivity').on('change', updateSensitivityHint);

    $('#lift-z-checkbox').on('change', function() {
        if ($(this).is(':checked')) {
            $('#id_lift_z_on_pause').prop('disabled', false);
        } else {
            $('#id_lift_z_on_pause').prop('disabled', true);
            $('#id_lift_z_on_pause').val(0);
        }
    });

    $('#retract-checkbox').on('change', function() {
        if ($(this).is(':checked')) {
            $('#id_retract_on_pause').prop('disabled', false);
        } else {
            $('#id_retract_on_pause').prop('disabled', true);
            $('#id_retract_on_pause').val(0);
        }
    });
    updateSensitivityHint();
});
