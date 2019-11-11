$(document).ready(function () {
    $('input#tos-checkbox').on('change', function() {
        if (this.checked) {
            $('a.btn').removeClass('disabled');
            $('button.btn').removeClass('disabled');
        } else {
            $('a.btn').addClass('disabled');
            $('button.btn').addClass('disabled');
        }
    });
    $('.popover').popover({
        container: 'body'
    });
});
