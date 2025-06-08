import pluralize from 'pluralize'
import i18next from '@src/i18n/i18n.js'

export default {
  computed: {
    cannedMessages() {
      return {
        greeting: {
          role: 'assistant',
          content: "🤖 Hi, I'm JusBot, your 3D printing AI assistant.",
        },
        needToAddPrinters: {
          role: 'assistant',
          content:
            "I notice you haven't added any printers yet. You need to add at least one printer before you can use JusPrin.",
        },
        needToAddFilaments: {
          role: 'assistant',
          content:
            "I notice you haven't added any filaments yet. You need to add at least one filament before you can use JusPrin.",
        },
        noModelObjects: {
          role: 'assistant',
          content:
            "I notice you don't have any models on your plate.\n\nAdd some models to see the magic. 😀",
        },
        noSupportForMultiplePlatesOrFilaments: {
          role: 'assistant',
          content:
            'I notice your model uses multiple plates or filaments.\n\nJusPrin is still in beta and does not support multiple plates or filaments yet.\n\nPlease manually slice your model. Also stay tuned for our product update.',
        },
        currentPresetSelections: (printerName, filamentName) => ({
          role: 'assistant',
          content: `You are currently using:\n- Printer: **${printerName}**\n- Filament: **${filamentName}**`,
        }),
        currentModelObjects: (modelObjectCount) => ({
          role: 'assistant',
          content:
            modelObjectCount === 1
              ? this.$i18next.t('You have {num} model on your plate.', {
                  num: modelObjectCount,
                })
              : this.$i18next.t('You have {num} models on your plate.', {
                  num: modelObjectCount,
                }),
        }),
        newModelObjects: (newModelObjects) => {
          let content = ''
          if (newModelObjects.length === 1) {
            content = `I see "${newModelObjects[0].name}" added to your plate.`
          } else if (newModelObjects.length > 1) {
            content = `I see "${newModelObjects[0].name}" and ${
              newModelObjects.length - 1
            } more ${pluralize('model', newModelObjects.length)} added to your plate.`
          }
          return {
            role: 'assistant',
            content,
          }
        },
        generalError: {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request.',
        },
      }
    },
  },
}
