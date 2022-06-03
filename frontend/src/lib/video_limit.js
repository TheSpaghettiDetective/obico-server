import { isLocalStorageSupported } from '@static/js/utils'

export default function VideoLimit(countDownCallback) {
  let self = {
    countDownTimer: null
  }

  self.startOrResumeVideoCycle = function () {
    if (!self.countDownTimer) {
      self.countDownTimer = setInterval( () => self.countDown(), 1000)
    }
  }

  self.resumeVideoCycle = function () {
    if (remainingSeconds < 60 && !self.countDownTimer) {
      self.countDownTimer = setInterval( () => self.countDown(), 1000)
    }
  }

  self.countDown = function () {
    self.updateRemainingSeconds(remainingSeconds - 1)

    if (isLocalStorageSupported()) {
      localStorage.setItem('tsNextVideoCycle', (new Date().getTime())/1000 + remainingSeconds)
    }

    if (remainingSeconds < 0) {
      self.updateRemainingSeconds(60)
      clearInterval(this.countDownTimer)
      this.countDownTimer = null
    }
  }

  self.updateRemainingSeconds = function (newValue) {
    remainingSeconds = newValue
    const remainingViewableSeconds = remainingSeconds - 30
    const remainingSecondsUntilNextCycle = remainingSeconds > 30 ? -1 : remainingSeconds
    countDownCallback(remainingViewableSeconds, remainingSecondsUntilNextCycle)
  }

  let remainingSeconds
  if (isLocalStorageSupported()) {
    const tsNextVideoCycle = parseFloat(localStorage.getItem('tsNextVideoCycle'))
    const now = (new Date().getTime())/1000
    if (!tsNextVideoCycle || now > tsNextVideoCycle) {
      self.updateRemainingSeconds(60)
    } else {
      self.updateRemainingSeconds(Math.round((tsNextVideoCycle - now)))
    }
  } else {
    self.updateRemainingSeconds(60)
  }

  return self
}