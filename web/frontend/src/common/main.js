import Vue from 'vue'

// SVG sprite
import SvgSprite from '@common/SvgSprite.vue'
if (document.getElementById('svg-sprite')) {
  new Vue({
    components: { SvgSprite }
  }).$mount('#svg-sprite')
}