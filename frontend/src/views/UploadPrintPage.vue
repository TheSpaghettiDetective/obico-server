<template>
  <layout>
    <template v-slot:content>
      <b-container>
        <b-row class="justify-content-center">
          <b-col lg="8" class="text-center">
            <h1 class="pb-2">Upload Time-lapse</h1>
            <p class="pb-2">Upload time-lapse videos to test Obico's AI failure detection.</p>
            <vue-dropzone
              class="upload-box"
              id="dropzone"
              :options="dropzoneOptions"
              :useCustomSlot="true"
              @vdropzone-success="printUploadSuccess"
            >
              <div class="dz-message needsclick">
                <i class="fas fa-upload fa-2x"></i> <br>
                Drop files here or click to upload.<br>
                *.mp4 or *.mpg files only. Up to 100MB each.
              </div>
            </vue-dropzone>
            <div v-show="uploaded" class="pt-5">
              <div id="tl-uploaded">
                <img style="height: auto; width: 12rem;" :src="require('@static/img/detective-working.gif')" />
                <div class="py-2 text-center">
                  <div class="py-2">The Obico Server is running failure detection on the time-lapse video(s) you
                    uploaded.</div>
                  <div>We will send you email when it is done.</div><a href="/prints/">Check status now >>></a>
                </div>
              </div>
            </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import Layout from '@src/components/Layout.vue'

export default {
  name: 'UploadPrintPage',

  components: {
    vueDropzone: vue2Dropzone,
    Layout,
  },

  props: {
    csrf: {
      type: String,
      requeired: true,
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
        headers: {'X-CSRFToken': this.csrf},
      },
      uploaded: false,
    }
  },

  methods: {
    printUploadSuccess(file) {
      console.log(file)
      this.uploaded = true
    },
  }
}
</script>
