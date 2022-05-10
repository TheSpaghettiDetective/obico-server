<template>
  <section class="profile">
    <h2 class="section-title">Authorized Apps</h2>
    <div class="obico-table break-md mt-3">
      <div class="table-head">
        <div class="table-row">
          <div>App Name</div>
          <div>Printer to Access</div>
          <div></div>
        </div>
      </div>
      <div class="table-body">
        <div v-for="item in authorizedApps" :key="item.id" class="table-row">
          <div>{{ item.app }}</div>
          <div>{{ item.printer.name }}</div>
          <div><a href="#" @click.prevent="removeAccess(item.id)">Remove Access</a></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'
import urls from '@config/server-urls'

export default {
  name: 'AuthorizedApps',

  data() {
    return {
      authorizedApps: []
    }
  },

  created() {
    axios
      .get(urls.tunnels())
      .then(response => {
        this.authorizedApps = response.data
      })
      .catch(error => {
        this.$swal.Reject.fire({
          title: 'Oops',
          text: error.message,
        })
      })
  },

  methods: {
    removeAccess(id) {
      axios
        .delete(urls.tunnel(id))
        .then(() => {
          this.authorizedApps = this.authorizedApps.filter(app => app.id !== id)
        })
        .catch(error => {
          this.$swal.Reject.fire({
            title: 'Oops',
            text: error.message,
          })
        })
    }
  },
}
</script>
