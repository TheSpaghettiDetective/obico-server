import { callAgentAction, getAgentActionResponse } from '../lib/agentAction'
import i18next from '@src/i18n/i18n.js'

export default {
  data() {
    return {
      quickButtonsStack: [],
    }
  },
  computed: {
    quickButtons() {
      return this.quickButtonsStack[this.quickButtonsStack.length - 1] || []
    },
    cannedActions() {
      return {
        addPrinters: {
          message: this.$i18next.t('Add printer'),
          onClick: () => {
            this.popQuickButtons()
            this.callLongRunningAgentActionThenRefreshPresets('add_printers')
          },
        },
        addFilaments: {
          message: this.$i18next.t('Add filament'),
          onClick: () => {
            this.popQuickButtons()
            this.callLongRunningAgentActionThenRefreshPresets('add_filaments')
          },
        },
        changePrinter: {
          message: this.$i18next.t('Change printer'),
          onClick: () => this.showPresetOptions('printer'),
        },
        changeFilament: {
          message: this.$i18next.t('Change filament'),
          onClick: () => this.showPresetOptions('filament'),
        },
        moreOptions: {
          message: this.$i18next.t('More options'),
          onClick: () => this.showMoreOptions(),
        },
        cancel: {
          message: this.$i18next.t('Cancel'),
          onClick: () => this.popQuickButtons(),
        },
        sliceWithCurrentSettings: {
          message: this.$i18next.t('Slice with current settings'),
          onClick: () => this.doSliceWithCurrentSettings(),
        },
        endTroubleshooting: {
          message: this.$i18next.t('End troubleshooting'),
          onClick: () => {
            this.current_workflow = null
            this.onUserQueryQuickButton(this.$i18next.t('I want to end troubleshooting'))
          },
        },
        stayInTroubleshooting: {
          message: this.$i18next.t('Stay in troubleshooting'),
          onClick: () => {
            this.onUserQueryQuickButton(this.$i18next.t('I want to continue troubleshooting'))
          },
        },
        startOver: {
          message: this.$i18next.t('Start over'),
          onClick: () => this.startOver(),
        },
        exportGCode: {
          message: this.$i18next.t('Export G-code'),
          onClick: () => this.callAgentAction('export_gcode'),
        },
        switchToPreview: {
          message: this.$i18next.t('Switch to preview'),
          onClick: () => this.callAgentAction('switch_to_preview'),
        },
        autoOrient: {
          message: this.$i18next.t('Auto-orient models'),
          onClick: () => {
            this.autoOrientAllObjects()
          },
        },
        undoAutoOrient: {
          message: this.$i18next.t('Undo auto-orient'),
          onClick: () => {
            callAgentAction('plater_undo')
            this.messages.push({
              role: 'assistant',
              content: this.$i18next.t('Got it! Auto-orient is undone.'),
            })
            this.removeQuickButtons([this.cannedActions.undoAutoOrient])
          },
        },
        undoAutoArrange: {
          message: this.$i18next.t('Undo auto-arrange'),
          onClick: () => {
            callAgentAction('plater_undo')
            this.messages.push({
              role: 'assistant',
              content: this.$i18next.t('Got it! Auto-arrange is undone.'),
            })
            this.removeQuickButtons([this.cannedActions.undoAutoArrange])
          },
        },
        enableSupport: {
          message: this.$i18next.t('Enable support'),
          onClick: async () => {
            await getAgentActionResponse(
              'apply_config',
              this.paramOverridesToApplyConfigPayload({ enable_support: '1' }, 'print')
            )
            this.messages.push({
              role: 'assistant',
              content: this.$i18next.t('Support enabled.'),
            })
            this.removeQuickButtons([this.cannedActions.enableSupport])
            this.setQuickButtons([this.cannedActions.undoEnableSupport, ...this.quickButtons])
          },
        },
        undoEnableSupport: {
          message: this.$i18next.t('Undo enable support'),
          onClick: async () => {
            await getAgentActionResponse(
              'apply_config',
              this.paramOverridesToApplyConfigPayload({ enable_support: '0' }, 'print')
            )
            this.messages.push({
              role: 'assistant',
              content: this.$i18next.t('Got it! Support is now disabled.'),
            })
            this.removeQuickButtons([this.cannedActions.undoEnableSupport])
          },
        },
        tellMeWhatNotificationMeans: {
          message: this.$i18next.t('Explain it to me'),
          onClick: () => {
            // Find the last assistant message that contains a notification
            const lastErrorMessage = [...this.messages]
              .reverse()
              .find((msg) => msg.role === 'assistant' && msg.jusprinNotification)

            // Get the original error message if found
            let originalErrorMessage = ''
            if (lastErrorMessage && lastErrorMessage.jusprinNotification) {
              originalErrorMessage = lastErrorMessage.jusprinNotification.text
            }

            // Format the new message
            const newMessage = this.$i18next.t('JusPrin displays this message: *"{originalErrorMessage}"* Explain it to me.', {
              originalErrorMessage
            })

            // Send the message
            this.onUserQueryQuickButton(newMessage)
          },
        },
        acknowledgeError: {
          message: this.$i18next.t('Okay'),
          onClick: () => {
            this.messages.pop()
            this.popQuickButtons()
          },
        },
        commonPrintingPrompts: {
          message: this.$i18next.t('Common printing prompts'),
          onClick: () => this.showCommonPrintingPrompts(),
        },
        testRender: {
          message: this.$i18next.t('Test render'),
          onClick: () => this.renderPlateForAnalysis(),
        },
        analyseModel: {
          message: this.$i18next.t('✨ Do your magic!'),
          onClick: () => this.getAnalysisResult(),
        },
        plateAnalysisLooksGoodToMe: {
          message: this.$i18next.t('Looks good to me'),
          onClick: () => this.queryWithSuggestedPrintingMethod(),
        },
        plateAnalysisIsNotGood: {
          message: this.$i18next.t('You got it wrong. Scratch that.'),
          onClick: () => this.removePlateAnalysis(),
        },
        editPlateAnalysis: {
          message: this.$i18next.t('Let me change it'),
          onClick: () => this.editPlateAnalysis(),
        },
      }
    },
    shouldShowSliceWithCurrentSettingsQuickButton() {
      const lastMessage = this.messages[this.messages.length - 1]
      return lastMessage && this.slicingSettingsInMessage(lastMessage)
    },
    shouldShowStartOverQuickButton() {
      return this.messages.some((message) => message.role === 'user')
    },
    shouldShowPlateAnalysisQuickButton() {
      return !this.haveDonePlateAnalysis && this.hasModelObjects
    },
  },
  methods: {
    pushQuickButtons(actions) {
      this.quickButtonsStack.push(actions)
    },
    popQuickButtons() {
      this.quickButtonsStack.pop()
    },
    removeQuickButtons(actions) {
      const actionMessages = actions.map((action) => action.message)
      let topActions = this.quickButtonsStack[this.quickButtonsStack.length - 1] || []
      topActions = topActions.filter((action) => !actionMessages.includes(action.message))
      this.$set(this.quickButtonsStack, this.quickButtonsStack.length - 1, topActions)
    },
    clearQuickButtons() {
      this.quickButtonsStack = []
    },
    setQuickButtons(actions) {
      this.clearQuickButtons()
      this.pushQuickButtons(actions)
    },
    initUserQueryHintButtons() {
      const initQueryHints = [
        this.$i18next.t('Just do a standard print. Nothing special.'),
        this.$i18next.t('I want to do a fast print. Draft quality.'),
        this.$i18next.t('Print a strong part.'),
        this.$i18next.t('My last print did not stick to the bed. Help me fix it.'),
      ]

      return initQueryHints.map((hint) => ({
        message: hint,
        onClick: () => this.onUserQueryQuickButton(hint),
      }))
    },
    showCommonPrintingPrompts() {
      this.pushQuickButtons([...this.initUserQueryHintButtons(), this.cannedActions.cancel])
    },
    async showPresetOptions(presetType) {
      const presets = (await getAgentActionResponse('get_presets'))[`${presetType}Presets`] || []
      const options = presets.map((preset) => ({
        message: preset.name,
        onClick: async () => {
          await getAgentActionResponse(`select_preset`, {
            type: presetType,
            name: preset.name,
          })
          await this.refreshSelectedPresets()
          this.populateQuickButtons()
        },
      }))
      this.messages.push({
        role: 'assistant',
        content: this.$i18next.t('Select a {presetType}. If the {presetType} is not listed, use the "Add {presetType}" button to add it first.', {
          presetType
        }),
      })
      this.pushQuickButtons([
        ...options,
        this.cannedActions[`add${presetType.charAt(0).toUpperCase() + presetType.slice(1)}s`],
        this.cannedActions.cancel,
      ])
    },
    showMoreOptions() {
      const additionalActions = [
        this.cannedActions.changePrinter,
        this.cannedActions.changeFilament,
        this.cannedActions.addPrinters,
        this.cannedActions.addFilaments,
        this.cannedActions.startOver,
      ]
      this.removeQuickButtons([this.cannedActions.moreOptions])

      const topActions = this.quickButtons
      // Filter out actions that are already present in topActions
      const newActions = additionalActions.filter(
        (newAction) => !topActions.some((existing) => existing.message === newAction.message)
      )

      if (newActions.length > 0) {
        this.popQuickButtons()
        this.pushQuickButtons([...topActions, ...newActions])
      }
    },
    populateQuickButtons() {
      const quickButtons = []
      if (this.shouldShowSliceWithCurrentSettingsQuickButton) {
        quickButtons.push(this.cannedActions.sliceWithCurrentSettings)
        quickButtons.push(this.cannedActions.startOver)
        quickButtons.push(this.cannedActions.moreOptions)
        this.setQuickButtons(quickButtons)
        return
      }

      if (this.shouldShowPlateAnalysisQuickButton) {
        quickButtons.push(this.cannedActions.analyseModel)
      }

      if (this.hasModelObjects) {
        quickButtons.push(this.cannedActions.commonPrintingPrompts)
      }

      if (this.shouldShowStartOverQuickButton) {
        quickButtons.push(this.cannedActions.startOver)
      }

      quickButtons.push(this.cannedActions.moreOptions)
      this.setQuickButtons(quickButtons)
    },
    populateQuickButtonsOnError() {
      this.setQuickButtons([this.cannedActions.startOver])
    },
  },
}
