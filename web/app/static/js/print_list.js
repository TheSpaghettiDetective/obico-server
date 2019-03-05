$(document).ready(function () {

    var predictionMap = JSON.parse($('#prediction_urls').text());

    $.when.apply($, predictionMap.map(function(pm) {
        return $.ajax(pm.prediction_json_url);
    })).done( function() {
        // there will be one argument passed to this callback for each ajax call
        // each argument is of this form [data, statusText, jqXHR]
        for (var i = 0; i < arguments.length; i++) {
            try {
                predictionMap[i].predictions = JSON.parse(arguments[i][0]);
            } catch(e) {
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
                var alertBanner = $('#alert-banner-' + pId);
                vjs.on('timeupdate', function (e) {
                    var num = Math.floor(this.currentTime() * 30);
                    var p = _.get(frame_p[num], 'fields.ewm_mean');
                    updateGauge(gauge, p);
                    if (p > ALERT_THRESHOLD) {
                        alertBanner.show();
                    } else {
                        alertBanner.hide();
                    }
                });

                $('#fullscreen-btn-' + pId).click( function() {
                    vjs.pause();
                    var currentTime = vjs.currentTime();

                    var modalVjs = videojs('tl-fullscreen-vjs');
                    modalVjs.src(tl.video_url);
                    modalVjs.currentTime(currentTime);
                    modalVjs.play();
                    var modalAlertBanner = $('#alert-banner-fullscreen');
                    modalVjs.on('timeupdate', function (e) {
                        var num = Math.floor(this.currentTime() * 25);
                        var p = frame_p[num].p;
                        updateGauge($('#gauge-fullscreen'), p);
                        if (p > ALERT_THRESHOLD) {
                            modalAlertBanner.show();
                        } else {
                            modalAlertBanner.hide();
                        }
                    });
                });

            })();
        }
    });
    $('#tl-fullscreen-modal').on('hide.bs.modal', function (e) {
        var player = videojs('tl-fullscreen-vjs');
        player.pause();
    });
});
