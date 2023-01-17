<template>
  <page-layout>
    <!-- Tob bar -->
    <template #topBarRight>
      <b-dropdown right no-caret toggle-class="icon-btn">
        <template #button-content>
          <i class="fas fa-ellipsis-v"></i>
        </template>
        <cascaded-dropdown
          :menu-options="menuOptions"
          :menu-selections="menuSelections"
          @menuSelectionChanged="menuSelectionChanged"
        >
        </cascaded-dropdown>
      </b-dropdown>
    </template>

    <!-- Page content -->
    <template #content>
      <!-- Active filter notice -->
      <a
        v-if="shouldShowFilterWarning"
        href="#"
        class="active-filter-notice"
        @click.prevent="onShowAllClicked"
      >
        <div class="filter">
          <i class="fas fa-filter mr-2"></i>
          {{ activeFiltering }}
        </div>
        <div class="action-btn">SHOW ALL</div>
      </a>
      <!-- Prints list -->
      <b-container>
        <b-row>
          <b-col v-if="prints.length || loading">
            <print-history-item
              v-for="print of prints"
              :key="print.id"
              :print="print"
              class="print-item"
            ></print-history-item>
            <mugen-scroll :handler="fetchMoreData" :should-handle="!loading">
              <loading-placeholder v-if="!noMoreData" />
            </mugen-scroll>
          </b-col>
          <b-col v-else class="text-center my-5">You don't have print history yet</b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import axios from 'axios'
import MugenScroll from 'vue-mugen-scroll'
import urls from '@config/server-urls'
import { normalizedPrint } from '@src/lib/normalizers'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import PageLayout from '@src/components/PageLayout.vue'
import CascadedDropdown from '@src/components/CascadedDropdown'
import PrintHistoryItem from '@src/components/prints/PrintHistoryItem.vue'

const LOCAL_PREF_NAMES = {
  filtering: 'prints-filtering',
  sorting: 'prints-sorting',
}
const PAGE_SIZE = 24

export default {
  name: 'PrintHistoryPage',

  components: {
    MugenScroll,
    PageLayout,
    CascadedDropdown,
    PrintHistoryItem,
  },

  data: function () {
    return {
      prints: [],
      loading: false,
      noMoreData: false,
      menuSelections: {
        'Sort By': getLocalPref(LOCAL_PREF_NAMES.sorting, 'date_desc'),
        'Filter By': getLocalPref(LOCAL_PREF_NAMES.filtering, 'none'),
      },
      menuOptions: {
        'Sort By': {
          iconClass: 'fas fa-sort-amount-up',
          options: [
            { value: 'date_asc', title: 'Oldest First', iconClass: 'fas fa-long-arrow-alt-up' },
            { value: 'date_desc', title: 'Newest First', iconClass: 'fas fa-long-arrow-alt-down' },
          ],
        },
        'Filter By': {
          iconClass: 'fas fa-filter',
          options: [
            { value: 'none', title: 'All' },
            { value: 'finished', title: 'Succeeded' },
            { value: 'cancelled', title: 'Cancelled' },
            { value: 'need_alert_overwrite', title: 'Review Needed' },
            { value: 'need_print_shot_feedback', title: 'Focused-Review Needed' },
          ],
        },
      },
    }
  },

  computed: {
    shouldShowFilterWarning() {
      return this.menuSelections['Filter By'] !== 'none'
    },
    activeFiltering() {
      const found = this.menuOptions['Filter By'].options.filter(
        (option) => option.value === this.menuSelections['Filter By']
      )
      return found.length ? found[0].title : null
    },
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
          },
        })
        .then((response) => {
          this.loading = false
          this.noMoreData = response.data.length < PAGE_SIZE
          this.prints.push(...response.data.map((data) => normalizedPrint(data)))
        })
        .catch((error) => {
          this._showErrorPopup(error)
        })
    },
    refetchData() {
      this.prints = []
      this.noMoreData = false
      this.fetchMoreData()
    },
    menuSelectionChanged(menu, selectedOption) {
      this.$set(this.menuSelections, menu, selectedOption.value)
      const prefName = menu === 'Sort By' ? LOCAL_PREF_NAMES.sorting : LOCAL_PREF_NAMES.filtering
      setLocalPref(prefName, selectedOption.value)
      this.refetchData()
    },
    onShowAllClicked() {
      this.$set(this.menuSelections, 'Filter By', 'none')
      setLocalPref(LOCAL_PREF_NAMES.filtering, 'none')
      this.refetchData()
    },
  },
}
</script>

<style lang="sass" scoped>
.print-item
  margin-bottom: 10px
</style>
