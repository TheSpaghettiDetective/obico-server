<template>
  <div class="timelapse" sticky-container>
    <div
      class="menu-bar px-sm-4 d-flex justify-content-between"
      v-sticky
      sticky-offset="{top: 0, bottom: 30}"
      sticky-side="both"
      on-stick="onMenuStick"
    >
      <a role="button" class="btn btn-outline-primary" href="/prints/upload/">
        <i class="fas fa-upload fa-lg mx-2"></i>
      </a>
      <div>
        <b-dropdown
          toggle-class="text-decoration-none no-corner no-border no-shadow"
          :variant="filterBtnVariant"
          no-caret
        >
          <template v-slot:button-content>
            <i class="fas fa-filter"></i>
          </template>
          <b-dropdown-item @click="onFilterClick('none')">
            <i class="fas fa-check" :style="{visibility: filter === 'none' ? 'visible' : 'hidden'}"></i>All
          </b-dropdown-item>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item @click="onFilterClick('finished')">
            <i
              class="fas fa-check"
              :style="{visibility: filter === 'finished' ? 'visible' : 'hidden'}"
            ></i>Finished
          </b-dropdown-item>
          <b-dropdown-item @click="onFilterClick('cancelled')">
            <i
              class="fas fa-check"
              :style="{visibility: filter === 'cancelled' ? 'visible' : 'hidden'}"
            ></i>Cancelled
          </b-dropdown-item>
          <b-dropdown-item @click="onFilterClick('need_alert_overwrite')">
            <i
              class="fas fa-check"
              :style="{visibility: filter === 'need_alert_overwrite' ? 'visible' : 'hidden'}"
            ></i>Review needed
          </b-dropdown-item>
          <b-dropdown-item @click="onFilterClick('need_print_shot_feedback')">
            <i
              class="fas fa-check"
              :style="{visibility: filter === 'need_print_shot_feedback' ? 'visible' : 'hidden'}"
            ></i>Focused-review needed
          </b-dropdown-item>
        </b-dropdown>
        <b-dropdown
          toggle-class="text-decoration-none no-corner no-border no-shadow"
          variant="outline-secondary"
          no-caret
        >
          <template v-slot:button-content>
            <i class="fas" :class="sortingBtnClasses"></i>
          </template>
          <b-dropdown-item @click="onSortingClick('date_desc')">
            <i
              class="fas fa-check"
              :style="{visibility: sorting === 'date_desc' ? 'visible' : 'hidden'}"
            ></i>Newest to oldest
          </b-dropdown-item>
          <b-dropdown-item @click="onSortingClick('date_asc')">
            <i
              class="fas fa-check"
              :style="{visibility: sorting === 'date_asc' ? 'visible' : 'hidden'}"
            ></i>Oldest to newest
          </b-dropdown-item>
        </b-dropdown>

        <button
          type="button"
          class="btn ml-3"
          :class="{'btn-light': !anyPrintsSelected, 'btn-danger': anyPrintsSelected}"
          :disabled="!anyPrintsSelected"
          @click="onDeleteBtnClick"
        >
          <i class="fas fa-trash-alt"></i>
          Delete {{ anyPrintsSelected ? ' (' + selectedPrintIds.size + ')' : '' }}
        </button>
      </div>
    </div>
    <div class="row">
      <print-card
        v-for="print of prints"
        :key="print.id"
        :print="print"
        @selectedChanged="onSelectedChanged"
        @printDeleted="onPrintDeleted"
        @printDataChanged="printDataChanged"
        @fullscreen="openFullScreen"
      ></print-card>
    </div>

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
  </div>
</template>

<script>
import axios from 'axios'
import findIndex from 'lodash/findIndex'
import MugenScroll from 'vue-mugen-scroll'

import apis from '../lib/apis'
import { normalizedPrint } from '../lib/normalizers'
import PrintCard from './PrintCard.vue'
import FullScreenPrintCard from './FullScreenPrintCard.vue'

export default {
  name: 'PrintsPage',
  components: {
    MugenScroll,
    PrintCard,
    FullScreenPrintCard
  },
  data: function() {
    return {
      prints: [],
      selectedPrintIds: new Set(),
      loading: false,
      noMoreData: false,
      filter: 'none',
      sorting: 'date_desc',
      fullScreenPrint: null,
      fullScreenPrintVideoUrl: null
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
    }
  },
  methods: {
    fetchMoreData() {
      if (this.noMoreData) {
        return
      }

      this.loading = true
      axios
        .get(apis.prints(), {
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
      this.selectedPrintIds = []
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
      this.$swal({
        title: 'Are you sure?',
        text: `Delete ${this.selectedPrintIds.size} print(s)? This action can not be undone.`,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
      }).then(userAction => {
        if (userAction.isConfirmed) {
          axios
            .post(apis.printsBulkDelete(), { print_ids: selectedPrintIds })
            .then(() => {
              selectedPrintIds.forEach(printId => this.onPrintDeleted(printId))
              this.selectedPrintIds = []
            })
        }
      })
    },
    onPrintDeleted(printId) {
      const i = findIndex(this.prints, p => p.id == printId)
      this.$delete(this.prints, i)
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

 <!-- Can not make the styles scoped, because otherwise filter-btn styles won't be apply -->
<style lang="sass">
@use "~main/theme"

.timelapse
  margin-top: 1.5rem

.menu-bar
  background-color: darken(theme.$color-bg-dark, 10)
  padding: 0.75rem

#tl-fullscreen-modal
  .modal-full
    max-width: 100%

  .modal-body
    padding: 0

  .video-js
    height: calc(100vh - 200px)
</style>
