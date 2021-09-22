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
    <!-- Main view (with top-bar) -->
    <div
      class="content-wrapper"
      :class="{
        'hide-top-nav-on-desktop': !search && !$slots.desktopActions && !sortOptions.length && !filterOptions.length,
        'hide-kebab-menu-on-mobile': !$slots.mobileActions && !sortOptions.length && !filterOptions.length,
        'no-sort-and-filter': !sortOptions.length && !filterOptions.length,
      }"
    >
      <!-- Top-bar -->
      <b-navbar class="top-nav">
        <div class="d-flex">
          <b-button @click="collapsed = !collapsed" variant="_" class="shadow-none p-0 mr-3 toggle-sidebar">
            <i class="fas fa-bars"></i>
          </b-button>
          <search-input v-if="search" @input="updateSearch" class="search-input mr-3"></search-input>
          <div v-if="actionsWithSelected.length" class="actions-with-selected-desktop">
            <b-form-group class="m-0">
              <b-form-checkbox
                v-model="allSelectedInner"
                size="lg"
              ></b-form-checkbox>
            </b-form-group>
            <div class="select-all-content">
              <span class="label" @click="allSelectedInner = !allSelectedInner" v-show="!numberOfSelected">Select all</span>
              <b-dropdown v-show="numberOfSelected" class="" toggle-class="btn btn-sm">
                <template #button-content>
                  {{ numberOfSelected }} item{{ numberOfSelected === 1 ? '' : 's' }} selected...
                </template>
                <b-dropdown-item v-for="action in actionsWithSelected" :key="action.value">
                  <div :class="action.wrapperClass" @click="$emit('actionWithSelected', action.value)">
                    <i v-if="action.iconClass" :class="action.iconClass"></i>Delete
                  </div>
                </b-dropdown-item>
              </b-dropdown>
            </div>
          </div>
        </div>
        <div class="toolbar">
          <div class="desktop-actions-slot">
            <slot name="desktopActions"></slot>
          </div>
          <b-dropdown right no-caret class="kebab-menu" toggle-class="icon-btn">
            <template #button-content>
              <i class="fas fa-ellipsis-v"></i>
            </template>
            <div class="actions-with-selected-mobile">
              <template v-if="numberOfSelected">
                <b-dropdown-item v-for="action in actionsWithSelected" :key="action.value">
                  <div :class="action.wrapperClass" @click="$emit('actionWithSelected', action.value)">
                    <i v-if="action.iconClass" :class="action.iconClass"></i>Delete
                  </div>
                </b-dropdown-item>
                <b-dropdown-divider></b-dropdown-divider>
              </template>
              <template v-if="actionsWithSelected.length">
                <b-dropdown-item>
                  <div class="clickable-area" @click.stop.prevent="allSelectedInner = !allSelectedInner">
                    <i v-show="!allSelected" class="far fa-square"></i>
                    <i v-show="allSelected" class="fas fa-check-square text-primary"></i>
                    Select all
                  </div>
                </b-dropdown-item>
              </template>
            </div>
            <div class="mobile-actions-slot" v-show="!sortOpened && !filterOpened">
              <slot name="mobileActions"></slot>
            </div>
            <b-dropdown-divider class="d-md-none" v-if="$slots.mobileActions && (sortOptions.length || filterOptions.length)"></b-dropdown-divider>
            <template v-if="!sortOpened && !filterOpened">
              <b-dropdown-item v-if="sortOptions.length">
                <div class="d-flex justify-content-between clickable-area" @click.stop.prevent="sortOpened = true">
                  <div><i class="fas fa-sort-amount-up"></i>Sort</div>
                  <div><i class="fas fa-chevron-right m-0"></i></div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item v-if="filterOptions.length">
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
              <b-dropdown-item v-for="option in sortOptions" :key="option.value">
                <div @click="$emit('updateSort', option.value); sortOpened = false" class="clickable-area">
                  <i class="fas fa-check text-primary" :style="{visibility: activeSort === option.value ? 'visible' : 'hidden'}"></i>
                  {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
                </div>
              </b-dropdown-item>
            </template>
            <template v-else-if="filterOpened">
              <b-dropdown-item>
                <div @click.stop.prevent="filterOpened = false" class="clickable-area">
                  <i class="fas fa-arrow-left"></i>Back
                </div>
              </b-dropdown-item>
              <b-dropdown-item v-for="option in filterOptions" :key="option.value">
                <div @click="$emit('updateFilter', option.value); filterOpened = false" class="clickable-area">
                  <i class="fas fa-check text-primary" :style="{visibility: activeFilter === option.value ? 'visible' : 'hidden'}"></i>
                  {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
                </div>
              </b-dropdown-item>
            </template>
          </b-dropdown>
        </div>
      </b-navbar>
      <!-- Page content -->
      <div class="page-content">
        <b-alert :show="needsEmailVerification" variant="warning" class="custom-alert text-center mb-3">
          You will not get notified by email on print failure, as your primary email address is not verified.
          <a href="/accounts/email/">Verify your email address.</a>
        </b-alert>
        <slot name="content"></slot>
      </div>
    </div>
    <div class="content-overlay" @click="collapsed = true"></div>
  </div>
</template>

<script>
import moment from 'moment'
import { inMobileWebView } from '@lib/page_context'
import DarkLightImage from '@common/DarkLightImage.vue'
import SearchInput from '@common/SearchInput.vue'

export default {
  name: 'Layout',

  components: {
    DarkLightImage,
    SearchInput,
  },

  props: {
    // To display search input set this 'true' and listen @updateSearch event from parent
    search: {
      type: Boolean,
      default: false,
    },

    // To enable sorting pass these props and listen @updateSort event from parent
    sortOptions: {
      type: Array,
      default: () => [],
      // Example: [{value: 'date_asc', title: 'Sort By Date', iconClass{OPTIONAL}: 'fas fa-long-arrow-alt-up'}, ...]
    },
    activeSort: {
      type: String,
      default: '',
    },

    // To enable filtering pass these props and listen @updateFilter event from parent
    filterOptions: {
      type: Array,
      default: () => [],
      // Example: [{value: 'need_print_shot_feedback', title: 'Focused-review needed'}, ...]
    },
    activeFilter: {
      type: String,
      default: '',
    },

    // To enable specific actions for selected items pass these props and listen @updateAllSelected and @actionWithSelected events from parent
    actionsWithSelected: {
      type: Array,
      default: () => [],
      // Example: [{value: 'delete', title: 'Delete', iconClass{OPTIONAL}: 'far fa-trash-alt', wrapperClass{OPTIONAL}: 'text-danger'}, ...]
    },
    allSelected: {
      type: Boolean,
      default: false,
    },
    numberOfSelected: {
      type: Number,
      default: 0,
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
      sortOpened: false,
      filterOpened: false,
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
    },
    allSelectedInner: {
      get: function() {
        return this.allSelected
      },
      set: function(newValue) {
        this.$emit('updateAllSelected', newValue)
      }
    },
  },

  created() {
    const {ACCOUNT_ALLOW_SIGN_UP, IS_ENT} = JSON.parse(document.querySelector('#settings-json').text)
    this.allowSignUp = !!ACCOUNT_ALLOW_SIGN_UP
    this.isEnt = !!IS_ENT
    this.user = JSON.parse(document.querySelector('#user-json').text)
    this.isInMobile = inMobileWebView() || this.path.startsWith('/mobile/') || new URLSearchParams(window.location.search).get('inMobile') === 'true'
  },

  mounted() {
    // Temporary solution to correctly show alerts inserted by `snippets/messages.html` from Django
    const staticAlert = document.querySelector('.alert:not(.custom-alert)')
    if (staticAlert) {
      staticAlert.style.marginTop = '50px'
    }
  },

  methods: {
    updateSearch(search) {
      this.$emit('updateSearch', search)
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
  background: rgb(var(--color-surface-primary))
  position: fixed
  left: 0
  top: 0
  height: 100%
  display: flex
  flex-direction: column
  z-index: 1000
  overflow-y: scroll
  transition: all .2s ease-out
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

.content-wrapper
  width: 100%

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

.search-input
  height: 30px

.mobile-actions-slot
  display: none

.actions-with-selected-desktop
  display: flex
  align-items: center
  .label
    cursor: pointer

.actions-with-selected-mobile
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

  .content-wrapper
    align-items: start
    &.hide-kebab-menu-on-mobile
      .kebab-menu
        display: none

  .top-nav
    padding-left: 15px
    background: rgb(var(--color-surface-primary)) !important

  .toggle-sidebar
    display: block

  .actions-with-selected-desktop
    display: none

  .actions-with-selected-mobile
    display: block

  .desktop-actions-slot
    display: none

  .mobile-actions-slot
    display: block

  ::v-deep .search-input input
    background-color: rgb(var(--color-surface-secondary))
    border: rgb(var(--color-surface-secondary))

  .page-content
    padding: 15px 0
    padding-top: calc(50px + 15px)
</style>
