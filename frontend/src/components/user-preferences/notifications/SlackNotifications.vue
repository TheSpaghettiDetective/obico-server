<template>
  <section v-if="notificationChannel.channelInfo">
    <h2 class="section-title">Slack</h2>

    <div v-if="slackEnabled">
      <div v-if="notificationChannel.channelInfo.config && notificationChannel.channelInfo.config.access_token">
        <p class="lead">
          <i class="far fa-check-circle text-success"></i>&nbsp;&nbsp;The Spaghetti Detective Slack App has been successfully added to your workspace.
        </p>
        <br />
        <h2>What's Next?</h2>
        <br />
        <p>1. Make sure The Spaghetti Detective Slack App to the channels you want the notifications to be sent to.</p>
        <img class="mw-100" :src="require('@static/img/slack_setup1.png')" />
        <br /><br />
        <p>2. There is no 2. You are all set. It's this simple. :)</p>

        <div class="mt-4">
          <div class="row">
            <div class="col">
              <h5 class="font-weight-bold">Alerts settings</h5>
            </div>
          </div>

          <notification-setting-switch
            settingId="enabled"
            settingTitle="Enable"
            :errorMessages="errorMessages"
            :saving="saving"
            :notificationChannel="notificationChannel"
            @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
          />

          <div :class="{'inactive': !notificationsEnabled}">
            <hr class="my-1">
            <div
              v-for="setting in notificationSettings"
              :key="setting.id"
            >
              <template v-if="setting.id === 'printer_status_change'">
                <div class="row">
                  <div class="col col-form-label">
                    <saving-animation :errors="[]" :saving="false">
                      <div class="custom-control custom-checkbox form-check-inline">
                        <input
                          type="checkbox"
                          class="custom-control-input"
                          :id="`id_${notificationChannel.channelName}_printer_status_change`"
                          :disabled="!notificationsEnabled"
                          v-model="printerStatusChangeNotifications"
                        >
                        <label class="custom-control-label" :for="`id_${notificationChannel.channelName}_printer_status_change`">
                          {{ setting.title }}
                          <span v-if="setting.description" class="text-muted setting-description"><br>{{ setting.description }}</span>
                        </label>
                      </div>
                    </saving-animation>
                  </div>
                </div>
              </template>
              <template v-else>
                <notification-setting-switch
                  :settingId="setting.id"
                  :settingTitle="setting.title"
                  :settingDescription="setting.description"
                  :disabled="!notificationsEnabled"
                  :errorMessages="errorMessages"
                  :saving="saving"
                  :notificationChannel="notificationChannel"
                  @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
                />
              </template>
              <div v-if="setting.subcategories">
                <notification-setting-switch
                  v-for="subcategory in setting.subcategories"
                  :key="subcategory.id"
                  :settingId="subcategory.id"
                  :settingTitle="subcategory.title"
                  :settingDescription="subcategory.description"
                  :isSubcategory="true"
                  :disabled="!notificationsEnabled"
                  :errorMessages="errorMessages"
                  :saving="saving"
                  :notificationChannel="notificationChannel"
                  @updateNotificationChannel="(notificationChannel, settingIds) => $emit('updateNotificationChannel', notificationChannel, settingIds)"
                />
              </div>
            </div>
          </div>
        </div>

        <br /><br />
         <h2>Test Notifications</h2>
        <br />
        <div class="btn btn-sm btn-primary float-left" @click="onSlackTest($event)">Test Slack Notification</div>
        <br />
        <br />
        <br />
        <br />
        <h2>Questions?</h2>
        <br />
        <p>Q: How do I remove The Spaghetti Detective Slack App from a slack channel so that it won't send notifications to that channel?</p>
        <p>A: </p>
        <img class="mw-100 mb-2" :src="require('@static/img/slack_setup2.png')" />
        <img class="mw-100 mb-2" :src="require('@static/img/slack_setup3.png')" />
        <img class="mw-100 mb-2" :src="require('@static/img/slack_setup4.png')" />
        <br /><br />
        <p>Q: How do I remove The Spaghetti Detective Slack App from the entire workspace?</p>
        <p>A: Please follow the instructions in <a href="https://slack.com/help/articles/360003125231-Remove-apps-and-custom-integrations-from-your-workspace">this Slack help doc</a>.</p>
      </div>
      <div v-else>
        <p class="lead">Click the button below to add The Spaghetti Detective Slack App into your workspace:</p>
        <a :href="`https://slack.com/oauth/v2/authorize?client_id=${slackClientId}&scope=channels:read,chat:write,groups:read&redirect_uri=${redirectUri}`">
          <img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" />
        </a>
      </div>
    </div>
    <div v-else>
      <p class="text-warning">Please configure the following variables in the "docker-compose.override.yml" file to enable Slack:</p>
      <ul class="text-warning">
        <li>SLACK_CLIENT_ID</li>
        <li>SLACK_CLIENT_SECRET</li>
      </ul>
    </div>
  </section>
