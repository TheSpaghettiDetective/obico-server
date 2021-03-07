<template>
  <div>
    <div class="control-panel">
      <search-input v-model="searchText" class="search-input"></search-input>
      <a role="button" class="btn btn-outline-primary" href="/gcodes/" title="Upload more G-Code">
        <i class="fas fa-upload fa-lg mx-2"></i>
      </a>
    </div>
    <br>
    <div v-if="gcodeFiles.length">
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
              <div class="pr-3"><span class="text-muted">Size: </span> {{ gcf.filesize }}</div>
              <div><span class="text-muted">Uploaded: </span> {{ gcf.created_at.fromNow() }}</div>
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
    </div>
    <div v-else>
      <p class="text-center font-weight-bold my-3">No G-Codes yet. You can upload them <a href="/gcodes/">here</a>.</p>
    </div>
  </div>
</template>

<script>
import SearchInput from '@common/SearchInput.vue'

export default {
  name: 'StartPrint',
  components: {
    SearchInput,
  },
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
      isSending: false,
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
    },
  }
}
</script>

<style lang="sass" scoped>
.control-panel
  display: flex

  .search-input
    flex: 1

  .btn
    margin-left: 10px
    flex: 0 0 auto
</style>