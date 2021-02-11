<template>
  <pull-to-reveal
    :enable="pullToReveal"
    :id="'main-nav'"
    :maxElementHeight="56"
    :zIndex="9"
    :showEdge="true"
    v-on:hide="hideDropdowns"
  >
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark static-top">
      <div class="container">
        <a class="navbar-brand" href="/printers/">
        <img :src="require('@static/img/logo-inverted.png')" style="height: 32px;" alt="The Spaghetti Detective" /></a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive"
          aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation" ref="mobileDropdown">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive" ref="mobileDropdownContent">
          <ul class="navbar-nav">

            <li v-if="user" class="nav-item" v-bind:class="{'active': viewName.includes('printers')}">
              <a class="nav-link" href="/printers/">Printer
              </a>
            </li>
            <li v-if="user" class="nav-item" v-bind:class="{'active': viewName.includes('prints')}">
              <a class="nav-link" href="/prints/">Time-lapse
              </a>
            </li>
            <li v-if="user" class="nav-item" v-bind:class="{'active': viewName.includes('gcodes')}">
              <a class="nav-link" href="/gcodes/">G-Code
              </a>
            </li>

            <li v-if="!user" class="nav-item" v-bind:class="{'active': viewName === 'publictimelapse_list'}">
              <a class="nav-link glowing" href="/publictimelapses/">Spaghetti Gallery</a>
            </li>

            <li v-if="isEnt" class="nav-item" v-bind:class="{'active': viewName === 'pricing'}">
              <a class="nav-link" href="/ent/pricing/">Pricing</a>
            </li>

            <li class="nav-item">
              <a class="nav-link" href="https://www.thespaghettidetective.com/help">Help</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://discord.gg/hsMwGpD">Forum</a>
            </li>
          </ul>

          <ul class="navbar-nav ml-auto">
            <li v-if="!user" class="nav-item">
              <a class="nav-link" href="/accounts/login/">Sign In</a>
            </li>
            <li v-if="!user && allowSignUp" class="nav-item">
              <a class="nav-link" href="/accounts/signup/">Sign up</a>
            </li>

            <li v-if="isEnt" class="nav-item">
              <a href="/ent/subscription/#detective-hour-balance" class="nav-link badge-btn">
                  <img :src="require('@static/img/detective-hour-inverse.png')">
                  <span id="user-credits" class="badge badge-light">{{dhBadgeNum}}</span>
                  <span class="sr-only">Detective Hours</span>
              </a>
            </li>

            <li v-if="user" class="nav-item dropdown" ref="accountDropdown">
              <a class="nav-link dropdown-toggle user-menu" data-toggle="dropdown" href="#" :id="user.id" aria-expanded="false">
                {{user.first_name || user.email}}
                <span class="caret"></span>
              </a>
              <div class="dropdown-menu dropdown-menu-right" aria-labelledby="themes" ref="accountDropdownContent">
                <a class="dropdown-item" href="/user_preferences/"><i class="fas fa-sliders-h"></i>Preferences</a>
                <a v-if="isEnt" class="dropdown-item" href="/ent/subscription/"><i class="far fa-user-circle"></i>Account</a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item" href="/accounts/logout/"><i class="fas fa-sign-out-alt"></i>Log out</a>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </pull-to-reveal>
</template>

<script>
import PullToReveal from './PullToReveal.vue'

export default {
  name: 'Navbar',

  components: {
    PullToReveal,
  },

  data() {
    return {
      user: null,
      allowSignUp: false,
      isEnt: false,
    }
  },

  props: {
    pullToReveal: {
      default() {return false},
      type: Boolean,
    },
    viewName: {
      default() {return ''},
      type: String,
    },
  },

  created() {
    const {ACCOUNT_ALLOW_SIGN_UP, IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = JSON.parse(document.querySelector('#user-json').text)
  },

  computed: {
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return'\u221E'
      } else {
        return Math.round(this.user.dh_balance)
      }
    }
  },

  methods: {
    hideDropdowns() {
      // Check account dropdown (preferences and logout)
      const accountDropdown = this.$refs.accountDropdown
      if (accountDropdown.classList.contains('show')) {
        accountDropdown.classList.remove('show')
        this.$refs.accountDropdownContent.classList.remove('show')
      }

      // Check main menu toggler (on mobiles)
      const mobileDropdown = this.$refs.mobileDropdown
      if (mobileDropdown.getAttribute('aria-expanded')) {
        mobileDropdown.classList.add('collapsed')
        this.$refs.mobileDropdownContent.classList.remove('show')
      }
    }
  }
}
</script>

<style lang="sass" scoped>
.navbar
  padding: 0.5rem 1rem

  a.navbar-brand
    margin-top: -3px

  .nav-item
    text-transform: uppercase

    &.active, &:hover
      background-color: #596a7b

  .user-menu
    text-transform: none

  a.glowing
    text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #9965f4, 0 0 70px #9965f4, 0 0 80px #9965f4, 0 0 100px #9965f4, 0 0 150px #9965f4

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
      background-color: #9965f4
      transition: transform 0.2s

      /* Animation */
      &:hover
        transform: scale(1.3)

  @media (min-width: 992px)
    padding: 0rem 1rem

    .nav-item
      padding: 0.5rem 0.24rem
</style>





