<template>
  <layout>
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
    <template v-slot:topBarRight>
      <div>
        <a href="/prints/upload/" class="btn shadow-none icon-btn d-none d-md-inline" title="Upload Time-Lapse">
          <i class="fas fa-upload"></i>
        </a>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <b-dropdown-item href="/prints/upload/" class="d-md-none">
            <i class="fas fa-upload"></i>Upload Time-Lapse
          </b-dropdown-item>
          <b-dropdown-divider class="d-md-none"></b-dropdown-divider>

          <cascaded-dropdown
            :menuOptions="menuOptions"
            :menuSelections="menuSelections"
            @menuSelectionChanged="menuSelectionChanged"
          >
          </cascaded-dropdown>
        </b-dropdown>
      </div>
    </template>
    <template v-slot:content>
      <a v-if="shouldShowFilterWarning"  @click="onShowAllClicked" class="active-filter-notice">
        <div class="filter">
          <i class="fas fa-filter mr-2"></i>
          {{ activeFiltering }}
        </div>
        <div>SHOW ALL</div>
      </a>
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

import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import PrintCard from '@src/components/prints/PrintCard.vue'
import FullScreenPrintCard from '@src/components/prints/FullScreenPrintCard.vue'
import Layout from '@src/components/Layout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'

const LocalPrefNames = {
  filtering: 'prints-filtering',
  sorting: 'prints-sorting',
}

export default {
  name: 'PrintsPage',
  components: {
    MugenScroll,
    PrintCard,
    FullScreenPrintCard,
    Layout,
    CascadedDropdown,
  },
  data: function() {
    return {
      prints: [],
      selectedPrintIds: new Set(),
      loading: false,
      noMoreData: false,
      fullScreenPrint: null,
      fullScreenPrintVideoUrl: null,
      menuSelections: {
        'Sort By': getLocalPref(
          LocalPrefNames.sorting,
          'date_desc'),
        'Filter By': getLocalPref(
          LocalPrefNames.filtering,
          'none'),
      },
      menuOptions: {
        'Sort By': {
          iconClass: 'fas fa-sort-amount-up',
          options: [
            {value: 'date_asc', title: 'Sort By Date', iconClass: 'fas fa-long-arrow-alt-up'},
            {value: 'date_desc', title: 'Sort By Date', iconClass: 'fas fa-long-arrow-alt-down'},
          ]
        },
        'Filter By': {
          iconClass: 'fas fa-filter',
          options: [
            {value: 'none', title: 'All'},
            {value: 'finished', title: 'Succeeded'},
            {value: 'cancelled', title: 'Cancelled'},
            {value: 'need_alert_overwrite', title: 'Review Needed'},
            {value: 'need_print_shot_feedback', title: 'Focused-Review Needed'},
          ],
        }
      },
    }
  },
  computed: {
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
    shouldShowFilterWarning() {
      return this.menuSelections['Filter By'] !== 'none'
    },
    activeFiltering() {
      const found = this.menuOptions['Filter By'].options.filter(option => option.value === this.menuSelections['Filter By'])
      return found.length ? found[0].title : null
    }
  },

  created() {
    this.refetchData()
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
            filter: this.menuSelections['Filter By'],
            sorting: this.menuSelections['Sort By'],
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

    menuSelectionChanged(menu, selectedOption) {
      this.$set(this.menuSelections, menu, selectedOption.value)
      const prefName = menu === 'Sort By' ? LocalPrefNames.sorting : LocalPrefNames.filtering
      setLocalPref(prefName, selectedOption.value)
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
    },
    onShowAllClicked(){
      this.$set(this.menuSelections, 'Filter By', 'none')
      setLocalPref(
        LocalPrefNames.filtering,
        'none'
      )
      this.refetchData()
    },
  }
}
</script>

<style lang="sass" scoped>
.print-cards
  margin-top: calc(var(--gap-between-blocks) * -1)

.menu-bar
  background-color: var(--color-surface-secondary)
  padding: 0.75rem 1.25rem

#tl-fullscreen-modal
  .modal-full
    max-width: 100%

  .modal-body
    padding: 0

  .video-js
    height: calc(100vh - 200px)

::v-deep .btn-outline-secondary
  color: var(--color-text-primary)
  border-color: var(--color-text-primary)

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
