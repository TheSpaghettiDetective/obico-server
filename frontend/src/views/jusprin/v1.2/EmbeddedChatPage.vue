<template>
  <div>
    <chat-panel-header
      ref="chatHeader"
      @action="callAgentAction"
      :should-popup-chat-panel="Boolean(oauthAccessToken)"
      @show-contact-support-form="showContactSupportForm"
      @show-discord-support-message="showDiscordSupportMessage"
      @show-upgrade-modal="openUpgradeModal"
      :credits-info="creditsInfo"
    />

    <!-- Upgrade Modal -->
    <upgrade-modal
      :show="showUpgradeModal"
      :oauth-access-token="oauthAccessToken"
      @close="closeUpgradeModal"
    />



    <div v-if="oauthAccessToken" class="chat-container mt-3">
      <div ref="chatMessageContainer" class="chat-messages" @scroll="handleChatScroll">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.role"
        >
          <div v-if="message.content" class="message-block">
            <div class="message-content">
              <div v-if="message.has_upgrade_link" class="upgrade-message">
                <div>{{ $t('Since you are on a Free plan, please join our Discord server to seek support from the community.') }}</div>
                <div>
                  <i18next :translation="$t('You can also {localizedDom} to get email support from the Obico team.')">
                    <template #localizedDom>
                      <a href="#" @click.prevent="openUpgradeModal" class="upgrade-link">{{ $t('upgrade to the Unlimited plan') }}</a>
                    </template>
                  </i18next>
                </div>
              </div>
              <VueMarkdown v-else>{{ message.content }}</VueMarkdown>
              <gradient-fadable-container
                v-if="
                  message.per_override_explanations && message.per_override_explanations.length > 0
                "
              >
                <div class="pt-2 pb-1">{{ $t("Detailed explanations:") }}</div>
                <div v-for="(explanation, index) in message.per_override_explanations" :key="index">
                  <div>
                    <b>{{ explanation.parameter }}:</b> {{ explanation.explanation }}
                  </div>
                </div>
              </gradient-fadable-container>
            </div>
          </div>
          <div
            v-if="message.slicing_profiles && slicingSettingsInMessage(message)"
            class="message-block mt-2"
          >
            <div class="message-content">
              <gradient-fadable-container>
                <div class="pt-2 pb-1">{{ $t("I have applied the following settings:") }}</div>
                <div v-if="message.slicing_profiles.use_print_process_preset">
                  {{ $t("- Process preset:") }} <b>{{ message.slicing_profiles.use_print_process_preset }}</b>
                </div>
                <div>
                  {{ $t("- Additional slicing parameters:") }}
                  <b v-if="Object.keys(changedParams(message)).length === 0">{{ $t("None") }}</b>
                  <div v-for="(value, key) in changedParams(message)" :key="key">
                    &nbsp;&nbsp;&nbsp;&nbsp;- {{ key }}:
                    <span class="font-weight-bold">{{ value }}</span>
                  </div>
                </div>
              </gradient-fadable-container>
              <div v-if="index !== messages.length - 1" class="quick-button pt-2">
                <quick-button-component
                  :message="$t('Re-apply settings')"
                  @click="applySettingsInMessage(message)"
                />
              </div>
            </div>
          </div>
          <div v-if="message.suggested_printing_method" class="message-block mt-2">
            <div class="message-content">
              <div class="pt-2 pb-1">{{ $t("I suggest the following to achieve the best results:") }}</div>
              <VueMarkdown>{{ message.suggested_printing_method }}</VueMarkdown>
            </div>
          </div>
          <div v-if="message.jusprinNotification" class="message-block mt-2">
            <div class="message-content">
              <div class="pt-2 pb-1">{{ $t("Oh no! My slicing algorithm lord just said:") }}</div>
              <div class="notification-text" :class="message.jusprinNotification.level">
                <i
                  :class="
                    message.jusprinNotification.level === 'error'
                      ? 'mdi mdi-alert-circle'
                      : 'mdi mdi-alert'
                  "
                ></i>
                {{ message.jusprinNotification.text }}
              </div>
            </div>
          </div>
          <div v-if="message.discord_support" class="message-block mt-2">
            <div class="message-content">
              <div class="discord-support-container">
                <div class="discord-info">
                  <div class="discord-url">
                    <strong>Discord Server:</strong>
                    <code>{{ message.discord_support.url }}</code>
                  </div>
                  <div class="discord-instructions">
                    {{ $t("Scan this QR code with your phone to join our Discord server:") }}
                  </div>
                </div>
                <div class="qr-code-container">
                  <img
                    :src="message.discord_support.qr_code_url"
                    alt="Discord QR Code"
                    class="qr-code"
                    @error="handleQRCodeError"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="thinking" class="message assistant">
          <div class="message-block align-items-center">
            <div class="message-content thinking-animation">
              <VueMarkdown>_{{ $t("Thinking...") }}_</VueMarkdown>
            </div>
          </div>
        </div>
        <contact-support-form
          v-if="showContactSupport"
          :messages="messages"
          :oauth-access-token="oauthAccessToken"
          @form-dismissed="handleContactSupportFormDismissed"
        />
        <div v-if="slicingProgress" class="message assistant">
          <div
            class="message-block slicing-message-block"
            :class="{ 'fade-out': slicingProgress.fadeOut }"
          >
            <div class="message-content">
              <p>
                {{
                  slicingProgress.overrun
                    ? $t('It seems to be taking awfully long to slice. Maybe something went wrong...? You can start over, or continue waiting.')
                    : slicingProgress.text || $t('Slicing in progress...')
                }}
              </p>
              <div class="slicing-progress-container">
                <div
                  class="slicing-progress-bar"
                  :style="{ width: `${slicingProgress?.percentage * 100}%` }"
                ></div>
                <div class="slicing-progress-text">
                  {{ Math.round(slicingProgress?.percentage * 100) }}%
                </div>
              </div>
              <div
                v-if="slicingProgress.errors && slicingProgress.errors.length > 0"
                class="slicing-errors"
              >
                <div
                  v-for="(error, index) in slicingProgress.errors"
                  :key="index"
                  class="error-message"
                >
                  {{ error }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="quickButtons.length > 0" class="quick-button pt-2">
          <quick-button-component
            v-for="(action, index) in quickButtons"
            :key="index"
            :message="action.message"
            @click="action.onClick"
          />
        </div>
      </div>
      <button v-show="showScrollButton" class="scroll-to-bottom" @click="scrollToBottom">
        <i class="mdi mdi-arrow-down large-icon"></i>
      </button>

      <div class="chat-input">
        <textarea
          ref="chatTextarea"
          rows="1"
          v-model="userInput"
          type="text"
          :disabled="!readyForUserQuery"
          :placeholder="
            readyForUserQuery
              ? $t('Type your message here...')
              : $t('Select printer, filament, and add models first')
          "
          @keydown.enter.prevent="handleEnterKey"
        />
        <button class="send-button" :disabled="!readyForUserQuery" @click="onUserInput">
          <i class="mdi mdi-arrow-up send-icon"></i>
        </button>
      </div>
    </div>
    <div v-else>
      <div class="login-container">
        <div>
          <button
            id="signUpSignInBtn"
            class="btn btn-primary"
            @click="() => callAgentAction('show_login')"
          >
            {{ $t("Sign Up/Sign In to Get Started") }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VueMarkdown from 'vue-markdown'
import urls from '@config/server-urls'
import QuickButtonComponent from './components/QuickButtonComponent.vue'
import api from './lib/api'
import QuickButtonsMixin from './mixins/quickButtonsMixin'
import MessagesMixin from './mixins/messagesMixin'
import SlicingParamFixerMixin from './mixins/slicingParamFixerMixin'
import GradientFadableContainer from './components/GradientFadableContainer.vue'
import ChatPanelHeader from './components/ChatPanelHeader.vue'
import userNotificationMixin from './mixins/userNotificationMixin'
import { callAgentAction, getAgentActionResponse, setAgentActionRetVal } from './lib/agentAction'
import ContactSupportForm from './components/ContactSupportForm'
import UpgradeModal from './components/UpgradeModal'

export default {
  name: 'EmbeddedChatPage',
  components: {
    VueMarkdown,
    QuickButtonComponent,
    GradientFadableContainer,
    ChatPanelHeader,
    ContactSupportForm,
    UpgradeModal,
  },
  mixins: [QuickButtonsMixin, MessagesMixin, SlicingParamFixerMixin, userNotificationMixin],
  data() {
    return {
      oauthAccessToken: null,
      currentChatId: null,
      userInput: '',
      thinking: false,
      messages: [],
      modelObjects: [],
      supportedActions: [],
      autoOrientInProgress: false,
      isDevMode: false,
      haveDonePlateAnalysis: false,
      showScrollButton: false,
      slicingProgress: null,
      current_workflow: null,
      showUpgradeModal: false,
      creditsInfo: null, // Will be populated from API responses
      userInfo: null, // Will be populated from /jusprin/api/me/
    }
  },
  computed: {
    readyForUserQuery() {
      if (this.slicingProgress || this.thinking) {
        return false
      }
      return true
    },
    readyToSlice() {
      return this.messages.some(
        (message) => message.role === 'assistant' && this.slicingSettingsInMessage(message)
      )
    },
    hasModelObjects() {
      return this.modelObjects.length > 0
    },
    showContactSupport() {
      // Check if any message has a contact_support agent action using higher-order function
      return this.messages.some(
        (message) =>
          message.role === 'assistant' &&
          message.agent_actions?.some((action) => action.name === 'contact_support')
      )
    },
  },
  watch: {
    messages: 'onChatContentChanged',
    quickButtons: 'onChatContentChanged',
    userInput() {
      this.$nextTick(() => {
        this.adjustTextareaHeight()
      })
    },
    oauthAccessToken(newValue, oldValue) {
      // When token becomes available (changes from null to non-null), fetch user data
      if (newValue && !oldValue) {
        this.fetchUserData()
      }
    },
  },
  created() {
    const urlParams = new URLSearchParams(window.location.search)
    this.isDevMode = urlParams.get('devmode') === 'true'
  },
  mounted() {
    this.initMessagesAndQuickButtons()
  },
  methods: {
    callAgentAction,
    setAgentActionRetVal, // For JusPrin CallEmbeddedChatMethod
    async fetchUserData() {
      if (!this.oauthAccessToken) {
        return
      }
      const response = await api.get(urls.jusprinMe(), this.oauthAccessToken)
      this.userInfo = response.data.user
      this.creditsInfo = response.data.ai_credits
    },
    async withCreditCheck(apiCall) {
      // Check if balance is 0 before making the call
      if (this.creditsInfo && this.creditsInfo.ai_credit_free_monthly_quota !== -1) {
        const remainingCredits = Math.max(0, this.creditsInfo.ai_credit_free_monthly_quota - (this.creditsInfo.ai_credit_used_current_month || 0))
        if (remainingCredits <= 0) {
          this.openUpgradeModal()
          return {
            data: {
              message: {
                role: 'assistant',
                content: this.$t("You're on a free plan and your account has run out of AI credits.")
              }
            }
          }
        }
      }

      try {
        const result = await apiCall()

        // Refresh user data after successful call
        await this.fetchUserData()

        return result
      } catch (error) {
        // Catch 402 errors and show UpgradeModal
        if (error.response && error.response.status === 402) {
          this.openUpgradeModal()
          return {
            data: {
              message: {
                role: 'assistant',
                content: this.$t("You're on a free plan and your account has run out of AI credits.")
              }
            }
          }
        }

        // Let all other errors bubble up to Sentry
        throw error
      }
    },
    async callLongRunningAgentActionThenRefreshPresets(action, payload = null) {
      await getAgentActionResponse(action, payload, 1000 * 60 * 60 * 24) // Make timeout super long as it's hard to know how long it takes user to finish things like adding a printer
      this.refreshSelectedPresets(false)
      this.populateQuickButtons()
    },
    processAgentEvent(event) {
      if (event.type === 'modelObjectsChanged') {
        this.processModelObjectsChangedEvent(event)
      } else if (event.type === 'autoOrient') {
        this.processAutoOrientEvent(event)
      } else if (event.type === 'nativeErrorOccurred') {
        this.processNativeErrorOccurredEvent(event)
      } else if (event.type === 'notificationPushed') {
        this.processNotificationPushedEvent(event)
      } else if (event.type === 'chatPanelFocus') {
        this.$refs.chatHeader.processChatPanelFocusEvent(event)
      } else if (event.type === 'slicingProgress') {
        this.processSlicingProgressEvent(event)
      }
    },

    editedPreset(presetType, editedPresets = {}) {
      return editedPresets[
        `edited${presetType.charAt(0).toUpperCase() + presetType.slice(1)}Preset`
      ]
    },

    overridesFromEditedPreset(presetType, editedPresets = {}) {
      const editedPreset = this.editedPreset(presetType, editedPresets)
      const { config, dirty_options } = editedPreset

      if (!dirty_options || dirty_options.length === 0) {
        return {}
      }

      const overrides = {}
      dirty_options.forEach((option) => {
        if (Object.prototype.hasOwnProperty.call(config, option)) {
          overrides[option] = config[option]
        }
      })

      return overrides
    },

    selectedPreset(presetType, presets) {
      return presets[`${presetType}Presets`]?.find((preset) => preset.is_selected) || null
    },

    slicingSettingsInMessage(message) {
      return (
        message.slicing_profiles?.use_print_process_preset ||
        message.slicing_profiles?.filament_overrides ||
        message.slicing_profiles?.print_process_overrides
      )
    },

    async onUserQueryQuickButton(msg) {
      this.messages.push({ role: 'user', content: msg })
      await this.sendUserQuery()
    },

    async onUserInput() {
      if (this.userInput.trim()) {
        this.clearQuickButtons()
        this.messages.push({ role: 'user', content: this.userInput })
        this.userInput = ''
        // Reset textarea height to one line after clearing input
        const textarea = this.$refs.chatTextarea
        if (textarea) {
          textarea.style.height = 'auto'
        }
        await this.sendUserQuery()
      }
    },
    startOver() {
      this.slicingProgress = null
      this.processedNotifications = new Set()
      this.current_workflow = null
      this.initMessagesAndQuickButtons()
    },

    async sendUserQuery() {
      this.thinking = true
      this.clearQuickButtons()

      try {
        const presets = await getAgentActionResponse('get_presets')
        const editedPresets = await getAgentActionResponse('get_edited_presets')
        const currentProject = await getAgentActionResponse('get_current_project')
        const plates = currentProject.plates
        if (!this.userQueryPreconditionsMet(presets, editedPresets, plates)) {
          this.thinking = false
          return
        }

        // TODO: It's an important assumption that selected preset should be the same as edited preset
        // Remove this check once it's in production for a while with no messages captured in sentry
        for (const preset_type of ['filament', 'printProcess', 'printer']) {
          if (
            this.editedPreset(preset_type, editedPresets)?.name !==
            this.selectedPreset(preset_type, presets)?.name
          ) {
            window.Sentry?.captureMessage(
              `Selected preset ${preset_type} is not the same as edited preset ${
                this.editedPreset(preset_type, editedPresets)?.name
              }`
            )
          }
        }

        const currentChatId = await this.getCurrentChatId()
        const response = await this.withCreditCheck(async () => {
          return api.post(urls.jusprinChatMessages(), this.oauthAccessToken, {
            messages: this.messages,
            current_workflow: this.current_workflow,
            slicing_profiles: {
              filament_presets: [this.selectedPreset('filament', presets)],
              print_process_presets: presets.printProcessPresets,
              filament_overrides: this.overridesFromEditedPreset('filament', editedPresets),
              print_process_overrides: this.overridesFromEditedPreset('printProcess', editedPresets),
            },
            plates: plates,
            chat_id: currentChatId,
          })
        })
        this.thinking = false

        this.processChatResponse(response.data, presets)
      } catch (error) {
        window.Sentry?.captureException(error)
        this.thinking = false
        this.messages.push(this.cannedMessages.generalError)
        this.populateQuickButtonsOnError()
      }
    },

    async getCurrentChatId() {
      if (!this.currentChatId) {
        const chatsApiUrl = urls.jusprinChats(this.currentChatId)
        const newChatResponse = await api['post'](chatsApiUrl, this.oauthAccessToken, {
          messages: JSON.stringify(this.messages),
        })
        this.currentChatId = newChatResponse?.data?.id // Assign the new chat ID
      }
      return this.currentChatId
    },

    async processChatResponse(responseData, presets) {
      const message = responseData.message
      this.messages.push(message)

      const payload = {
        messages: JSON.stringify(this.messages),
        machine_name: this.selectedPreset('printer', presets)?.name,
        filament_name: this.selectedPreset('filament', presets)?.name,
        print_process_name: this.selectedPreset('printProcess', presets)?.name,
      }
      this.populateDatabaseWithChat(payload)

      if (this.slicingSettingsInMessage(message)) {
        this.applySettingsInMessage(message)
      }

      if (message.agent_actions?.length) {
        await this.processAgentActions(message)
      } else {
        this.populateQuickButtons() // If there are no agent actions, we can populate default quick buttons
      }
    },

    async populateDatabaseWithChat(payload = null) {
      const currentChatId = await this.getCurrentChatId()
      const chatsApiUrl = urls.jusprinChats(currentChatId)
      const chatsApiVerb = currentChatId ? 'put' : 'post'
      await api[chatsApiVerb](chatsApiUrl, this.oauthAccessToken, payload)
    },

    async processAgentActions(message) {
      if (!message.agent_actions?.length) return
      this.clearQuickButtons()

      for (const action of message.agent_actions) {
        if (action.name === 'slice_model') {
          await this.doSliceWithCurrentSettings()
        } else if (action.name === 'start_chat_over') {
          await this.startOver()
        } else if (action.name === 'add_printers') {
          await this.callLongRunningAgentActionThenRefreshPresets('add_printers')
        } else if (action.name === 'add_filaments') {
          await this.callLongRunningAgentActionThenRefreshPresets('add_filaments')
        } else if (action.name === 'change_printer') {
          await this.showPresetOptions('printer')
        } else if (action.name === 'change_filament') {
          await this.showPresetOptions('filament')
        } else if (action.name === 'contact_support') {
          this.scrollToBottom()
        } else if (action.name === 'auto_orient_all_models') {
          await this.autoOrientAllObjects()
        } else if (action.name === 'auto_arrange_all_models') {
          await this.autoArrangeAllObjects()
        } else if (action.name === 'set_print_troubleshooting_flow') {
          this.current_workflow = 'print_troubleshooting'
        } else if (action.name === 'confirm_print_troubleshooting_flow') {
          this.confirmPrintTroubleshootingFlow()
        } else if (action.name === 'confirm_end_troubleshooting') {
          this.confirmEndTroubleshooting()
        } else if (action.name === 'ask_user_to_choose_from_options') {
          this.showOptionsAsQuickButtons(action.arguments)
        }
      }

      this.populatePrintTroubleshootingQuickButtonsIfNeeded()
    },

    async applySettingsInMessage(message) {
      if (!this.slicingSettingsInMessage(message)) {
        // If LLM didn't select a preset, it didn't know how to process the query. Nothing should be assumed in this case.
        return
      }

      this.clearQuickButtons()

      try {
        if (message.slicing_profiles.use_print_process_preset) {
          await getAgentActionResponse('select_preset', {
            type: 'print',
            name: message.slicing_profiles.use_print_process_preset,
          })
        }

        let filamentOverrides = message.slicing_profiles?.filament_overrides || {}
        filamentOverrides = this.fixFilamentParamOverrides(filamentOverrides)

        let param_overrides = [
          ...this.paramOverridesToApplyConfigPayload(filamentOverrides, 'filament'),
          ...this.paramOverridesToApplyConfigPayload(
            message.slicing_profiles?.print_process_overrides || {},
            'print'
          ),
        ]

        if (param_overrides.length > 0) {
          await getAgentActionResponse('apply_config', param_overrides)
        }
      } catch (error) {
        window.Sentry?.captureException(error)
        this.messages.push(this.cannedMessages.generalError)
        this.populateQuickButtonsOnError()
        return
      }
    },
    async doSliceWithCurrentSettings() {
      const currentProject = await getAgentActionResponse('get_current_project')
      const plates = currentProject.plates
      const hasModels = plates.some((plate) => plate.model_objects?.length > 0)
      if (!hasModels) {
        this.messages.push(this.cannedMessages.noModelObjects)
        this.setQuickButtons([this.cannedActions.startOver, this.cannedActions.moreOptions])
        return
      }

      if (!this.readyToSlice) {
        const presets = await getAgentActionResponse('get_presets')
        this.messages.push({
          role: 'assistant',
          content: `${this.$t("I have not set any slicing parameters for you. Do you want me to slice your model with these?")}\n${this.$t("- Filament:")} **${
            this.selectedPreset('filament', presets)?.name
          }**\n${this.$t("- Process preset:")} **${this.selectedPreset('printProcess', presets)?.name}**`,
        })

        this.pushQuickButtons([
          {
            message: this.$t('Yes'),
            onClick: () => this.doSlice(),
          },
          {
            message: this.$t('No'),
            onClick: () => this.popQuickButtons(),
          },
        ])
        return
      } else {
        this.doSlice()
      }
    },
    async doSlice() {
      this.clearQuickButtons()
      this.slicingProgress = { percentage: 0, errors: [] }
      callAgentAction('start_slicer_all')

      setTimeout(() => {
        if (this.slicingProgress && this.slicingProgress.percentage < 1.0 - 1e-6) {
          this.slicingProgress.overrun = true
          this.setQuickButtons([this.cannedActions.startOver])
        }
      }, 1000 * 60 * 2)
    },
    async autoOrientAllObjects() {
      let agentActionName = 'auto_orient_all_objects'

      // TODO: Remove this once 0.4 is no longer supported
      if (this.supportedActions.includes('auto_orient_object')) {
        agentActionName = 'auto_orient_object'
      }

      callAgentAction(agentActionName, {})
      this.autoOrientInProgress = true
      this.populateQuickButtons()
    },
    async autoArrangeAllObjects() {
      setTimeout(() => {
        callAgentAction('arrange_all_objects', {})
        this.autoArrangeInProgress = true
      }, 100)
      this.messages.push({
        role: 'assistant',
        content: this.$t('Models auto-arranged.'),
      })
      this.populateQuickButtons()
      this.setQuickButtons([this.cannedActions.undoAutoArrange, ...this.quickButtons])
    },
    changedParams(message) {
      return {
        ...(message.slicing_profiles?.filament_overrides ?? {}),
        ...(message.slicing_profiles?.print_process_overrides ?? {}),
      }
    },
    initMessagesAndQuickButtons() {
      this.currentChatId = null

      // Reset messages and quick actions
      this.messages = [this.cannedMessages.greeting]
      setTimeout(async () => {
        await this.refreshSelectedPresets(true)
        await this.refreshModelObjects()
        this.populateQuickButtons()
      }, 10)
    },

    async refreshModelObjects() {
      const project = await getAgentActionResponse('get_current_project')
      this.modelObjects = this.distinctModelObjectsInProject(project)
      if (this.modelObjects.length > 0) {
        this.messages.push(this.cannedMessages.currentModelObjects(this.modelObjects.length))
      } else {
        this.messages.push(this.cannedMessages.noModelObjects)
      }
    },
    async refreshSelectedPresets(isFirstTime = false) {
      const presets = await getAgentActionResponse('get_presets')
      this.messages.push(
        this.cannedMessages.currentPresetSelections(
          this.selectedPreset('printer', presets)?.name,
          this.selectedPreset('filament', presets)?.name,
          isFirstTime
        )
      )
    },
    fixBrokenMarkdown(text) {
      // Markdown returned from LLM may be broken.
      const formattedText = text.replace(/ (\d\.) /g, '\n$1 ')
      return formattedText
    },
    scrollToBottom() {
      const chatMessageContainer = this.$refs.chatMessageContainer
      if (chatMessageContainer) {
        chatMessageContainer.scrollTop = chatMessageContainer.scrollHeight
      }
    },
    onChatContentChanged() {
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    paramOverridesToApplyConfigPayload(params, type) {
      const param_overrides = []
      for (const [key, value] of Object.entries(params)) {
        param_overrides.push({ type, key, value })
      }
      return param_overrides
    },
    userQueryPreconditionsMet(presets, editedPresets, plates) {
      if (
        (presets?.printerPresets && presets.printerPresets?.length < 1) ||
        presets.printerPresets?.every((preset) => preset.is_default)
      ) {
        this.messages.push(this.cannedMessages.needToAddPrinters)
        this.setQuickButtons([this.cannedActions.addPrinters])
        return false
      } else if (
        (presets?.filamentPresets && presets.filamentPresets?.length < 1) ||
        presets.filamentPresets?.every((preset) => preset.is_default)
      ) {
        this.messages.push(this.cannedMessages.needToAddFilaments)
        this.setQuickButtons([this.cannedActions.addFilaments])
        return false
      }
      return true
    },

    modelObjectsWithOverhang(modelObjects) {
      return modelObjects.filter((obj) => (obj.features?.overhang ?? 0) > 0.001)
    },

    distinctModelObjectsInProject(project) {
      return project.plates
        .flatMap((plate) => plate.model_objects)
        .reduce((unique, obj) => {
          const exists = unique.find((item) => item.id === obj.id)
          return exists ? unique : [...unique, obj]
        }, [])
    },

    processModelObjectsChangedEvent(event) {
      const currentProject = event.data
      const currentModelObjects = this.distinctModelObjectsInProject(currentProject)
      const newModelObjects = currentModelObjects.filter(
        (obj) => !this.modelObjects.some((item) => item.id === obj.id)
      )
      this.modelObjects = currentModelObjects
      if (newModelObjects.length > 0) {
        this.messages.push(this.cannedMessages.newModelObjects(newModelObjects))
        this.$refs.chatHeader.popupChatPanelIfNecessary()
        if (this.modelObjectsWithOverhang(currentModelObjects).length > 0) {
          this.messages.push({
            role: 'assistant',
            content:
              this.$t('I notice some of your models have overhangs. I can try to auto-orient them to minimize the need for supports.'),
          })
        }
        const quickButtons = [this.cannedActions.autoOrient, this.cannedActions.enableSupport]
        if (this.shouldShowPlateAnalysisQuickButton) {
          quickButtons.push(this.cannedActions.analyseModel)
        }
        this.setQuickButtons([
          ...quickButtons,
          this.cannedActions.commonPrintingPrompts,
          this.cannedActions.moreOptions,
        ])
        return
      }

      this.populateQuickButtons()
    },
    processAutoOrientEvent(event) {
      const currentProject = event.data?.currentProject
      const currentModelObjects = this.distinctModelObjectsInProject(currentProject)
      this.modelObjects = currentModelObjects

      if (!this.autoOrientInProgress) {
        return
      }

      this.autoOrientInProgress = false
      if (event.data?.status === 'completed') {
        let msg = this.$t('Models auto-oriented.')
        let quickButtons = [this.cannedActions.undoAutoOrient]
        if (this.modelObjectsWithOverhang(currentModelObjects).length > 0) {
          msg +=
            ` ${this.$t('However, some models still have overhangs. I recommend enabling support to make sure they can be printed successfully.')}`
          quickButtons.push(this.cannedActions.enableSupport)
        }

        this.messages.push({
          role: 'assistant',
          content: msg,
        })
        this.removeQuickButtons([
          this.cannedActions.autoOrient,
          this.cannedActions.enableSupport,
          this.cannedActions.undoAutoOrient,
        ])
        this.setQuickButtons([...quickButtons, ...this.quickButtons])
      }
    },
    processNativeErrorOccurredEvent(event) {
      window.Sentry?.captureMessage(event.data?.errorMessage, 'error')
    },
    processSlicingProgressEvent(event) {
      if (!this.slicingProgress) {
        return
      }

      const percentage = event.data?.percentage
      if (percentage !== undefined) {
        this.slicingProgress.percentage = percentage
        this.slicingProgress.text = event.data?.text
      }

      if (percentage && percentage < 1.0 - 1e-6) {
        return
      }

      // Add fade-out class first
      this.slicingProgress.fadeOut = true

      // Remove the progress bar after fade out animation completes
      setTimeout(() => {
        const quickButtons = [this.cannedActions.startOver, this.cannedActions.moreOptions]

        if (this.slicingProgress.errors && this.slicingProgress.errors.length > 0) {
          this.messages.push({
            role: 'assistant',
            content: `${this.$t("My slicing algorithm lord just said:")}\n *"${this.slicingProgress.errors.join(
              '\n'
            )}"*`,
          })
          quickButtons.unshift(this.cannedActions.tellMeWhatNotificationMeans)
        } else {
          if (this.supportedActions.includes('switch_to_preview')) {
            quickButtons.unshift(this.cannedActions.switchToPreview)
          }
          quickButtons.unshift(this.cannedActions.exportGCode)
        }

        this.setQuickButtons(quickButtons)

        this.slicingProgress = null
      }, 2000) // Match the transition duration in CSS
    },

    async callPlateAnalysis() {
      const project = await getAgentActionResponse('get_current_project')
      const plates = project.plates
      const images = await this.renderPlateForAnalysis()
      const currentChatId = await this.getCurrentChatId()

      const payload = {
        images: images,
        plates: plates,
        chat_id: currentChatId,
      }

      const response = await this.withCreditCheck(async () => {
        return api.post(
          urls.jusprinPlateAnalysisProcess(),
          this.oauthAccessToken,
          payload
        )
      })

      // Handle credit response structure - if it's a credit message, restructure it for processAnalysisResponse
      if (response.data && response.data.message && response.data.message.role === 'assistant') {
        return { message: response.data.message }
      }

      return response.data
    },

    async renderPlateForAnalysis() {
      // This function now only fetches and renders the plate images,
      // then returns an array of base64 image strings.
      const cameraPositionByDegrees = (target, xyPlaneAngle, zPlaneAngle) => {
        const distanceFromTarget = 1000 // OrcaSlicer default
        const xyPlaneAngleRadians = xyPlaneAngle * (Math.PI / 180)
        const zPlaneAngleRadians = zPlaneAngle * (Math.PI / 180)
        return {
          x: target.x + distanceFromTarget * Math.sin(xyPlaneAngleRadians),
          y: target.y - distanceFromTarget * Math.cos(xyPlaneAngleRadians),
          z: target.z + distanceFromTarget * Math.sin(zPlaneAngleRadians),
        }
      }

      const currentProject = await getAgentActionResponse('get_current_project')
      const plates = currentProject.plates
      if (plates.length === 0) {
        return []
      }

      const { index, bounding_box, model_objects } = plates[0]
      if (!model_objects || model_objects.length === 0) {
        return []
      }

      const target = {
        x: (bounding_box.max.x + bounding_box.min.x) / 2,
        y: (bounding_box.max.y + bounding_box.min.y) / 2,
        z: 0,
      }

      const views = [
        { camera_position: cameraPositionByDegrees(target, 0, 45), target: target },
        { camera_position: cameraPositionByDegrees(target, -30, 45), target: target },
        { camera_position: cameraPositionByDegrees(target, -210, 45), target: target },
        { camera_position: cameraPositionByDegrees(target, 0, -45), target: target },
      ]

      const renderResult = await getAgentActionResponse('render_plate', {
        plate_index: index,
        views: views,
      })

      // Build an array of all images from renderResult and return it.
      const images = renderResult.filter((result) => result.base64).map((result) => result.base64)

      return images
    },

    async getAnalysisResult() {
      this.thinking = true
      this.clearQuickButtons()

      try {
        const analysisResponse = await this.callPlateAnalysis()
        await this.processAnalysisResponse(analysisResponse)
      } catch (error) {
        window.Sentry?.captureException(error)
        this.thinking = false
        this.messages.push(this.cannedMessages.generalError)
        this.populateQuickButtonsOnError()
      }
    },

    async processAnalysisResponse(response) {
      this.messages.push(response.message)
      this.thinking = false

      const payload = {
        messages: JSON.stringify(this.messages),
      }
      this.populateDatabaseWithChat(payload)

      if (response.message.suggested_printing_method) {
        this.pushQuickButtons([
          this.cannedActions.plateAnalysisLooksGoodToMe,
          this.cannedActions.plateAnalysisIsNotGood,
          this.cannedActions.editPlateAnalysis,
          this.cannedActions.moreOptions,
        ])
      } else {
        this.populateQuickButtons()
      }

      return
    },

    ensurePlateAnalysisMessageExists() {
      const lastMessage = this.messages[this.messages.length - 1]
      if (!lastMessage?.suggested_printing_method) {
        this.messages.push(this.cannedMessages.generalError)
        this.populateQuickButtonsOnError()
        return false
      }
      return true
    },

    async queryWithSuggestedPrintingMethod() {
      this.clearQuickButtons()
      if (!this.ensurePlateAnalysisMessageExists()) {
        return
      }

      const lastMessage = this.messages[this.messages.length - 1]
      this.messages.push({
        role: 'user',
        content: `${this.$t("Please set the slicing settings based on the suggested strategy:")}\n\n${lastMessage.suggested_printing_method}`,
      })
      this.sendUserQuery()
    },

    removePlateAnalysis() {
      if (!this.ensurePlateAnalysisMessageExists()) {
        return
      }

      this.messages.pop()
      this.popQuickButtons()
      this.populateQuickButtons()
    },

    editPlateAnalysis() {
      if (!this.ensurePlateAnalysisMessageExists()) {
        return
      }

      const plateAnalysisMessage = this.messages.pop()
      this.clearQuickButtons()
      this.userInput = `${this.$t("Please set the slicing settings based on the suggested strategy:")}\n\n${plateAnalysisMessage.suggested_printing_method}`
    },

    handleChatScroll() {
      const chatMessageContainer = this.$refs.chatMessageContainer
      const atBottom =
        chatMessageContainer.scrollHeight - chatMessageContainer.scrollTop <=
        chatMessageContainer.clientHeight
      this.showScrollButton = !atBottom
    },
    adjustTextareaHeight() {
      const textarea = this.$refs.chatTextarea
      const chatMessages = this.$refs.chatMessageContainer
      if (!textarea || !chatMessages) return

      // Reset height to auto to get correct scrollHeight
      textarea.style.height = 'auto'
      // Set new height based on scrollHeight, with max of 150px
      const newHeight = Math.min(textarea.scrollHeight, 150)
      textarea.style.height = newHeight + 'px'

      // Update chat messages padding to match input height plus padding
      const chatInput = textarea.closest('.chat-input')
      if (chatInput) {
        const inputTotalHeight = chatInput.offsetHeight
        chatMessages.style.paddingBottom = `${inputTotalHeight + 8}px`
      }
    },
    handleEnterKey(e) {
      if (e.shiftKey || e.metaKey || e.ctrlKey || e.altKey) {
        this.userInput += '\n'
        return
      }
      this.onUserInput()
    },
    handleContactSupportFormDismissed(data) {
      // Find the index of the message with contact_support agent action
      const supportMsgIndex = this.messages.findIndex(
        (message) =>
          message.role === 'assistant' &&
          message.agent_actions?.some(action => action.name === 'contact_support')
      )

      // Remove the message if found
      if (supportMsgIndex !== -1) {
        this.messages.splice(supportMsgIndex, 1)
      }

      // Add new assistant message with the response
      this.messages.push({
        role: 'assistant',
        content: data.message,
      })

      this.populateQuickButtons()
      this.scrollToBottom()
    },
    showContactSupportForm() {
      this.clearQuickButtons()
      this.messages.push({
        role: 'assistant',
        content: null,
        agent_actions: [{ name: 'contact_support', arguments: {} }],
      })
      this.scrollToBottom()
    },
    showDiscordSupportMessage() {
      this.clearQuickButtons()
      this.messages.push({
        role: 'assistant',
        content: this.$t('Since you are on a Free plan, please join our Discord server to seek support from the community. You can also upgrade to the Unlimited plan to get email support from the Obico team.'),
        discord_support: {
          url: 'https://discord.gg/Tx67dHNYH3',
          qr_code_url: 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https%3A%2F%2Fdiscord.gg%2FTx67dHNYH3'
        },
        has_upgrade_link: true
      })
      this.setQuickButtons([this.cannedActions.moreOptions])
      this.scrollToBottom()
    },

    // Methods for handling the print troubleshooting flow
    populatePrintTroubleshootingQuickButtonsIfNeeded() {
      if (this.current_workflow === 'print_troubleshooting') {
        // Check if the last message contains slicing settings
        const lastMessage = this.messages[this.messages.length - 1]
        if (lastMessage && this.slicingSettingsInMessage(lastMessage)) {
          this.removeQuickButtons([this.cannedActions.sliceWithCurrentSettings])
          this.setQuickButtons([this.cannedActions.sliceWithCurrentSettings, ...this.quickButtons])
        }

        this.removeQuickButtons([this.cannedActions.endTroubleshooting])
        this.setQuickButtons([...this.quickButtons, this.cannedActions.endTroubleshooting])
      }
    },
    confirmPrintTroubleshootingFlow() {
      const startTroubleshootingMsg = this.$t('Troubleshoot settings in current project')
      const startTroubleshootingOtherProjectMsg = this.$t('Troubleshoot settings in other project')
      const startTroubleshootingFromGCodeMsg = this.$t('Troubleshoot settings from G-Code file')
      const dontWantTroubleshootingMsg = this.$t("I don't want troubleshooting")
      this.setQuickButtons([
        {
          message: startTroubleshootingMsg,
          onClick: () => {
            this.current_workflow = 'print_troubleshooting'
            this.onUserQueryQuickButton(startTroubleshootingMsg)
          },
        },
        {
          message: startTroubleshootingOtherProjectMsg,
          onClick: () => {
            this.messages.push({
              role: 'assistant',
              content:
                this.$t('Please close this project and open the project for the print that you want to troubleshoot.'),
            })
          },
        },
        {
          message: startTroubleshootingFromGCodeMsg,
          onClick: () => {
            this.messages.push({
              role: 'user',
              content: this.$t('I want to do troubleshooting from a G-Code file.'),
            })
            this.messages.push({
              role: 'assistant',
              content:
                this.$t('Go to the [3D Printing AI Tools](https://www.3dp-ai.tools/troubleshooting) website to troubleshoot your G-Code file.'),
            })
          },
        },
        {
          message: dontWantTroubleshootingMsg,
          onClick: () => this.onUserQueryQuickButton(dontWantTroubleshootingMsg),
        },
      ])
    },
    showOptionsAsQuickButtons(args) {
      const options = args?.user_options_to_choose_from || []
      if (!options || !Array.isArray(options)) return

      const newQuickButtons = options.map((option) => ({
        message: option,
        onClick: () => this.onUserQueryQuickButton(option),
      }))

      // Remove any existing buttons with the same messages
      this.removeQuickButtons(newQuickButtons)

      // Add the new buttons to the existing ones
      this.pushQuickButtons([...this.quickButtons, ...newQuickButtons])
    },
    confirmEndTroubleshooting() {
      this.setQuickButtons([
        this.cannedActions.endTroubleshooting,
        this.cannedActions.stayInTroubleshooting,
      ])
    },
    // End of methods for handling the print troubleshooting flow

    // Modal methods
    openUpgradeModal() {
      this.showUpgradeModal = true
    },
    closeUpgradeModal() {
      this.showUpgradeModal = false
    },
    handleQRCodeError(event) {
      // Hide the QR code if it fails to load
      event.target.style.display = 'none'
      console.warn('Failed to load QR code for Discord support')
    },
  },
}
</script>

<style lang="sass" scoped>
@import './styles/EmbeddedChatPage'
</style>
