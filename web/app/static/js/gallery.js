$(document).ready(function () {

    for (var i = 0; i < timelapses; i++) {
        var tl = timelapses[i];
        var vjs = videojs('tl-'+tl.id);
        vjs.on('timeupdate', function() {
            console.log('kkk');
        });
    }

});