<template>
  <div class="chat-container">
    <div class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
        <div v-if="message.role === 'assistant'" class="assistant-avatar">
          <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
          <VueMarkdown :key="message.content">{{ message.content }}</VueMarkdown>
          <div v-if="Object.keys(changedParams(message)).length > 0" class="pt-2">
            <div>{{ $t('I have changed the following parameters:') }}</div>
            <div v-for="(value, key) in changedParams(message)" :key="key">
              - {{ key }}: {{ value }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VueMarkdown from 'vue-markdown'

export default {
  name: 'JusPrinChatHistory',
  components: {
    VueMarkdown,
  },
  props: {
    messages: {
      type: Array,
      required: true
    }
  },
  methods: {
    changedParams(message) {
      return {
        ...(message.slicing_profiles?.filament_overrides?.[0] ?? {}),
        ...message.slicing_profiles?.print_process_overrides ?? {},
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.chat-container
  display: flex
  flex-direction: column
  height: 100%
  overflow-y: auto

.chat-messages
  flex-grow: 1
  overflow-y: auto
  padding: 1rem 0.5rem
  display: flex
  flex-direction: column

.message
  max-width: 80%
  margin-bottom: 1.5rem
  padding: 0.5rem
  border-radius: 18px
  line-height: 1.4
  position: relative
  color: black

  &.user
    align-self: flex-end
    background-color: #dcf8c6

  &.assistant
    align-self: flex-start
    background-color: #fff
    display: flex
    align-items: flex-start

.assistant-avatar
  width: 30px
  height: 30px
  background-color: #8e44ad
  border-radius: 50%
  display: flex
  align-items: center
  justify-content: center
  margin-right: 8px
  flex-shrink: 0

  i
    color: white

</style>
