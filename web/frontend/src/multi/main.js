import Vue from 'vue'
import Welcome from './Welcome.vue'

// list all components here
let components = {Welcome, };

['DOMContentLoaded'].map(e =>
  document.addEventListener(e, () => {

    if(window.vueapp == null){
      window.vueapp = []
    }

    if(window.vueapp != null){
      for(var i=0, len=window.vueapp.length; i < len; i++){
        window.vueapp[i].$destroy()
      }
      window.vueapp = []
    }

    var myNodeList = document.querySelectorAll('.vue-container')
    myNodeList.forEach(element => {
      if (element != null) {
        var vueapp = new Vue({
          el: element,
          components: components
        })
        window.vueapp.push(vueapp)
      }
    })
  })
)
