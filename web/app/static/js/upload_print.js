
// Can't be put inside document.ready(). https://github.com/enyo/dropzone/issues/1423

var dgEarned = 0;

Dropzone.options.printUpload = {
    paramName: "file", // The name that will be used to transfer the file
    maxFilesize: 200, // MB
    acceptedFiles: "video/mp4,video/mpeg",
    success: function (file) {
        $('#tl-uploaded').show();
        dgEarned += 4;
        $('#dg-earned').html('You earned ' + '<img class="dg-icon" src="/static/img/detective-gear-inverse.png" />'.repeat(dgEarned));
    }
};

