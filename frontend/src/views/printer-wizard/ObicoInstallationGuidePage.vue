<template>
  <page-layout>
    <template #content>
      <div class="container">
        <div class="row">
          <h3 class="col-sm-12 text-center p-3">{{ $t("Plugin Setup") }}</h3>
        </div>
        <b-row class="center mt-3 mb-5 pb-5">
          <div class="col-sm-12 col-lg-8">
            <PrinterProgress :step="1"></PrinterProgress>
          </div>
        </b-row>
        <div>
          <div v-if="targetKlipperPreInstall" class="kilpper-pre-install-wrap">
            <img src="@static/img/printer-wizard/command-line.png" alt="">
            <div class="text-wrap">
              <h4>{{ $t("If you haven’t installed Obico Klipper, You need to find the right guide for your printer to install it.The basic steps involves") }}:</h4>
              <ol>
                <li>{{ $t('SSH to the device your Klipper runs on.') }}</li>
                <li>{{ $t('Enter the terminal commands for your printer.') }}</li>
                <li>{{ $t('Follow the installation steps.') }}</li>
                <li>{{ $t('Get the one time passcode from the terminal.') }}</li>
              </ol>
            </div>
          </div>
          <div v-if="targetOctoPrint" class="octo-wrap">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-10">
                <ol>
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
            <div class="row justify-content-center">
              <div class="col-sm-12 col-lg-8 img-container">
                <img class="mx-auto screenshot" :src="require('@static/img/octoprint-plugin-guide/install_plugin.png')
            " @click="zoomIn($event)" />
              </div>
            </div>
          </div>
          <div v-if="targetKlipper" class="klipper-wrap">
            <div class="row justify-content-center pb-3">
              <div class="col-sm-12 col-lg-10">
                <ol>
                  <li>{{ $t("SSH to the Raspberry Pi your Klipper runs on.") }}</li>
                  <li>
                    <div>{{ $t("Run:") }}</div>
                    <pre class="mt-2">
cd ~
git clone https://github.com/TheSpaghettiDetective/moonraker-obico.git
cd moonraker-obico
./install.sh
                  </pre>
                  </li>
                  <li>{{ $t("Follow the installation steps.") }}</li>
                </ol>
              </div>
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
        </div>
        <div class="d-flex justify-content-between button-wrap">
          <div class="back" @click="$router.back()">
            <i class="fas fa-chevron-left"></i>
            <span> {{ $t("Back") }}</span>
          </div>
            <b-button variant="primary" @click="goForward">
              {{ $t("Next") }}
            </b-button>
        </div>
        <div class="center mt-5">
          <i18next :translation="$t(`Need help? Check out the {localizedDom}`)">
            <template #localizedDom>
              <a target="_blank" :href="targetKlipper? 'https://www.obico.io/docs/user-guides/klipper-setup/':'https://www.obico.io/docs/user-guides/octoprint-plugin-setup/'">{{$t("step-by-step set up guide")}}.</a>
            </template>
          </i18next>
        </div>
      </div>
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
    targetKlipper() {
      return this.$route.params.targetPlatform === 'klipper-generic'
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
.container {
  background-color: #2D3E4F;
  padding: 70px 140px 10px;
  border-radius: 16px;
  margin-top: 60px;


  .kilpper-pre-install-wrap {
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
        font-size: 24px;
        line-height:34px;
      }
      ol{
        padding-left:15px;
        margin-top:20px;
        li{
          margin-top:10px;
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
