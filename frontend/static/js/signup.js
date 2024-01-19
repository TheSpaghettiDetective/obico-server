$(document).ready(function () {
    $('input#tos-checkbox').on('change', function () {
        if (this.checked) {
            $('a.btn').removeClass('disabled');
            $('button.btn').removeClass('disabled');
            $('button.btn').removeAttr('disabled');
        } else {
            $('a.btn').addClass('disabled');
            $('button.btn').addClass('disabled');
            $('button.btn').attr("disabled", true);
        }
    });
    $('.popover').popover({
        container: 'body'
    });

    jQuery.fn.preventDoubleSubmission = function() {
        $(this).on('submit', function(event) {
            var $form = $(this);
            var $submitButton = $form.find('button[type="submit"]');
            $submitButton.prop('disabled', true).addClass('disabled');

            setTimeout(function() {
                $submitButton.prop('disabled', false).removeClass('disabled');
            }, 3000);
        });
    };

   $('#signup_form').preventDoubleSubmission();
});
