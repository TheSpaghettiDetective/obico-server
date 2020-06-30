<template>
  <div>
    <div class="example">
      {{ msg }}
      <b
        v-b-popover.hover="{title:'Popover', content:'This is the content of popover'}"
      >POPOVER</b>
    </div>
    <div>
      <img :src="logo" />
      <img :src="require('./assets/logo.png')" />
      <img :src="require('../../../app/static/img/logo.png')" />
    </div>
    <b-card
      title="Card Title"
      :img-src="logo"
      img-alt="Image"
      img-top
      tag="article"
      style="max-width: 20rem;"
      class="mb-2"
    >
      <b-card-text>
        Here you can see a
        <b
          v-b-popover.hover="{title:'Popover', content:'This is the content of popover'}"
        >POPOVER</b>
        in action.
      </b-card-text>

      <b-button href="#" variant="primary">Go somewhere</b-button>
    </b-card>
    <div class="form-group mt-2">
      <div v-for="ch in ['a', 'b']" class="custom-control custom-radio" :key="ch">
        <input
          type="radio"
          class="custom-control-input"
          name="select"
          :id="'select-' + ch"
          v-model="choice"
          :value="ch"
        />
        <label class="custom-control-label" :for="'select-' + ch">Choice: {{ ch }}</label>
      </div>
    </div>
  </div>
</template>

<script>
import logo from './assets/logo.png'
import { BCard, BCardText, BButton } from 'bootstrap-vue'

export default {
  components: {
    BCard,
    BCardText,
    BButton
  },
  data() {
    return {
      msg: 'Hello from vue!',
      choice: 'a',
      logo: logo
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

b
  color: theme.$primary

img
  width: 200px
  display: block

.example
  color: theme.$primary
</style>
