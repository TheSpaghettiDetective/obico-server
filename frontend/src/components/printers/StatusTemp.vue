<template>
  <div class="py-2">
      <div class="row text-muted">
        <div class="col-2">
          <i class="fas fa-thermometer-half fa-lg"></i>
        </div>
        <small class="col-5">
            Actual
        </small>
        <small class="col-5">
            Target
        </small>
      </div>
    <div
      v-for="item in temperatures"
      :key="item.id"
      class="row"
    >
      <div class="col-2 numbers">
        <span class="text-subscript text-muted">{{item.toolName}}</span>
      </div>
      <div class="col-5 numbers">
        {{item.actual}}<span class="text-subscript text-muted">°C</span>
      </div>
      <div
        :id="item.id"
        class="col-5 numbers"
        @click="onEditClicked(item)"
      >{{item.target}}<span class="text-subscript text-muted">°C</span>
        <span
          v-if="editable"
        >&nbsp;<i class="fas fa-pencil-alt" style="font-size: 0.6em;"></i></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatusTemp',
  props: {
    temperatures: {
      type: Array,
      required: true
    },
    editable: {
      type: Boolean,
      required: true
    }
  },
  methods: {
    onEditClicked(item) {
      if (this.editable) {
        this.$emit('TempEditClicked', item)
      }
    }
  }
}
</script>
