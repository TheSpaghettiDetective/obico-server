$(document).ready(function () {

    var vjs = videojs('my-video');
    vjs.on('timeupdate', function() {
        console.log('kkk');
    })

});