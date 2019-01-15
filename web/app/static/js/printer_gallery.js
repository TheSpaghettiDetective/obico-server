$(document).ready(function() {
    var timers = [];
    $('.printer-card').each( function() {
        var printer_card = $(this);
        var printer_id = printer_card.attr('id');
        timers += setInterval( function() {
            $.ajax({
                url: '/api/printers/' + printer_id + '/',
                type: 'GET',
                dataType: 'json',
            })
            .done( function( printer ) {
                printer_card.find("img.webcam_img").attr('src', printer.current_img_url);
            })
        }, 5*1000);
    } );
 });