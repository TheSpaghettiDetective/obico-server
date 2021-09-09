<template>
  <section class="email">
    <h2 class="section-title">Email</h2>
    <div class="row">
      <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Primary Email</label>
      <div class="col-md-10 col-sm-9 col-form-label text-muted">{{user.email}} ({{user.is_primary_email_verified ? 'Verified' : 'Unverified'}})
        <div class="form-text"><a href="/accounts/email">Manage email addresses</a></div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'EmailPreferences',

  props: {
    user: {
      type: Object,
      required: true,
    },
  },
}
</script>