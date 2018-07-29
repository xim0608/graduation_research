// import Vue from "vue";
var Vue = require('vue/dist/vue.js')

import Demo from "./components/Demo.vue";

const app = new Vue({
    el: '#app',
    components: {
        Demo
    }
});
