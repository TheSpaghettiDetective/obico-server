<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row>
          <b-col>
            <div class="form-container full-on-mobile border-radius-lg">
              <div class="row">
                <h1 class="col-sm-12 text-center p-3 wizard-page-title-font">{{ $t("Install Obico") }}</h1>
              </div>
              <b-row class="center mt-3 mb-5 pb-5">
                <div class="col-sm-12 col-lg-8">
                  <PrinterProgress :step="1"></PrinterProgress>
                </div>
              </b-row>
              <div>
                <div v-if="targetKlipperPreInstall" class="klipper-pre-install-wrap">
                  <img src="@static/img/printer-wizard/commandLinePrompt.png" alt="">
                  <div class="text-wrap">
                    <h3>{{ $t("Install Obico for Klipper") }}</h3>
                    <ol class="secondary-font">
                      <li><a :href="getDocUrl('/user-guides/klipper-setup/')" target="_blank">{{ $t("Find the Guide for Your Printer to install Obico for Klipper.") }}</a></li>
                      <li>{{ $t('SSH to your device.') }}</li>
                      <li>{{ $t('Enter the installation commands.') }}</li>
                      <li>{{ $t('Alternatively, you can use KIAUH to install Obico.') }}</li>
                      <li>{{ $t('Upon "Scanning the networking...", come back here and click "Next".') }}</li>
                    </ol>
                  </div>
                </div>
                <div v-if="targetOctoPrint"  class="kilpper-pre-install-wrap">
                  <img class="octoprint-image" src="@static/img/octoprint-plugin-guide/install_plugin.png" alt="">
                  <div class="text-wrap">
                    <h3>{{ $t("Install Obico for OctoPrint") }}</h3>
                    <ol class="secondary-font">
                        <li>{{ $t("Open OctoPrint in another browser tab.") }}</li>
                        <li>
                          {{ $t("Select") }}
                          <em>"{{ $t("OctoPrint settings menu → Plugin Manager → Get More...") }}"</em>.
                        </li>
                        <li>{{ $t("Enter '{brandName}' to locate the plugin. Click", { brandName: $syndicateText.brandName }) }}
                          <em>"{{ $t("Install") }}"</em>.</li>
                        <li>{{ $t("Restart OctoPrint when prompted.") }}</li>
                      </ol>
                    </div>
                  </div>
                </div>
                <div v-if="targetKlipperGeneric"  class="kilpper-pre-install-wrap">
                  <img src="@static/img/klipper_logo.jpg" alt="">
                  <div class="text-wrap">
                    <h3>{{ $t("Install Obico for Klipper") }}</h3>
                    <ol class="secondary-font">
                        <li>{{ $t("SSH to the Raspberry Pi (or other SBC) your Klipper runs on.") }}</li>
                        <li>
                          <div>{{ $t("Run:") }}</div>
                          <pre class="mt-2">
      cd ~
      git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
      cd moonraker-obico
      ./install.sh
                        </pre>
                        </li>
                      <li>{{ $t('Alternatively, you can use KIAUH to install Obico.') }}</li>
                      <li>{{ $t('Upon "Scanning the networking...", come back here and click "Next".') }}</li>
                    </ol>
                  </div>
                </div>
                <div v-if="printerItem" class="printer-item">
                  <div class="printer-left">
                    <h5>{{ printerItem.brand +" " +  printerItem.model }}</h5>
                    <div class="img-wrap">
                      <img :src="printerItem.image_url" alt="">
                    </div>

                  </div>
                  <div class="line"></div>
                  <div class="printer-right">
                    <ol>
                      <li>{{ $t('1. Unbox and assemble the 3D printer following the manufacturers instructions') }}</li>
                      <li>{{ $t('2. Power on the 3D printer and make sure it is connected to WiFi.') }}</li>
                      <li>{{ $t('3. Tap “Next” when you are ready.') }}</li>
                    </ol>

                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-center button-wrap">
                  <div class="back" @click="$router.back()">
                    <i class="fas fa-chevron-left"></i>
                    <span> {{ $t("Back") }}</span>
                  </div>
                    <b-button variant="primary" @click="goForward">
                      {{ $t("Next") }}
                    </b-button>
                </div>
                <div class="text-center mt-5 wizard-default-font">
                  <i18next :translation="$t(`Need help? Check out the {localizedDom}`)">
                    <template #localizedDom>
                      <a target="_blank" :href="targetKlipper? getDocUrl('/user-guides/klipper-setup/'):getDocUrl('/user-guides/octoprint-plugin-setup/')">{{$t("step-by-step set up guide")}}.</a>
                    </template>
                  </i18next>
                </div>
              </div>
          </b-col>
        </b-row>
      </b-container>
    </template>
  </page-layout>
</template>

<script>
import PageLayout from '@src/components/PageLayout.vue'
import PrinterProgress from '../../components/printers/wizard/PrinterProgress.vue';
export default {
  components: {
    PageLayout,
    PrinterProgress
  },
  computed: {
    printerItem(){
      if(this.$route.query.printerItem){
        return JSON.parse(this.$route.query.printerItem)
      }
      return
    },
    targetOctoPrint() {
      return this.$route.params.targetPlatform === 'octoprint'
    },
    targetKlipperPreInstall() {
      return this.$route.params.targetPlatform === 'klipper-preinstalled'
    },
    targetKlipperGeneric() {
      return this.$route.params.targetPlatform === 'klipper-generic'
    },
    targetKlipper() {
      return this.$route.params.targetPlatform.startsWith('klipper-');
    },
  },
  methods: {
    goForward() {
      this.$router.push({
        path: `/printers/wizard/link/${this.$route.params.targetPlatform}/`,
        query: {
          ...this.$route.query,
        }
      });
    },
  },
}
</script>

<style lang="scss" scoped>
.octoprint-image {
  width: 100%; 
  margin-bottom: 1em;
}
.form-container {
  .klipper-pre-install-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;

    img {
      width: 150px;
    }

    .text-wrap {
      width: 70%;
      margin-top:20px;
      h4 {
        color: #EBEBEB;
        font-size: 22px;
        line-height:34px;
        margin-top: 1em;
        font-weight: 600;
      }
      ol{
        padding-left:15px;
        margin-top:8px;
        li{
          margin-top:10px;
        }
      }
      .find-printer-link {
        color: var(--color-primary);
        i {
          transform: rotate(45deg);
        }
        a {
          margin-right: 4px;
          font-weight: 600;
          text-decoration: underline;
        }
      }
    }
  }
  .octo-wrap{
    img{
      width:100%;
    }
  }
  .klipper-wrap{
    color:#EBEBEB;
    font-size:20px;
  }
  .printer-item{
    display:flex;
    justify-content: space-between;
    align-items:center;
    gap:40px;

    .printer-left{
      flex:1;
      display:flex;
      flex-direction: column;
      align-items:center;

      .img-wrap{
        margin-top:20px;
        background-color: var(--color-surface-primary);
        border-radius:var(--border-radius-lg);
        padding:20px;
        img{
          width:300px;
        }
      }
    }
    .line{
      align-self: stretch;
      width:1px;
      background-color: #fff;

    }
    .printer-right{
      flex:1;
      p{
        margin-bottom:30px;
        font-size:20px;
      }
    }
  }
  .button-wrap{
    margin-top:80px;
    .back{
      cursor: pointer;
    }
  }

}
</style>
