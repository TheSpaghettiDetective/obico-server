$(document).ready(function () {

    var timelapses = JSON.parse($('#timelapses-data').text());

    for (var i = 0; i < timelapses.length; i++) {
        (function () {          // Self-invoking function for closure scope
            var tl = timelapses[i];
            var frame_p = tl.frame_p;

            var gauge = $('#gauge-' + tl.id);
            var vjs = videojs('tl-' + tl.id);
            vjs.on('timeupdate', function (e) {
                var num = Math.floor(this.currentTime() * 25);
                var p = frame_p[num].p;
                updateGauge(gauge, p);
            });
        })();
    }

});