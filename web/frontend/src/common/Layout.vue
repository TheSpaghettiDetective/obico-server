<template>
  <div class="page-wrapper" :class="{'collapsed': collapsed, 'is-in-mobile': inMobileWebView}">
    <!-- Sidebar -->
    <nav class="side-nav">
      <a href="/" class="sidebar-header">
        <dark-light-image path="logo-bat" ext="png" alt="TSD" class="logo-small"></dark-light-image>
      </a>
      <ul class="list-unstyled m-0">
        <li v-if="user" :class="{'active': path === '/printers/'}">
          <a href="/printers/">
            <svg viewBox="0 0 359 383" width="100%" height="1.4em" fill="currentColor" style="margin-bottom: 5px">
              <use href="#svg-3d-printer" />
            </svg>
            Printers
          </a>
        </li>
        <li v-if="user" :class="{'active': path === '/prints/'}">
          <a href="/prints/">
            <i class="fas fa-video"></i>
            Time-Lapses
          </a>
        </li>
        <li v-if="user" :class="{'active': path === '/gcodes/'}">
          <a href="/gcodes/">
            <i class="far fa-file-code"></i>
            G-Codes
          </a>
        </li>
        <li v-if="isEnt && !user" class="glowing" :class="{'active': path === '/ent_pub/publictimelapses/'}">
          <a href="/ent_pub/publictimelapses/">
            <i class="fas fa-images"></i>
            Spaghetti Gallery
          </a>
        </li>
        <li v-if="isEnt" :class="{'active': path === '/ent_pub/pricing/'}">
          <a href="/ent_pub/pricing/">
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
            Community
          </a>
        </li>
      </ul>
      <div class="side-nav-footer">
        <ul class="list-unstyled m-0">
          <li v-if="user">
            <a v-b-toggle:userActions class="dropdown-toggle">
              <i class="fas fa-user"></i>
              <span>{{ user.first_name || user.email }}</span>
            </a>
            <b-collapse id="userActions">
              <ul class="list-unstyled">
                <li :class="{'active': path === '/user_preferences/'}">
                  <a href="/user_preferences/">Preferences</a>
                </li>
                <li v-if="isEnt" :class="{'active': path === '/ent/subscription/'}">
                  <a href="/ent/subscription/">Account</a>
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
    <!-- Main view (with top-bar) -->
    <div
      class="content-wrapper"
      :class="{
        'hide-top-nav': !$slots.topBarLeft && !$slots.topBarRight
      }"
    >
      <!-- Top-bar -->
      <b-navbar class="top-nav">
        <div class="d-flex">
          <b-button @click="collapsed = !collapsed" variant="_" class="shadow-none p-0 mr-3 toggle-sidebar">
            <i class="fas fa-bars"></i>
          </b-button>
          <slot name="topBarLeft"></slot>
        </div>
        <slot name="topBarRight"></slot>
      </b-navbar>
      <!-- Page content -->
      <div class="page-content">
        <slot name="content"></slot>
      </div>
    </div>
    <div class="content-overlay" @click="collapsed = true"></div>
  </div>
</template>

<script>
import { inMobileWebView } from '@lib/page_context'
import DarkLightImage from '@common/DarkLightImage.vue'

export default {
  name: 'Layout',

  components: {
    DarkLightImage,
  },

  data() {
    return {
      collapsed: true,
      path: window.location.pathname,
      user: null,
      allowSignUp: false,
      isEnt: false,
    }
  },

  computed: {
    inMobileWebView() {
      return inMobileWebView()
    },
  },

  created() {
    const {ACCOUNT_ALLOW_SIGN_UP, IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = JSON.parse(document.querySelector('#user-json').text)
  },

  mounted() {
    // Temporary solution to correctly show alerts inserted by `snippets/messages.html` from Django
    const staticAlert = document.querySelector('.alert:not(.custom-alert)')
    if (staticAlert) {
      staticAlert.style.marginTop = '50px'
    }
  },
}
</script>

<style lang="sass" scoped>
.page-wrapper
  display: flex
  padding-left: 100px
  &.is-in-mobile
    padding-left: 0
    .side-nav
      display: none
    .toggle-sidebar
      display: none

    .content-wrapper.hide-top-nav
      .top-nav
        display: none
      .page-content
        padding: 15px 0

.side-nav
  min-width: 100px
  max-width: 100px
  text-align: center
  background: var(--color-surface-primary)
  position: fixed
  left: 0
  top: 0
  height: 100%
  display: flex
  flex-direction: column
  z-index: 1000
  overflow-y: auto
  transition: all .2s ease-out
  border-right: 1px solid var(--color-divider)
  .sidebar-header
    flex: 0 0 50px
    display: flex
    align-items: center
    justify-content: center
    border-bottom: 1px solid var(--color-divider)
  ul
    li
      a
        display: block
        color: var(--color-text-primary)
        padding: 10px 5px
        text-align: center
        font-size: 0.85em
        &:hover, &[aria-expanded="true"]
          color: var(--color-text-primary)
        &:hover
          background: var(--color-hover)
        &.dropdown-toggle
          cursor: pointer
          padding-bottom: 20px
        i
          margin-right: 0
          display: block
          font-size: 1.4em
          margin-bottom: 5px
      &.active > a
        background: var(--color-hover)
      &.glowing
        text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px var(--color-primary), 0 0 70px var(--color-primary), 0 0 80px var(--color-primary), 0 0 100px var(--color-primary), 0 0 150px var(--color-primary)
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
    height: 36px
    width: auto
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

.content-wrapper
  width: 100%

.top-nav
  height: 50px
  background: var(--color-surface-primary) !important
  position: fixed
  top: 0
  left: 0
  width: 100%
  padding-left: calc(100px + 15px)
  padding-right: 32px
  z-index: 100
  box-shadow: var(--shadow-top-nav)
  justify-content: space-between

.toggle-sidebar
  color: var(--color-text-primary)
  display: none

.page-content
  padding: calc(50px + var(--gap-between-blocks)) calc(var(--gap-between-blocks) - 15px) var(--gap-between-blocks)
  display: flex
  flex-direction: column
  min-height: calc(100vh - 68px)

.content-overlay
  position: fixed
  top: 0
  left: 0
  width: 100%
  height: 100%
  z-index: 100
  background: rgb(0,0,0,.5)
  display: none

::v-deep .search-input input
  background-color: var(--color-surface-secondary)
  border-color: var(--color-surface-secondary)

@media (min-width: 769px)
  .content-wrapper
    &.hide-top-nav
      .top-nav
        display: none
      .page-content
        padding-top: 30px
        min-height: calc(100vh - 68px)

@media (max-width: 768px)
  .page-wrapper
    padding-left: 0
    &:not(.collapsed) .content-overlay
      display: block
    &.collapsed
      .side-nav
        transform: translateX(-100px)

  .top-nav
    padding-left: 15px
    padding-right: 15px
    background: var(--color-surface-primary) !important

  .toggle-sidebar
    display: block

  .page-content
    padding: 15px 0
    padding-top: calc(50px + 15px)
    justify-content: start

::v-deep .dropdown-menu
  .dropdown-item
    .clickable-area
      margin: -0.25rem -1.5rem
      padding: 0.25rem 1.5rem
    i
      width: 20px
      margin-right: .5rem


</style>
