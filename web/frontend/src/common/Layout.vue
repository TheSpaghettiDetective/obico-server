<template>
  <div class="page-wrapper" :class="{'collapsed': collapsed, 'is-in-mobile': isInMobile}">

    <!-- Sidebar -->
    <nav class="side-nav">
      <a href="/" class="sidebar-header">
        <dark-light-image path="logo-square" ext="png" alt="TSD" class="logo-small"></dark-light-image>
      </a>

      <ul class="list-unstyled m-0">
        <li v-if="user" :class="{'active': path === '/printers/'}">
          <a href="/printers/">
            <i class="fas fa-print"></i>
            Printers
          </a>
        </li>
        <li v-if="user" :class="{'active': path === '/prints/'}">
          <a href="/prints/">
            <i class="fas fa-video"></i>
            Time-Lapse
          </a>
        </li>
        <li v-if="user" :class="{'active': path === '/gcodes/'}">
          <a href="/gcodes/">
            <i class="fas fa-code"></i>
            G-Code
          </a>
        </li>
        <li v-if="!user" class="glowing" :class="{'active': path === '/publictimelapses/'}">
          <a href="/publictimelapses/">
            <i class="fas fa-images"></i>
            Spaghetti Gallery
          </a>
        </li>
        <li v-if="isEnt" :class="{'active': path === '/ent/pricing/'}">
          <a href="/ent/pricing/">
            <i class="fas fa-dollar-sign"></i>
            Pricing
          </a>
        </li>
        <li>
          <a href="https://www.thespaghettidetective.com/help/">
            <i class="fas fa-question"></i>
            Help
          </a>
        </li>
        <li>
          <a href="https://discord.gg/hsMwGpD">
            <i class="fas fa-comments"></i>
            Forum
          </a>
        </li>
      </ul>

      <div class="side-nav-footer">
        <ul class="list-unstyled m-0">
          <!-- <li>
            <a href="#">
              <svg viewBox="0 0 384 550" width="14.66" height="21">
                <use href="#svg-detective-hours" />
              </svg>
              <br />
              <span id="user-credits" class="badge badge-light">20</span>
              <span class="sr-only">Detective Hours</span>
            </a>
          </li> -->
          <li v-if="user">
            <a v-b-toggle:userActions class="dropdown-toggle">
              <i class="fas fa-user"></i>
              <span>{{ user.first_name || user.email }}</span>
            </a>
            <b-collapse id="userActions">
              <ul class="list-unstyled">
                <li :class="{'active': path === '/user_preferences/'}">
                  <a href="/user_preferences/">Settings</a>
                </li>
                <li>
                  <a href="/accounts/logout/">Logout</a>
                </li>
              </ul>
            </b-collapse>
          </li>
          <li v-if="!user">
            <a href="/accounts/login/">
              Sign In
            </a>
          </li>
          <li v-if="!user && allowSignUp">
            <a href="/accounts/signup/">
              Sign Up
            </a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="content-wrapper" :class="{'hide-toolbar': !toolbar}">
      <b-navbar class="top-nav">
        <b-button @click="collapsed = !collapsed" variant="_" class="shadow-none p-0 toggle-menu">
          <i class="fas fa-align-left"></i>
        </b-button>

        <div class="toolbar">
          <slot name="toolbar"></slot>
        </div>
      </b-navbar>

      <div class="page-content">
        <b-alert :show="needsEmailVerification" variant="warning" class="text-center mb-3">
          You will not get notified by email on print failure, as your primary email address is not verified.
          <a href="/accounts/email/">Verify your email address.</a>
        </b-alert>
        <slot name="content"></slot>
      </div>
    </div>

    <div class="overlay" @click="collapsed = true"></div>
  </div>
</template>

<script>
import moment from 'moment'
import DarkLightImage from '@common/DarkLightImage.vue'
import { isMobile } from '@lib/app_platform'

