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
});
