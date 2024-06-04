<template>
  <div class="card-body consent-section">
    <div>
      {{$t("Number of snapshots")}}:
      <span class="feedback-estimate">{{ print.printshotfeedback_set.length }}</span>
    </div>
    <p>
      {{$t("Estimated time to finish")}}:
      <span class="feedback-estimate">{{ estimatedFeedbackTime }}</span>
    </p>
    <p class="font-weight-light">
      <i18next :translation="$t('Help Obi get better at detecting failures by giving her in-depth feedback on the snapshots of the print. You will earn {localizedDom} after you finish this Focused Feedback. {localizedDom2}')">
        <template #localizedDom>
          <strong class="text-light">{{$t("2 non-expirable AI Detection Hours")}}</strong>
        </template>
        <template #localizedDom2>
          <a target="_blank" :href="getDocUrl('/user-guides/how-does-credits-work/')">{{$t('Learn more')}}. <small><i class="fas fa-external-link-alt"></i></small ></a>
        </template>
      </i18next>
    </p>
    <br />
    <button
      :disabled="!consentChecked"
      class="btn btn-primary btn-block"
      type="button"
      @click="$emit('continue-btn-pressed')"
    >
      {{$t("Start Focused Feedback")}}
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
        {{ $t("I grant the {brandName} app team members the permission to review the time-lapse video of the print shown on this page.", {brandName:$syndicateText.brandName}) }}

        <a
          target="_blank"
          :href="getDocUrl('/user-guides/how-does-credits-work#you-need-to-grant-permission-to-tsd-team-to-review-your-time-lapse')"
          >{{$t("Why is this necessary? ")}}<small><i class="fas fa-external-link-alt"></i></small
        ></a>
      </label>
    </div>
    <br />
    <div>
      <span class="text-muted">{{ $t("File") }}:</span>
      {{ print.filename }}
    </div>
    <div>
      <span class="text-muted">{{ $t("Printed") }}:</span>
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
        return `${seconds} ${this.$i18next.t('seconds')}`
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
