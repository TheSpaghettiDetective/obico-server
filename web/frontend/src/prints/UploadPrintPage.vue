<template>
  <div>
    <pull-to-reveal>
      <navbar view-name="app.views.web_views.upload_print"></navbar>
    </pull-to-reveal>

    <div class="row justify-content-center pt-5 pb-2">
      <div class="col-sm-12 col-lg-8 text-center">
        <h1>Upload Time-lapse</h1>
      </div>
    </div>
    <div class="row justify-content-center pb-2">
      <div class="col-sm-12 col-lg-8  text-center">
        <p>Upload time-lapse videos to see if The Detective can correctly tell the bad prints from the good ones.</p>
      </div>
    </div>
    <div class="row justify-content-center">
      <div class="col-sm-12 col-lg-8">
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
            *.mp4 or *.mpg files only. Up to 200MB each.
          </div>
        </vue-dropzone>
      </div>
    </div>
    <div class="row justify-content-center py-5">
      <div id="tl-uploaded" class="col-sm-12 col-lg-8 text-center" v-show="uploaded">
        <img style="height: auto; width: 12rem;" :src="require('@static/img/detective-working.gif')" />
        <div class="py-2 text-center">
          <div class="py-2">The Detective is busy looking at the time-lapse video(s) you
            uploaded.</div>
          <div>We will send you email when she is done.</div><a href="/prints/">Check status now >>></a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import PullToReveal from '@common/PullToReveal.vue'
import Navbar from '@common/Navbar.vue'

  export default {
    name: 'UploadPrintPage',

    components: {
      vueDropzone: vue2Dropzone,
      PullToReveal,
      Navbar,
    },

    props: {
      csrf: {
        type: String,
        requeired: true,
      },
      appPlatform: {
        type: String,
        requeired: true,
      },
    },

    data() {
      return {
        dropzoneOptions: {
          withCredentials: true,
          maxFilesize: 200, // MB
          timeout: 60 * 60 * 1000, // For large files
          acceptedFiles: this.appPlatform === '' ? 'video/mp4, video/mpeg' : 'file/*', // use file/* to so that stupid ios want show camera and stupid apple reviewer won't freak out.
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
