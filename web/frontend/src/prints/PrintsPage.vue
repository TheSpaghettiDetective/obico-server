<template>
  <layout ref="layout">
    <template v-slot:topBarLeft>
      <div class="actions-with-selected-desktop">
        <b-form-group class="m-0">
          <b-form-checkbox
            v-model="allPrintsSelected"
            size="lg"
          ></b-form-checkbox>
        </b-form-group>
        <div>
          <span class="label" @click="allPrintsSelected = !allPrintsSelected" v-show="!selectedPrintIds.size">Select all</span>
          <b-dropdown v-show="selectedPrintIds.size" class="" toggle-class="btn btn-sm actions-with-selected-btn">
            <template #button-content>
              {{ selectedPrintIds.size }} item{{ selectedPrintIds.size === 1 ? '' : 's' }} selected...
            </template>
            <b-dropdown-item>
              <div class="text-danger" @click="onDeleteBtnClick">
                <i class="far fa-trash-alt"></i>Delete
              </div>
            </b-dropdown-item>
          </b-dropdown>
        </div>
      </div>
    </template>
    <template v-slot:desktopActions>
      <a href="https://app.thespaghettidetective.com/prints/upload/" class="btn shadow-none icon-btn" title="Upload Time-Lapse">
        <i class="fas fa-upload"></i>
      </a>
    </template>
    <template v-slot:mobileActions>
      <b-dropdown-item href="https://app.thespaghettidetective.com/prints/upload/">
        <i class="fas fa-upload"></i>Upload Time-Lapse
      </b-dropdown-item>
    </template>
    <template v-slot:sort>
      <b-dropdown-item v-for="option in sortOptions" :key="option.value">
        <div @click="onSortingClick(option.value); $refs.layout.sortOpened = false;" class="clickable-area">
          <i class="fas fa-check text-primary" :style="{visibility: sorting === option.value ? 'visible' : 'hidden'}"></i>
          {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
        </div>
      </b-dropdown-item>
    </template>
    <template v-slot:filter>
      <b-dropdown-item v-for="option in filterOptions" :key="option.value">
        <div @click="onFilterClick(option.value); $refs.layout.filterOpened = false;" class="clickable-area">
          <i class="fas fa-check text-primary" :style="{visibility: filter === option.value ? 'visible' : 'hidden'}"></i>
          {{ option.title }} <i v-if="option.iconClass" :class="option.iconClass"></i>
        </div>
      </b-dropdown-item>
    </template>
    <template v-slot:content>
      <b-container>
        <b-row class="print-cards" v-show="prints.length">
          <print-card
            v-for="print of prints"
            :key="print.id"
            :print="print"
            :selected="selectedPrintIds.has(print.id)"
            @selectedChanged="onSelectedChanged"
            @printDeleted="onPrintDeleted"
            @printDataChanged="printDataChanged"
            @fullscreen="openFullScreen"
          ></print-card>
        </b-row>

        <mugen-scroll :handler="fetchMoreData" :should-handle="!loading" class="text-center p-4">
          <div v-if="noMoreData" class="text-center p-2">End of your time-lapse list.</div>
          <b-spinner v-if="!noMoreData" label="Loading..."></b-spinner>
        </mugen-scroll>

        <b-modal
          id="tl-fullscreen-modal"
          size="full"
          @hidden="fullScreenClosed"
          :hideHeader="true"
          :hideFooter="true"
        >
          <FullScreenPrintCard
            :print="fullScreenPrint"
            :videoUrl="fullScreenPrintVideoUrl"
            :autoplay="true"
          />
        </b-modal>
      </b-container>
    </template>
  </layout>
</template>

<script>
import axios from 'axios'
import findIndex from 'lodash/findIndex'
import MugenScroll from 'vue-mugen-scroll'
import map from 'lodash/map'

import urls from '../lib/server_urls'
import { normalizedPrint } from '../lib/normalizers'
import PrintCard from './PrintCard.vue'
import FullScreenPrintCard from './FullScreenPrintCard.vue'
import Layout from '@common/Layout.vue'

export default {
  name: 'PrintsPage',
  components: {
    MugenScroll,
    PrintCard,
    FullScreenPrintCard,
    Layout,
  },
  data: function() {
    return {
      prints: [],
      selectedPrintIds: new Set(),
      loading: false,
      noMoreData: false,
      fullScreenPrint: null,
      fullScreenPrintVideoUrl: null,
      filter: 'none',
      sorting: 'date_desc',
      sortOptions: [
        {value: 'date_asc', title: 'Sort By Date', iconClass: 'fas fa-long-arrow-alt-up'},
        {value: 'date_desc', title: 'Sort By Date', iconClass: 'fas fa-long-arrow-alt-down'},
      ],
      filterOptions: [
        {value: 'none', title: 'All'},
        {value: 'finished', title: 'Finished'},
        {value: 'cancelled', title: 'Cancelled'},
        {value: 'need_alert_overwrite', title: 'Review needed'},
        {value: 'need_print_shot_feedback', title: 'Focused-review needed'},
      ]
    }
  },
  computed: {
    filterBtnVariant() {
      return this.filter === 'none' ? 'outline-secondary' : 'outline-primary'
    },

    sortingBtnClasses() {
      return this.sorting === 'date_asc'
        ? ' fa-sort-amount-up'
        : 'fa-sort-amount-down'
    },

    anyPrintsSelected() {
      return this.selectedPrintIds.size > 0
    },

    allPrintsSelected: {
      get: function () {
        return (this.selectedPrintIds.size >= this.prints.length) && (this.prints.length !== 0)
      },
      set: function (selected) {
        if (selected) {
          this.selectedPrintIds = new Set(map(this.prints, 'id'))
        } else {
          this.selectedPrintIds = new Set()
        }
      }
    },
  },

  methods: {
    fetchMoreData() {
      if (this.noMoreData) {
        return
      }

      this.loading = true
      axios
        .get(urls.prints(), {
          params: {
            start: this.prints.length,
            limit: 6,
            filter: this.filter,
            sorting: this.sorting
          }
        })
        .then(response => {
          this.loading = false
          this.noMoreData = response.data.length < 6
          this.prints.push(...response.data.map(data => normalizedPrint(data)))
        })
    },

    refetchData() {
      this.prints = []
      this.selectedPrintIds = new Set()
      this.noMoreData = false
      this.fetchMoreData()
    },

    onSelectedChanged(printId, selected) {
      const selectedPrintIdsClone = new Set(this.selectedPrintIds)
      if (selected) {
        selectedPrintIdsClone.add(printId)
      } else {
        selectedPrintIdsClone.delete(printId)
      }
      this.selectedPrintIds = selectedPrintIdsClone
    },

    onMenuStick(data) {
      console.log(data)
    },

    onFilterClick(filter) {
      this.filter = filter
      this.refetchData()
    },

    onSortingClick(sorting) {
      this.sorting = sorting
      this.refetchData()
    },

    onDeleteBtnClick() {
      const selectedPrintIds = Array.from(this.selectedPrintIds)
      this.$swal.Prompt.fire({
        title: 'Are you sure?',
        text: `Delete ${this.selectedPrintIds.size} print(s)? This action can not be undone.`,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
      }).then(userAction => {
        if (userAction.isConfirmed) {
          axios
            .post(urls.printsBulkDelete(), { print_ids: selectedPrintIds })
            .then(() => {
              selectedPrintIds.forEach(printId => this.onPrintDeleted(printId, false))
              this.$swal.Toast.fire({
                title: `${selectedPrintIds.length} time-lapse(s) deleted!`,
              })
              this.selectedPrintIds = new Set()
            })
        }
      })
    },
    onPrintDeleted(printId, toast=true) {
      const i = findIndex(this.prints, p => p.id == printId)
      const print = this.prints[i]
      this.$delete(this.prints, i)
      if (toast) {
        this.$swal.Toast.fire({
          title: `Time-lapse ${print.filename} deleted!`,
        })
      }
    },
    printDataChanged(data) {
      const i = findIndex(this.prints, p => p.id == data.id)
      this.$set(this.prints, i, normalizedPrint(data))
    },
    openFullScreen(printId, videoUrl) {
      const i = findIndex(this.prints, p => p.id == printId)
      if (i != -1) {
        this.fullScreenPrint = this.prints[i]
        this.fullScreenPrintVideoUrl = videoUrl
        this.$bvModal.show('tl-fullscreen-modal')
      }
    },
    fullScreenClosed() {
      this.fullScreenPrint = null
      this.fullScreenPrintVideoUrl = null
    }
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

.print-cards
  margin-top: calc(var(--gap-between-blocks) * -1)

.menu-bar
  background-color: rgb(var(--color-surface-secondary))
  padding: 0.75rem 1.25rem

#tl-fullscreen-modal
  .modal-full
    max-width: 100%

  .modal-body
    padding: 0

  .video-js
    height: calc(100vh - 200px)

::v-deep .btn-outline-secondary
  color: rgb(var(--color-text-primary))
  border-color: rgb(var(--color-text-primary))

  &:hover
    background: none
    opacity: .8

.actions-with-selected-desktop
  display: flex
  align-items: center
  .label
    cursor: pointer
  ::v-deep .actions-with-selected-btn
    border-radius: 0

</style>
