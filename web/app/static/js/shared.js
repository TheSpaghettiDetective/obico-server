function scaleP(p) {
    var CUT_OFF = 0.45;
    var scaleAboveCutOff = (100.0/3.0) / (1-CUT_OFF);
    var scaleBelowCutOff = (200.0/3.0) / CUT_OFF;
    if (p > CUT_OFF) {
        return (p - CUT_OFF) * scaleAboveCutOff + 200.0/3.0;
    } else {
        return p * scaleBelowCutOff;
    }
}

function updateGauge(gaugeEle, p) {
    var scaledP = scaleP(p);
    gaugeEle.attr('data-value', scaledP);
    if (scaledP > 66) {
        gaugeEle.attr('data-title', 'Failing!');
       gaugeEle.attr('data-color-title', 'rgba(255,30,0,.75)');
    } else if (scaledP > 33) {
       gaugeEle.attr('data-title', 'Fishy...');
       gaugeEle.attr('data-color-title', 'rgb(255,165,0,.75)');
    } else {
       gaugeEle.attr('data-title', 'Looking Good');
       gaugeEle.attr('data-color-title', 'rgba(0,255,30,.75)');
    }
}
