<template>
  <div class="chat-header">
    <div class="header-left">
      <div class="custom-control custom-checkbox">
        <input
          id="dont-show-checkbox"
          v-model="chatPanelPopUpOnErrors"
          class="custom-control-input"
          type="checkbox"
        />
        <label class="custom-control-label" for="dont-show-checkbox"> {{ $t("Pop up on errors") }} </label>
      </div>
    </div>
    <div class="header-actions">
      <button
        class="header-button"
        :title="$t('Contact Support')"
        @click="$emit('show-contact-support-form')"
      >
        <i class="mdi mdi-message-question-outline large-icon"></i>
      </button>

      <div class="header-divider">|</div>
      <button
        v-if="curChatPanelViewMode !== 'large'"
        class="header-button"
        :title="$t('Large Chat Window')"
        @click="changeChatPanelViewMode('large', true)"
      >
        <i class="mdi mdi-arrow-expand large-icon"></i>
      </button>

      <button
        v-if="curChatPanelViewMode !== 'small'"
        class="header-button"
        :title="$t('Small Chat Window')"
        @click="changeChatPanelViewMode('small', true)"
      >
        <i class="mdi mdi-arrow-collapse large-icon"></i>
      </button>

      <button class="header-button" :title="$t('Close')" @click="changeChatPanelVisibility(false)">
        <i class="mdi mdi-close large-icon"></i>
      </button>
    </div>
  </div>
</template>

<script>
import { getAgentActionResponse, callAgentAction } from '../lib/agentAction'

export default {
  name: 'ChatPanelHeader',
  props: {
    shouldPopupChatPanel: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      curChatPanelViewMode: 'large',
      preferredChatPanelViewModeValue:
        localStorage.getItem('jusprin.preferredChatPanelViewMode') || 'large',
      curChatPanelVisible: false,
      popupChatPanelTimeout: null,
      notificationBadgeCount: {
        green_badge: 0,
        orange_badge: 0,
        red_badge: 0,
      },
      chatPanelPopUpOnErrorsValue:
        localStorage.getItem('jusprin.chatPanelPopUpOnErrors') !== 'false',
    }
  },
  computed: {
    chatPanelPopUpOnErrors: {
      get() {
        return this.chatPanelPopUpOnErrorsValue
      },
      set(newValue) {
        this.chatPanelPopUpOnErrorsValue = newValue
        localStorage.setItem('jusprin.chatPanelPopUpOnErrors', newValue.toString())
      },
    },
    preferredChatPanelViewMode: {
      get() {
        return this.preferredChatPanelViewModeValue
      },
      set(newViewMode) {
        this.preferredChatPanelViewModeValue = newViewMode
        localStorage.setItem('jusprin.preferredChatPanelViewMode', newViewMode)
      },
    },
  },
  async mounted() {
    const devMode = new URLSearchParams(window.location.search).get('devmode') === 'true'
    await this.changeChatPanelViewMode(this.preferredChatPanelViewMode, false)
    await this.changeChatPanelVisibility(devMode) // If dev mode, show the chat panel so that we can debug it
  },

  methods: {
    async popupChatPanelIfNecessary(level) {
      if (this.curChatPanelVisible) return // Don't popup if the panel is already open

      if (!this.chatPanelPopUpOnErrors) {
        if (level === 'error') {
          this.notificationBadgeCount.red_badge += 1
        } else if (level === 'warning') {
          this.notificationBadgeCount.orange_badge += 1
        } else {
          this.notificationBadgeCount.green_badge += 1
        }
        callAgentAction('set_btn_notification_badges', this.notificationBadgeCount)
        return
      }
      await this.changeChatPanelViewMode('small', false)
      await this.changeChatPanelVisibility(true)
    },
    async changeChatPanelViewMode(newViewMode, savePreferredViewMode = false) {
      const { view_mode } = await getAgentActionResponse('change_chatpanel_display', {
        view_mode: newViewMode,
      })

      this.curChatPanelViewMode = view_mode
      if (savePreferredViewMode) {
        this.preferredChatPanelViewMode = view_mode
      }
    },
    async changeChatPanelVisibility(newVisible) {
      const { visible } = await getAgentActionResponse('change_chatpanel_display', {
        visible: newVisible,
      })
      this.curChatPanelVisible = visible
    },
    async processChatPanelFocusEvent(event) {
      if (!event?.data?.focusEventType) return

      const { focusEventType } = event.data
      if (focusEventType === 'in_focus') {
        await this.changeChatPanelViewMode(this.preferredChatPanelViewMode, false)
        await this.changeChatPanelVisibility(true)

        this.notificationBadgeCount = {
          green_badge: 0,
          orange_badge: 0,
          red_badge: 0,
        }
        callAgentAction('set_btn_notification_badges', this.notificationBadgeCount)
      } else if (focusEventType === 'out_of_focus') {
        this.changeChatPanelVisibility(false)
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.chat-header
  display: flex
  justify-content: space-between
  align-items: center
  padding: 2px 16px
  background-color: var(--color-primary)
  color: white
  position: sticky
  top: 0
  z-index: 10

.header-left
  display: flex
  align-items: center

.header-actions
  display: flex
  align-items: center
  gap: 8px

.header-button
  background: none
  border: none
  color: white
  padding: 4px
  cursor: pointer
  display: flex
  align-items: center
  justify-content: center
  &:hover
    opacity: 0.8

.header-divider
  color: rgba(255, 255, 255, 0.5)
  margin: 0 8px

.custom-control-input
  cursor: pointer

.custom-control-label
  cursor: pointer
  font-size: 14px
  margin-bottom: 0

.custom-control-label::before
  border-color: white !important
  border-width: 1px
  border-style: solid

.custom-control-input:checked ~ .custom-control-label::before
  border-color: white !important
  border-width: 1px
  border-style: solid

.large-icon
  font-size: 24px
</style>
