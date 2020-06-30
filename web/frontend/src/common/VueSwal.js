import Vue from 'vue'
import VueSwal from 'vue-sweetalert2'


let openModalWithComponent = (C, props, modalOptions) => {
  let wrapper = document.createElement('div')
  const c = new Vue({
    render: h => h(C, {props: props}),
  }).$mount(wrapper)

  return Vue.swal({
    ...modalOptions,
    html: '<div id="replace-here">Placeholder</div>',
    onBeforeOpen: (el) => {
      el.querySelector('#replace-here').replaceWith(c.$el)
    },
    onDestroy: () => {
      c.$destroy()
      wrapper.remove()
    }
  })
}


let openModalWithElement = (element, props, modalOptions) => {
  return Vue.swal({
    ...modalOptions,
    html: '<div id="replace-here">Placeholder</div>',
    onBeforeOpen: (el) => {
      el.querySelector('#replace-here').replaceWith(element)
    },
  })
}


const install = (Vue, options) => {
  Vue.use(VueSwal, options)
  Vue.prototype.$swal['openModalWithComponent'] = openModalWithComponent
  Vue.prototype.$swal['openModalWithElement'] = openModalWithElement
}

export default {install: install}
