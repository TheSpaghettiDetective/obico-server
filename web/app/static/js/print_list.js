$(document).ready(function () {

    videojs.addLanguage('en', { "The media could not be loaded, either because the server or network failed or because the format is not supported.": "The timelapse is being processed. Grab a coffee and come back." });

    var predictionMap = JSON.parse($('#prediction_urls').text());

    $.when.apply($, predictionMap.map(function (pm) {
        return $.ajax(pm.prediction_json_url);
    })).done(function () {
        // there will be one argument passed to this callback for each ajax call
        // each argument is of this form [data, statusText, jqXHR]
        for (var i = 0; i < arguments.length; i++) {
            try {
                predictionMap[i].predictions = JSON.parse(arguments[i][0]);
            } catch (e) {
                predictionMap[i].predictions = [];
            }
        }
        for (var i = 0; i < predictionMap.length; i++) {
            (function () {          // Self-invoking function for closure scope
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

                $("[id^=fullscreen-btn-"+pId+"]").click(function () {
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

            })();
        }
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
