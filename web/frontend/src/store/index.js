import Vue from 'vue';
import Vuex from 'vuex';

import app from './modules/app';

Vue.use(Vuex);

const strict = process.env.NODE_ENV !== 'production';

const store = new Vuex.Store({
  strict: strict,  // process.env.NODE_ENV !== 'production',
  modules: {
    app
  }
})

export default store