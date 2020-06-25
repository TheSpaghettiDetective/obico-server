"use strict";

/****** Gauge */
var ALERT_THRESHOLD = 0.4;

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

/**** Utils */
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


/**** Printer functions */

function getLocalPref(prefId, defaultValue) {
    var val = localStorage.getItem(prefId) || defaultValue;
    // Hack to deal with data type such as boolean and number
    try {
        return JSON.parse(val);
    } catch (e) {
        return val;
    }
}

function setLocalPref(prefId, value) {
    return localStorage.setItem(prefId, value);
}

function getPrinterLocalPref(prefix, printerId, defaultValue) {
    var itemId = prefix + String(printerId);
    var val = localStorage.getItem(itemId) || defaultValue;
    try {
        return JSON.parse(val);
    } catch (e) {
        return val;
    }
}

function setPrinterLocalPref(prefix, printerId, value) {
    var itemId = prefix + String(printerId);
    return localStorage.setItem(itemId, value);
}

function sendPrinterAction(printerId, action, octoprintCommand) {
    printerGet(printerId, action, function (result) {
        var toastHtml = '';
        if (octoprintCommand) {
            toastHtml += '<h6>Successfully sent command to OctoPrint!</h6>' +
                '<p>It may take a while to be executed by OctoPrint.</p>';
        }
        if (toastHtml != '') {
            Toast.fire({
                type: 'success',
                html: toastHtml,
            });
        }
    });
}

/**** Printer state  */

function isPrinterIdle(printerState) {
    return _.get(printerState, 'text', '') === 'Operational';
}

function isPrinterPaused(printerState) {
    return _.get(printerState, 'flags.paused', false);
}

function isPrinterDisconnected(printerState) {
    return _.get(printerState, 'flags.closedOrError', true);
}

function printerHasError(printerState) {
    return _.get(printerState, 'flags.error') || _.get(printerState, 'text', '').toLowerCase().includes('error');
}

function printInProgress(printerState) {
    return !isPrinterDisconnected(printerState) && _.get(printerState, 'text', '') !== 'Operational';
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


/**** AJAX calls ***/

function printerPostApi(path, printerId, data) {
    return $.ajax({
        url: '/api/v1/printers/' + printerId + path,
        type: 'POST',
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify(data),
    });
}

function printerGet(printerId, uri, callback) {
    $.ajax({
        url: '/api/v1/printers/' + printerId + uri,
        type: 'GET',
        dataType: 'json',
    }).done(function (result) { callback(result); });
}

/**** Streaming */

function expandThumbnailToFull(ele) {
    if (ele.parent().hasClass("thumbnail")) {
        var currentThumbnail = ele.parent().parent().find(".thumbnail");
        var currentFull = ele.parent().parent().find(".full");
        currentFull.addClass("thumbnail").removeClass("full");
        currentThumbnail.removeClass("thumbnail").addClass("full");
    }
}

/******** End of streaming functions */


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
