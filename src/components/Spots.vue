<template>
  <v-container>
    <div id="spots">
      <b-row>
        <b-col cols="3" v-for="result in results" :key="result.id">
          <div @click="clickCard(result.id)">
            <b-card :title="result.title"
                    img-src="https://picsum.photos/600/300/?image=25"
                    img-alt="Image"
                    img-top
                    tag="article"
                    style="max-width: 20rem;max-height: 50rem;"
                    class="mb-2"
                    :class="{'card-border': selected.indexOf(result.id) !== -1}"
            >
              <p class="card-text">
                {{ result.title }}
              </p>
              <b-button :href="result.url" variant="primary">Show Reviews</b-button>
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
        selected: []
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
  .card-border {
    border-color: yellow;
  }
</style>
