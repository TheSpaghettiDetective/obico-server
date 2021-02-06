<template>
  <pull-to-reveal
    :enable="pullToReveal"
    :id="'main-nav'"
    :maxElementHeight="56"
    :zIndex="9"
    :showEdge="true"
  >
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark static-top">
      <div class="container">
        <a class="navbar-brand" href="/printers/">
        <img :src="require('@static/img/logo-inverted.png')" style="height: 32px;" alt="The Spaghetti Detective" /></a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive"
          aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive">
          <ul class="navbar-nav">

            <li v-if="userData" class="nav-item" v-bind:class="{'active': viewName.includes('printers')}">
              <a class="nav-link" href="/printers/">Printer
              </a>
            </li>
            <li v-if="userData" class="nav-item" v-bind:class="{'active': viewName.includes('prints')}">
              <a class="nav-link" href="/prints/">Time-lapse
              </a>
            </li>
            <li v-if="userData" class="nav-item" v-bind:class="{'active': viewName.includes('gcodes')}">
              <a class="nav-link" href="/gcodes/">G-Code
              </a>
            </li>

            <li v-if="!userData" class="nav-item"  v-bind:class="{'active': viewName === 'publictimelapse_list'}">
              <a class="nav-link glowing" href="/publictimelapses/">Spaghetti Gallery</a>
            </li>

            <slot name="nav_item_pricing"></slot>

            <li class="nav-item">
              <a class="nav-link" href="https://www.thespaghettidetective.com/help">Help</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="https://discord.gg/hsMwGpD">Forum</a>
            </li>
          </ul>

          <ul class="navbar-nav ml-auto">
            <li v-if="!userData" class="nav-item">
              <a class="nav-link" href="/accounts/login/">Sign In</a>
            </li>
            <li v-if="!userData && allowSignUp" class="nav-item">
              <a class="nav-link" href="/accounts/signup/">Sign up</a>
            </li>

            <slot name="nav_item_dh_balance"></slot>

            <li v-if="userData" class="nav-item dropdown">
              <a class="nav-link dropdown-toggle user-menu" data-toggle="dropdown" href="#" :id="userData.id" aria-expanded="false">
                {{userData.first_name || userData.email}}
                <span class="caret"></span>
              </a>
              <div class="dropdown-menu dropdown-menu-right" aria-labelledby="themes">
                <a class="dropdown-item" href="/user_preferences/"><i class="fas fa-sliders-h"></i>Preferences</a>

                <slot name="nav_item_account"></slot>

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
import PullToReveal from '@/common/PullToReveal.vue'

export default {
  name: 'Navbar',

  components: {
    PullToReveal,
  },

  data() {
    return {
      
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
    userData: { // id, email, first_name (optional); if Null, assumes that user isn't authenticated
      default() {return null},
      type: Object,
    },
    allowSignUp: {
      default() {return true},
      type: Boolean,
    }
  },
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





