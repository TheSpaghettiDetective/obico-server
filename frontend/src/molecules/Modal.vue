<template>
  <div v-show="isModalOpen" class="content-container">
    <!-- First Layer Overlay -->
    <div @click.self="$emit('close')" class="first-layer-overlay">
      <!-- First Layer modal -->
      <div class="first-layer-modal">
        <b-row>
          <div class="close-button mb-1">
            <button @click="$emit('close')">
              <i class="far fa-window-close"></i>
            </button>
          </div>
        </b-row>

        <!-- Modal Content -->
        <slot></slot>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    isModalOpen: {
      type: Boolean,
      required: false,
    },
  },
  watch: {
    isModalOpen: function(value) {
      if (!!value) {
        document.body.classList.add('tsd-modal-open');
      } else {
        document.body.classList.remove('tsd-modal-open');
      }
    },
  }
}
</script>

<style lang="sass" scoped>
.content-container
  margin: 0 auto
  position: relative
.first-layer-overlay
  position: fixed
  z-index: 1000
  top: 0
  left: 0
  overflow: auto
  height: 100vh
  background-color: rgba(0, 0, 0, 0.5)
  @media (max-width: 768px)
    width: 100%
    padding-left: 15px
    padding-right: 15px
    
.first-layer-modal
  border-radius: var(--border-radius-lg)
  padding: auto 1em !important
  padding: 10px 20px
  background-color: var(--color-surface-secondary)
  margin: 2em 2em 0 8em
  .close-button
    padding-top: 6px
    padding-left: 7px
    button
      color: var(--color-text-primary)
      background: transparent
      border: none
      font-size: 22px
  @media (max-width: 768px)
    margin-top: 3em
    margin-left: 0
    margin-right: 0


</style>
<style>
body.tsd-modal-open {
  overflow: hidden;
}
</style>