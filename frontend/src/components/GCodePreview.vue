<template>
  <div>
    <canvas ref="preview"></canvas>
    
    <div>topLayerColor: {{topLayerColor}}</div>
    <div>lastSegmentColor: {{lastSegmentColor}}</div>
    <div>endLayer: {{endLayer}}</div>
    <div>startLayer: {{startLayer}}</div>
    <div>lineWidth: {{lineWidth}}</div>
  </div>
</template>

<script>
'use strict'
import * as GCodePreview from 'gcode-preview';
import * as THREE from 'three';

const chunkSize = 250;

export default {
  props: {
    url: String,
    topLayerColor: String,
    lastSegmentColor: String,
    endLayer: Number,
    startLayer: Number,
    lineWidth: Number
  },
  data() {
    return {
      layerCount: 0
    }
  },
  async mounted() {
    this.preview = new GCodePreview.init({
      canvas: this.$refs.preview,
      endLayer: this.endLayer,
      startLayer: this.startLayer,
      topLayerColor: new THREE.Color(this.topLayerColor).getHex(),
      lastSegmentColor: new THREE.Color(this.lastSegmentColor).getHex(),
      lineWidth: this.lineWidth,
      buildVolume: {x: 250, y:220, z: 150},
      initialCameraPosition: [0, 400, 450]
    });
    window.addEventListener('resize', () => {
      this.preview.resize();
    });

    const lines1 = await this.fetchGcode('https://storage.googleapis.com/prod-tsd-gcodes/11011/107347?Expires=1914362545&GoogleAccessId=appserviceaccount%40tsdtechnology.iam.gserviceaccount.com&Signature=tq%2BejmiSrhTEZR3JABFy8ezH4Tr0nChbliE4Zi4juboKhSWf6SWQ0e3wQT8dk3s0baaHoEFwVr1TAljiwLLlwqfwbMh%2F%2B5zHShAghs3Lslax6jPgklvASLQPGi0j6XVMYaaRJ0OsWywp1VfooPpiKeijh5AdSVLRpFxsPpbOdxVjdE58vqlAs2k%2BqY%2BFmNE%2FPSG6Bgu6b5IOLahrY4vUmcS2OTTYiK6HsJbFm97al8fRA5r5VrPjUxfSb%2BU4W1wuckka%2FFpp9IE4F%2FaUbhwhskIXacLA3RA7UnGVCikpuxINqwdgMKjNwlQyLLMY84Hyq%2F3qiWEsEknxCZnfGFAIEg%3D%3D'); //this.url);
    this.loadPreviewChunked(this.$refs.gcodePreview1, lines1, 50);

  },
  methods: {
    processGCode(gcode) {
      this.preview.processGCode(gcode);
      this.layerCount = this.preview.layers.length;
    },
    async fetchGcode(url) {
      const response = await fetch(url);
      if (response.status !== 200) {
        throw new Error(`status code: ${response.status}`);
      }
      const file = await response.text();
      return file.split('\n');
    },
    loadPreviewChunked(lines, delay) {
      let c = 0;
      const id = '__animationTimer__' + Math.random().toString(36).substr(2, 9);
      const loadProgressive = () => {
        const start = c*chunkSize;
        const end = (c+1)*chunkSize;
        const chunk = lines.slice(start, end);
        this.processGCode(chunk)
        c++;
        if (c*chunkSize < lines.length) { 
          window[id] = setTimeout(loadProgressive, delay);
        }
      }
      // cancel loading process if one is still in progress
      // mostly when hot reloading
      window.clearTimeout(window[id]);
      loadProgressive();
    }
  }
}
</script>
<style scoped>
  canvas {
    outline: none;
    width: 100%;
    height: 100%;
  }
</style>