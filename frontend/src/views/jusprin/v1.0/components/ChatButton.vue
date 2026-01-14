<template>
  <div class="bottomsheet-buttons">
    <button class="btn btn-primary slice-button" @click="$emit('click')">
      <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
    </button>
  </div>
</template>

<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faWandMagicSparkles } from '@fortawesome/free-solid-svg-icons'

library.add(faWandMagicSparkles)

export default {
  components: {
    FontAwesomeIcon,
  },
}
</script>

<style lang="sass" scoped>
.bottomsheet-buttons
  display: flex
  justify-content: space-between
  width: 100%

.slice-button
  padding: 0.5em
  width: 3.5em
  height: 3.5em
  border-radius: 50%
  display: flex
  justify-content: center
  align-items: center
  background-color: var(--color-primary)
  border: none
  cursor: pointer
  transition: background-color 0.3s ease

  &:hover
    background-color: var(--color-primary-hover)

  svg
    width: 1.5em
    height: 1.5em
    color: gold
</style>
