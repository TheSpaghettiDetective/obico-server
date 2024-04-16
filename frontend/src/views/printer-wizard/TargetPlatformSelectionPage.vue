<template>
  <page-layout>
    <template #content>
      <b-container>
        <b-row>
          <b-col>
            <div class="form-container full-on-mobile border-radius-lg">
              <b-row v-if="printerIdToLink">
                <div class="col-sm-12 col-lg-8">
                  <div class="text-warning">
                    <i18next :translation="$t(`Warning: Re-Linking OctoPrint should be your last resort to solve issues. Please make sure you have exhausted all options on {localizedDom}.`)">
                      <template #localizedDom>
                        <a href="https://www.obico.io/help/">{{$t("{brandName}'s help website",{brandName:$syndicateText.brandName})}}</a>
                      </template>
                    </i18next>
                  </div>
                </div>
              </b-row>
              <div class="row">
                <h1 class="col-sm-12 text-center p-3 wizard-page-title-font">{{ $t("Device Selection") }}</h1>
              </div>
              <b-row class="center mt-3 mb-5 pb-5">
                <div class="col-sm-12 col-lg-8"><PrinterProgress :step="0"></PrinterProgress></div>
              </b-row>
              <div v-if="devicesWithObicoPreInstalled.length > 0" class="row">
                <div class="col-sm-12 col-lg-6 py-4">
                  <h4 class="py-3">{{ $t("Devices with Obico Pre-installed") }}</h4>
                  <div class="printer-list">
                    <div v-for="item in devicesWithObicoPreInstalled" :key="item.id" @click="targetPlatformClicked('klipper-obico-enabled',item)" class="printer-item">
                      <div class="img-wrap clickable">
                        <img :src="item.image_url" alt="">
                      </div>
                      <div class="item-label">{{ item.brand }}</div>
                      <h5 class="item-label"><b>{{ item.model }}</b></h5>
                    </div>
                  </div>

                </div>
              </div>
              <div class="wizard-card-list py-4">
                <div class="wizard-card-horizontal" @click="targetPlatformClicked('klipper-preinstalled')">
                    <div class="img-wrap">
                      <img :src="require('@static/img/klipper_logo.jpg')" />
                    </div>
                    <div class="text-wrap">
                      <h3 class="wizard-default-font">{{ $t("Pre-Installed Klipper Printer") }}</h3>
                      <h4 class="wizard-secondary-text-font text-secondary">{{ $t("Creality K1, Sonic Pad, Sovol SV07, Kingroon KLP1, Elegoo Neptune 4, etc...") }}</h4>
                    </div>
                  </div>
                  <div class="wizard-card-horizontal" @click="targetPlatformClicked('klipper-generic')">
                    <div class="img-wrap">
                      <img :src="require('@static/img/klipper_logo.jpg')" />
                      <div class="img-tip">
                        <img :src="require('@static/img/mainsail_logo.png')" />
                        <img :src="require('@static/img/fluidd_logo.png')" />
                      </div>
                    </div>
                    <div class="text-wrap">
                      <h3 class="wizard-default-font">{{ $t("Generic Klipper - Self Installed") }}</h3>
                      <h4 class="wizard-secondary-text-font text-secondary">{{ $t("If you installed Klipper yourself on a Raspberry Pi or other linux device. E.g., Voron, RatRig") }}</h4>
                    </div>
                  </div>
                  <div class="wizard-card-horizontal" @click="targetPlatformClicked('octoprint')">
                    <div class="img-wrap">
                      <img :src="require('@static/img/octoprint_logo.png')" />
                    </div>

                    <div class="text-wrap">
                      <h3 class="wizard-default-font">OctoPrint</h3>
                      <h4 class="wizard-secondary-text-font text-secondary">{{ $t("Including OctoPrint for Klipper such as OctoKlipper.") }}</h4>
                    </div>
                  </div>
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
  data() {
    return {
      devicesWithObicoPreInstalled: [],
    }
  },
  computed: {
    printerIdToLink() {
      return this.$route.query.printerId;
    },
  },
  async created() {
    const response = await fetch(`https://storage.googleapis.com/public-versioned/devices_with_obico_preinstalled.json?ts=${Date.now()}`);
    this.devicesWithObicoPreInstalled = await response.json();
  },
  methods: {
    targetPlatformClicked(platform,printerItem) {
      this.$router.push({
        path: `/printers/wizard/guide/${platform}/`,
        query: {
          ...this.$route.query,
          printerItem:printerItem?JSON.stringify(printerItem):undefined
        }
      });
    },
  },
}
</script>

<style lang="scss" scoped>


.clickable {
  &:hover{
    cursor: pointer;
  }
}
.form-container{

  .printer-list{
    display:flex;
    gap:20px;
    .printer-item{
      .img-wrap{
        padding:20px;
        background:#485B71;
        border-radius:6px;
        img{
          width:100px;
          height:auto;
        }
      }
      .item-label{
        margin-top:3px;
        text-align:center;
      }
    }
  }
}


.wizard-card-list{
  margin-top:40px;

  .wizard-card-horizontal{
    margin-top:20px;
    display:flex;
    align-items:center;
    gap:30px;
    background-color: var(--color-surface-primary);
    border-radius: var(--border-radius-md);
    padding:20px;
    cursor: pointer;

  .img-wrap{
    img{
      width: 5em;
    }
    .img-tip{
      display:flex;
      justify-content:space-between;
      img{
        width:2em;
      }
    }
  }
  .text-wrap{
    h5{
      margin-top:10px;
      color:#AAACB0;
      font-size:16px;
    }
  }
}
}

</style>
