<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <div class="my-3">
        <b-alert v-if="!supported" variant="warning">
          Push notifications are unfortunately not supported in your browser.
        </b-alert>
        <b-alert v-else-if="denied" variant="warning">
          Please click the small icon next to app.obico.io in the navigation bar and allow notifications, then add this device.
        </b-alert>
        <small v-else class="form-text text-muted">
          You need to allow notifications on every device you want notifications to.
        </small>
      </div>
    </template>
    
    <template #configuration>
      <b-container fluid class="p-0">
        <b-row v-if="supported && !subscribed" class="my-3">
          <b-col md="6">
            <b-form-input id="name" v-model="name" class="my-2" trim></b-form-input>
          </b-col>
          <b-col md="6">
            <b-button :disabled="!validName" variant="primary" class="my-2" @click="subscribe">Add this device</b-button>
          </b-col>
        </b-row>

        <b-row v-if="configSubscriptions.length > 0" class="my-3">
          <b-col>
            <h3 class="lg">Devices</h3>
            <hr class="my-3">
            <div v-for="device in configSubscriptions" :key="device.endpoint" class="device-card my-2">
              <div class="device-text">
                <div class="title my-2">
                  {{ device.name }}
                </div>
              </div>
              <b-button class="mr-1" variant="warning" size="sm" @click="removeDevice(device)">
                <i class="fas fa-trash-alt"></i>
              </b-button>
            </div>

            <b-button variant="primary" class="my-3" @click="onBrowserTest($event)">
              Test Browser Notification
            </b-button>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'
import axios from 'axios'
import urls from '@config/server-urls'

export default {
  name: 'BrowserPlugin',

  components: {
    NotificationChannelTemplate,
  },

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
      required: true,
    },
    notificationChannel: {
      type: Object,
      required: true,
    },
  },

  data: () => ({
    denied: false,
    subscription: null,
    name: '',
    configSubscriptions: []
  }),

  computed: {
    vapidPublicKey() {
      return this.notificationChannel.pluginInfo?.env_vars.VAPID_PUBLIC_KEY.value
    },

    validName() {
      return this.name.trim().length > 0
    },

    subscribed() {
      return this.configSubscriptions.some(s => s.endpoint === this.subscription?.endpoint)
    },

    supported() {
      return !!window && "Notification" in window
    }
  },

  mounted() {
    if (Notification?.permission === "denied") {
      this.denied = true;
    }
    this.configSubscriptions = this.notificationChannel.channelInfo?.config.subscriptions ?? []
    navigator.serviceWorker.getRegistration().then(registration => {
      registration.pushManager.getSubscription().then(subscription => this.subscription = subscription);
    });
  },

  methods: {
    async subscribe() {
      if (Notification?.permission === "denied") {
        this.denied = true;
        return;
      }
      const result = await Notification?.requestPermission();
      if (result === "granted") {
        const registration = await navigator.serviceWorker.getRegistration();
        this.subscription = await registration.pushManager.getSubscription();
        if (!this.subscription) {
          this.subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: this.vapidPublicKey,
          });
        }
        this.configSubscriptions.push({ ...this.subscription.toJSON(), name: this.name })
        this.updateConfig()
      }
      else {
        this.denied = true
      }
    },
    
    removeDevice(device) {
      this.$bvModal
        .msgBoxConfirm(`Remove the device ${device.name}?`, {
          id: 'b-modal-confirm-delete',
          centered: true,
          okTitle: 'Remove',
          okVariant: 'warning',
          autoFocusButton: 'ok',
        })
        .then(async (confirmed) => {
          if (confirmed) {
            this.configSubscriptions = this.configSubscriptions.filter(subscription => subscription.endpoint !== device.endpoint)
            this.updateConfig()
          }
        })
    },

    updateConfig() {
      if (!this.notificationChannel.channelInfo) {
        this.$emit('createNotificationChannel', { 
          section: this.notificationChannel, 
          config: {
            subscriptions: this.configSubscriptions
          }
        })
      }
      else if (this.configSubscriptions.length === 0) {
        this.$emit('deleteNotificationChannel', this.notificationChannel)
      }
      else {
        this.$emit('updateNotificationChannel', {
          section: this.notificationChannel,
          propNames: ['config'],
          propValues: [{ subscriptions: this.configSubscriptions }],
        })
      }
    },

    onBrowserTest(event) {
      return axios
        .post(urls.testNotificationChannel(this.notificationChannel.channelInfo.id))
        .catch((err) => {
          this.$swal.Reject.fire({
            title: 'Error',
            html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
              Browser notification test failed
            </p>`,
            showConfirmButton: false,
            showCancelButton: true,
            cancelButtonText: 'Close',
          })
        })
    },
  },
}
</script>

<style lang="sass" scoped>
.device-card
  display: flex
  justify-content: space-between
  align-items: center
  border-radius: var(--border-radius-sm)
  background-color: var(--color-surface-primary)
  border-left: solid thick

.device-text
  flex: 1
  padding: 0px 14px
  overflow: hidden

  .title
    display: flex
    justify-content: space-between

h3.lg
  font-size: 1.25em
  font-weight: bolder

#b-modal-confirm-delete
  .modal-body
    font-size: 1.125rem
    text-align: center
  .modal-footer
    justify-content: center
</style>
