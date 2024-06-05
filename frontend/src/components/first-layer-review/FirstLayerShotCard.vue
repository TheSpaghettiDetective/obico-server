<template>
  <div>
    <img class="card-img-top" :src="shot.image_url" />
    <div class="px-3 pt-4">
      <p>{{ $t('What issues do you see in this snapshot? Select all that apply.') }}</p>
      <div class="mb-4">
        <b-form>
          <b-form-checkbox v-model="labels.raisedRipples" class="pr-5">
            <i18next :translation="$t(`Raised ripples ({localizedDom})`)">
              <template #localizedDom>
                <a href="#" @click.prevent="() => openExample('raised', 'Raised ripples')">{{
                  $t('examples')
                }}</a>
              </template>
            </i18next>
          </b-form-checkbox>
          <b-form-checkbox v-model="labels.bubbling" class="pr-5">
            <i18next :translation="$t(`Bubbling ({localizedDom})`)">
              <template #localizedDom>
                <a href="#" @click.prevent="() => openExample('bubbling', 'Bubbling')">{{
                  $t('examples')
                }}</a>
              </template>
            </i18next>
          </b-form-checkbox>
          <b-form-checkbox v-model="labels.bumpsAndRoughSurface" class="pr-5">
            <i18next :translation="$t(`Bumps or rough surfaces ({localizedDom})`)">
              <template #localizedDom>
                <a
                  href="#"
                  @click.prevent="() => openExample('bumps', 'Bumps or rough surfaces')"
                  >{{ $t('examples') }}</a
                >
              </template>
            </i18next>
          </b-form-checkbox>
          <b-form-checkbox v-model="labels.detached" class="pr-5">
            <i18next :translation="$t(`Detached or warping ({localizedDom})`)">
              <template #localizedDom>
                <a href="#" @click.prevent="() => openExample('detached', 'Detached or warping')">{{
                  $t('examples')
                }}</a>
              </template>
            </i18next>
          </b-form-checkbox>
          <b-form-checkbox v-model="labels.gaps" class="pr-5">
            <i18next :translation="$t(`Gaps between lines ({localizedDom})`)">
              <template #localizedDom>
                <a href="#" @click.prevent="() => openExample('gaps', 'Gaps between lines')">{{
                  $t('examples')
                }}</a>
              </template>
            </i18next>
          </b-form-checkbox>
          <b-form-checkbox v-model="labels.other" class="pr-5">{{ $t('Other') }}</b-form-checkbox>
          <b-form-checkbox v-model="labels.noIssues" class="pr-5">{{
            $t('No issues')
          }}</b-form-checkbox>
          <b-form-checkbox v-model="labels.notANozzleCam" class="pr-5">
            <i18next :translation="$t(`Oops, this is {localizedDom}`)">
              <template #localizedDom>
                <a :href="getDocUrl('/user-guides/nozzle-camera-configuration')" target="_blank"
                  >&nbsp;{{ $t('not a nozzle camera') }}</a
                >
              </template>
            </i18next>
          </b-form-checkbox>
        </b-form>
      </div>
      <div class="navigation-container my-4">
        <b-button :disabled="isFirst" variant="outline-secondary" @click="$emit('prev')">
          <i class="fas fa-chevron-left"></i>&nbsp;&nbsp;{{ $t('Previous') }}
        </b-button>

        <b-button :disabled="!labelsSelected" variant="outline-secondary" @click="onNext">
          {{ isLast ? $t('Finish') : $t('Next') }}&nbsp;&nbsp;<i class="fas fa-chevron-right"></i>
        </b-button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import raised1 from '@src/components/first-layer-review/example-images/raisedRipples-2.jpg'
import raised2 from '@src/components/first-layer-review/example-images/raisedRipples-3.jpg'
import bubbling1 from '@src/components/first-layer-review/example-images/bubbling-1.jpg'
import bubbling2 from '@src/components/first-layer-review/example-images/bubbling-2.jpg'
import bumps1 from '@src/components/first-layer-review/example-images/bumpsAndRoughSurface-1.jpg'
import bumps2 from '@src/components/first-layer-review/example-images/bumpsAndRoughSurface-2.jpg'
import detached1 from '@src/components/first-layer-review/example-images/detached-1.jpg'
import detached2 from '@src/components/first-layer-review/example-images/detached-2.jpg'
import gaps1 from '@src/components/first-layer-review/example-images/gaps-1.jpg'
import gaps2 from '@src/components/first-layer-review/example-images/gaps-2.jpg'

export default {
  name: 'FirstLayerShotCard',

  props: {
    shot: {
      type: Object,
      required: true,
    },
    totalShots: {
      type: Number,
      required: true,
    },
    shotIndex: {
      type: Number,
      required: true,
    },
  },

  computed: {
    labelsSelected() {
      return this.labelsToString(this.labels) !== ''
    },
    isFirst() {
      return this.shotIndex === 0
    },
    isLast() {
      return this.totalShots - 1 === this.shotIndex
    },
  },
  watch: {
    shot: {
      immediate: true,
      handler(shot) {
        this.parseLabelsString(shot.labels)
      },
    },
  },

  data() {
    return {
      answer: this.shot.answer,
      labels: {
        bubbling: false,
        raisedRipples: false,
        bumpsAndRoughSurface: false,
        detached: false,
        gaps: false,
        other: false,
        noIssues: false,
        notANozzleCam: false,
      },
    }
  },

  methods: {
    labelsToString: function (labels) {
      return Object.keys(labels)
        .filter((key) => labels[key])
        .join('|')
    },

    onNext: function () {
      this.updateLabels()
      this.$emit('next')
    },

    updateLabels: function () {
      const labelsString = this.labelsToString(this.labels)

      axios
        .patch(`/ent/api/first_layer_inspection_image/${this.shot.id}/`, {
          labels: labelsString,
        })
        .then((response) => {
          this.$emit('imageUpdated', response.data)
        })
    },
    parseLabelsString(labels) {
      const labelArray = labels.split('|')
      for (const key in this.labels) {
        this.$set(this.labels, key, labelArray.includes(key))
      }
    },
    openExample(type, desc) {
      const imageUrls = {
        raised: [raised1, raised2],
        bubbling: [bubbling1, bubbling2],
        bumps: [bumps1, bumps2],
        detached: [detached1, detached2],
        gaps: [gaps1, gaps2],
      }
      this.$swal.fire({
        title: `<p style="text-align:center">${desc}</p>`,
        html: `
          <div style="display:flex; align-items:center; justify-content:center; width: 100%; gap: 10px; flex-direction: column;">
              <img src=${imageUrls[type][0]} width="100%" height="400" alt="${type} example 1"></img>
              <img src=${imageUrls[type][1]} width="100%" height="400" alt="${type} example 2"></img>
            </div>
            `,
        customClass: {
          container: 'dark-backdrop',
        },
      })
    },
  },
}
</script>

<style lang="sass" scoped>
.navigation-container
  display: flex
  justify-content: space-between
  align-items: center
  gap: 1rem
  margin: -1.5em
  margin-bottom: .5em
  padding: 1em 1.5em
  background-color: var(--color-surface-primary)
  .btn
    flex-shrink: 0
</style>
