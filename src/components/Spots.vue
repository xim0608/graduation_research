<template>
  <v-container>
    <div id="spots">
        <div class="card-columns">
                <div class="item-card-container" v-scroll="infiniteScroll">

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
        recommends: [],
        nextPage: null
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
      flickrUrl: function (owner) {
        const self = this;
        return 'https://www.flickr.com/photos/' + owner
      },
      async fetch() {
        const self = this
        axios
          .get(this.nextPage)
          .then(response => {
            self.results.push(...response.data.results)
            self.nextPage = response.data.next
          })
          .catch(error => {
            console.log(error)
            this.errored = true
          })
      },
      infiniteScroll: function (event) {
        // スクロールの現在位置 + 親（.item-container）の高さ >= スクロール内のコンテンツの高さ
        // console.log(event.target.scrollingElement.scrollTop + event.target.scrollingElement.offsetHeight)
        // console.log(event.target.scrollingElement.scrollHeight)
        // console.log(window.height)

        // if ((event.target.scrollingElement.scrollTop + event.target.scrollingElement.offsetHeight) >= event.target.scrollingElement.scrollHeight) {
        if ((event.currentTarget.scrollTop + event.currentTarget.offsetHeight - 500) >= event.currentTarget.scrollHeight) {
          console.log(event.target.scrollingElement.scrollHeight)
          // this.fetch();
        }
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
          self.nextPage = response.data.next
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
