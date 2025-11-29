<template>
  <div
    class="page-wrapper"
    :class="{ collapsed: collapsed, 'is-in-mobile': inMobileWebView, 'is-in-popup': isPopup }"
  >
    <!-- Sidebar -->
    <nav class="side-nav">
      <a href="/" class="sidebar-header">
        <SyndicateAwareSVG href="#svg-logo-compact" width="100" height="30" />
      </a>
      <ul class="list-unstyled m-0">
        <li v-if="isEnt && !user.is_pro" :class="{ active: path === '/ent_pub/pricing/' }">
          <a href="/ent_pub/pricing/" class="primary">
            <font-awesome-icon icon="star" />
            {{$t("Upgrade to Pro")}}
          </a>
        </li>
        <li v-if="user" :class="{ active: path.includes('/printers/') }">
          <a href="/printers/">
            <svg width="1.4em" height="1.4em" style="margin-bottom: 5px">
              <use href="#svg-3d-printer" />
            </svg>
            <br />
            {{$t("Printers")}}
          </a>
        </li>
        <li v-if="user" :class="{ active: path.includes('/g_code_') }">
          <a href="/g_code_folders/cloud/">
            <font-awesome-icon icon="fa-file-code" />
            {{$t("G-Codes")}}
          </a>
        </li>
        <li
          v-if="user"
          :class="{ active: path.includes('/print_history/') || path.includes('/prints/') }"
        >
          <a href="/print_history/">
            <font-awesome-icon icon="fa-calendar-days" />
            {{$t("Print History")}}
          </a>
        </li>
        <li v-if="user" :class="{ active: path.includes('/stats/') }">
          <a href="/stats/">
            <font-awesome-icon icon="fa-chart-pie" />
            {{$t("Statistics")}}
          </a>
        </li>
      </ul>
      <div class="side-nav-footer">
        <ul class="list-unstyled m-0">
          <li v-if="isEnt" :class="{ active: path === '/ent_pub/pricing/' }">
            <a href="/ent_pub/pricing/">
              <font-awesome-icon icon="fa-money-check-dollar" />
              {{$t("Pricing")}}
            </a>
          </li>
          <li>
            <a href="https://www.obico.io/help/" target="_blank">
              <font-awesome-icon icon="fa-circle-question" />
              {{$t("Help")}}
            </a>
          </li>
          <li>
            <a href="https://obico.io/discord" target="_blank">
              <font-awesome-icon icon="fa-brands fa-discord" />
              {{$t("Community")}}
            </a>
          </li>
          <li>
            <hr class="my-0 mx-2" />
          </li>
          <li v-if="user" :class="{ active: path === '/printer_events/' }">
            <a href="/printer_events/">
              <div class="position-relative">
                <font-awesome-icon icon="fas fa-bell" />
                <span v-if="hasUnseenPrinterEvents" class="badge">{{
                  unseenPrinterEventsDisplay
                }}</span>
              </div>
              <span class="trim-text">{{ $t("Notifications") }}</span>
            </a>
          </li>
          <li v-if="user" :class="{ active: path.includes('/user_preferences/') }">
            <a href="/user_preferences/">
              <font-awesome-icon icon="fas fa-cog" />
              <span class="trim-text">{{ $t("Preferences") }}</span>
            </a>
          </li>
        </ul>
      </div>
    </nav>
    <!-- Main view (with top-bar) -->
    <div
      class="content-wrapper"
      :class="{
        'hide-top-nav': (!$slots.topBarLeft && !$slots.topBarRight) || hideHeader,
      }"
    >
      <!-- Top-bar -->
      <b-navbar class="top-nav">
        <div class="d-flex align-items-center">
          <b-button
            variant="_"
            class="shadow-none p-0 mr-3 position-relative toggle-sidebar"
            @click="collapsed = !collapsed"
          >
            <i class="fas fa-bars position-relative">
              <div v-if="hasUnseenPrinterEvents" class="notification-dot">
                <svg width="8px" height="8px">
                  <use href="#svg-circle-icon" />
                </svg>
              </div>
            </i>
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
import get from 'lodash/get'
import { inMobileWebView, user, settings } from '@src/lib/page-context'

export default {
  name: 'PageLayout',

  props: {
    isPopup: {
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
    }
  },

  computed: {
    inMobileWebView() {
      return inMobileWebView()
    },
    hideHeader() {
      const urlParams = new URLSearchParams(window.location.search)
      return urlParams.get('hide_header') === 'true'
    },
    hasUnseenPrinterEvents() {
      return get(this.user, 'unseen_printer_events', 0) > 0
    },
    unseenPrinterEventsDisplay() {
      const num = get(this.user, 'unseen_printer_events', 0)
      return num > 99 ? '99+' : num
    },
  },

  created() {
    const { ACCOUNT_ALLOW_SIGN_UP, IS_ENT } = settings()
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = user()
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
  background-color: var(--color-background)
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

  &.is-in-popup
    padding-left: 0
    .side-nav
      display: none
    .toggle-sidebar
      display: none

    .top-nav
      position: relative
      padding: 0 15px
    .page-content
      padding: 15px 0
      min-height: unset

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
        margin: 4px
        border-radius: var(--border-radius-sm)
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
        i, ::v-deep .svg-inline--fa
          margin-right: 0
          display: block
          font-size: 1.4em
          margin-bottom: 5px
        ::v-deep .svg-inline--fa
          margin: 0 auto 5px
        .badge
          border-radius: 2em
          position: absolute
          top: -0.35em
          right: 2em
          padding: 0.25em 0.3em
          font-family: var(--default-font-family)
          font-size: .714rem
          font-weight: bold
          color: var(--color-on-danger)
          background-color: var(--color-danger)
          min-width: 1.6em
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

  ::v-deep .action-panel
    .action-btn
      box-sizing: border-box
      width: 36px
      padding-left: 0
      padding-right: 0
      @media (max-width: 768px)
        display: none

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
  min-height: 100vh

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

.notification-dot
  height: 50%
  top: -9px
  right: -3px
  position: absolute
  width: 50%
  color: var(--color-danger)

@media (min-width: 769px)
  .content-wrapper
    &.hide-top-nav
      .top-nav
        display: none
      .page-content
        padding-top: 30px
        min-height: 100vh

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
    i, .custom-svg-icon
      width: 20px
      margin-right: .5rem
  .b-dropdown-text
    padding-left: 0.75rem
    padding-right: 0.75rem
</style>
