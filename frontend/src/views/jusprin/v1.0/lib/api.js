import axios from 'axios'

export default {
  get: (url, authToken) => {
    return axios.get(url, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    })
  },
  post: (url, authToken, data) => {
    return axios.post(url, data, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    })
  },
  put: (url, authToken, data) => {
    return axios.put(url, data, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    })
  },
}
