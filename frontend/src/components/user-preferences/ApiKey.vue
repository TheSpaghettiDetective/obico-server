<template>
  <section>
    Your API Key is 
    <code>{{ apiKey }}</code>
  </section>
</template>

<script>

import axios from 'axios'
import urls from '@config/server-urls'

export default {
  name: 'ApiKeySettings',

  data() {
    return {
      apiKey: "",
    }
  },

  created() {
    axios
      .get(urls.getApiKey())
      .then((response) => {
        this.apiKey = response.data.api_key
      })
      .catch((error) => {
        this.errorDialog(error, 'Failed to fetch api key')
      })
  },
}
</script>
