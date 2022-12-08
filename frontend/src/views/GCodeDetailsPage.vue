<template>
  <layout>

    <!-- Tob bar -->
    <template v-slot:topBarLeft>
    </template>
    <template v-slot:topBarRight>
    </template>

    <!-- Page content -->
    <template v-slot:content>
      <b-container>
        <b-row>
          <b-col>
            <p>Hi there!</p>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </layout>
</template>

<script>
import Layout from '@src/components/Layout.vue'
import urls from '@config/server-urls'
import axios from 'axios'
import { normalizedGcode } from '@src/lib/normalizers'
import { user } from '@src/lib/page_context'

export default {
  name: 'GCodeDetailsPage',

  components: {
    Layout,
  },

  // props: {
  //   csrf: {
  //     type: String,
  //     requeired: true,
  //   },
  // },

  data() {
    return {
      user: null,
      gcode: null,
    }
  },

  created() {
    this.user = user()
  },
}
</script>

<style lang="sass" scoped>

</style>
