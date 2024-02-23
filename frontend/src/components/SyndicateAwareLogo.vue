<template>
    <div>
      <template v-if="currentLogo.type === 'svg'">
        <svg :width="currentLogo.width" :height="currentLogo.height">
          <use :xlink:href="currentLogo.src" />
        </svg>
      </template>
      <template v-else-if="currentLogo.type === 'img'">
        <img :src="currentLogo.src" :alt="currentLogo.alt" :width="currentLogo.width" :height="currentLogo.height" />
      </template>
    </div>
  </template>

  <script>
  export default {
    name: 'SyndicateAwareLogo',
    data() {
      return {
        syndicateLogos: {
          yumi: {
            type: 'svg',
            src: '#yumi-svg-logo-full',
            width: '100',
            height: '30',
          },
          mintion: {
            type: 'img',
            src: '/static/mintion/img/logo-mintion.png',
            alt: 'Mintion Logo',
            width: '100',
            height: '50',
          },
          base: {
            type: 'svg',
            src: '#svg-logo-compact',
            width: '100',
            height: '30',
          },
        },
      };
    },
    computed: {
      currentLogo() {
        const syndicate = this.$syndicate;
        return this.syndicateLogos[syndicate] || this.syndicateLogos.base;
      },
    },
  };
  </script>
