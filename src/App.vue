<template>
  <v-app>
    <!--<Header/>-->
    <v-content>
      <Spots/>
    </v-content>
  </v-app>

</template>
<script>
  import Header from './components/Header'
  import Spots from './components/Spots'

  export default {
    data() {
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
      Header,
      Spots
    }
  }
</script>
