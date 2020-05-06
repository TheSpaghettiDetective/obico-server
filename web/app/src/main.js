import Vue from 'vue';
import VueRouter from 'vue-router';
import store from './store';
import {routes} from './router/routes';

import Prints from './views/prints.vue';
Vue.component('prints', Prints);

Vue.config.productionTip = false

Vue.use(VueRouter);
const router = new VueRouter({
    routes,
    linkActiveClass: 'open active',
    scrollBehavior: () => ({ y: 0 }),
    mode: 'history'
    // mode: 'hash'
});
// new Vue({
//     router,
//     store,
//     render: h => h(App),
// }).$mount('#app');

const app = new Vue({
    el: '#app',
    store,
})