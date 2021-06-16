<template>
  <div>
    <nav
      v-if="!isInMobile"
      class="navbar navbar-expand-lg bg-dark static-top flex-column"
      :class="{'navbar-dark': theme === themes.Dark, 'navbar-light': theme === themes.Light}"
    >
      <div class="container">
        <a class="navbar-brand" href="/printers/">
          <dark-light-image path="navbar-brand" ext="png" alt="The Spaghetti Detective"></dark-light-image>
        </a>
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
              <a class="nav-link" href="https://help.thespaghettidetective.com/">Help</a>
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

            <li v-if="isEnt && user" class="nav-item">
              <a href="/ent/subscription/#detective-hour-balance" class="nav-link badge-btn">
                  <svg class="detective-hours" width="14.66" height="21" viewBox="0 0 384 550" xmlns="http://www.w3.org/2000/svg">
                    <path d="M363.11 44V43.85H370.48C372.207 43.85 373.918 43.5095 375.513 42.8479C377.109 42.1863 378.558 41.2166 379.778 39.9943C380.999 38.772 381.966 37.3211 382.626 35.7246C383.285 34.1281 383.623 32.4173 383.62 30.69V13.84C383.621 12.1136 383.282 10.4038 382.623 8.80848C381.963 7.2131 380.995 5.76338 379.775 4.54216C378.555 3.32093 377.106 2.35215 375.511 1.69118C373.916 1.03021 372.206 0.690006 370.48 0.690006H13.54C11.8123 0.688692 10.1012 1.02785 8.50464 1.68811C6.90805 2.34838 5.45723 3.31679 4.23508 4.53801C3.01293 5.75923 2.04342 7.20932 1.38194 8.80541C0.720468 10.4015 0.380004 12.1123 0.380005 13.84V30.64C0.377371 32.3689 0.71597 34.0814 1.37639 35.6792C2.03681 37.2771 3.00606 38.7289 4.22861 39.9514C5.45115 41.1739 6.90294 42.1432 8.50078 42.8036C10.0986 43.464 11.8111 43.8026 13.54 43.8H22.24V44C22.24 49.52 23.35 194 139.49 274.93C22.24 351.59 22.24 506.2 22.24 506.2H13.54C11.8111 506.197 10.0986 506.536 8.50078 507.196C6.90294 507.857 5.45115 508.826 4.22861 510.049C3.00606 511.271 2.03681 512.723 1.37639 514.321C0.71597 515.919 0.377371 517.631 0.380005 519.36V536.16C0.380004 537.888 0.720468 539.598 1.38194 541.195C2.04342 542.791 3.01293 544.241 4.23508 545.462C5.45723 546.683 6.90805 547.652 8.50464 548.312C10.1012 548.972 11.8123 549.311 13.54 549.31H370.48C372.206 549.31 373.916 548.97 375.511 548.309C377.106 547.648 378.555 546.679 379.775 545.458C380.995 544.237 381.963 542.787 382.623 541.192C383.282 539.596 383.621 537.886 383.62 536.16V519.36C383.623 517.633 383.285 515.922 382.626 514.325C381.966 512.729 380.999 511.278 379.778 510.056C378.558 508.833 377.109 507.864 375.513 507.202C373.918 506.541 372.207 506.2 370.48 506.2H363.11C363.11 506.2 363.11 351.59 245.86 274.88C362 194 363.11 49.47 363.11 44ZM253.4 320C333.8 401.86 332.47 506.19 332.47 506.19H51.55C51.55 506.19 50.22 401.87 130.6 320C145.68 304.62 161.04 296.9 172.6 293.07C184.16 289.24 192 289.21 192 289.21C192 289.21 223.26 289.22 253.4 320ZM192 260.78C192 260.78 184.18 260.78 172.6 256.92C161.02 253.06 145.67 245.39 130.6 229.99C50.22 148.11 51.55 43.8 51.55 43.8H332.47C332.47 43.8 333.8 148.11 253.4 230C223.26 260.78 192 260.78 192 260.78Z" />
                    <path d="M320.24 490.4H64.63C64.63 446 192.05 346.4 192.05 346.4C192.05 346.4 320.24 446.85 320.24 490.4Z" />
                    <path d="M270.69 167.94C270.685 173.993 269.043 179.933 265.94 185.13C255.78 202.13 229.74 239.53 192.01 249.42C156.84 239.93 129.75 203.65 118.72 186.69C115.206 181.267 113.337 174.942 113.34 168.48V167.94H270.69Z" />
                    <path d="M320.24 490.4H64.63C64.63 446 192.05 346.4 192.05 346.4C192.05 346.4 320.24 446.85 320.24 490.4Z" />
                  </svg>
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
    <div v-if="needsEmailVerification" class="alert alert-warning text-center" role="alert">
      You will not get notified by email on print failure, as your primary email address is not verified. <a href="/accounts/email/">Verify your email address.</a>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import { isMobile } from '@lib/app_platform'
import DarkLightImage from '@common/DarkLightImage.vue'
import { Themes, theme } from '../main/themes.js'

export default {
  name: 'Navbar',

  components: {
    DarkLightImage,
  },

  data() {
    return {
      user: null,
      allowSignUp: false,
      isEnt: false,
      isInMobile: false,
      themes: Themes,
    }
  },

  props: {
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
    this.isInMobile = isMobile() || window.location.pathname.startsWith('/mobile/') || new URLSearchParams(window.location.search).get('inMobile') === 'true'
  },

  computed: {
    theme() {
      return theme.value
    },

    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return'\u221E'
      } else {
        return Math.round(this.user.dh_balance)
      }
    },
    needsEmailVerification() {
        if (!this.user) {
          return false
        }

        // Give user 1 day before bugging them to verify their email addresses
        const signedUpLongerThan1Day = moment(this.user.date_joined).isBefore(moment().subtract(15,'days'))
        return this.isEnt && !this.user.is_primary_email_verified && signedUpLongerThan1Day
    }
  },

  methods: {
    hideDropdowns() {
      // Check account dropdown (preferences and logout)
      const accountDropdown = this.$refs.accountDropdown
      if (accountDropdown && accountDropdown.classList.contains('show')) {
        accountDropdown.classList.remove('show')
        this.$refs.accountDropdownContent.classList.remove('show')
      }

      // Check main menu toggler (on mobiles)
      const mobileDropdown = this.$refs.mobileDropdown
      if (mobileDropdown && mobileDropdown.getAttribute('aria-expanded')) {
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

    ::v-deep img
      width: 232px

  .nav-item
    text-transform: uppercase

  .user-menu
    text-transform: none

  // a.glowing
  //   text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #9965f4, 0 0 70px #9965f4, 0 0 80px #9965f4, 0 0 100px #9965f4, 0 0 150px #9965f4

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
      // background-color: #9965f4
      transition: transform 0.2s

      /* Animation */
      &:hover
        transform: scale(1.3)

  @media (min-width: 992px)
    padding: 0rem 1rem

    .nav-item
      padding: 0.5rem 0.24rem
  
.detective-hours path
  fill: rgb(var(--color-dark-white))
</style>





