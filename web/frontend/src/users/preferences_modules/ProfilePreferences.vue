<template>
  <section class="profile">
    <h2 class="section-title">Profile</h2>
    <div class="form-group row">
      <label class="col-md-2 col-sm-3 col-form-label">Password</label>
      <div class="col-md-10 col-sm-9 col-form-label text-muted">
        <a href="/accounts/password/change">Change</a>
      </div>
    </div>
    <div class="form-group row">
      <label for="id_first_name" class="col-md-2 col-sm-3 col-form-label">First Name</label>
      <div class="col-md-10 col-sm-9">
        <saving-animation :errors="errorMessages.first_name" :saving="saving.first_name">
          <input
            type="text"
            maxlength="30"
            class="form-control"
            id="id_first_name"
            v-model="user.first_name"
          >
        </saving-animation>
      </div>
    </div>
    <div class="form-group row">
      <label for="id_last_name" class="col-md-2 col-sm-3 col-form-label">Last Name</label>
      <div class="col-md-10 col-sm-9">
        <saving-animation :errors="errorMessages.last_name" :saving="saving.last_name">
          <input
            type="text"
            maxlength="30"
            class="form-control"
            id="id_last_name"
            v-model="user.last_name"
          >
        </saving-animation>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@common/SavingAnimation.vue'

export default {
  name: 'ProfilePreferences',

  components: {
    SavingAnimation,
  },

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
      required: true,
    },
    user: {
      type: Object,
      required: true,
    },
  },
}
</script>