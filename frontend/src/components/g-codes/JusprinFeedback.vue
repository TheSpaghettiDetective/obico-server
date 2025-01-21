<template>
  <div v-if="chat" class="jusprin-feedback">
    <div class="d-flex align-items-center">
      <div>
        <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
      </div>
      <div class="ml-2">
        {{ $t('Sliced with Obico AI Assistant.') }}
        <a href="#" @click="showChatHistory"> {{ $t('View the chat history.') }} </a>
      </div>
    </div>
    <div class="feedback-question py-4">
      <div class="d-flex align-items-center justify-content-between">
        <div class="question-text d-flex align-items-center">{{ $t('Was AI Assistant helpful?') }}</div>
        <div class="icon-buttons d-flex align-items-center">
          <i
            class="fas fa-thumbs-up feedback-icon"
            :class="{ 'selected': userFeedback === 'positive' }"
            @click="submitFeedback('positive')"
          ></i>
          <i
            class="fas fa-thumbs-down feedback-icon"
            :class="{ 'selected':  userFeedback === 'negative' }"
            @click="submitFeedback('negative')"
          ></i>
        </div>
      </div>
    </div>
    <transition name="fade">
      <div v-if="showTextFeedback" class="text-feedback mt-3">
        <div class="form-group">
            <textarea
              v-model="textFeedback"
              class="form-control"
              rows="3"
              maxlength="1000"
              :placeholder="$t('Tell us more')"
            ></textarea>
        </div>
        <div class="text-right">
          <button @click="submitFeedbackText" class="btn btn-primary">
            {{ $t('Send') }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@config/server-urls'
import JusPrinChatHistory from './JusprinChatHistory.vue'

export default {
  name: 'JusPrintFeedback',

  props: {
    gCodeFileId: {
      type: Number,
      required: true
    }
  },

  data() {
    return {
      showTextFeedback: false,
      textFeedback: '',
      userFeedback: null,
      chat: null,
    }
  },

  created() {
    this.fetchChat()
  },

  computed: {
    thumbsUp() {
      return this.chat?.user_feedback === 'positive'
    },
    thumbsDown() {
      return this.chat?.user_feedback === 'negative'
    },
  },
  methods: {
    async fetchChat() {
      if (!urls.jusprinChats) {
        return  // No JusPrin chat API endpoint on the server
      }
      try {
        const response = await axios.get(urls.jusprinChats(), {
          params: { g_code_file_id: this.gCodeFileId }
        })
        this.chat = response.data[0]
        this.userFeedback = this.chat?.user_feedback
      } catch (error) {
        this.chat = null
        console.log('fetchChat error', error)
      }
    },

    async submitFeedback(feedback) {
      this.userFeedback = feedback
      // Show text feedback input after submitting initial feedback
      this.showTextFeedback = true

      axios.patch(urls.jusprinChats(this.chat.id), {
        user_feedback: feedback
      })
    },

    submitFeedbackText() {
      this.showTextFeedback = false
      axios.patch(urls.jusprinChats(this.chat.id), {
        user_feedback_text: this.textFeedback
      })
    },
    showChatHistory() {
      this.$swal
        .openModalWithComponent(
          JusPrinChatHistory,
          {
            messages: JSON.parse(this.chat?.messages)
          },
          {
            title: this.$t('Chat History'),  // Use this.$t instead of just $t
            showConfirmButton: false,
          }
      )
    },
  },
}
</script>

<style lang="sass" scoped>
.jusprin-feedback
  svg
    width: 1.5em
    height: 1.5em
    color: gold

.feedback-question
  display: flex
  flex-direction: column
  align-items: center

  .question-text
    font-size: 1.2rem
    margin-right: 20px

  .icon-buttons
    display: flex
    justify-content: center
    gap: 30px

    .feedback-icon
      font-size: 1.3rem
      cursor: pointer
      transition: color 0.3s ease

      &:hover
        opacity: .8

      &.selected
        color: var(--color-primary)

.text-feedback
  margin: 0 auto

  .form-group
    text-align: left

  textarea
    resize: vertical

  .text-right
    text-align: right


.fade-enter-active, .fade-leave-active
  transition: opacity 0.5s

.fade-enter, .fade-leave-to
  opacity: 0
</style>

