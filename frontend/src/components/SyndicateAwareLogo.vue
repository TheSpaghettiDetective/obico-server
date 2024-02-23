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
    props: {
      syndicate: {
        type: String,
        required: true,
      },
    },
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
            height: '30',
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
        return this.syndicateLogos[this.syndicate] || this.syndicateLogos.base;
      },
    },
  };
  </script>
