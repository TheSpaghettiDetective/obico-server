<template>
  <section>
    <h2 class="section-title">Slack</h2>

    <div v-if="slackClientId">
      <div v-if="user.slack_access_token">
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
        <br /><br />
        <h2>Questions?</h2>
        <br />
        <p>Q: How do I remove The Spaghetti Detective Slack App from a slack channel so that it won't send notifications to that channel?</p>
        <p>A: </p>
        <img class="mw-100" :src="require('@static/img/slack_setup2.png')" />
        <br /><br />
        <p>Q: How do I remove The Spaghetti Detective Slack App from the entire workspace?</p>
        <p>A: Please follow the instructions in <a href="https://slack.com/help/articles/360003125231-Remove-apps-and-custom-integrations-from-your-workspace">this Slack help doc</a>.</p>
      </div>
      <div v-else>
        <p class="lead">Click the button below to add The Spaghetti Detective Slack App into your workspace:</p>
        <a :href="`https://slack.com/oauth/v2/authorize?client_id=${slackClientId}&scope=channels:read,chat:write,groups:read`">
          <img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x">
        </a>
      </div>
    </div>
    <div v-else>
      <p class="text-warning">Please configure the follow variables in the "docker-compose.override.yml" file to enable Slack:</p>
      <ul class="text-warning">
        <li>SLACK_CLIENT_ID</li>
        <li>SLACK_CLIENT_SECRET</li>
      </ul>
    </div>
  </section>
</template>

<script>
import { settings } from '@src/lib/page_context'
const { SLACK_CLIENT_ID } = settings()

export default {
  name: 'SlackNotifications',

  props: {
    user: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      slackClientId: SLACK_CLIENT_ID,
    }
  },
}
</script>
