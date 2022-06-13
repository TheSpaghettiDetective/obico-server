<template>
  <div class="page-wrapper" :class="{'collapsed': collapsed, 'is-in-mobile': inMobileWebView}">
    <!-- Sidebar -->
    <nav class="side-nav">
      <a href="/" class="sidebar-header">
        <svg class="logo-small">
          <use href="#svg-logo-compact" />
        </svg>
      </a>
      <ul class="list-unstyled m-0">
        <li v-if="isEnt && !user.is_pro" :class="{'active': path === '/ent_pub/pricing/'}">
          <a href="/ent_pub/pricing/" class="primary">
            <i class="fas fa-star"></i>
            Upgrade to Pro
          </a>
        </li>
        <li v-if="user" :class="{'active': path === '/printers/'}">
          <a href="/printers/">
            <svg width="1.4em" height="1.4em" style="margin-bottom: 5px">
              <use href="#svg-3d-printer" />
            </svg>
            <br>
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
            <i class="fas fa-file-code"></i>
            G-Codes
          </a>
        </li>
      </ul>
      <div class="side-nav-footer">
        <ul class="list-unstyled m-0">
          <li v-if="isEnt" :class="{'active': path === '/ent_pub/pricing/'}">
            <a href="/ent_pub/pricing/">
              <i class="fas fa-dollar-sign"></i>
              Pricing
            </a>
          </li>
          <li>
            <a href="https://www.obico.io/help/" target="_blank">
              <i class="fas fa-question"></i>
              Help
            </a>
          </li>
          <li>
            <a href="https://obico.io/discord" target="_blank">
              <i class="fas fa-comments"></i>
              Community
            </a>
          </li>
          <li>
            <hr class="my-0 mx-2">
          </li>
          <li v-if="user" :class="{'active': path === '/user_preferences/'}">
            <a href="/user_preferences/">
              <i class="fas fa-cog"></i>
              <span class="trim-text">Preferences</span>
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
        <content-top v-if="layoutSections.contentTop"></content-top>
        <slot name="content"></slot>
      </div>
    </div>
    <div class="content-overlay" @click="collapsed = true"></div>
  </div>
</template>

<script>
import { inMobileWebView } from '@src/lib/page_context'
import layoutSections from '@config/layout/sections'

export default {
  name: 'Layout',

  components: {
    ...Object.keys(layoutSections).reduce((obj, name) => {
      return Object.assign(obj, { [name]: layoutSections[name].importComponent })
    }, {}),
  },

  data() {
    return {
      layoutSections,
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
    const staticAlert = document.querySelector('.message-snippet')
    if (staticAlert && this.inMobileWebView) {
      staticAlert.classList.add('is-in-mobile')
    }
    if (this.inMobileWebView) {
      document.querySelector('body').style.paddingBottom = 0
    }
  },
}
</script>

<style lang="sass">
.message-snippet
  margin-top: 50px
  margin-left: 100px
  @media (max-width: 768px)
    margin-left: 0
  &.is-in-mobile
    margin-left: 0
</style>

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
        &.primary
          color: var(--color-primary)
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
  ::v-deep .logo-small
    width: 30px
    height: 30px
    color: var(--color-text-primary)
  .dropdown-toggle
    position: relative
    &::after
      display: block
      position: absolute
      top: 50%
      right: 20px
      transform: translateY(-50%)
  .side-nav-footer
    margin-top: auto
  .trim-text
    white-space: nowrap
    text-overflow: ellipsis
    display: inline-block
    overflow: hidden
    width: 100%

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

.is-in-mobile .top-nav
  padding-left: 15px
  padding-right: 15px
  background: var(--color-surface-primary) !important

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
    padding: 0.25rem 0.75rem
    .clickable-area
      margin: -0.25rem -0.75rem
      padding: 0.25rem 0.75rem
    i
      width: 20px
      margin-right: .5rem

::v-deep .active-filter-notice
  display: flex
  align-items: center
  justify-content: space-between
  padding: 0.5rem 1rem
  background-color: var(--color-surface-secondary)
  margin: calc(-1 * var(--gap-between-blocks)) -15px var(--gap-between-blocks)

  .filter
    color: var(--color-primary)

  @media (max-width: 768px)
    font-size: .875rem
    margin-left: 0
    margin-right: 0
</style>
