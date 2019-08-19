
// Can't be put inside document.ready(). https://github.com/enyo/dropzone/issues/1423

Dropzone.options.printUpload = {
    paramName: "file", // The name that will be used to transfer the file
    maxFilesize: 200, // MB
    acceptedFiles: "video/mp4,video/mpeg",
    success: function (file) {
        var html = '<div style="display: flex; flex-flow: column; align-items: center">' +
                    '<img style="height: auto; width: 12rem;" src="/static/img/detective-working.gif" />' +
                    '<div class="py-2 text-center" style="max-width: 16rem;">The Detective is busy looking at the time-lapse video you uploaded. We will send you email when she is done.</div></div>';
        Toast.fire({
            html: html,
        });
    }
};

