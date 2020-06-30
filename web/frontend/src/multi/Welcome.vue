<template>
  <div>
    <p>
      Welcome <b>{{ username }}</b>!
      <span v-if="data.id">Your user id is <code>{{ data.id }}</code>!</span>
    </p>
  </div>
</template>

<script>
export default {
  name: 'Welcome',
  props: {
    username: {
      default: 'friend',
      type: String
    },
    data: {
      default: function() {return {}},
      type: Object
    }
  },
}
</script>

<style>
</style>
