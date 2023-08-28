<template>
  <page-layout>
    <!-- Tob bar -->
    <template #topBarLeft>
      <div class="printer-name truncated">
        {{ printer ? printer.name : '' }}
      </div>
    </template>
    <template #topBarRight>
      <div v-if="printer" class="action-panel">
        <!-- Tunnel -->
        <a
          :href="`/tunnels/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="OctoPrint Tunnel"
        >
          <svg class="custom-svg-icon">
            <use href="#svg-tunnel" />
          </svg>
          <span class="sr-only">OctoPrint Tunnel</span>
        </a>
        <!-- Configure -->
        <a
          :href="`/printers/${printer.id}/`"
          class="btn shadow-none action-btn icon-btn"
          title="Configure"
        >
          <i class="fas fa-wrench"></i>
          <span class="sr-only">Configure</span>
        </a>
        <!-- Mobile Menu -->
        <b-dropdown right no-caret toggle-class="icon-btn d-md-none">
          <template #button-content>
            <i class="fas fa-ellipsis-v"></i>
          </template>
          <cascaded-dropdown
            ref="cascadedDropdown"
            :menu-options="[
              {
                key: 'tunnel',
                svgIcon: 'svg-tunnel',
                title: 'OctoPrint Tunnel',
                href: `/tunnels/${printer.id}/`,
              },
              {
                key: 'settings',
                icon: 'fas fa-wrench',
                title: 'Configure',
                href: `/printers/${printer.id}/`,
              },
            ]"
            @menuOptionClicked="onMenuOptionClicked"
          />
        </b-dropdown>
      </div>
    </template>
    <!-- Page content -->
    <template #content>
      <div class="contentWrap">
        <div class="controlsWrap">
          <div class="inputWrap">
            <input
              :disabled="!terminalPower"
              v-model="inputValue"
              type="text"
              class="textInput"
              placeholder="Enter code..."
              @keyup.enter="sendMessage"
            />
            <b-button :disabled="!terminalPower" class="sendBtn" @click="sendMessage">
              <i class="fas fa-chevron-right sendIcon"></i>
            </b-button>
          </div>
          <div class="buttonWrap">
            <b-button
              v-if="!isMoonraker && meetsPowerVersion"
              class="buttonHolder"
              @click="toggleTerminalPower"
            >
              <b-spinner v-if="terminalPower === null" small />
              <i v-else class="fas fa-power-off actionIcon"></i>
            </b-button>
            <b-button :disabled="!terminalPower" class="buttonHolder" @click="clearFeed">
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
                    @click.native.capture.stop.prevent="
                      updateFilterPrefs('gcode', !hideGCodeMessages)
                    "
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
        </div>
        <terminal-window
          class="feedWrap"
          :terminal-feed-array="terminalFeedArray"
          :show-powered-off="!isMoonraker && meetsPowerVersion && terminalPower === false"
        />
      </div>
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import { printerCommManager } from '@src/lib/printer-comm'
import urls from '@config/server-urls'
import { normalizedPrinter } from '@src/lib/normalizers'
import { user } from '@src/lib/page-context'
import split from 'lodash/split'
import CascadedDropdown from '@src/components/CascadedDropdown'
import terminalMixin from '@src/components/terminal/terminal-mixin.js'
import TerminalWindow from '@src/components/terminal/TerminalWindow'

export default {
  name: 'PrinterTerminalPage',

  components: {
    PageLayout,
    CascadedDropdown,
    TerminalWindow,
  },

  mixins: [terminalMixin],

  data: function () {
    return {
      user: null,
      printerId: null,
      printer: null,
    }
  },

  created() {
    this.user = user()
    this.printerId = split(window.location.pathname, '/').slice(-3, -2).pop()
    this.printerComm = printerCommManager.getOrCreatePrinterComm(
      this.printerId,
      urls.printerWebSocket(this.printerId),
      {
        onPrinterUpdateReceived: (data) => {
          this.printer = normalizedPrinter(data, this.printer)
          if (this.webrtc && !this.webrtc.initialized) {
            this.webrtc.openForPrinter(this.printer.id, this.printer.auth_token)
            this.printerComm.setWebRTC(this.webrtc)
          }
        },
        onTerminalFeedReceived: this.onNextTerminalFeed,
      }
    )
    this.printerComm.connect()
  },

  methods: {
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'share') {
        this.onSharePrinter()
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.printer-name
  font-size: 1rem
  max-width: 360px
  font-weight: bold
  @media (max-width: 768px)
    max-width: 200px

.custom-svg-icon
  height: 1.25rem
  width: 1.25rem

.contentWrap
  flex: 1
  display: flex
  flex-direction: column

.controlsWrap
  width: 100%
  align-items: center
  margin-top: 0
  height: 3rem
  max-height: 3rem
  display: flex
  flex: 1

.inputWrap
  height: 3rem
  margin-right: 10px
  display: flex
  flex: 1
  flex-direction: row
  align-items: center
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)
  @media (max-width: 450px)
      max-width: 45%
      flex: 0 1

.textInput
  height: 100%
  flex: 1
  border: none
  padding: 0px 20px
  background-color: var(--color-surface-secondary)
  @media (max-width: 450px)
    max-width: 75%

.sendBtn
  width: 3rem
  height: 100%
  display: flex
  flex-direction: row
  align-items: center
  justify-content: center
  border-radius: var(--border-radius-md)
  transition: all 0.2s ease-in-out
  &:hover
    opacity: 0.8
    cursor: pointer
    background-color: var(--color-surface-primary)

.buttonWrap
  display: flex
  align-items: center
  justify-content: flex-start
  height: 3rem
  gap: 10px
  @media (max-width: 450px)
    flex: 1
    justify-content: flex-end

.buttonHolder
  padding: 10px 16px
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)
  transition: all 0.2s ease-in-out
  &:hover
    cursor: pointer
    background-color: var(--color-surface-primary)

.actionBtnNoP
  height: 100%
  display: flex
  align-items: center
  justify-content: center
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)
  z-index: 1
  transition: all 0.2s ease-in-out
  &:hover
    cursor: pointer
    background-color: var(--color-surface-primary)

.actionIcon
  color: var(--color-text-primary)

.feedWrap
  margin-top: 15px
  padding: 20px
  flex: 1
  margin-bottom: -68px

.filterItemH
  display: flex
  flex-direction: row
  align-items: center
</style>
