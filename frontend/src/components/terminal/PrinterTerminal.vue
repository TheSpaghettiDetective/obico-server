<template>
  <div class="fullHeight">
    <div class="actionWrap">
      <a :href="`/printers/${printer.id}/terminal/`">
        <b-button class="actionBtn">
          <i class="fas fa-expand actionIcon"></i>
        </b-button>
      </a>
      <b-button
        v-if="!isMoonraker && meetsPowerVersion"
        class="actionBtn"
        @click="toggleTerminalPower"
      >
        <b-spinner v-if="terminalPower === null" small />
        <i v-else class="fas fa-power-off actionIcon"></i>
      </b-button>
      <b-button class="actionBtn" @click="clearFeed">
        <i class="fas fa-trash actionIcon"></i>
      </b-button>
      <b-dropdown
        :disabled="!terminalPower"
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
            <b-dropdown-text class="small text-secondary">Filter</b-dropdown-text>
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
                  <div class="text">Suppress Temperature</div>
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
                  <div class="text">Suppress SD Status Messages</div>
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
                  <div class="text">Suppress Position Messages</div>
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
                  <div class="text">Suppress 'OK' Messages</div>
                </div>
              </div>
            </b-dropdown-item>
          </div>
        </div>
      </b-dropdown>
    </div>
    <div class="wrapper fullHeight">
      <terminal-window
        class="feedWrap fullHeight"
        :terminal-feed-array="terminalFeedArray"
        :show-powered-off="!isMoonraker && meetsPowerVersion && terminalPower === false"
      />
      <div class="inputWrap">
        <input
          :disabled="!terminalPower"
          v-model="inputValue"
          type="text"
          class="textInput"
          placeholder="Enter code..."
          @keyup.enter="sendMessage"
        />
        <b-button
          :disabled="!terminalPower"
          variant="outline-primary"
          class="sendBtn"
          @click="sendMessage"
        >
          Send
        </b-button>
      </div>
    </div>
  </div>
</template>

<script>
import terminalMixin from '@src/components/terminal/terminal-mixin.js'
import TerminalFeedView from '@src/components/terminal/TerminalFeedView'

export default {
  name: 'PrinterTerminal',

  components: {
    TerminalFeedView,
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

.fullHeight
  flex: 1
  display: flex
  flex-direction: column

.wrapper
  display: flex
  flex-direction: column
  align-items: center
  gap: .825rem
  padding-bottom: 1rem
  position: relative

.feedWrap
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
