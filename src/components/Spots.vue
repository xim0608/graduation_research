<template>
  <v-container>
    <div id="spots">
      <b-row>
        <b-col cols="3" v-for="result in results" :key="result.id">
          <b-card :title="result.title"
                  img-src="https://picsum.photos/600/300/?image=25"
                  img-alt="Image"
                  img-top
                  tag="article"
                  style="max-width: 20rem;max-height: 50rem;"
                  class="mb-2">
            <p class="card-text">
              {{ result.title }}
            </p>
            <b-button :href="result.url" variant="primary">Show Reviews</b-button>
          </b-card>
        </b-col>
      </b-row>
    </div>
  </v-container>
</template>

<script>
  import axios from 'axios';

  export default {
    name: "Spots",
    data: function () {
      return {
        results: [],
        errored: false
      }
    },
    mounted() {
      const self = this
      axios
        .get('/api/spots')
        .then(response => {
          self.results = response.data.results
        })
        .catch(error => {
          console.log(error)
          this.errored = true
        })
    }
  }
</script>

<style scoped>

</style>