</template>

<script>
import NotificationSettingSwitch from '@src/components/user-preferences/notifications/NotificationSettingSwitch.vue'
import axios from 'axios'
import urls from '@config/server-urls'
import SavingAnimation from '@src/components/SavingAnimation.vue'

export default {
  name: 'SlackNotifications',

  components: {
    NotificationSettingSwitch,
    SavingAnimation,
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

  data() {
    return {
      notificationSettings: [
        {
          id: 'notify_on_failure_alert',
          title: 'Failure alerts',
          description: 'When possible failures are detected',
        },
        {
          id: 'printer_status_change',
          title: 'Printer status change',
          subcategories: [
            {
              id: 'notify_on_print_done',
              title: 'When print is done',
              enabledByDefault: true,
            },
            {
              id: 'notify_on_print_cancelled',
              title: 'When print is cancelled',
              enabledByDefault: false,
            },
            {
              id: 'notify_on_filament_change',
              title: 'When filament runs out or needs a change',
              enabledByDefault: true,
            },
            {
              id: 'notify_on_other_print_events',
              title: 'When other event happens',
              description: 'Print start, pause, resume, etc. (TBD. Help wanted!)',
              enabledByDefault: false,
            },
          ]
        },
        {
          id: 'notify_on_heater_status',
          title: 'Heater status change',
          description: 'Reached target or cooled down (TBD. Help wanted!)',
        },
      ],
    }
  },

  computed: {
    slackEnabled() {
      const envVars = this.notificationChannel.pluginInfo ? (this.notificationChannel.pluginInfo.env_vars || {}) : {}
      for (const variable of Object.values(envVars)) {
        if (variable.is_required && !variable.is_set) {
          return false
        }
      }
      return true
    },
    slackClientId() {
      return this.notificationChannel.pluginInfo.env_vars.SLACK_CLIENT_ID.value
    },
    notificationsEnabled() {
      return this.notificationChannel.channelInfo ? this.notificationChannel.channelInfo.enabled : false
    },
    printerStatusChangeNotifications: {
      get: function() {
        if (!this.notificationChannel.channelInfo) {
          return null
        }
        const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
        for (const subcategory of subcategories) {
          if (this.notificationChannel.channelInfo[subcategory.id]) {
            return true
          }
        }
        return false
      },
      set: function(newValue) {
        if (newValue) {
          const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
          let changedProps = []
          for (const subcategory of subcategories) {
            if (subcategory.enabledByDefault) {
              this.notificationChannel.channelInfo[subcategory.id] = true
              changedProps.push(subcategory.id)
            }
          }
          if (changedProps.length) {
            this.$emit('updateNotificationChannel', this.notificationChannel, changedProps)
          }
        } else {
          const subcategories = this.notificationSettings.filter(setting => setting.id === 'printer_status_change')[0].subcategories
          let changedProps = []
          for (const subcategory of subcategories) {
            if (this.notificationChannel.channelInfo[subcategory.id]) {
              this.notificationChannel.channelInfo[subcategory.id] = false
              changedProps.push(subcategory.id)
            }
          }
          if (changedProps.length) {
            this.$emit('updateNotificationChannel', this.notificationChannel, changedProps)
          }
        }
      }
    },
    redirectUri() {
      return `${window.location.origin}/slack_oauth_callback`
    },
  },

  created() {
    if (!this.notificationChannel.channelInfo) {
      this.$emit('createNotificationChannel', this.notificationChannel.channelName)
    }
  },

  methods: {
    onSlackTest(event) {
      event.target.classList.add('disabled')

      return axios
        .post(urls.testNotificationChannel(this.notificationChannel.channelInfo.id))
        .then(() => {
          event.target.classList.add('btn-success')
        })
        .catch(err => {
          event.target.classList.remove('disabled')
          this.$emit('errorAlert', 'Slack test failed.')
          console.log(err)
        })
    }
  },
}
</script>
