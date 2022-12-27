<template>
  <layout>

    <!-- Tob bar -->
    <template v-slot:topBarRight>
      <b-dropdown right no-caret toggle-class="icon-btn">
        <template #button-content>
          <i class="fas fa-ellipsis-v"></i>
        </template>
        <cascaded-dropdown
          :menuOptions="menuOptions"
          :menuSelections="menuSelections"
          @menuSelectionChanged="menuSelectionChanged"
        >
        </cascaded-dropdown>
      </b-dropdown>
    </template>

    <!-- Page content -->
    <template v-slot:content>
      <!-- Active filter notice -->
      <a v-if="shouldShowFilterWarning"  @click.prevent="onShowAllClicked" href="#" class="active-filter-notice">
        <div class="filter">
          <i class="fas fa-filter mr-2"></i>
          {{ activeFiltering }}
        </div>
        <div class="action-btn">SHOW ALL</div>
      </a>
      <!-- Prints list -->
      <b-container>
        <b-row>
          <b-col v-if="prints.length">
            <print-item
              v-for="print of prints"
              :key="print.id"
              :print="print"
              class="print-item"
            ></print-item>
            <mugen-scroll :handler="fetchMoreData" :should-handle="!loading">
              <div class="text-center p-4" v-if="!noMoreData">
                <b-spinner label="Loading..."></b-spinner>
              </div>
            </mugen-scroll>
          </b-col>
          <b-col v-else>
            Not found
          </b-col>
        </b-row>
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
import Layout from '@src/components/Layout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import PrintItem from '@src/components/prints/PrintItem.vue'

const LOCAL_PREF_NAMES = {
  filtering: 'prints-filtering',
  sorting: 'prints-sorting',
}

const PAGE_SIZE = 24

export default {
  name: 'PrintsPage',

  components: {
    MugenScroll,
    Layout,
    CascadedDropdown,
    PrintItem,
  },

  data: function() {
    return {
      prints: [],
      loading: false,
      noMoreData: false,
      menuSelections: {
        'Sort By': getLocalPref(
          LOCAL_PREF_NAMES.sorting,
          'date_desc'),
        'Filter By': getLocalPref(
          LOCAL_PREF_NAMES.filtering,
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
            limit: PAGE_SIZE,
            filter: this.menuSelections['Filter By'],
            sorting: this.menuSelections['Sort By'],
          }
        })
        .then(response => {
          this.loading = false
          this.noMoreData = response.data.length < PAGE_SIZE
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
      const prefName = menu === 'Sort By' ? LOCAL_PREF_NAMES.sorting : LOCAL_PREF_NAMES.filtering
      setLocalPref(prefName, selectedOption.value)
      this.refetchData()
    },

    onShowAllClicked() {
      this.$set(this.menuSelections, 'Filter By', 'none')
      setLocalPref(
        LOCAL_PREF_NAMES.filtering,
        'none'
      )
      this.refetchData()
    },
  }
}
</script>

<style lang="sass" scoped>
.print-item
  margin-bottom: 10px
</style>
