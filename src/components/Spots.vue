<template>
  <v-container>
    <div id="spots">
      <div class="item-card-container">
        <b-row>
          <b-col cols="3" v-for="result in results" :key="result.id">
            <div @click="clickCard(result.id)">
              <div>
                <b-card no-body
                        tag="article"
                        style="max-width: 450px;"
                        class="mb-3 p-2 card-block"
                        :class="{'border-primary': selected.indexOf(result.id) !== -1, 'shadow': selected.indexOf(result.id) === -1}"
                >
                  <div v-if="result.image.url!== ''">
                    <b-card-img :src="result.image.url"
                                alt="Image"
                                top
                                fluid style="max-height: 200px;"
                    ></b-card-img>
                    <b-card-body :title="result.title">
                      <p class="card-text">
                      <span class="text-muted">
                        Original Update by <u><a class="text-muted" :href="flickrUrl(result.image.owner)">{{ result.image.owner_name }}</a></u>
                      </span>
                      </p>
                      <a :href="result.url">See Reviews</a>
                    </b-card-body>
                  </div>
                  <div v-else>
                    <b-card-img :src="images.noImage"
                                alt="Image"
                                top
                                fluid style="max-height: 200px;"
                    ></b-card-img>
                    <b-card-body :title="result.title">
                      <p class="card-text">
                        Sorry..No Image
                      </p>
                      <a :href="result.url">See Reviews</a>
                    </b-card-body>
                  </div>
                </b-card>
              </div>
            </div>
          </b-col>
        </b-row>
      </div>
    </div>
    <infinite-loading @infinite="infiniteHandler"></infinite-loading>
    <transition name="fade">
      <div class="footer" v-show="showRecommend">
        <b-btn v-b-modal.recommendModal @click="getRecommend" variant="warning" size="lg">See Recommend Spots</b-btn>
        <b-button @click="selected=[]" variant="danger" size="lg">Clear</b-button>
      </div>
    </transition>
    <div>
      <b-modal id="recommendModal">
        <h3>Recommend Spots</h3>
        <b-container>
          <div v-for="recommend in recommends">
            <b-row>
              <b-img :src="recommend.image.url" fluid style="max-width: 150px;"/>
              <p>{{ recommend.title }}</p>
            </b-row>
            <hr>
          </div>
        </b-container>
      </b-modal>
    </div>
  </v-container>

</template>

<script>
  import axios from 'axios';
  import InfiniteLoading from 'vue-infinite-loading';

  export default {
    name: "Spots",
    data: function () {
      return {
        results: [],
        errored: false,
        selected: [],
        recommends: [],
        nextPage: null,
        distance: -Infinity,
        loading: true,
        recommend_loading: true,
        recommend_errored: false,
        images: {
          noImage: require('../assets/no_image.png')
        }
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
      infiniteHandler($state) {
        if (self.loading !== true) {
          self.loading = true
          setTimeout(() => {
            const self = this
            axios
              .get(this.nextPage)
              .then(response => {
                self.results = self.results.concat(response.data.results)
                self.nextPage = response.data.next
              })
              .catch(error => {
                console.log(error)
                this.errored = true
              })
            $state.loaded();
          }, 2000);
        }
        self.loading = false
      },
      getRecommend: function () {
        const self = this
        self.recommend_loading = true
        axios
          .get('/api/search', {
            params: {
              id: self.selected
            }
          })
          .then(response => {
            self.recommends = response.data.recommends
            console.log(self.recommends)
            self.recommend_loading = false
          })
          .catch(error => {
            console.log(error)
            this.recommend_errored = true
          })
      }

    },
    computed: {
      showRecommend: function () {
        return this.selected.length > 0
      }
    },
    mounted() {
      const self = this
      self.loading = true
      axios
        .get('/api/spots')
        .then(response => {
          self.results = response.data.results
          self.nextPage = response.data.next
          self.loading = false
        })
        .catch(error => {
          console.log(error)
          this.errored = true
        })
    },
    components: {
      InfiniteLoading
    }
  }
</script>

<style scoped>
  .footer {
    background: rgba(45, 45, 45, 0.5);
    position: fixed;
    padding: 5px;
    left: 0;
    bottom: 0;
    width: 100%;
    text-align: center;
  }
</style>
