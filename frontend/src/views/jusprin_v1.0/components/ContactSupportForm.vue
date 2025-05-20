<template>
  <div class="message assistant">
    <div class="message-block">
      <div class="message-content">
        <div class="contact-support-form">
          <p>Would you like to send a support request?</p>
          <textarea
            v-model="supportMessage"
            class="form-control mb-3"
            rows="4"
            placeholder="Describe your issue here..."
          ></textarea>
          <div class="d-flex justify-content-between">
            <button class="btn btn-primary" @click="sendSupportRequest" :disabled="isSubmitting">
              <i class="mdi mdi-message-question-outline mr-1"></i>
              {{ isSubmitting ? 'Sending...' : 'Ask for tech support' }}
            </button>
            <button
              class="btn btn-secondary"
              @click="cancelSupportRequest"
              :disabled="isSubmitting"
            >
              Nah, I'm good
            </button>
          </div>
          <div v-if="error" class="alert alert-danger mt-3">
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@config/server-urls'

export default {
  name: 'ContactSupportForm',
  props: {
    messages: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      supportMessage: '',
      isSubmitting: false,
      error: null,
    }
  },
  computed: {
    lastUserMessage() {
      // Find the last user message in the messages array using higher-order function
      const lastUserMsg = [...this.messages].reverse().find((message) => message.role === 'user')

      return lastUserMsg ? lastUserMsg.content : ''
    },
  },
  created() {
    // Pre-fill with the last user message
    this.supportMessage = this.lastUserMessage
  },
  methods: {
    async sendSupportRequest() {
      if (!this.supportMessage.trim()) {
        this.error = 'Please enter a message before submitting.'
        return
      }

      this.isSubmitting = true
      this.error = null

      try {
        await axios.post(urls.jusprinContactSupport(), {
          message: this.supportMessage,
        })

        this.$emit('form-dismissed', {
          message:
            'Your support request has been sent. Our team will get back to you as soon as possible.',
        })
      } catch (error) {
        console.error('Failed to send support request:', error)
        this.error = 'Failed to send your support request. Please try again later.'
        this.isSubmitting = false
      }
    },
    cancelSupportRequest() {
      this.$emit('form-dismissed', {
        message: "No problem! Let me know if there's anything else I can help you with.",
      })
    },
  },
}
</script>

<style scoped>
.contact-support-form {
  width: 100%;
}
</style>
