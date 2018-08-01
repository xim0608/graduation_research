<template>
  <v-container>
    <div id="spots">
      <div class="card-columns">
        <div v-for="result in results" :key="result.id">
          <div @click="clickCard(result.id)">
            <div>
              <b-card :title="result.title"
                      img-src="https://farm3.staticflickr.com/2566/3954085314_79c919437d_m.jpg"
                      v-bind:img-src="result.image.url"
                      img-alt="Image"
                      img-top
                      tag="article"
                      style="max-width: 450px;"
                      class="mb-3 p-2"
                      :class="{'border-primary': selected.indexOf(result.id) !== -1, 'shadow': selected.indexOf(result.id) === -1}"
              >
                <p class="card-text">
                  <span class="text-muted">
                  Original Update by <u><a class="text-muted" :href="flickrUrl(result.image.owner)">{{ result.image.owner_name }}</a></u>
                </span>
                </p>
                <b-button :href="result.url" variant="primary">Reviews</b-button>
              </b-card>
            </div>
          </div>
        </div>
      </div>
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
      },
      flickrUrl: function(owner){
        const self = this;
        return 'https://www.flickr.com/photos/' + owner
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
  .card-columns {
    /*@include media-breakpoint-only(lg) {*/
    /*column-count: 4;*/
    /*}*/
    /*@include media-breakpoint-only(xl) {*/
    /*column-count: 5;*/
    /*}*/
    /*column-count: 4;*/
  }
</style>
