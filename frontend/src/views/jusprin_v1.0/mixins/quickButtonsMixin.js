import { callAgentAction, getAgentActionResponse } from '../lib/agentAction'

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
          message: 'Add printer',
          onClick: () => {
            this.popQuickButtons()
            this.callLongRunningAgentActionThenRefreshPresets('add_printers')
          },
        },
        addFilaments: {
          message: 'Add filament',
          onClick: () => {
            this.popQuickButtons()
            this.callLongRunningAgentActionThenRefreshPresets('add_filaments')
          },
        },
        changePrinter: {
          message: 'Change printer',
          onClick: () => this.showPresetOptions('printer'),
        },
        changeFilament: {
          message: 'Change filament',
          onClick: () => this.showPresetOptions('filament'),
        },
        moreOptions: {
          message: 'More options',
          onClick: () => this.showMoreOptions(),
        },
        cancel: {
          message: 'Cancel',
          onClick: () => this.popQuickButtons(),
        },
        sliceWithCurrentSettings: {
          message: 'Slice with current settings',
          onClick: () => this.doSliceWithCurrentSettings(),
        },
        endTroubleshooting: {
          message: 'End troubleshooting',
          onClick: () => {
            this.current_workflow = null
            this.onUserQueryQuickButton('I want to end troubleshooting')
          },
        },
        stayInTroubleshooting: {
          message: 'Stay in troubleshooting',
          onClick: () => {
            this.onUserQueryQuickButton('I want to continue troubleshooting')
          },
        },
        startOver: {
          message: 'Start over',
          onClick: () => this.startOver(),
        },
        exportGCode: {
          message: 'Export G-code',
          onClick: () => this.callAgentAction('export_gcode'),
        },
        switchToPreview: {
          message: 'Switch to preview',
          onClick: () => this.callAgentAction('switch_to_preview'),
        },
        autoOrient: {
          message: 'Auto-orient models',
          onClick: () => {
            this.autoOrientAllObjects()
          },
        },
        undoAutoOrient: {
          message: 'Undo auto-orient',
          onClick: () => {
            callAgentAction('plater_undo')
            this.messages.push({
              role: 'assistant',
              content: 'Got it! Auto-orient is undone.',
            })
            this.removeQuickButtons([this.cannedActions.undoAutoOrient])
          },
        },
        undoAutoArrange: {
          message: 'Undo auto-arrange',
          onClick: () => {
            callAgentAction('plater_undo')
            this.messages.push({
              role: 'assistant',
              content: 'Got it! Auto-arrange is undone.',
            })
            this.removeQuickButtons([this.cannedActions.undoAutoArrange])
          },
        },
        enableSupport: {
          message: 'Enable support',
          onClick: async () => {
            await getAgentActionResponse(
              'apply_config',
              this.paramOverridesToApplyConfigPayload({ enable_support: '1' }, 'print')
            )
            this.messages.push({
              role: 'assistant',
              content: 'Support enabled.',
            })
            this.removeQuickButtons([this.cannedActions.enableSupport])
            this.setQuickButtons([this.cannedActions.undoEnableSupport, ...this.quickButtons])
          },
        },
        undoEnableSupport: {
          message: 'Undo enable support',
          onClick: async () => {
            await getAgentActionResponse(
              'apply_config',
              this.paramOverridesToApplyConfigPayload({ enable_support: '0' }, 'print')
            )
            this.messages.push({
              role: 'assistant',
              content: 'Got it! Support is now disabled.',
            })
            this.removeQuickButtons([this.cannedActions.undoEnableSupport])
          },
        },
        tellMeWhatNotificationMeans: {
          message: 'Explain it to me',
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
            const newMessage = `JusPrin displays this message: *"${originalErrorMessage}"* Explain it to me.`

            // Send the message
            this.onUserQueryQuickButton(newMessage)
          },
        },
        acknowledgeError: {
          message: 'Okay',
          onClick: () => {
            this.messages.pop()
            this.popQuickButtons()
          },
        },
        commonPrintingPrompts: {
          message: 'Common printing prompts',
          onClick: () => this.showCommonPrintingPrompts(),
        },
        testRender: {
          message: 'Test render',
          onClick: () => this.renderPlateForAnalysis(),
        },
        analyseModel: {
          message: '✨ Do your magic!',
          onClick: () => this.getAnalysisResult(),
        },
        plateAnalysisLooksGoodToMe: {
          message: 'Looks good to me',
          onClick: () => this.queryWithSuggestedPrintingMethod(),
        },
        plateAnalysisIsNotGood: {
          message: 'You got it wrong. Scratch that.',
          onClick: () => this.removePlateAnalysis(),
        },
        editPlateAnalysis: {
          message: 'Let me change it',
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
        'Just do a standard print. Nothing special.',
        'I want to do a fast print. Draft quality.',
        'Print a strong part.',
        'My last print did not stick to the bed. Help me fix it.',
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
        content: `Select a ${presetType}. If the ${presetType} is not listed, use the "Add ${presetType}" button to add it first.`,
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
