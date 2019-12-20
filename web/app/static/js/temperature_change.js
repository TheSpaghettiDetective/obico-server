function initTempEditIcon(tempDiv, temperatures, tempProfiles){
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
                        printerPostApi(
                            '/send_command/',
                            printerId,
                            {cmd: 'set_temperature', args: [tempKey, targetTemp]}
                            ).done(function(result) {
                                console.log(result);
                                // printerList[printerId] = result.printer;
                                // updatePrinterCard(printerCard);
                            });
                    }
                });
            })(_.split($(ele.currentTarget).attr('id'), '-'));
        });
    })
}

function initTempChangeDiv(tempChangeDiv, temperature) {
    tempChangeDiv.find('select.selectpicker').selectpicker();
    tempChangeDiv.find('select.selectpicker').on('change', function(e){
        updateTargetTemp(this.value);
        updateSlider(this.value);
    })
    var slider = tempChangeDiv.find('#target-temp').slider();
    slider.slider('on', 'change', function(v){
        updateTargetTemp(v.newValue);
    });
    updateSlider(temperature.target);
    updateTargetTemp(temperature.target);

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
}
