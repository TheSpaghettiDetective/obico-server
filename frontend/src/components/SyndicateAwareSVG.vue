<template>
  <svg v-bind="$attrs">
    <use :xlink:href="syndicateAwareHref" />
  </svg>
</template>

<script>
export default {
  name: 'SyndicateAwareSVG',
  props: ['href'],
  computed: {
    syndicateAwareHref() {
      return this.$syndicate ? `#${this.$syndicate}${this.href.slice(1)}` : `${this.href}`;
    },
  },
};
</script>