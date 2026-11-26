<template>
  <div></div>
</template>

<script>
import split from 'lodash/split'
import { isLocalStorageSupported } from '@static/js/utils'

// Opens the printer's page through the tunnel in this window. The tunnel is not shown in a
// frame: on a tunnel domain of its own, the tunnel's cookies would be third-party cookies there.
export default {
  name: 'OctoPrintTunnelPage',

  mounted() {
    const printerId = split(window.location.pathname, '/').slice(-2, -1).pop()
    // replace(): Back returns to the page before this one, not to this page that moves on again
    const openTunnel = () => window.location.replace(`/octoprint/${printerId}/`)

    const skipWarning = isLocalStorageSupported()
      ? localStorage.getItem('skip-tunneling-warning')
      : null
    if (skipWarning === 'yes') {
      openTunnel()
      return
    }

    this.$swal.Prompt.fire(
      {
        html: `
        <h4 class="text-center p-2">
          <svg class="menu-icon" style="height: 1.1em; width: 1em; margin-right: 0.75em;">
            <use href="#svg-tunnel" />
          </svg>
          ${this.$i18next.t("OctoPrint/Klipper Secure Tunnel")}
        </h4>
        <div class="p-1">
          ${this.$i18next.t("It may take long time for OctoPrint/Mainsail/Fluidd page to load as it is securely tunneled via the {brandName} app server.",{brandName:this.$syndicateText.brandName})}
        </div>
        <div class="p-1">
          <a target="_blank" href="${this.getDocUrl('/user-guides/octoprint-tunneling/#is-octoprint-tunneling-free-to-all-users')}">
          ${this.$i18next.t("Learn more about OctoPrint/Klipper tunnel's security and page load speed.")}
          <i class="fas fa-external-link-alt"></i>
        </a>
      </div>
      `,
        input: 'checkbox',
        inputPlaceholder: `${this.$i18next.t("Don't show again")}`,
      },
      'octoprint-tunnel.warning'
    ).then((result) => {
      if (result.isConfirmed && result.value && isLocalStorageSupported()) {
        localStorage.setItem('skip-tunneling-warning', 'yes')
      }
      openTunnel()
    })

    // Scale up popup on mobiles, otherwise it's too small (because of disabled meta viewport tag)
    if (window.matchMedia('(pointer:none), (pointer:coarse)')) {
      document.querySelector('.swal2-popup').classList.add('x150')
    }
  },
}
</script>

<style lang="sass">
@media (pointer:none), (pointer:coarse)
  .swal2-popup.x150
    transform: scale(1.5)
</style>
