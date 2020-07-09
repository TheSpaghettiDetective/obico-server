<template>
  <div :id="printer.id"
    class="col-sm-12 col-lg-6 printer-card"
  >
    <div class="card">
      <div class="card-header">
        <div class="title-box">
          <div class="primary-title print-filename"></div>
          <div class="printer-name">{{ printer.name || 'Printer #' + printer.id }}</div>
        </div>
        <div class="dropdown">
          <button
            class="btn icon-btn"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            :aria-label="printer.name + ' Controls'"
          ><i class="fas fa-ellipsis-v"></i>
          </button>

          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">

            <a class="dropdown-item" :href="shareUrl()">
              <i class="fas fa-share-alt fa-lg"></i>Share
            </a>

            <div class="dropdown-divider"></div>

            <a
              class="dropdown-item"
              :href="settingsUrl()"
            ><i class="fas fa-cog fa-lg"></i>Settings
            </a>

            <a
              id="delete-print"
              class="dropdown-item text-danger"
              href="#"
              @click="$emit('DeleteClicked', printer.id)"
            ><i class="fas fa-trash-alt fa-lg"></i>Delete
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- webcam stream include TODO -->


    <div
      v-if="failureDetected"
      class="failure-alert card-body bg-warning px-2 py-1"
    >
      <i class="fas fa-exclamation-triangle align-middle"></i>
      <span class="align-middle">Failure Detected!</span>
      <button
        type="button"
        id="not-a-failure"
        class="btn btn-outline-primary btn-sm float-right"
        @click="$emit('NotAFailureClicked', printer.id)"
      >Not a failure?</button>
    </div>

  </div>
</template>

<script>
export default {
  name: 'PrinterCard',
  props: {
    printer: {
      type: Object,
      required: true
    }
  },
  computed: {
    failureDetected() {
      return true // TODO
    }
  },
  methods: {
    shareUrl() {
      return `/printers/${this.printer.id}/share/`
    },
    settingsUrl() {
      return `/printers/${this.printer.id}/`
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

</style>
