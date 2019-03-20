$(document).ready(function () {

    videojs.addLanguage('en', { "The media could not be loaded, either because the server or network failed or because the format is not supported.": "The timelapse is being processed. Grab a coffee and come back." });

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
                        var num = Math.floor(this.currentTime() * 30);
                        var p = _.get(frame_p[num], 'fields.ewm_mean');
                        updateGauge(gauge, p);
                        updateAlertBanner($('#alert-banner-' + pId), p);
                    });

                    $("[id^=fullscreen-btn-" + pId + "]").click(function () {
                        vjs.pause();

                        var modalVjs = videojs('tl-fullscreen-vjs');
                        modalVjs.src(vjs.currentSrc());
                        modalVjs.currentTime(vjs.currentTime());
                        modalVjs.play();
                        modalVjs.on('timeupdate', function (e) {
                            var num = Math.floor(this.currentTime() * 30);
                            var p = _.get(frame_p[num], 'fields.ewm_mean');
                            updateGauge($('#gauge-fullscreen'), p);
                            updateAlertBanner($('#alert-banner-fullscreen'), p);
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
        })
    });
});
