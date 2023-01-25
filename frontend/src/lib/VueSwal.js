import Vue from 'vue'
import VueSwal from 'vue-sweetalert2'

import { getLocalPref, setLocalPref } from '@src/lib/pref'

const openModalWithComponent = (C, props, modalOptions) => {
  let wrapper = document.createElement('div')
  const c = new Vue({
    render: (h) => h(C, { props: props }),
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
    },
  })
}

const openModalWithElement = (element, props, modalOptions) => {
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

  const Reject = Vue.swal.mixin({
    icon: 'error',
    customClass: {
      container: 'dark-backdrop error-alert',
    },
  })

  const Prompt = Vue.swal.mixin({
    customClass: {
      container: 'dark-backdrop',
    },
  })

  const DismissableToast = (swalOpt, dismissKey) => {
    if (!getLocalPref(dismissKey, false)) {
      const opt = {
        ...swalOpt,
        position: 'top-end',
        confirmButtonText: "Gotcha! Don't show this again.",
      }
      return Vue.swal(opt).then(function (result) {
        if (result.value) {
          setLocalPref(dismissKey, true)
          console.log(result)
        }
      })
    }
  }

  Vue.prototype.$swal['openModalWithComponent'] = openModalWithComponent
  Vue.prototype.$swal['openModalWithElement'] = openModalWithElement
  Vue.prototype.$swal['Confirm'] = Confirm
  Vue.prototype.$swal['Toast'] = Toast
  Vue.prototype.$swal['DismissableToast'] = DismissableToast
  Vue.prototype.$swal['Reject'] = Reject
  Vue.prototype.$swal['Prompt'] = Prompt
}

export default { install: install }
