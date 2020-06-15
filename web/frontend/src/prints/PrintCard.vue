<template>
  <div class="col-sm-12 col-md-6 col-lg-4 timelapse-card">
    <card>
      <card-header>
        <div
          class="custom-control custom-checkbox form-check-inline float-left"
          style="padding-top: 2px;"
        >
          <input
            type="checkbox"
            name="selected_print_ids"
            class="custom-control-input"
            form="prints-form"
          />
          <label class="custom-control-label"></label>
        </div>
        <a
          role="button"
          class="btn btn-outline-danger float-right btn-sm borderless"
          data-toggle="tooltip"
          data-placement="top"
          title="Delete"
        >
          <i class="fas fa-trash-alt fa-lg"></i>
        </a>
        <div class="dropdown float-right">
          <a
            role="button"
            class="btn btn-sm borderless dropdown-toggle"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
          >
            <i class="fas fa-download"></i>
          </a>
          <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
            <a
              class="download dropdown-item"
              data-mime-type="video/mp4"
            >Download Original Time-lapse</a>
            <a class="download dropdown-item" data-mime-type="video/mp4">Download Detective View</a>
          </div>
        </div>
      </card-header>
    </card>
  </div>
</template>

<script>
import Card from "../common/Card.vue";
import CardHeader from "../common/CardHeader.vue";

export default {
  name: "PrintCard",
  components: {
    Card,
    CardHeader
  },
  props: {},
  computed: {}
};
</script>

<style></style>
