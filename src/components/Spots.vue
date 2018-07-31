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
            <b-button href="#" variant="primary">Go somewhere</b-button>
          </b-card>
        </b-col>
      </b-row>
    </div>
  </v-container>
</template>

<script>
  import Vue from 'vue';
  import axios from 'axios';

  export default {
    name: "Spots",
    data: function() {
      return {
        results: [
          {"id": 1, "title": "横浜 みなとみらい 21 (横浜市)"},
          {"id": 2, "title": "三渓園 (横浜市)"},
          {"id": 3, "title": "横浜港大さん橋 国際客船ターミナル (横浜市)"},
          {"id": 4, "title": "高徳院（鎌倉大仏） (鎌倉市)"},
          {"id": 5, "title": "大山阿夫利神社 (伊勢原市)"},
          {"id": 6, "title": "江の島シーキャンドル （江の島展望灯台） (藤沢市)"},
          {"id": 7, "title": "横浜ランドマークタワー (横浜市)"},
          {"id": 8, "title": "日本郵船 氷川丸 (横浜市)"},
          {"id": 9, "title": "大涌谷園地 (箱根町)"},
          {"id": 10, "title": "日本丸メモリアルパーク (横浜市)"},
          {"id": 11, "title": "日産グローバル本社ギャラリー (横浜市)"},
          {"id": 12, "title": "鎌倉高校前駅 (鎌倉市)"},
          {"id": 13, "title": "横浜中華街 (横浜市)"},
          {"id": 14, "title": "横浜赤レンガ倉庫 (横浜市)"},
          {"id": 15, "title": "小田原城 (小田原市)"},
          {"id": 16, "title": "鎌倉 小町通り (鎌倉市)"},
          {"id": 17, "title": "横浜元町商店街 (横浜市)"},
          {"id": 18, "title": "マリンタワー (横浜市)"},
          {"id": 19, "title": "馬車道 (横浜市)"},
          {"id": 20, "title": "乙女峠 (箱根町)"}
        ],
        content: 'hello'
      }
    }
  }
  // const vm = new Vue({
  //   el: '#spots',
  //
  // });
</script>

<style scoped>

</style>
