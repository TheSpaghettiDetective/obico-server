import axios from 'axios'
import i18n from '@src/i18n/i18n'

const getHeaders = (authToken) => ({
  Authorization: `Bearer ${authToken}`,
})

const getConfig = (authToken) => ({
  headers: getHeaders(authToken),
  params: {
    lang: i18n.language,
  },
})

export default {
  get: (url, authToken) => {
    return axios.get(url, getConfig(authToken))
  },
  post: (url, authToken, data) => {
    return axios.post(url, data, getConfig(authToken))
  },
  put: (url, authToken, data) => {
    return axios.put(url, data, getConfig(authToken))
  },
}
