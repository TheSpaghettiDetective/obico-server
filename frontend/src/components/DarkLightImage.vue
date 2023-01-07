<template>
  <div>
    <img
      v-show="theme === themes.Light"
      :src="require(`@static/img/${path}/${filename}_light-scheme.${format}`)"
      draggable="false"
      :alt="alt"
    />
    <img
      v-show="theme === themes.Dark"
      :src="require(`@static/img/${path}/${filename}_dark-scheme.${format}`)"
      draggable="false"
      :alt="alt"
    />
  </div>
</template>

<script>
import { Themes } from '@static/js/color-scheme'
import { currentThemeValue } from '@src/lib/color-scheme-controller'

export default {
  name: 'DarkLightImage',

  props: {
    path: {
      type: String, // i.e. 'logo/compact'
      required: true,
    },
    filename: {
      type: String, // i.e. 'logo-compact'
      required: true,
    },
    format: {
      type: String, // i.e. 'png'
      required: true,
    },
    alt: {
      type: String, // i.e. 'Logo'
      default: '',
    },
  },

  data() {
    return {
      themes: Themes,
    }
  },

  computed: {
    theme() {
      return currentThemeValue()
    },
  },
}
</script>
