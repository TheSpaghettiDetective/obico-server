
var ALERT_THRESHOLD = 0.5;

function scaleP(p) {
    var scaleAboveCutOff = (100.0 / 3.0) / (1 - ALERT_THRESHOLD);
    var scaleBelowCutOff = (200.0 / 3.0) / ALERT_THRESHOLD;
    if (p > ALERT_THRESHOLD) {
        return (p - ALERT_THRESHOLD) * scaleAboveCutOff + 200.0 / 3.0;
    } else {
        return p * scaleBelowCutOff;
    }
}

function updateGauge(gaugeEle, p) {
    var scaledP = scaleP(p);
    gaugeEle.attr('data-value', scaledP);
    if (scaledP > 66) {
        gaugeEle.attr('data-title', 'Failing!');
        gaugeEle.attr('data-color-title', '#d9534f');
    } else if (scaledP > 33) {
        gaugeEle.attr('data-title', 'Fishy...');
        gaugeEle.attr('data-color-title', '#f0ad4e');
    } else {
        gaugeEle.attr('data-title', 'Looking Good');
        gaugeEle.attr('data-color-title', '#5cb85c');
    }
}

function updateAlertBanner(banner, p) {
    if (p > ALERT_THRESHOLD) {
        banner.show();
    } else {
        banner.hide();
    }
}

function setTooltip(btn, message) {
    $(btn).tooltip('hide')
        .attr('data-original-title', message)
        .tooltip('show');
}

function hideTooltip(btn) {
    setTimeout(function () {
        $(btn).tooltip('hide');
    }, 1000);
}

/*** Swal Mixins */

var Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 5000,
});

var Confirm = Swal.mixin({
    title: 'Are you sure?',
    showCancelButton: true,
    confirmButtonText: 'Yes',
    cancelButtonText: 'No',
});

$(document).ready(function () {

    $('#copy-to-clipboard').tooltip({
        trigger: 'click',
        placement: 'bottom'
    });

    var clipboard = new ClipboardJS('#copy-to-clipboard');
    clipboard.on('success', function (e) {
        setTooltip(e.trigger, 'Copied!');
        hideTooltip(e.trigger);
    });

    clipboard.on('error', function (e) {
        setTooltip(e.trigger, 'Failed!');
        hideTooltip(e.trigger);
    });

});
