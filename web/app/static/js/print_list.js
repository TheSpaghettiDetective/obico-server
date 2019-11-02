$(document).ready(function () {

    videojs.addLanguage('en', { 'The media could not be loaded, either because the server or network failed or because the format is not supported.': 'The timelapse is being processed. Grab a coffee and come back.' });

    var predictionMap = JSON.parse($('#prediction_urls').text());

    $.when(
        $.map(predictionMap, function (pm) {
            return $.ajax(pm.prediction_json_url);
        })
    ).always(function (arr) {
        $.each(arr, function (i, value) {
            // `success`
            value.then(
                function (data, textStatus, jqxhr) {
                    predictionMap[i].predictions = JSON.parse(data);
                    var printPred = predictionMap[i];
                    var pId = printPred.print_id;
                    var frame_p = printPred.predictions;

                    var gauge = $('#gauge-' + pId);
                    var vjs = videojs('tl-' + pId);
                    vjs.on('timeupdate', function (e) {
                        var num = Math.round(frame_p.length * (this.currentTime() / this.duration()));
                        var p = _.get(frame_p[num], 'fields.ewm_mean');
                        updateGauge(gauge, p);
                    });

                    $('[id^=fullscreen-btn-' + pId + ']').click(function () {
                        vjs.pause();

                        var modalVjs = videojs('tl-fullscreen-vjs');
                        modalVjs.src(vjs.currentSrc());
                        modalVjs.currentTime(vjs.currentTime());
                        modalVjs.play();
                        modalVjs.on('timeupdate', function (e) {
                            var num = Math.round(frame_p.length * (this.currentTime() / this.duration()));
                            var p = _.get(frame_p[num], 'fields.ewm_mean');
                            updateGauge($('#gauge-fullscreen'), p);
                        });
                    });
                },
                // `error`
                function (jqxhr, textStatus, errorThrown) {
                    predictionMap[i].predictions = [];
                });
        });
    });
    $('#tl-fullscreen-modal').on('hide.bs.modal', function (e) {
        var player = videojs('tl-fullscreen-vjs');
        player.pause();
    });

    $('.timelapse-card').each(function () {
        var printCard = $(this);
        printCard.find('input.view-toggle').on('change', function (e) {
            if ($(this).is(':checked')) {
                printCard.find('.plain-view').hide();
                printCard.find('.detective-view').show();
            } else {
                printCard.find('.plain-view').show();
                printCard.find('.detective-view').hide();
            }
        });
    });

    function updateBtns() {
        if ($('input[id^="select-print-"]:checked').length > 0) {
            $('#delete-prints-btn').prop('disabled', false);
            $('#delete-prints-btn').removeClass('btn-light').addClass('btn-danger');
        } else {
            $('#delete-prints-btn').prop('disabled', true);
            $('#delete-prints-btn').addClass('btn-light').removeClass('btn-danger');
        }

        if ($('input[id^="select-print-"]:checked').length == $('input[id^="select-print-"]').length) {
            $('#select-all-btn').text('De-select All');
        } else {
            $('#select-all-btn').text('Select All');
        }
    }

    $('input[id^="select-print-"]').on('change', function () {
        updateBtns();
    });

    $('#select-all-btn').on('click', function () {
        if ($('#select-all-btn').text() == 'Select All') {
            $('input[id^="select-print-"]').prop('checked', true);
        } else {
            $('input[id^="select-print-"]').prop('checked', false);
        }
        updateBtns();
    });

    $('#delete-prints-btn').on('click', function () {
        var numSelected = $('input[id^="select-print-"]:checked').length;

        Confirm.fire({
            text: 'Delete ' + numSelected + ' time-lapses permanently?',
        }).then(function (result) {
            if (result.value) {  // When it is confirmed
                $('#prints-form').submit();
            }
        });
    });

    $("input[type=radio][name=alert_overwrite]").on('change', function (event) {
        var form = $(event.target.form);
        $.ajax({
            url: '/api/prints/' + form.data('print-id') + '/alert_overwrite/?value=' + form.serializeArray()[0].value,
            type: 'GET',
            dataType: 'json',
        }).done(function (result) {
            var html = '<h6>Thank you for helping The Detective get better.</h6>';
            if (result.user_credited) {
                html += '<a href="/ent/detective_hours/">You just earned ' + '<img class="dh-icon" src="/static/img/detective-hour-2-primary.png" />.</a>';
            }

            Toast.fire({
                type: 'success',
                html: html,
            });
        });
    })
});

