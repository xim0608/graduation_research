<template>
  <v-app>
    <Header/>
  </v-app>
</template>
<script>
import HelloWorld from './components/HelloWorld'
import Header from './components/Header'

export default {
  data () {
    return {
      clipped: false,
      drawer: true,
      fixed: false,
      items: [{
        icon: 'bubble_chart',
        title: 'Inspire'
      }],
      miniVariant: false,
      right: true,
      rightDrawer: false,
      title: 'Vuetify.js'
    }
  },
  name: 'App',
  components: {
    Header
  }
}
</script>
