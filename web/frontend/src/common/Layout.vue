<template>
  <div class="page-wrapper" :class="{'collapsed': collapsed, 'is-in-mobile': inMobileWebView}">
    <!-- Sidebar -->
    <nav class="side-nav">
      <a href="/" class="sidebar-header">
        <dark-light-image path="logo-square" ext="png" alt="TSD" class="logo-small"></dark-light-image>
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
                <li :class="{'active': path === '/ent/subscription/'}">
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
        'hide-top-nav-on-desktop': !$slots.topBarLeft && !$slots.desktopActions && !$slots.sort && !$slots.filter,
        'hide-kebab-menu-on-mobile': !$slots.mobileActions && !$slots.sort && !$slots.filter,
        'no-sort-and-filter': !$slots.sort && !$slots.filter,
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
        <div class="toolbar">
          <div class="desktop-actions-slot">
            <slot name="desktopActions"></slot>
          </div>

          <b-dropdown right no-caret class="kebab-menu" toggle-class="icon-btn">
            <template #button-content>
              <i class="fas fa-ellipsis-v"></i>
            </template>

            <div class="mobile-actions-slot" v-show="!sortOpened && !filterOpened">
              <slot name="mobileActions"></slot>
            </div>
            <b-dropdown-divider class="d-md-none" v-if="$slots.mobileActions && ($slots.sort || $slots.filter)"></b-dropdown-divider>

            <template v-if="!sortOpened && !filterOpened">
              <b-dropdown-item v-if="$slots.sort">
                <div class="d-flex justify-content-between clickable-area" @click.stop.prevent="sortOpened = true">
                  <div><i class="fas fa-sort-amount-up"></i>Sort</div>
                  <div><i class="fas fa-chevron-right m-0"></i></div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item v-if="$slots.filter">
                <div class="d-flex justify-content-between clickable-area" @click.stop.prevent="filterOpened = true">
                  <div><i class="fas fa-filter"></i>Filter</div>
                  <div><i class="fas fa-chevron-right m-0"></i></div>
                </div>
              </b-dropdown-item>
            </template>
            <template v-if="sortOpened">
              <b-dropdown-item>
                <div @click.stop.prevent="sortOpened = false" class="clickable-area">
                  <i class="fas fa-chevron-left"></i>Back
                </div>
              </b-dropdown-item>
              <slot name="sort"></slot>
            </template>
            <template v-else-if="filterOpened">
              <b-dropdown-item>
                <div @click.stop.prevent="filterOpened = false" class="clickable-area">
                  <i class="fas fa-arrow-left"></i>Back
                </div>
              </b-dropdown-item>
              <slot name="filter"></slot>
            </template>
          </b-dropdown>
        </div>
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
      sortOpened: false,
      filterOpened: false,
    }
  },

  computed: {
    inMobileWebView() {
      return inMobileWebView()
    },
    dhBadgeNum() {
      if (this.user && this.user.is_dh_unlimited) {
        return'\u221E'
      } else {
        return Math.round(this.user.dh_balance)
      }
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
    .side-nav
      display: none
    .toggle-sidebar
      display: none

    .content-wrapper.hide-top-nav-on-desktop
      .top-nav
        display: none
      .page-content
        padding: 15px 0

.side-nav
  min-width: 100px
  max-width: 100px
  text-align: center
  background: rgb(var(--color-surface))
  position: fixed
  left: 0
  top: 0
  height: 100%
  display: flex
  flex-direction: column
  z-index: 1000
  overflow-y: scroll
  transition: all .2s ease-out
  border-right: 1px solid rgb(var(--color-divider))
  .sidebar-header
    flex: 0 0 50px
    display: flex
    align-items: center
    justify-content: center
    border-bottom: 1px solid rgb(var(--color-divider))
    // border-right: 1px solid rgb(var(--color-divider))
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
        &:hover
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
        background: rgb(var(--color-hover) / 0.075)
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

.content-wrapper
  width: 100%

.top-nav
  height: 50px
  background: rgb(var(--color-surface)) !important
  position: fixed
  top: 0
  left: 0
  width: 100%
  padding-left: calc(100px + 15px)
  padding-right: 32px
  z-index: 100
  // box-shadow: var(--shadow-top-nav)
  justify-content: space-between

::v-deep .dropdown-menu
  .dropdown-item
    .clickable-area
      margin: -0.25rem -1.5rem
      padding: 0.25rem 1.5rem
    i
      width: 20px
      margin-right: .5rem

.toggle-sidebar
  color: rgb(var(--color-text-primary))
  display: none

.mobile-actions-slot
  display: none

.toolbar
  display: flex
  align-items: center

.page-content
  padding: calc(50px + var(--gap-between-blocks)) calc(var(--gap-between-blocks) - 15px) var(--gap-between-blocks)
  display: flex
  flex-direction: column
  justify-content: center
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

@media (min-width: 769px)
  .content-wrapper
    &.hide-top-nav-on-desktop
      .top-nav
        display: none
      .page-content
        padding-top: 30px
        min-height: calc(100vh - 68px)
    &.no-sort-and-filter .kebab-menu
      display: none

@media (max-width: 768px)
  .page-wrapper
    padding-left: 0
    &:not(.collapsed) .content-overlay
      display: block
    &.collapsed
      .side-nav
        transform: translateX(-100px)

  .content-wrapper.hide-kebab-menu-on-mobile .kebab-menu
    display: none

  .top-nav
    padding-left: 15px
    padding-right: 15px
    background: rgb(var(--color-surface)) !important

  .toggle-sidebar
    display: block

  .desktop-actions-slot
    display: none

  .mobile-actions-slot
    display: block

  .page-content
    padding: 15px 0
    padding-top: calc(50px + 15px)
    justify-content: start
</style>
