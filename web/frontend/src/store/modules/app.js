'use strict';

const state = {
    isAuthenticated: true,
    token: null
};

const actions = {

};

const mutations = {

};

const getters = {
    isAuthenticated : state =>  state.isAuthenticated,
    getToken: state => state.token
}


export default {
	state,
	actions,
	mutations,
	getters
}
