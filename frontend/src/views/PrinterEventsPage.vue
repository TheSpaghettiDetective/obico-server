<template>
  <page-layout>
    <template #topBarRight>
      <div>
        <b-dropdown right no-caret toggle-class="icon-btn">
          <template #button-content>
            <i class="fas fa-filter"></i>
          </template>
          <b-dropdown-item
            v-for="eventClass in eventClassFiltering"
            :key="eventClass.key"
            @click="toggleEventFiltering('eventClassFiltering', eventClass.key)"
          >
            <i
              class="fas fa-check text-primary"
              :style="{ visibility: eventClass.selected ? 'visible' : 'hidden' }"
            ></i
            ><span :class="cssClassFromEventClass(eventClass.key)">{{ eventClass.title }}</span>
          </b-dropdown-item>
          <b-dropdown-divider />
          <b-dropdown-item
            v-for="eventType in eventTypeFiltering"
            :key="eventType.key"
            @click="toggleEventFiltering('eventTypeFiltering', eventType.key)"
          >
            <i
              class="fas fa-check text-primary"
              :style="{ visibility: eventType.selected ? 'visible' : 'hidden' }"
            ></i
            >{{ eventType.title }}
          </b-dropdown-item>
        </b-dropdown>
      </div>
    </template>
    <template #content>
      <b-container>
        <b-row class="justify-content-center">
          <div class="col-sm-12 col-md-10 col-lg-8">
            <div v-if="!loading && printerEvents.length === 0" class="text-center">
              <img :src="require('@static/img/vacation.gif')" class="w-25 my-4" />
              <h5 class="text-primary">{{ $t("Nothing to look here. Enjoy your vacation!") }}</h5>
            </div>
            <div v-else>
              <printer-event-card
                v-for="item in printerEvents"
                :key="item.id"
                :printer-event="item"
              />
              <mugen-scroll
                :handler="fetchMoreData"
                :should-handle="!loading"
                class="text-center p-4"
              >
                <div v-if="noMoreData" class="text-center p-2">{{ $t("No more notifications.") }}</div>
                <b-spinner v-if="!noMoreData" label="Loading..."></b-spinner>
              </mugen-scroll>
            </div>
          </div>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import filter from 'lodash/filter'
import map from 'lodash/map'
import axios from 'axios'
import MugenScroll from 'vue-mugen-scroll'

import urls from '@config/server-urls'
import PageLayout from '@src/components/PageLayout.vue'
import PrinterEventCard from '@src/components/printer-events/PrinterEventCard.vue'
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import { normalizedPrinterEvent } from '@src/lib/normalizers'
import findIndex from 'lodash/findIndex'

const LOCAL_PREF_NAMES = {
  eventClassFiltering: 'printer-event-class-filtering',
  eventTypeFiltering: 'printer-event-type-filtering',
}

const localPrefKey = (prefix, key) => {
  return `${LOCAL_PREF_NAMES['prefix']}.${key}`
}

const localPref = (prefix, key, defaultValue) => {
  return getLocalPref(localPrefKey(prefix, key), defaultValue)
}

const PAGE_SIZE = 12

export default {
  name: 'PrinterEventsPage',

  components: {
    MugenScroll,
    PageLayout,
    PrinterEventCard,
  },

  props: {},

  data() {
    return {
      printerEvents: [],
      loading: false,
      noMoreData: false,
      eventClassFiltering: [
        { key: 'ERROR', title: 'Error', selected: localPref('eventClassFiltering', 'ERROR', true) },
        {
          key: 'WARNING',
          title: 'Warning',
          selected: localPref('eventClassFiltering', 'WARNING', true),
        },
        {
          key: 'SUCCESS',
          title: 'Successs',
          selected: localPref('eventClassFiltering', 'SUCCESS', true),
        },
        { key: 'INFO', title: 'Other', selected: localPref('eventClassFiltering', 'INFO', true) },
      ],
      eventTypeFiltering: [
        {
          key: 'ALERT',
          title: 'Failure Detection',
          selected: localPref('eventTypeFiltering', 'ALERT', true),
        },
        {
          key: 'ENDED',
          title: 'Print Job Ended',
          selected: localPref('eventTypeFiltering', 'ENDED', true),
        },
        {
          key: 'STARTED',
          title: 'Print Job Started',
          selected: localPref('eventTypeFiltering', 'STARTED', true),
        },
        {
          key: 'PAUSE_RESUME',
          title: 'Print Job Paused/Resumed',
          selected: localPref('eventTypeFiltering', 'PAUSE_RESUME', true),
        },
        {
          key: 'FILAMENT_CHANGE',
          title: 'Filament Change',
          selected: localPref('eventTypeFiltering', 'FILAMENT_CHANGE', true),
        },
        {
          key: 'PRINTER_ERROR',
          title: 'Printer Error',
          selected: localPref('eventTypeFiltering', 'PRINTER_ERROR', true),
        },
      ],
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
      const filter_by_classes = map(filter(this.eventClassFiltering, 'selected'), 'key')
      const filter_by_types = map(filter(this.eventTypeFiltering, 'selected'), 'key')
      axios
        .get(urls.printerEvents(), {
          params: {
            start: this.printerEvents.length,
            limit: PAGE_SIZE,
            filter_by_classes,
            filter_by_types,
          },
        })
        .then((response) => {
          this.loading = false
          this.noMoreData = response.data.length < PAGE_SIZE
          this.printerEvents.push(...response.data.map((data) => normalizedPrinterEvent(data)))
        })
    },
    refetchData() {
      this.printerEvents = []
      this.noMoreData = false
      this.fetchMoreData()
    },
    cssClassFromEventClass(eventClass) {
      switch (eventClass) {
        case 'ERROR':
          return 'text-danger'
        case 'INFO':
          return ''
        default:
          return `text-${eventClass.toLowerCase()}`
      }
    },
    toggleEventFiltering(filter, key) {
      const i = findIndex(this[filter], (f) => f.key == key)
      const original = this[filter][i]
      this.$set(this[filter], i, { ...original, selected: !original.selected })
      setLocalPref(localPrefKey('eventClassFiltering', filter.key), !original.selected)
      this.refetchData()
    },
  },
}
</script>

<style lang="sass" scoped></style>
