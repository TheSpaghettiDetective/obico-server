<template>
  <div>
    <b-navbar
      v-if="!inMobileWebView"
      toggleable="xl"
      :class="{
        'navbar-dark': theme === themes.Dark,
        'navbar-light': theme === themes.Light,
      }"
    >
      <b-container class="p-0">
        <b-navbar-brand href="/">
          <SyndicateAwareSVG href="#svg-logo-compact" width="100" height="30" />
        </b-navbar-brand>

        <b-navbar-toggle target="navbar-toggle-collapse">
          <span class="navbar-toggler-icon"></span>
        </b-navbar-toggle>

        <b-collapse id="navbar-toggle-collapse" v-model="showMainMenu" is-nav>
          <b-navbar-nav>
            <b-nav-item
              v-if="user"
              href="/printers/"
              :class="{ active: viewName.includes('printers') }"
              >{{ $t("Printers") }}</b-nav-item
            >
            <b-nav-item
              v-if="user"
              href="/print_history/"
              :class="{ active: viewName.includes('print_history') }"
              >{{ $t("Print History") }}</b-nav-item
            >
            <b-nav-item
              v-if="user"
              href="/g_code_folders/cloud/"
              :class="{ active: viewName.includes('g_code_folders') }"
              >{{ $t("G-Codes") }}</b-nav-item
            >
            <b-nav-item
              v-if="isEnt && !user"
              href="/ent_pub/publictimelapses/"
              :class="{ active: viewName === 'publictimelapse_list' }"
              class="glowing"
              >{{ $t("Spaghetti Gallery") }}</b-nav-item
            >
            <b-nav-item
              v-if="isEnt"
              href="/ent_pub/pricing/"
              :class="{ active: viewName === 'pricing' }"
              >{{ $t("Pricing") }}</b-nav-item
            >
            <b-nav-item href="https://www.obico.io/help/">{{ $t("Help") }}</b-nav-item>
            <b-nav-item href="https://obico.io/discord">{{ $t("Community") }}</b-nav-item>
          </b-navbar-nav>

          <b-navbar-nav class="ml-auto">
            <b-nav-item v-if="!user" href="/accounts/login/">{{ $t("SIGN IN") }}</b-nav-item>
            <b-nav-item v-if="!user && allowSignUp" href="/accounts/signup/">{{ $t("SIGN UP") }}</b-nav-item>
            <b-nav-item-dropdown
              v-if="user"
              ref="accountDropdown"
              right
              toggle-class="user-menu"
              :text="user.first_name || user.email"
            >
              <b-dropdown-item href="/user_preferences/">
                <i class="fas fa-cog mr-2"></i>{{$t("Preferences")}}
              </b-dropdown-item>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item href="/accounts/logout/">
                <i class="fas fa-sign-out-alt mr-2"></i>{{$t("Log out")}}
              </b-dropdown-item>
            </b-nav-item-dropdown>
          </b-navbar-nav>
        </b-collapse>
      </b-container>
    </b-navbar>
  </div>
</template>

<script>
import { inMobileWebView, user, settings } from '@src/lib/page-context'
import { Themes } from '@static/js/color-scheme'
import { currentThemeValue } from '@src/lib/color-scheme-controller'

export default {
  name: 'NavBar',

  components: {},

  props: {
    viewName: {
      default() {
        return ''
      },
      type: String,
    },
  },

  data() {
    return {
      user: null,
      allowSignUp: false,
      isEnt: false,
      themes: Themes,
      showMainMenu: false,
    }
  },

  computed: {
    inMobileWebView() {
      return inMobileWebView()
    },

    theme() {
      return currentThemeValue()
    },
  },

  created() {
    const { ACCOUNT_ALLOW_SIGN_UP, IS_ENT } = settings()
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = user()
  },

  methods: {
    hideDropdowns() {
      this.showMainMenu = false

      // Check account dropdown (preferences and logout)
      const accountDropdown = this.$refs.accountDropdown
      if (accountDropdown) {
        accountDropdown.hide()
      }
    },
  },
}
</script>

<style lang="sass" scoped>
::v-deep .navbar
  padding: 0.5rem 1rem

  a.navbar-brand
    margin-top: -3px

  .navbar-toggler
    color: var(--color-text-primary)

  .nav-item
    text-transform: uppercase

  .user-menu
    text-transform: none

  .badge-btn
    position: relative
    height: 1.8rem
    margin-right: 1.5em

    img
      height: 1.3rem

    .badge
      position: absolute
      left: 22px
      top: 1px
      height: 18px
      border-radius: 4px
      transition: transform 0.2s

      /* Animation */
      &:hover
        transform: scale(1.3)

  @media (min-width: 1200px)
    padding: 0rem 1rem

    .nav-item
      padding: 0.5rem 0.24rem
</style>
