<template>
  <div class="card-body consent-section">
    <div>
      Number of snapshots:
      <span class="feedback-estimate">{{ print.printshotfeedback_set.length }}</span>
    </div>
    <p>
      Estimated time to finish:
      <span class="feedback-estimate">{{ estimatedFeedbackTime }}</span>
    </p>
    <p class="font-weight-light">
      Help Obi get better at detecting failures by giving her in-depth feedback on the snapshots of
      the print. You will earn
      <strong class="text-light">2 non-expirable AI Detection Hours</strong> after you finish this
      Focused Feedback.
      <a target="_blank" href="https://www.obico.io/docs/user-guides/how-does-credits-work/"
        >Learn more. <small><i class="fas fa-external-link-alt"></i></small
      ></a>
    </p>
    <br />
    <button
      :disabled="!consentChecked"
      class="btn btn-primary btn-block"
      type="button"
      @click="$emit('continue-btn-pressed')"
    >
      Start Focused Feedback
    </button>
    <br />
    <div class="custom-control custom-checkbox form-check-inline">
      <input
        id="consented-checkbox"
        v-model="consentChecked"
        type="checkbox"
        name="consented"
        class="custom-control-input"
      />
      <label class="custom-control-label" style="font-size: 16px" for="consented-checkbox">
        I grant the {{$t('brand_name')}} app team members the permission to review the time-lapse video of the
        print shown on this page.
        <a
          target="_blank"
          href="https://www.obico.io/docs/user-guides/how-does-credits-work#you-need-to-grant-permission-to-tsd-team-to-review-your-time-lapse"
          >Why is this necessary? <small><i class="fas fa-external-link-alt"></i></small
        ></a>
      </label>
    </div>
    <br />
    <div>
      <span class="text-muted">File:</span>
      {{ print.filename }}
    </div>
    <div>
      <span class="text-muted">Printed:</span>
      {{ print.started_at.fromNow() }}
    </div>
    <br />
    <video-box
      v-if="print.video_url"
      :video-url="print.video_url"
      :poster-url="print.poster_url"
      :full-screen-btn="false"
    />
    <div v-else>
      <detective-working />
    </div>
  </div>
</template>

<script>
import moment from 'moment'

import VideoBox from '@src/components/VideoBox'
import DetectiveWorking from '@src/components/DetectiveWorking'

export default {
  name: 'FocusedFeedbackConsent',

  components: { VideoBox, DetectiveWorking },

  props: {
    print: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      consentChecked: false,
    }
  },

  computed: {
    estimatedFeedbackTime() {
      const seconds = this.print.printshotfeedback_set.length * 12
      if (seconds < 60) {
        return `${seconds} seconds`
      } else {
        return moment.duration(seconds, 'seconds').humanize()
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.consent-section
  background: var(--color-surface-secondary)

.feedback-estimate
  font-size: 1.2em
  font-weight: bolder
  color: var(--color-primary)
</style>
