<template>
  <v-container>
    <div id="spots">
      <b-row>
        <b-col cols="3" v-for="result in results" :key="result.id">
          <div @click="clickCard(result.id)">
            <b-card :title="result.title"
                    img-src="https://farm3.staticflickr.com/2566/3954085314_79c919437d_m.jpg"
                    img-alt="Image"
                    img-top
                    tag="article"
                    style="max-width: 250px;"
                    class="mb-2"
                    :class="{'border-primary': selected.indexOf(result.id) !== -1, 'shadow': selected.indexOf(result.id) === -1}"
            >
              <p class="card-text">
                {{ result.title }}
              </p>
              <b-button :href="result.url" variant="primary">Reviews</b-button>
              <b-button :href="result.url" variant="primary">Image</b-button>
            </b-card>
          </div>
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
        errored: false,
        selected: [],
        recommends: []
      }
    },
    methods: {
      clickCard: function (spot_id) {
        const self = this
        console.log(self.selected)
        const index = self.selected.indexOf(spot_id)
        console.log(index)
        if (index === -1) {
          self.selected.push(spot_id)
        } else {
          self.selected.splice(index, 1)
        }
        console.log(self.selected)
      }

    },
    // computed: {
    //   selectedCard:
    // },
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
    },
  }
</script>

<style scoped>

</style>
