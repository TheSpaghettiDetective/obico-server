<template>
  <div>
    <pull-to-reveal :enable="false">
      <navbar view-name="share-printer"></navbar>
    </pull-to-reveal>

    <div v-if="user && printer" class="row justify-content-center py-3">
      <div class="col-sm-11 col-md-10 col-lg-8">
        <div class="form-container printer-settings">
          <div v-if="!user.is_pro">
            <h5 class="mb-5">Wait! You need to <a href="/ent/pricing/">upgrade to Pro plan</a> to enable Printer feed. </h5>
            <p>Printer feed sharing is a Pro feature.</p>
            <p><a
                href="https://www.thespaghettidetective.com/docs/upgrade-to-pro/#what-cant-the-detective-just-work-for-free-people-love-free-you-know">Running
                TSD incurs non-trivial amount of costs</a>. With little more than 1 Starbucks per month, you can upgrade to a
              Pro account and help us run TSD smoothly.</p>
            <p><a href="/ent/pricing/">Check out Pro pricing >>></a></p>
          </div>
          <div v-else>
            <h2 class="mb-4">{{ printer.name }} feed sharing</h2>
            <div class="py-3">
              <div class="form-group">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input type="checkbox" name="shared" class="custom-control-input" id="share-checkbox" v-model="share">
                  <label class="custom-control-label" style="font-size: 16px;" for="share-checkbox">Share link</label>
                </div>
                <div v-show="sharedLink">
                  <div class="input-group mt-4 mb-2">
                    <input
                      type="text"
                      id="secret-token-input"
                      class="form-control"
                      aria-label="Secret token"
                      readonly
                      :value="sharedLink"
                      ref="sharedLink"
                    >
                    <div class="input-group-append">
                      <button id="copy-link" class="btn btn-outline-primary no-corner" type="button"
                        data-clipboard-target="#secret-token-input" aria-label="Copy secure link to clipboard"
                        @click="copyToClipboard">
                        <i class="fas fa-clipboard"></i>
                      </button>
                      <b-tooltip :show.sync="copyStatus" target="copy-link" triggers="click" placement="bottom">{{ copyMessage }}</b-tooltip>
                    </div>
                  </div>
                  <div class="my-1">Click the clipboard icon above to copy the secure shareable link to your clipboard.</div>
                  <div class="my-1">You can test the shareable link by right-clicking <a :href="sharedLink">here</a>
                    and select "Open Link in Incognito Window".</div>
                </div>
                <br />
                <em class="text-muted">
                  <small>
                    <div>Notes:</div>
                    <ul>
                      <li>Send the secure link to anyone you want to share your printer feed with. They do NOT need a The
                        Spaghetti Detective account to see your printer feed.</li>
                      <li>Anyone with this shareable link will be able to see your printer feed. <a href="https://www.thespaghettidetective.com/docs/printer-feed-sharing/">Learn more about what
                          they can see.</a></li>
                    </ul>
                  </small>
                </em>
              </div>
              <br />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import split from 'lodash/split'
  import axios from 'axios'
  import { normalizedPrinter } from '@lib/normalizers'
  import urls from '@lib/server_urls'
  import PullToReveal from '@/common/PullToReveal.vue'
  import Navbar from '@/common/Navbar.vue'

  export default {
    components: {
      PullToReveal,
      Navbar,
    },

    data() {
      return {
        user: null,
        printerId: null,
        printer: null,
        share: false,
        token: '',
        copyStatus: false,
        copyMessage: '',
      }
    },

    props: {
      csrf: {
        type: String,
        required: true
      },
    },

    created() {
      this.user = JSON.parse(document.querySelector('#user-json').text)
      this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
      this.fetchPrinter()
    },

    mounted() {
      console.log(this.user)
      console.log(this.printer)
      console.log(window.location)
    },

    computed: {
      sharedLink() {
        if (this.token) {
          const url = window.location
          return `${url.protocol}//${url.host}/printers/share_token/${this.token}/`
        }
        
        return ''
      }
    },

    watch: {
      share(val) {
        if (val) {
          // TODO: rewrite with new API

          let bodyFormData = new FormData()
          bodyFormData.append('shared', 'on')

          axios
            .post('', bodyFormData, {headers: {'X-CSRFToken': this.csrf}})
            .then(response => {
              console.log(response)
            })

          this.token = 'token'
        } else {
          this.token = ''
        }
      }
    },

    methods: {
      // Get printer data
      fetchPrinter() {
        return axios
          .get(urls.printer(this.printerId))
          .then(response => {
            this.printer = normalizedPrinter(response.data)
            console.log(this.printer)
          })
      },

      copyToClipboard() {
        this.copyStatus = true

        this.$refs.sharedLink.focus()
        this.$refs.sharedLink.select()
        try {
          document.execCommand('copy')
          this.copyMessage = 'Copied!'
        } catch (err) {
          console.error('Fallback: Oops, unable to copy', err)
          this.copyMessage = 'Failed!'
        }

        // $('#copy-to-clipboard').tooltip({
        //     trigger: 'click',
        //     placement: 'bottom'
        // });

        // var clipboard = new ClipboardJS('#copy-to-clipboard');
        // clipboard.on('success', function (e) {
        //     setTooltip(e.trigger, 'Copied!');
        //     hideTooltip(e.trigger);
        // });

        // clipboard.on('error', function (e) {
        //     setTooltip(e.trigger, 'Failed!');
        //     hideTooltip(e.trigger);
        // });
      }
    }
  }
</script>

<style lang="sass" scoped>

</style>