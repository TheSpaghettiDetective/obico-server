<template>
  <div class="printshots-container row justify-content-center">
    <div class="col-sm-12 col-lg-6">
      <div class="card">
        <div class="current-shot-container">
          <img class="card-img-top" :src=data.poster_url>
          <button class="prev-btn btn btn-primary"><i class="fas fa-lg fa-angle-left"></i></button>
          <button class="next-btn btn btn-primary"><i class="fas fa-lg fa-angle-right"></i></button>
        </div>
        <div class="card-body">
          <div class="text-center">
            <div class="form-group">
              <button type="button" class="btn btn-primary">
                <i class="fas fa-check"></i>
                It contains spaghetti
              </button>
            </div>
            <div class="form-group">
              <button type="button" class="btn btn-primary">It does NOT contain spaghetti</button>
            </div>
            <div class="form-group">
              <button type="button" class="btn btn-primary">I'll decide later</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      default: function() {return {}},
      type: Object
    },
  },
}
</script>

<style>
.printshots-container {
  margin-top: 1.5em;
}

.current-shot-container {
  position: relative;
}

.prev-btn {
  display: inline;
  position: absolute;
  left: 3%;
  top: 50%;
}

.next-btn {
  display: inline;
  position: absolute;
  right: 3%;
  top: 50%;
}
</style>
