import Vue from 'vue'
import setupSentry from '@lib/sentry'

setupSentry(Vue)

// SVG sprite
import SvgSprite from '@common/SvgSprite.vue'
if (document.getElementById('svg-sprite')) {
  new Vue({
    components: { SvgSprite }
  }).$mount('#svg-sprite')
}