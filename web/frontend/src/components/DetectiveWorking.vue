<template>
  <div class="card bg-dark text-white">
    <img
      class="card-img"
      :src="require('@static/img/detective-working.gif')"
      alt="Obi is still working"
    />
    <div class="card-img-overlay" style="background-color: rgba(0,0,0,0.6);">
      <h5
        class="card-title text-center"
        style="padding: 70px 0;"
      >Obi is still busy working on your time-lapse</h5>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DetectiveWorking'
}
</script>

<style></style>
