import axios from 'axios'
import { getCsrfFromDocument } from '@src/lib/utils'

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
let token = getCsrfFromDocument()
if (token) {
  axios.defaults.headers.common['X-CSRFToken'] = token
} else {
  console.error('CSRF token not found')
}

export default axios
