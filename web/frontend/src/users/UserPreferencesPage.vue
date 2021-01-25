<template>
  <div>
  </div>
</template>

<script>

export default {
  name: 'UserPreferencesPage',
  components: {
  },

  props: {
    twilioEnabled: {
      default() {return true},
      type: Boolean
    },
    slackEnabled: {
      default() {return true},
      type: Boolean
    },
  },
}
</script>

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass" scoped>
@use "~main/theme"

</style>
