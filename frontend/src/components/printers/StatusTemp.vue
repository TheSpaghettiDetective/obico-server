<template>
  <div class="wrapper">
    <temperature-item
      v-for="(item, key) in temperatures"
      :key="key"
      :temp-key="key"
      :temp-item="item"
      :is-plugin-version-sufficient="isPluginVersionSufficient"
      @TempEditClicked="onEditClicked(key, item)"
    />
  </div>
</template>

<script>
import TemperatureItem from '@src/components/printers/TemperatureItem.vue'

export default {
  name: 'StatusTemp',
  components: {
    TemperatureItem,
  },

  props: {
    temperatures: {
      type: Object,
      required: true,
    },
    isPluginVersionSufficient: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    onEditClicked(key, item) {
      if (this.isPluginVersionSufficient && item.target !== null) {
        this.$emit('TempEditClicked', key, item)
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding: 1rem 0 1rem
</style>
