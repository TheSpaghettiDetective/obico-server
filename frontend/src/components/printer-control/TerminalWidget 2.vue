<template>
  <widget-template>
    <template #title>{{ $t("Printer Terminal") }}</template>
    <template #content>
      <div class="actionWrap">
        <a :href="`/printers/${printer.id}/terminal/`">
          <div class="actionBtn">
            <i class="fas fa-expand actionIcon"></i>
          </div>
        </a>
        <div class="actionBtn" @click="clearFeed">
          <i class="fas fa-trash actionIcon"></i>
        </div>
        <b-dropdown
          right
          no-caret
          class="actionBtnNoP"
          toggle-class="action-btn icon-btn"
          menu-class="scrollable"
          title="Filter"
        >
          <template #button-content>
            <i class="fas fa-filter"></i>
          </template>
          <div>
            <div>
              <b-dropdown-text class="small text-secondary">{{ $t("Filter") }}</b-dropdown-text>
              <b-dropdown-item
                @click.native.capture.stop.prevent="
                  updateFilterPrefs('temperature', !hideTempMessages)
                "
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: hideTempMessages ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="filterItemH">
                    <i class="fas fa-fire"></i>
                    <div class="text">{{ $t("Suppress Temperature") }}</div>
                  </div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item
                @click.native.capture.stop.prevent="updateFilterPrefs('sd', !hideSDMessages)"
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: hideSDMessages ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="filterItemH">
                    <i class="fas fa-sd-card"></i>
                    <div class="text">{{ $t("Suppress SD Status Messages") }}</div>
                  </div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item
                @click.native.capture.stop.prevent="updateFilterPrefs('gcode', !hideGCodeMessages)"
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: hideGCodeMessages ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="filterItemH">
                    <i class="fas fa-code"></i>
                    <div class="text">{{ $t("Suppress Position Messages") }}</div>
                  </div>
                </div>
              </b-dropdown-item>
              <b-dropdown-item
                @click.native.capture.stop.prevent="updateFilterPrefs('ok', !hideOKMessages)"
              >
                <div class="dropdown-text-group">
                  <i
                    class="fas fa-check text-primary"
                    :style="{ visibility: hideOKMessages ? 'visible' : 'hidden' }"
                  ></i>
                  <div class="filterItemH">
                    <i class="fas fa-thumbs-up"></i>
                    <div class="text">{{ $t("Suppress 'OK' Messages") }}</div>
                  </div>
                </div>
              </b-dropdown-item>
            </div>
          </div>
        </b-dropdown>
      </div>
      <div class="wrapper">
        <terminal-window class="feedWrap" :terminal-feed-array="terminalFeedArray" />
        <div class="inputWrap">
          <input
            v-model="inputValue"
            type="text"
            class="textInput"
            :placeholder="$t('Enter code...')"
            @keyup.enter="sendMessage"
          />
          <b-button variant="outline-primary" class="sendBtn" @click="sendMessage">{{ $t(" Send ") }}</b-button>
        </div>
      </div>
    </template>
  </widget-template>
</template>

<script>
import WidgetTemplate from '@src/components/printer-control/WidgetTemplate'
import terminalMixin from '@src/components/terminal/terminal-mixin.js'
import TerminalWindow from '@src/components/terminal/TerminalWindow'

export default {
  name: 'TerminalWidget',

  components: {
    WidgetTemplate,
    TerminalWindow,
  },

  mixins: [terminalMixin],

  props: {
    printer: {
      type: Object,
      required: true,
    },
    printerComm: {
      type: Object,
      required: true,
    },
  },

  created() {
    this.printerComm.onTerminalFeedReceived = this.onNextTerminalFeed
  },
}
</script>

<style lang="sass" scoped>
.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem
  height: 300px
  position: relative

.feedWrap
  height: 250px
  padding: 10px
  width: 100%
  background-color: var(--color-background)
.feedWrap::-webkit-scrollbar
  background-color: var(--color-background)
.feedWrap::-webkit-scrollbar-thumb
  background-color: var(--color-surface-primary)

.inputWrap
  display: flex
  flex-direction: row
  justify-content: space-between
  height: 50px
  width: 100%
  gap: 1rem

.textInput
  height: 100%
  flex: 1
  padding: 10px

.sendBtn
  height: 100%
  width: auto

.actionBtn
  margin-left: 5px
  margin-right: 5px
  padding: 10px 16px
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-sm)
  &:hover
    cursor: pointer

.actionBtnNoP
  margin-left: 5px
  margin-right: 5px
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-primary)
  border-radius: var(--border-radius-sm)
  z-index: 1
  &:hover
    cursor: pointer

.actionIcon
  width: 16px
  height: 16px
  color: var(--color-text-primary)

.actionWrap
  position: absolute
  display: flex
  flex-direction: row
  top: 0px
  right: 15px
  align-items: center
  justify-content: flex-end
  width: 100%
  padding: 10px 15px

.filterItemH
  display: flex
  flex-direction: row
  align-items: center
</style>
