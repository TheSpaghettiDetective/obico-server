<template>
  <div class="page-wrapper" :class="{'collapsed': collapsed}">

    <!-- Sidebar -->
    <nav class="side-nav">
      <div class="sidebar-header">
        <svg class="logo" viewBox="0 0 1965 240">
          <use href="#svg-navbar-brand" />
        </svg>
        <dark-light-image path="logo-square" ext="png" alt="TSD" class="logo-small"></dark-light-image>
      </div>

      <ul class="list-unstyled m-0">
        <li class="active">
          <a href="#">
            <i class="fas fa-print"></i>
            Printers
          </a>
        </li>
        <li>
          <a href="#">
            <i class="fas fa-video"></i>
            Timelapse
          </a>
        </li>
        <li>
          <a href="#">
            <i class="fas fa-code"></i>
            G-Code
          </a>
        </li>
        <li>
          <a href="#">
            <i class="fas fa-dollar-sign"></i>
            Pricing
          </a>
        </li>
        <li>
          <a href="#">
            <i class="fas fa-question"></i>
            Help
          </a>
        </li>
        <li>
          <a href="#">
            <i class="fas fa-comments"></i>
            Forum
          </a>
        </li>
      </ul>

      <div class="side-nav-footer">
        <ul class="list-unstyled m-0">
          <li>
            <a href="#">
              <svg viewBox="0 0 384 550" width="14.66" height="21">
                <use href="#svg-detective-hours" />
              </svg>
              <br />
              <span id="user-credits" class="badge badge-light">20</span>
              <span class="sr-only">Detective Hours</span>
            </a>
          </li>
          <li>
            <a href="#pageSubmenu" data-toggle="collapse" aria-expanded="false" class="dropdown-toggle">
              <i class="fas fa-user"></i>
              Dmitry
            </a>
            <ul class="collapse list-unstyled" id="pageSubmenu">
              <li>
                <a href="#">Settings</a>
              </li>
              <li>
                <a href="#">Account</a>
              </li>
              <li>
                <a href="#">Logout</a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>

    <div class="content-wrapper">
      <!-- <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">

          <button @click="collapsed = !collapsed" type="button">
            <i class="fas fa-align-left"></i>
          </button>

        </div>
      </nav> -->

      <b-navbar class="top-nav">
        <b-button @click="collapsed = !collapsed" variant="_" class="shadow-none p-0">
          <i class="fas fa-align-left"></i>
        </b-button>
      </b-navbar>

      <div class="page-content">
        <slot name="content"></slot>
      </div>
    </div>
  </div>
</template>

<script>
import DarkLightImage from '@common/DarkLightImage.vue'
// import { Themes, theme } from '../main/themes.js'

export default {
  name: 'Layout',

  components: {
    DarkLightImage,
  },

  data() {
    return {
      collapsed: true,
    }
  },
}
</script>

<style lang="sass" scoped>
.page-wrapper
  display: flex
  align-items: stretch
  padding-left: 250px

  .side-nav
    min-width: 250px
    max-width: 250px
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
      padding: 0 1rem
      flex: 0 0 50px
      display: flex
      align-items: center
      justify-content: center

      .logo
        width: 100%
        height: auto
      
      .logo-small
          display: none

    .side-nav-footer
      margin-top: auto

    ul
      li
        a
          text-align: left
          padding: 10px
          font-size: 1.1em
          display: block
          color: rgb(var(--color-text-primary))
          &:hover, &[aria-expanded="true"]
            color: rgb(var(--color-on-primary))
            background: rgb(var(--color-hover) / .075)

          i
            margin-right: 10px
          
        &.active > a
          color: rgb(var(--color-on-primary))
          background: rgb(var(--color-primary))


      ul a
        font-size: 0.9em !important
        padding-left: 40px !important
    
    ul.components
      padding: 20px 0

    ::v-deep .logo-small img
      width: 1.875rem
      height: 1.875rem

    .dropdown-toggle
      position: relative
      &::after
        display: block
        position: absolute
        top: 50%
        right: 20px
        transform: translateY(-50%)

  .top-nav
    height: 50px
    background: rgb(var(--color-surface-secondary)) !important
    position: fixed
    top: 0
    left: 0
    width: 100%
    margin-left: 250px
    z-index: 1000

  .content-wrapper
    width: 100%
    min-height: 100vh

    .page-content
      padding: 2rem
      padding-top: calc(50px + 2rem)

  &.collapsed
    padding-left: 80px

    .side-nav
      min-width: 80px
      max-width: 80px
      text-align: center
      
      .sidebar-header .logo
        display: none

      .sidebar-header .logo-small
        display: block

      ul
        li a
          padding: 10px 5px
          text-align: center
          font-size: 0.85em

          &.dropdown-toggle
            padding-bottom: 20px

          i
            margin-right: 0
            display: block
            font-size: 1.4em
            margin-bottom: 5px

        ul a
          padding: 10px !important

        .dropdown-toggle::after
          top: auto
          bottom: 10px
          right: 50%
          -webkit-transform: translateX(50%)
          -ms-transform: translateX(50%)
          transform: translateX(50%)

    .top-nav
      margin-left: 80px

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



// @media (max-width: 768px)
//   .side-nav
//     min-width: 80px
//     max-width: 80px
//     text-align: center
//     margin-left: -80px !important

//   .dropdown-toggle::after
//     top: auto
//     bottom: 10px
//     right: 50%
//     -webkit-transform: translateX(50%)
//     -ms-transform: translateX(50%)
//     transform: translateX(50%)

//   .side-nav.collapsed
//     margin-left: 0 !important

//   .side-nav .sidebar-header .logo
//     display: none

//   .side-nav .sidebar-header .logo-small
//     display: block

//   .side-nav ul li a
//     padding: 20px 10px

//   .side-nav ul li a span
//     font-size: 0.85em

//   .side-nav ul li a i
//     margin-right: 0
//     display: block

//   .side-nav ul ul a
//     padding: 10px !important

//   .side-nav ul li a i
//     font-size: 1.3em

//   .side-nav
//     margin-left: 0

//   .side-navCollapse span
//     display: none
</style>