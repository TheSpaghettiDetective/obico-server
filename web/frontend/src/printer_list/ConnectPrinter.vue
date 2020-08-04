<template>
  <div>
    <div>
      <h5>Serial Port:</h5>
    </div>
    <div>
      <select
        name="port"
        class="form-control"
        id="connect-port"
        v-model="selection.port"
        @change="onSelectionChanged"
      >
        <option
          v-for="port in connectionOptions.ports"
          :key="port"
          :value="port"
        >{{ port }}</option>
      </select>
    </div>
    <br />
    <div>
      <h5>Baudrate:</h5>
    </div>
    <div>
      <select
        name="baudrate"
        class="form-control"
        id="connect-baudrate"
        v-model="selection.baudrate"
        @change="onSelectionChanged"
      >
        <option value="">Auto</option>
        <option
          v-for="brate in connectionOptions.baudrates"
          :key="brate"
          :value="brate"
        >{{ brate }}</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConnectPrinter',
  props: {
    connectionOptions: {
      type: Object,
      required: true
    },
    initial: {
      type: Object,
      default() {
        return {
          baudrate: '',
          port: ''
        }
      }
    }
  },
  data() {
    return {
      selection: this.initial
    }
  },
  methods: {
    onSelectionChanged() {
    }
  }
}
</script>
