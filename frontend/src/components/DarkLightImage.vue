<template>
  <div>
    <img
      v-show="theme === themes.Light"
      :src="require(`@static/img/${path}/${path}_light.${ext}`)"
      draggable="false"
      :alt="alt"
    >
    <img
      v-show="theme === themes.Dark"
      :src="require(`@static/img/${path}/${path}_dark.${ext}`)"
      draggable="false"
      :alt="alt"
    >
  </div>
</template>

<script>
import { Themes } from '@static/js/color-scheme'
import { currentThemeValue } from '@src/lib/color-scheme-controller'

export default {
  name: 'DarkLightImage',

  props: {
    path: {
      type: String, // i.e. 'logo'
      required: true,
    },
    ext: {
      type: String, // i.e. 'png'
      require: true,
    },
    alt: {
      type: String, // i.e. 'Logo'
      default: '',
    },
  },

  data() {
    return {
      themes: Themes
    }
  },

  computed: {
    theme() {
      return currentThemeValue()
    },
  },
}
</script>
