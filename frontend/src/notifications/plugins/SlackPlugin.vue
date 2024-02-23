<template>
  <notification-channel-template
    :error-messages="errorMessages"
    :saving="saving"
    :notification-channel="notificationChannel"
    :show-settings="setupCompleted"
    @createNotificationChannel="$emit('createNotificationChannel', $event)"
    @updateNotificationChannel="$emit('updateNotificationChannel', $event)"
    @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
    @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
  >
    <template #header>
      <div v-if="setupCompleted" class="mb-4">
        <p class="lead">
          <i class="far fa-check-circle text-success"></i>&nbsp;&nbsp;{{$t('brand_name')}} Messenger has been
          successfully added to your workspace.
        </p>
        <br />
        <h2>What's Next?</h2>
        <br />
        <p>
          1. Make sure {{$t('brand_name')}} Messenger is added to the channels you want the notifications to be
          sent to.
        </p>
        <img
          class="mw-100"
          :src="require('@static/img/notification-guides/slack/slack_setup1.png')"
        />
        <br /><br />
        <p>2. There is no 2. You are all set. It's this simple. :)</p>
      </div>
      <div v-else>
        <p class="lead">Click the button below to add the {{$t('brand_name')}} Slack App into your workspace:</p>
        <a
          :href="`https://slack.com/oauth/v2/authorize?client_id=${slackClientId}&scope=channels:read,chat:write,groups:read&redirect_uri=${redirectUri}`"
        >
          <img
            alt="Add to Slack"
            height="40"
            width="139"
            src="https://platform.slack-edge.com/img/add_to_slack.png"
            srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"
          />
        </a>
      </div>
    </template>

    <template #footer>
      <div v-if="setupCompleted">
        <br /><br />
        <h2>Test Notifications</h2>
        <br />
        <div class="btn btn-sm btn-primary float-left" @click="onSlackTest($event)">
          Test Slack Notification
        </div>
        <br />
        <br />
        <br />
        <br />
        <h2>Questions?</h2>
        <br />
        <p>
          Q: How do I remove the {{$t('brand_name')}} Slack App from a slack channel so that it won't send
          notifications to that channel?
        </p>
        <p>A:</p>
        <img
          class="mw-100 mb-2"
          :src="require('@static/img/notification-guides/slack/slack_setup2.png')"
        />
        <img
          class="mw-100 mb-2"
          :src="require('@static/img/notification-guides/slack/slack_setup3.png')"
        />
        <img
          class="mw-100 mb-2"
          :src="require('@static/img/notification-guides/slack/slack_setup4.png')"
        />
        <br /><br />
        <p>Q: How do I remove the {{$t('brand_name')}} Slack App from the entire workspace?</p>
        <p>
          A: Please follow the instructions in
          <a
            href="https://slack.com/help/articles/360003125231-Remove-apps-and-custom-integrations-from-your-workspace"
            >this Slack help doc</a
          >.
        </p>
      </div>
    </template>
  </notification-channel-template>
</template>

<script>
import NotificationChannelTemplate from '@src/components/user-preferences/notifications/NotificationChannelTemplate.vue'
import axios from 'axios'
import urls from '@config/server-urls'

export default {
  name: 'SlackPlugin',

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

  computed: {
    setupCompleted() {
      return !!this.notificationChannel.channelInfo?.config?.access_token
    },
    slackClientId() {
      return this.notificationChannel.pluginInfo?.env_vars.SLACK_CLIENT_ID.value
    },
    redirectUri() {
      return `${window.location.origin}/slack_oauth_callback/`
    },
  },

  methods: {
    onSlackTest(event) {
      event.target.classList.add('disabled')

      return axios
        .post(urls.testNotificationChannel(this.notificationChannel.channelInfo.id))
        .then(() => {
          event.target.classList.add('btn-success')
        })
        .catch((err) => {
          event.target.classList.remove('disabled')
          this.$swal.Reject.fire({
            title: 'Error',
            html: `<p style="line-height: 1.5; max-width: 400px; margin: 0 auto;">
              Slack test failed
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
