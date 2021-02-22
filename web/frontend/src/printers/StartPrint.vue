<template>
  <div>
    <input
      class="form-control"
      id="myInput"
      type="text"
      placeholder="Search file name ..."
      v-model="searchText"
    >
    <br>
    <div>
      <div
        v-for="gcf in visibleGcodeFiles"
        :key="gcf.id"
        class="card"
      >
        <div class="card-body" style="display: flex; justify-content: space-between;">
          <div style="width: 100%;">
            <strong class="gcode-filename">
            {{ gcf.filename }}
            </strong>
            <small class="gcode-info mt-1" style="display: flex; flex-wrap: wrap;">
              <div class="pr-3"><span class="text-muted">Size: </span> {{ gcf.num_bytes }}</div>
              <div><span class="text-muted">Uploaded: </span> {{ gcf.created_at }}</div>
            </small>
          </div>
          <button
            type="button" class="send-print btn btn-primary"
            @click="onSendPrintClicked(gcf.id)"
            :disabled="isSending"
          ><b-spinner small v-if="isSending" label="Loading..."></b-spinner>Print
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-body" style="display: flex; justify-content: space-between;">
          <a type="button" href="/gcodes/" class="btn btn-primary btn-block">
            <i class="fas fa-upload"></i>
            &nbsp;Upload more G-Code
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'StartPrint',
  props: {
    gcodeFiles: {
      type: Array,
      required: true
    },
    onGcodeFileSelected: {
      type: Function,
      required: true
    },
  },
  data() {
    return {
      searchText: '',
      isSending: false
    }
  },
  computed: {
    visibleGcodeFiles() {
      let q = this.searchText.toLowerCase()
      return this.gcodeFiles.filter(
        (gcf) => gcf.filename.toLowerCase().indexOf(q) > -1)
    },
  },
  methods: {
    onSendPrintClicked(gcodeFileId) {
      this.isSending = true
      this.onGcodeFileSelected(this.gcodeFiles, gcodeFileId)
    }
  }
}
</script>
