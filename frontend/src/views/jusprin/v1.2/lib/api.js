import axios from 'axios'
import i18n from '@src/i18n/i18n'

const getHeaders = (authToken) => ({
  Authorization: `Bearer ${authToken}`,
  'Accept-Language': i18n.language,
})

export default {
  get: (url, authToken) => {
    return axios.get(url, {
      headers: getHeaders(authToken),
    })
  },
  post: (url, authToken, data) => {
    return axios.post(url, data, {
      headers: getHeaders(authToken),
    })
  },
  put: (url, authToken, data) => {
    return axios.put(url, data, {
      headers: getHeaders(authToken),
    })
  },
}
