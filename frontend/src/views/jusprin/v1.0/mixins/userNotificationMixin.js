export default {
  data() {
    return {
      processedNotifications: new Set(),
    }
  },
  methods: {
    processNotificationPushedEvent(event) {
      if (!event.data?.text) return

      const { level, text } = event.data
      const notificationKey = `${level}:${text}`

      if (this.processedNotifications.has(notificationKey)) return

      this.processedNotifications.add(notificationKey)

      if (!['error', 'warning'].includes(level)) {
        return
      }

      if (this.slicingProgress) {
        this.slicingProgress.errors.push(text)
        return
      }

      this.messages.push({
        role: 'assistant',
        content: '', // jusprinNotification message is constructed from jusprinNotification field
        jusprinNotification: {
          level,
          text,
        },
      })

      this.pushQuickButtons([this.cannedActions.tellMeWhatNotificationMeans, this.cannedActions.acknowledgeError])
      this.$refs.chatHeader.popupChatPanelIfNecessary(level)
    },
  },
}
