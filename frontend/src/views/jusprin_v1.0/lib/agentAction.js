// Global state
window.stubAgentActionResponse = new Map()
window.agentActionCallMap = {}

import i18next from '@src/i18n/i18n.js'

// Helper functions
export function setAgentActionRetVal({ refId, retVal = null, error = null }) {
  window.agentActionCallMap[refId] = { retVal, error }
}

export function callAgentAction(action, payload = null, refId = null) {
  const message = { action }
  if (payload !== null) message.payload = payload
  if (refId !== null) message.refId = refId

  if (window.wx?.postMessage) {
    window.wx.postMessage(message)
  } else {
    console.log(`window.wx.postMessage(${JSON.stringify(message)})`)

    if (refId !== null && refId !== undefined) {
      setTimeout(() => {
        const retVal = window.stubAgentActionResponse.get(action) || {}
        setAgentActionRetVal({ refId, retVal })
      }, 10)
    }
  }
}

export function getAgentActionResponse(action, payload = {}, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const refId = Math.random().toString(36).substring(2, 15)
    window.agentActionCallMap[refId] = null // Initialize with null

    callAgentAction(action, payload, refId)

    const timeoutId = setTimeout(() => {
      if (refId in window.agentActionCallMap) {
        reject(new Error(i18next.t('Timeout: No response for action "{action}" within {timeout}ms', {
          action,
          timeout
        })))
        delete window.agentActionCallMap[refId] // Clean up
      }
    }, timeout)

    // Poll for response
    const checkResponse = () => {
      const response = window.agentActionCallMap[refId]
      if (response !== null && response !== undefined) {
        clearTimeout(timeoutId)
        delete window.agentActionCallMap[refId] // Clean up
        if (response.error) {
          reject(new Error(response.error))
        } else {
          resolve(response.retVal)
        }
      } else {
        setTimeout(checkResponse, 10) // Check again in 10ms
      }
    }
    checkResponse()
  })
}
