<template>
  <div class="feedWrap" colorScheme="background">
    <div v-if="!feedIsOn" style="width: 100%">
      <p style="margin: 0; margin-top: 5px; text-align: center">
        <i class="fas fa-power-off" style="margin-right: 5px"></i>{{$t("Terminal feed is off")}}
      </p>
    </div>
    <div v-else v-for="(feed, index) in terminalFeedArray" :key="index" class="itemWrap">
      <div v-if="feed?.msg" class="terminalText">
        <p class="messageTimeStamp">
          {{ feed.normalTimeStamp }}
        </p>
        <p class="messageText">
          {{ feed.msg }}
        </p>
      </div>
      <div class="divider"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TerminalFeedView',

  components: {},

  props: {
    terminalFeedArray: {
      type: Array,
      required: true,
    },
    feedIsOn: {
      type: Boolean,
      required: true,
    },
  },

  methods: {
    onMenuOptionClicked(menuOptionKey) {
      if (menuOptionKey === 'share') {
        this.onSharePrinter()
      }
    },
  },
}
</script>

<style lang="sass" scoped>
.feedWrap
  display: flex
  align-items: flex-start
  flex-direction: column
  overflow-y: scroll
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)

.feedWrap::-webkit-scrollbar
  background-color: var(--color-surface-secondary)
  border-radius: var(--border-radius-md)

.feedWrap::-webkit-scrollbar-thumb
  background-color: var(--color-surface-primary)
  border-radius:  var(--border-radius-md)

.filterItemH
  display: flex
  flex-direction: row
  align-items: center

.terminalText
  display: flex
  align-items: center
  flex-direction: row

.messageTimeStamp
  opacity: 0.8
  margin-right: 20px
  font-size: 0.7rem
  margin-top: 7px
  margin-bottom: 7px
.divider
  width: 100%
  background-color: var(--color-divider)
  height: 1px

.itemWrap
  display: flex
  flex-direction: column
  width: 100%
.messageText
  margin-top: 7px
  margin-bottom: 7px
  white-space: pre-wrap
  word-break: break-all
</style>