export default {
  name: 'Layout',

  components: {
    DarkLightImage,
  },

  props: {
    toolbar: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      collapsed: true,
      path: window.location.pathname,
      user: null,
      allowSignUp: false,
      isEnt: false,
      isInMobile: false,
    }
  },

  computed: {
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

  created() {
    const {ACCOUNT_ALLOW_SIGN_UP, IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = JSON.parse(document.querySelector('#user-json').text)
    this.isInMobile = isMobile() || this.path.startsWith('/mobile/') || new URLSearchParams(window.location.search).get('inMobile') === 'true'
  },

  mounted () {
  },
}
</script>

<style lang="sass" scoped>
.page-wrapper
  display: flex
  align-items: stretch
  padding-left: 100px

  .overlay
    display: none

  .side-nav
    min-width: 100px
    max-width: 100px
    text-align: center
    background: rgb(var(--color-surface-primary))
    position: fixed
    left: 0
    top: 0
    height: 100%
    display: flex
    flex-direction: column
    z-index: 1000
    overflow-y: scroll

    .sidebar-header
      flex: 0 0 50px
      display: flex
      align-items: center
      justify-content: center
      border-bottom: 1px solid rgb(var(--color-divider))

    ul
      li
        a
          display: block
          color: rgb(var(--color-text-primary))
          padding: 10px 5px
          text-align: center
          font-size: 0.85em
          &:hover, &[aria-expanded="true"]
            color: rgb(var(--color-text-primary))
            background: rgb(var(--color-hover) / .075)

          &.dropdown-toggle
            cursor: pointer
            padding-bottom: 20px

          i
            margin-right: 0
            display: block
            font-size: 1.4em
            margin-bottom: 5px

        &.active > a
          color: rgb(var(--color-on-primary))
          background: rgb(var(--color-primary))
        &.glowing
          text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px rgb(var(--color-primary)), 0 0 70px rgb(var(--color-primary)), 0 0 80px rgb(var(--color-primary)), 0 0 100px rgb(var(--color-primary)), 0 0 150px rgb(var(--color-primary))


      ul a
        font-size: 0.9em !important
        padding: 10px !important

      .dropdown-toggle::after
        top: auto
        bottom: 10px
        right: 50%
        -webkit-transform: translateX(50%)
        -ms-transform: translateX(50%)
        transform: translateX(50%)

    ul.components
      padding: 20px 0

    ::v-deep .logo-small img
      width: 30px
      height: 30px

    .dropdown-toggle
      position: relative
      span
        display: inline-block
        white-space: nowrap
        overflow: hidden
        text-overflow: ellipsis
        width: 100%
      &::after
        display: block
        position: absolute
        top: 50%
        right: 20px
        transform: translateY(-50%)

    .side-nav-footer
      margin-top: auto

  .top-nav
    height: 50px
    background: rgb(var(--color-surface-secondary)) !important
    position: fixed
    top: 0
    left: 0
    width: 100%
    padding-left: calc(100px + 15px)
    z-index: 100
    box-shadow: var(--shadow-top-nav)
    justify-content: space-between

    .toggle-menu
      visibility: hidden

    .toolbar
      display: flex
      align-items: center

  .content-wrapper
    width: 100%
    // min-height: calc(100vh - 68px)

    .page-content
      padding: 30px
      padding-top: calc(50px + 30px)
      display: flex
      flex-direction: column
      justify-content: center
      min-height: calc(100vh - 68px - 50px)

  @media (min-width: 769px)
    .content-wrapper.hide-toolbar
      .top-nav
        display: none
      .page-content
        padding-top: 30px
        min-height: calc(100vh - 68px)

  @media (max-width: 768px)
    padding-left: 0

    .side-nav
      transition: all .2s ease-out

    .top-nav
      padding-left: 15px

      .toggle-menu
        visibility: visible

    .content-wrapper
      transform: translateX(100px)
      transition: all .2s ease-out

      .page-content
        padding: 15px 0
        padding-top: calc(50px + 15px)

    .overlay
      position: fixed
      top: 0
      left: 0
      width: 100%
      height: 100%
      z-index: 100
      background: rgb(0,0,0,.5)
      display: block

    &.collapsed
      .side-nav
        transform: translateX(-100px)
      .content-wrapper
        transform: translateX(0)
      .overlay
        display: none

  &.is-in-mobile
    .side-nav
      display: none !important
    .top-nav
      display: none !important
    .content-wrapper
      .page-content
        padding: 15px !important









// .badge-btn
//   position: relative
//   height: 1.8rem
//   margin-right: 1.5em

//   img
//     height: 1.3rem

//   .badge
//     position: absolute
//     left: 22px
//     top: 1px
//     height: 18px
//     border-radius: 4px
//     transition: transform 0.2s

//     /* Animation */
//     &:hover
//       transform: scale(1.3)
</style>
