import pluralize from 'pluralize'
import i18next from '@src/i18n/i18n.js'

export default {
  computed: {
    cannedMessages() {
      return {
        greeting: {
          role: 'assistant',
          content: this.$i18next.t("🤖 Hi, I'm JusBot, your 3D printing AI assistant."),
        },
        needToAddPrinters: {
          role: 'assistant',
          content: this.$i18next.t(
            "I notice you haven't added any printers yet. You need to add at least one printer before you can use JusPrin."
          ),
        },
        needToAddFilaments: {
          role: 'assistant',
          content: this.$i18next.t(
            "I notice you haven't added any filaments yet. You need to add at least one filament before you can use JusPrin."
          ),
        },
        noModelObjects: {
          role: 'assistant',
          content: this.$i18next.t(
            "I notice you don't have any models on your plate.\n\nAdd some models to see the magic. 😀"
          ),
        },
        noSupportForMultiplePlatesOrFilaments: {
          role: 'assistant',
          content: this.$i18next.t(
            'I notice your model uses multiple plates or filaments.\n\nJusPrin is still in beta and does not support multiple plates or filaments yet.\n\nPlease manually slice your model. Also stay tuned for our product update.'
          ),
        },
        currentPresetSelections: (printerName, filamentName) => ({
          role: 'assistant',
          content: `${this.$i18next.t('You are currently using:')}\n- ${this.$i18next.t('Printer:')} **${printerName}**\n- ${this.$i18next.t('Filament:')} **${filamentName}**`,
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
            content = this.$i18next.t('I see "{modelName}" added to your plate.', {
              modelName: newModelObjects[0].name
            })
          } else if (newModelObjects.length > 1) {
            content = (newModelObjects.length - 1) === 1 ? this.$i18next.t('I see "{modelName}" and {num} other model added to your plate.', {
                  modelName: newModelObjects[0].name,
                  num: newModelObjects.length - 1,
                })
              : this.$i18next.t('I see "{modelName}" and {num} other models added to your plate.', {
                  modelName: newModelObjects[0].name,
                  num: newModelObjects.length - 1,
                })
          }
          return {
            role: 'assistant',
            content,
          }
        },
        generalError: {
          role: 'assistant',
          content: this.$i18next.t('Sorry, there was an error processing your request.'),
        },
      }
    },
  },
}
