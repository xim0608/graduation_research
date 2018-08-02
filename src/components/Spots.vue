<template>
  <div>
    <div id="top"></div>
    <b-navbar toggleable="md" type="dark" variant="info" fixed="top">

      <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

      <b-navbar-brand href="#">Review Based Recommendation</b-navbar-brand>

      <b-collapse is-nav id="nav_collapse">

        <b-navbar-nav>
          <b-nav-item @click="resetSpot">Spots</b-nav-item>
        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">

          <b-nav-form v-on:submit.prevent="search">
            <b-form-input size="sm" class="mr-sm-2" type="text" placeholder="Search" v-model="keyword"/>
            <b-button size="sm" class="my-2 my-sm-0" @click="search">Search</b-button>
          </b-nav-form>
        </b-navbar-nav>

      </b-collapse>
    </b-navbar>
    <v-container style="padding-top: 80px;">
      <div id="spots">
        <div id="loading-circle" v-show="search_loading" style="padding-top: 300px;text-align: center;">
          <search-loading-circle></search-loading-circle>
        </div>
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
          <b-btn v-b-modal.recommendModal @click="getRecommend" variant="primary" size="lg">See Recommend Spots</b-btn>
          <b-button @click="selected=[]" variant="danger" size="lg">Clear</b-button>
        </div>
      </transition>
      <div>
        <b-modal id="recommendModal" title="Recommend Spots">
          <b-container>
            <div v-for="recommend in recommends">
              <b-row>
                <b-col cols="6">
                <span v-if="recommend.image.url!==''">
                  <b-img :src="recommend.image.url" fluid style="max-width: 150px;"/>
                </span>
                  <span v-else>
                  <b-img :src="images.noImage" fluid style="max-width: 150px;"/>
                </span>
                </b-col>
                <b-col cols="6">
                  <p>{{ recommend.title }}</p>
                </b-col>
              </b-row>
              <hr>
            </div>
          </b-container>
        </b-modal>
      </div>
    </v-container>
  </div>
</template>

<script>
  import axios from 'axios';
  import InfiniteLoading from 'vue-infinite-loading';
  import VueScrollTo from 'vue-scrollto';
  import {scroller} from 'vue-scrollto/src/scrollTo';
  import {Circle as SearchLoadingCircle} from 'vue-loading-spinner'

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
        search_loading: false,
        keyword: '',
        images: {
          noImage: require('../assets/no_image.png')
        }
      }
    },
    methods: {
      resetSpot: function (e) {
        const self = this
        const topscrollTo = scroller()
        topscrollTo('#top')
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
      search: function () {
        const self = this
        self.results = []
        const topscrollTo = scroller()
        topscrollTo('#top')

        self.search_loading = true
        axios
          .get('/api/search', {
            params: {
              q: self.keyword
            }
          })
          .then(response => {
            self.results = response.data.spots
            self.search_loading = false
          })
          .catch(error => {
            console.log(error)
            this.errored = true
          })
      },
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
          .get('/api/recommend', {
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
      InfiniteLoading,
      VueScrollTo,
      SearchLoadingCircle
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
