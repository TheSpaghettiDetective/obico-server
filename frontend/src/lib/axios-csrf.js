import axios from 'axios'

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
let token = document.getElementsByName('csrfmiddlewaretoken')
if (token) {
  axios.defaults.headers.common['X-CSRFToken'] = token[0].value
} else {
  console.error('CSRF token not found')
}

export default axios
