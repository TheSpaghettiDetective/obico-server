<template>
  <div>
    <h2 class="text-center">{{ $t("Printer Feed Sharing") }}</h2>
    <hr />
    <div v-if="!isProAccount">
      <h5 class="mb-5">
        <i18next :translation="$t('Wait! You need to {localizedDom} to enable Printer feed.')">
          <template #localizedDom>
            <a href="/ent_pub/pricing/">{{$t("upgrade to the Pro plan")}}</a>
          </template>
        </i18next>

      </h5>
      <p>{{ $t("Printer feed sharing is a Pro feature.") }}</p>
      <p>
        <a  :href="getDocUrl('/user-guides/upgrade-to-pro#why-cant-the-detective-just-work-for-free-people-love-free-you-know')">
          {{ $t('Running the {brandName} app incurs non-trivial amount of costs',{brandName:$syndicateText.brandName}) }}
          </a>.
          {{ $t('With little more than 1 Starbucks per month, you can upgrade to a Pro account and help us run the {brandName} app smoothly.',{brandName:$syndicateText.brandName}) }}

      </p>
      <p><a href="/ent_pub/pricing/">{{ $t("Check out Pro pricing >>>") }}</a></p>
    </div>
    <div v-else>
      <div class="py-3">
        <div class="custom-control custom-switch">
          <input
            :id="'sharing_enabled-toggle-' + printer.id"
            type="checkbox"
            class="custom-control-input update-printer"
            :checked="sharedResource"
            @click="onSharingToggled"
          />
          <label
            class="custom-control-label"
            :for="'sharing_enabled-toggle-' + printer.id"
            style="font-size: 1rem"
            >{{ $t("Share live feed for printer ") }}"<b>{{ printer.name }}</b
            >"</label
          >
        </div>
        <div class="form-group">
          <div v-show="sharedLink">
            <div class="input-group mt-4 mb-2">
              <input
                id="secret-token-input"
                ref="sharedLink"
                type="text"
                class="form-control shared-link-text"
                aria-label="Secret token"
                readonly
                :value="sharedLink"
              />
              <div class="input-group-append">
                <div
                  id="copy-link"
                  class="copy-button"
                  data-clipboard-target="#secret-token-input"
                  aria-label="Copy secure link to clipboard"
                  @click="copyToClipboard"
                >
                  <i class="fas fa-clipboard"></i>
                </div>
                <b-tooltip
                  :show.sync="copyStatus"
                  target="copy-link"
                  triggers="click"
                  placement="bottom"
                  >{{ copyMessage }}</b-tooltip
                >
              </div>
            </div>
            <div class="my-1">
              {{$t("Click the clipboard icon above to copy the secure shareable link to your clipboard.")}}
            </div>
            <div class="my-1">
              <i18next :translation="$t(`You can test the shareable link by right-clicking {localizedDom} and select 'Open Link in Incognito Window'.`)">
                <template #localizedDom>
                  <a :href="sharedLink">{{$t("here")}}</a>
                </template>
              </i18next>

            </div>
            <br />
            <em class="text-muted">
              <small>
                <div>{{ $t("Notes") }}:</div>
                <ul>
                  <li>
                    {{ $t('Send the secure link to anyone you want to share your printer feed with. They do NOT need the {brandName} account to see your printer feed.',{brandName:$syndicateText.brandName}) }}

                  </li>
                  <li>
                    {{$t("Anyone with this shareable link will be able to see your printer feed.")}}
                    <a :href="getDocUrl('/user-guides/printer-feed-sharing/')"
                      >{{ $t("Learn more about what they can see.") }}</a
                    >
                  </li>
                </ul>
              </small>
            </em>
          </div>
        </div>
        <br />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@config/server-urls'

export default {
  props: {
    isProAccount: {
      type: Boolean,
      default: false,
    },
    printer: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      share: false,
      sharedResource: null,
      copyStatus: false,
      copyMessage: '',
    }
  },

  computed: {
    sharedLink() {
      if (this.sharedResource) {
        const url = window.location
        return `${url.protocol}//${url.host}/printers/share_token/${this.sharedResource.share_token}/`
      }

      return ''
    },
  },

  created() {
    this.fetchSharedResources()
  },

  methods: {
    fetchSharedResources() {
      return axios.get(urls.sharedResources({ printer_id: this.printer.id })).then((response) => {
        if (response.data.length > 0) {
          this.sharedResource = response.data[0]
        }
      })
    },
    postSharedResources() {
      return axios.post(urls.sharedResources({ printer_id: this.printer.id })).then((response) => {
        if (response.data.length > 0) {
          this.sharedResource = response.data[0]
        }
      })
    },
    deleteSharedResources() {
      return axios.delete(urls.sharedResource(this.sharedResource.id)).then(() => {
        this.sharedResource = null
      })
    },
    onSharingToggled() {
      if (this.sharedResource) {
        this.deleteSharedResources()
      } else {
        this.postSharedResources()
      }
    },
    // Copy share link to clipboard
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
    },
  },
}
</script>

<style lang="sass" scoped>
hr
  background-color: var(--color-divider)

.shared-link-text
  color: var(--text-primary) !important
  height: 40px
  border-color: var(--color-divider)
  background-color: var(--color-input-background) !important

.copy-button
  color: var(--color-primary)
  border: 2px solid var(--color-primary)
  border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0
  background-color: transparent
  display: inline-flex
  align-items: center
  justify-content: center
  padding: 0 .75rem
  font-size: 1rem
  line-height: 1.5

  &:hover
    background-color: var(--color-primary)
    color: var(--color-on-primary)
    cursor: pointer
</style>
