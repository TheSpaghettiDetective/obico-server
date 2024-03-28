<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row class="justify-content-center">
          <b-col lg="8" class="text-center">
            <h1 class="pb-2">{{ $t("Upload Time-lapse") }}</h1>
            <p class="pb-2">{{ $t("Upload time-lapse videos to test {brandName}'s AI failure detection.",{brandName:$syndicateText.brandName}) }}</p>
            <vue-dropzone
              id="dropzone"
              class="upload-box"
              :options="dropzoneOptions"
              :use-custom-slot="true"
              @vdropzone-success="printUploadSuccess"
            >
              <div class="dz-message needsclick">
                <i class="fas fa-upload fa-2x"></i> <br />
                {{$t("Drop files here or click to upload.")}}<br />
                {{$t("*.mp4 or *.mpg files only. Up to 100MB each.")}}
              </div>
            </vue-dropzone>
            <div v-show="uploaded" class="pt-5">
              <div id="tl-uploaded">
                <img
                  class="detective-working"
                  :src="require('@static/img/detective-working.gif')"
                />
                <div class="py-2 text-center">
                  <div class="py-2">
                    {{ $t("The {brandName} Server is running failure detection on the time-lapse video(s) you uploaded.",{brandName:$syndicateText.brandName}) }}
                  </div>
                  <div>{{ $t("We will send you email when it is done.") }}</div>
                  <a href="/prints/">{{ $t("Check status now >>>") }}</a>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import PageLayout from '@src/components/PageLayout.vue'

export default {
  name: 'UploadPrintPage',

  components: {
    vueDropzone: vue2Dropzone,
    PageLayout,
  },

  props: {
    csrf: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      dropzoneOptions: {
        withCredentials: true,
        maxFilesize: 100, // MB
        timeout: 60 * 60 * 1000, // For large files
        acceptedFiles: 'video/mp4, video/mpeg',
        url: '?',
        headers: { 'X-CSRFToken': this.csrf },
      },
      uploaded: false,
    }
  },

  methods: {
    printUploadSuccess(file) {
      console.log(file)
      this.uploaded = true
    },
  },
}
</script>

<style lang="sass" scoped>
img.detective-working
  height: auto
  width: 12rem
  border-radius: var(--border-radius-sm)
</style>
