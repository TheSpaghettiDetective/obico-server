<template>
  <section class="personalization">
    <h2 class="section-title">{{ $t("Appearance") }}</h2>
    <div class="form-group row mt-3">
      <label class="col-md-2 col-sm-3 col-form-label">{{ $t("Theme") }}</label>
      <div class="col-sm-9 col-md-10">
        <div class="theme-controls">
          <div class="theme-toggle" :class="[themeValue]" @click="toggleTheme">
            <svg class="icon" :class="{ active: themeValue === Themes.Dark }">
              <use href="#svg-moon-icon" />
            </svg>
            <div class="label">
              <span v-show="themeValue === Themes.Dark" class="dark">{{ $t("DARK") }}</span>
              <span v-show="themeValue === Themes.Light" class="light">{{ $t("LIGHT") }}</span>
            </div>
            <svg class="icon" :class="{ active: themeValue === Themes.Light }">
              <use href="#svg-sun-icon" />
            </svg>
            <div class="active-indicator" :class="{ right: themeValue === Themes.Light }">
              <div class="circle"></div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="showSystemTheme" class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <div class="custom-control custom-checkbox form-check-inline system-theme-control">
          <input
            id="id_theme_system"
            v-model="systemTheme"
            type="checkbox"
            class="custom-control-input"
          />
          <label class="custom-control-label" for="id_theme_system">
            {{$t("Sync theme with system settings")}}
          </label>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { Themes } from '@static/js/color-scheme'
import { theme, setTheme, currentThemeValue } from '@src/lib/color-scheme-controller'
import { mobilePlatform } from '@src/lib/page-context'

export default {
  name: 'ThemePreferences',

  data() {
    return {
      Themes: Themes,
    }
  },

  computed: {
    themeValue() {
      return currentThemeValue()
    },
    showSystemTheme() {
      return mobilePlatform() !== 'android'
    },
    systemTheme: {
      get() {
        return theme.value === Themes.System
      },
      set(newValue) {
        theme.value = Themes.System
        this.selectTheme(newValue ? this.Themes.System : this.themeValue)
      },
    },
  },

  methods: {
    /**
     * Toggle color theme
     */
    toggleTheme() {
      const newTheme = this.themeValue === Themes.Light ? Themes.Dark : Themes.Light
      this.systemTheme = false
      this.selectTheme(newTheme)
    },
    selectTheme(newTheme) {
      setTheme(newTheme)
      if (window.ReactNativeWebView) {
        window.ReactNativeWebView.postMessage(JSON.stringify({ theme: newTheme }))
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.theme-controls
  display: flex
  align-items: center

.theme-toggle
  display: inline-flex
  align-items: center
  background-color: var(--color-input-background)
  border-radius: 100px
  position: relative
  margin-right: 26px

  &:hover
    cursor: pointer

  & > *
    position: relative
    z-index: 2

  .icon
    flex: 0 0 18px
    height: 18px
    width: 18px
    margin: 10px
    color: #ABB6C2

    &.active
      color: #4B5B69

  .label
    flex: 1
    text-align: center
    font-size: 12px
    color: var(--color-text-primary)
    padding: 0 8px

  .active-indicator
    position: absolute
    width: calc(100% - 8px)
    height: 30px
    top: 0
    bottom: 0
    left: 0
    right: 0
    margin: auto
    z-index: 1
    transition: all .3s ease-out

    .circle
      position: absolute
      width: 30px
      height: 30px
      border-radius: 30px
      background-color: #fff
      transition: all .3s ease-in-out

    &.right
      transform: translateX(100%)

      .circle
        transform: translateX(-100%)

.system-theme-control
  position: relative
  z-index: 3
</style>
