$(document).ready(function () {

    var timelapses = JSON.parse($('#timelapses-data').text());

    for (var i = 0; i < timelapses.length; i++) {
        (function () {          // Self-invoking function for closure scope
            var tl = timelapses[i];
            var frame_p = JSON.parse(tl.frame_p);

            var gauge = $('#gauge-' + tl.id);
            var vjs = videojs('tl-' + tl.id);
            vjs.on('timeupdate', function (e) {
                var num = Math.floor(this.currentTime() * 25);
                var p = frame_p[num].p;
                updateGauge(gauge, p);
                updateAlertBanner($('#alert-banner-' + tl.id), p);
            });

            $('#fullscreen-btn-' + tl.id).click( function() {
                vjs.pause();
                var currentTime = vjs.currentTime();

                $('#tl-modal-title').text('By ' + tl.creator_name);

                var modalVjs = videojs('tl-fullscreen-vjs');
                modalVjs.src(tl.video_url);
                modalVjs.currentTime(currentTime);
                modalVjs.play();
                modalVjs.on('timeupdate', function (e) {
                    var num = Math.floor(this.currentTime() * 25);
                    var p = frame_p[num].p;
                    updateGauge($('#gauge-fullscreen'), p);
                    updateAlertBanner($('#alert-banner-fullscreen'), p);
                });
            });

        })();
    }

    $('#tl-fullscreen-modal').on('hide.bs.modal', function (e) {
        var player = videojs('tl-fullscreen-vjs');
        player.pause();
    });
});
