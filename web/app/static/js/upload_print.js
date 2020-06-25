
// Can't be put inside document.ready(). https://github.com/enyo/dropzone/issues/1423
// Also https://stackoverflow.com/questions/33672327/dropzone-events-not-working-need-a-success-call-back
Dropzone.autoDiscover = false;

Dropzone.options.printUpload = {
    paramName: "file", // The name that will be used to transfer the file
    withCredentials: true,
    maxFilesize: 200, // MB
    timeout: 60 * 60 * 1000, // For large files
    acceptedFiles: "video/mp4,video/mpeg",
    init: function () {
        this.on("success", function (file) {
            $('#tl-verifying').hide();
            $('#tl-uploaded').show();
        });
    },
};

$('#print-upload').dropzone();

