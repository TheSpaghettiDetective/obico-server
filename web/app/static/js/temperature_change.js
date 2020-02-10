"use strict";

function initTempEditIcon(tempDiv, temperatures, tempProfiles, printerWs){
    temperatures.forEach( function(temperature){
        tempDiv.find('#'+temperature.id).on('click', function(ele) {
            _.spread(function(printerId, tempKey) {
                var presets;
                var maxTemp = 350;
                if (tempKey == 'bed') {
                    presets = _.map(tempProfiles, function(v) {return {name: v.name, target: v['bed']}});
                    maxTemp = 140;
                } else {
                    presets = _.map(tempProfiles, function(v) {return {name: v.name, target: v['extruder']}});
                }
                Swal.fire({
                    title: 'Set ' + _.capitalize(tempKey) + ' Temperature',
                    html: Mustache.template('temperature_change').render({presets: presets, maxTemp: maxTemp}),
                    confirmButtonText: 'Confirm',
                    showCancelButton: true,
                    onOpen: function(e){
                        initTempChangeDiv($(e), temperature, presets);
                    },
                }).then((result) => {
                    if (result.value) {
                        var targetTemp = parseInt($('input#target-temp').val());
                        printerWs.passThruToPrinter(printerId, {func: 'set_temperature', target: '_printer', args: [tempKey, targetTemp]});
                    }
                });
            })(_.split($(ele.currentTarget).attr('id'), '-'));
        });
    })
}

function initTempChangeDiv(tempChangeDiv, temperature, presets) {
    tempChangeDiv.find('select.selectpicker').selectpicker();
    tempChangeDiv.find('select.selectpicker').on('change', function(e){
        if (this.value == -1) {
            return;
        }
        updateTargetTemp(this.value);
        updateSlider(this.value);
    })
    var slider = tempChangeDiv.find('#target-temp').slider();
    slider.slider('on', 'change', function(v){
        updateTargetTemp(v.newValue);
        updateSelect(v.newValue);
    });
    updateSlider(temperature.target);
    updateTargetTemp(temperature.target);
    updateSelect(temperature.target);

    function updateTargetTemp(target){
        var targetText = 'OFF';
        if (target > 0){
            targetText = target+'<span class="text-subscript text-muted">°C</span>';
        }
        tempChangeDiv.find('.target-temp-degree').html(targetText);
    }

    function updateSlider(target) {
        slider.slider('setValue', target);
    }

    function updateSelect(target) {
        var presetTemps = _.concat(_.map(presets, 'target'), [0]);
        var selectVal = -1
        if (_.indexOf(presetTemps, target)!=-1) {
            selectVal = target;
        }
        tempChangeDiv.find('select.selectpicker').val(selectVal);
        tempChangeDiv.find('select.selectpicker').selectpicker('refresh');
    }
}
