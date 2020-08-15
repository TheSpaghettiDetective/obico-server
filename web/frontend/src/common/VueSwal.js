import Vue from 'vue'
import VueSwal from 'vue-sweetalert2'


let openModalWithComponent = (C, props, modalOptions) => {
  let wrapper = document.createElement('div')
  const c = new Vue({
    render: h => h(C, {props: props}),
  }).$mount(wrapper)

  return Vue.swal({
    ...modalOptions,
    customClass: {
      container: 'dark-backdrop',
    },
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
    customClass: {
      container: 'dark-backdrop',
    },
    html: '<div id="replace-here">Placeholder</div>',
    onBeforeOpen: (el) => {
      el.querySelector('#replace-here').replaceWith(element)
    },
  })
}

let toast = (options) => {
  return Vue.swal.fire({
    ...options,
    toast: true,
    backdrop: false,
    position: 'top-end',
    showConfirmButton: false,
    timer: 5000,
  })
}


const install = (Vue, options) => {
  Vue.use(VueSwal, options)

  const Confirm = Vue.swal.mixin({
    title: 'Are you sure?',
    showCancelButton: true,
    confirmButtonText: 'Yes',
    cancelButtonText: 'No',
    customClass: {
      container: 'dark-backdrop',
    },
  })

  const Toast = Vue.swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 5000,
  })

  Vue.prototype.$swal['openModalWithComponent'] = openModalWithComponent
  Vue.prototype.$swal['openModalWithElement'] = openModalWithElement
  Vue.prototype.$swal['toast'] = toast
  Vue.prototype.$swal['Confirm'] = Confirm
  Vue.prototype.$swal['Toast'] = Toast // FIXME Toast vs toast: caused by parallel development
}

export default {install: install}
