<template>
  <section class="sms">
    <h2 class="section-title">SMS</h2>
    <div class="form-group row">
      <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Phone Number</label>
      <div class="col-md-10 col-sm-9 col-form-label">
        <div v-if="twilioEnabled">
          <saving-animation :errors="errorMessages.phone" :saving="saving.phone">
            <div class="form-group form-row">
              <maz-phone-number-input
                @update="updatePhone"
                :defaultCountryCode="countryCode"
                :defaultPhoneNumber="user.phone_number"
                :onlyCountries="onlyCountries.map(country => country[1].toUpperCase())"
                :fetchCountry="!countryCode"
                show-code-on-list
              ></maz-phone-number-input>
            </div>
          </saving-animation>
        </div>
        <p v-else class="text-muted">Please configure TWILIO_* items in settings to enable phone alert.</p>
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
        <saving-animation :errors="errorMessages.alert_by_sms" :saving="saving.alert_by_sms">
          <div class="custom-control custom-checkbox form-check-inline">
            <input
              type="checkbox"
              class="custom-control-input"
              id="id_alert_by_sms"
              v-model="user.alert_by_sms"
              @change="$emit('updateSetting', 'alert_by_sms')"
            >
            <label class="custom-control-label" for="id_alert_by_sms">
              Alert me via SMS when print failures are detected
            </label>
          </div>
        </saving-animation>
        <small v-if="!user.is_pro" class="text-warning">Note: You won't be alerted via SMS because this is a Pro feature and you are on the Free plan.</small>
      </div>
    </div>
  </section>
</template>

<script>
import SavingAnimation from '@common/SavingAnimation.vue'
import { MazPhoneNumberInput } from 'maz-ui'

const allCountries = [
  ['Afghanistan', 'af', '93'],
  ['Albania', 'al', '355'],
  ['Algeria', 'dz', '213'],
  ['American Samoa', 'as', '1684'],
  ['Andorra', 'ad', '376'],
  ['Angola', 'ao', '244'],
  ['Anguilla', 'ai', '1264'],
  ['Antigua and Barbuda', 'ag', '1268'],
  ['Argentina', 'ar', '54'],
  ['Armenia', 'am', '374'],
  ['Aruba', 'aw', '297'],
  ['Australia', 'au', '61'],
  ['Austria', 'at', '43'],
  ['Azerbaijan', 'az', '994'],
  ['Bahamas', 'bs', '1242'],
  ['Bahrain', 'bh', '973'],
  ['Bangladesh', 'bd', '880'],
  ['Barbados', 'bb', '1246'],
  ['Belarus', 'by', '375'],
  ['Belgium', 'be', '32'],
  ['Belize', 'bz', '501'],
  ['Benin', 'bj', '229'],
  ['Bermuda', 'bm', '1441'],
  ['Bhutan', 'bt', '975'],
  ['Bolivia', 'bo', '591'],
  ['Bosnia and Herzegovina', 'ba', '387'],
  ['Botswana', 'bw', '267'],
  ['Brazil', 'br', '55'],
  ['British Indian Ocean Territory', 'io', '246'],
  ['British Virgin Islands', 'vg', '1284'],
  ['Brunei', 'bn', '673'],
  ['Bulgaria', 'bg', '359'],
  ['Burkina Faso', 'bf', '226'],
  ['Burundi', 'bi', '257'],
  ['Cambodia', 'kh', '855'],
  ['Cameroon', 'cm', '237'],
  ['Canada', 'ca', '1'],
  ['Cape Verde', 'cv', '238'],
  ['Caribbean Netherlands', 'bq', '599'],
  ['Cayman Islands', 'ky', '1345'],
  ['Central African Republic', 'cf', '236'],
  ['Chad', 'td', '235'],
  ['Chile', 'cl', '56'],
  ['China', 'cn', '86'],
  ['Christmas Island', 'cx', '61'],
  ['Cocos [Keeling] Islands', 'cc', '61'],
  ['Colombia', 'co', '57'],
  ['Comoros', 'km', '269'],
  ['Congo (DRC)', 'cd', '243'],
  ['Congo (Republic)', 'cg', '242'],
  ['Cook Islands', 'ck', '682'],
  ['Costa Rica', 'cr', '506'],
  ['Côte d’Ivoire', 'ci', '225'],
  ['Croatia', 'hr', '385'],
  ['Cuba', 'cu', '53'],
  ['Curaçao', 'cw', '599', 0],
  ['Cyprus', 'cy', '357'],
  ['Czech Republic', 'cz', '420'],
  ['Denmark', 'dk', '45'],
  ['Djibouti', 'dj', '253'],
  ['Dominica', 'dm', '1767'],
  ['Dominican Republic', 'do', '1'],
  ['Ecuador', 'ec', '593'],
  ['Egypt', 'eg', '20'],
  ['El Salvador', 'sv', '503'],
  ['Equatorial Guinea', 'gq', '240'],
  ['Eritrea', 'er', '291'],
  ['Estonia', 'ee', '372'],
  ['Ethiopia', 'et', '251'],
  ['Falkland Islands', 'fk', '500'],
  ['Faroe Islands', 'fo', '298'],
  ['Fiji', 'fj', '679'],
  ['Finland', 'fi', '358'],
  ['France', 'fr', '33'],
  ['French Guiana', 'gf', '594'],
  ['French Polynesia', 'pf', '689'],
  ['Gabon', 'ga', '241'],
  ['Gambia', 'gm', '220'],
  ['Georgia', 'ge', '995'],
  ['Germany', 'de', '49'],
  ['Ghana', 'gh', '233'],
  ['Gibraltar', 'gi', '350'],
  ['Greece', 'gr', '30'],
  ['Greenland', 'gl', '299'],
  ['Grenada', 'gd', '1473'],
  ['Guadeloupe', 'gp', '590'],
  ['Guam', 'gu', '1671'],
  ['Guatemala', 'gt', '502'],
  ['Guernsey', 'gg', '44'],
  ['Guinea', 'gn', '224'],
  ['Guinea-Bissau', 'gw', '245'],
  ['Guyana', 'gy', '592'],
  ['Haiti', 'ht', '509'],
  ['Honduras', 'hn', '504'],
  ['Hong Kong', 'hk', '852'],
  ['Hungary', 'hu', '36'],
  ['Iceland', 'is', '354'],
  ['India', 'in', '91'],
  ['Indonesia', 'id', '62'],
  ['Iran', 'ir', '98'],
  ['Iraq', 'iq', '964'],
  ['Ireland', 'ie', '353'],
  ['Isle of Man', 'im', '44'],
  ['Israel', 'il', '972'],
  ['Italy', 'it', '39'],
  ['Jamaica', 'jm', '1876'],
  ['Japan', 'jp', '81'],
  ['Jersey', 'je', '44'],
  ['Jordan', 'jo', '962'],
  ['Kazakhstan', 'kz', '7'],
  ['Kenya', 'ke', '254'],
  ['Kiribati', 'ki', '686'],
  ['Kosovo', 'xk', '383'],
  ['Kuwait', 'kw', '965'],
  ['Kyrgyzstan', 'kg', '996'],
  ['Laos', 'la', '856'],
  ['Latvia', 'lv', '371'],
  ['Lebanon', 'lb', '961'],
  ['Lesotho', 'ls', '266'],
  ['Liberia', 'lr', '231'],
  ['Libya', 'ly', '218'],
  ['Liechtenstein', 'li', '423'],
  ['Lithuania', 'lt', '370'],
  ['Luxembourg', 'lu', '352'],
  ['Macau', 'mo', '853'],
  ['Macedonia', 'mk', '389'],
  ['Madagascar', 'mg', '261'],
  ['Malawi', 'mw', '265'],
  ['Malaysia', 'my', '60'],
  ['Maldives', 'mv', '960'],
  ['Mali', 'ml', '223'],
  ['Malta', 'mt', '356'],
  ['Marshall Islands', 'mh', '692'],
  ['Martinique', 'mq', '596'],
  ['Mauritania', 'mr', '222'],
  ['Mauritius', 'mu', '230'],
  ['Mayotte', 'yt', '262'],
  ['Mexico', 'mx', '52'],
  ['Micronesia', 'fm', '691'],
  ['Moldova', 'md', '373'],
  ['Monaco', 'mc', '377'],
  ['Mongolia', 'mn', '976'],
  ['Montenegro', 'me', '382'],
  ['Montserrat', 'ms', '1664'],
  ['Morocco', 'ma', '212'],
  ['Mozambique', 'mz', '258'],
  ['Myanmar (Burma)', 'mm', '95'],
  ['Namibia', 'na', '264'],
  ['Nauru', 'nr', '674'],
  ['Nepal', 'np', '977'],
  ['Netherlands', 'nl', '31'],
  ['New Caledonia', 'nc', '687'],
  ['New Zealand', 'nz', '64'],
  ['Nicaragua', 'ni', '505'],
  ['Niger', 'ne', '227'],
  ['Nigeria', 'ng', '234'],
  ['Niue', 'nu', '683'],
  ['Norfolk Island', 'nf', '672'],
  ['North Korea', 'kp', '850'],
  ['Northern Mariana Islands', 'mp', '1670'],
  ['Norway', 'no', '47'],
  ['Oman', 'om', '968'],
  ['Pakistan', 'pk', '92'],
  ['Palau', 'pw', '680'],
  ['Palestine', 'ps', '970'],
  ['Panama', 'pa', '507'],
  ['Papua New Guinea', 'pg', '675'],
  ['Paraguay', 'py', '595'],
  ['Peru', 'pe', '51'],
  ['Philippines', 'ph', '63'],
  ['Poland', 'pl', '48'],
  ['Portugal', 'pt', '351'],
  ['Puerto Rico', 'pr', '1'],
  ['Qatar', 'qa', '974'],
  ['Réunion', 're', '262'],
  ['Romania', 'ro', '40'],
  ['Russia', 'ru', '7'],
  ['Rwanda', 'rw', '250'],
  ['Saint Barthélemy', 'bl', '590'],
  ['Saint Helena', 'sh', '290'],
  ['Saint Kitts and Nevis', 'kn', '1869'],
  ['Saint Lucia', 'lc', '1758'],
  ['Saint Martin', 'mf', '590'],
  ['Saint Pierre and Miquelon', 'pm', '508'],
  ['Saint Vincent and the Grenadines', 'vc', '1784'],
  ['Samoa', 'ws', '685'],
  ['San Marino', 'sm', '378'],
  ['São Tomé and Príncipe', 'st', '239'],
  ['Saudi Arabia', 'sa', '966'],
  ['Senegal', 'sn', '221'],
  ['Serbia', 'rs', '381'],
  ['Seychelles', 'sc', '248'],
  ['Sierra Leone', 'sl', '232'],
  ['Singapore', 'sg', '65'],
  ['Sint Maarten', 'sx', '1721'],
  ['Slovakia', 'sk', '421'],
  ['Slovenia', 'si', '386'],
  ['Solomon Islands', 'sb', '677'],
  ['Somalia', 'so', '252'],
  ['South Africa', 'za', '27'],
  ['South Korea', 'kr', '82'],
  ['South Sudan', 'ss', '211'],
  ['Spain', 'es', '34'],
  ['Sri Lanka', 'lk', '94'],
  ['Sudan', 'sd', '249'],
  ['Suriname', 'sr', '597'],
  ['Svalbard and Jan Mayen', 'sj', '47'],
  ['Swaziland', 'sz', '268'],
  ['Sweden', 'se', '46'],
  ['Switzerland', 'ch', '41'],
  ['Syria', 'sy', '963'],
  ['Taiwan', 'tw', '886'],
  ['Tajikistan', 'tj', '992'],
  ['Tanzania', 'tz', '255'],
  ['Thailand', 'th', '66'],
  ['Timor-Leste', 'tl', '670'],
  ['Togo', 'tg', '228'],
  ['Tokelau', 'tk', '690'],
  ['Tonga', 'to', '676'],
  ['Trinidad and Tobago', 'tt', '1868'],
  ['Tunisia', 'tn', '216'],
  ['Turkey', 'tr', '90'],
  ['Turkmenistan', 'tm', '993'],
  ['Turks and Caicos Islands', 'tc', '1649'],
  ['Tuvalu', 'tv', '688'],
  ['U.S. Virgin Islands', 'vi', '1340'],
  ['Uganda', 'ug', '256'],
  ['Ukraine', 'ua', '380'],
  ['United Arab Emirates', 'ae', '971'],
  ['United Kingdom', 'gb', '44'],
  ['United States', 'us', '1'],
  ['Uruguay', 'uy', '598'],
  ['Uzbekistan', 'uz', '998'],
  ['Vanuatu', 'vu', '678'],
  ['Vatican City', 'va', '39'],
  ['Venezuela', 've', '58'],
  ['Vietnam', 'vn', '84'],
  ['Wallis and Futuna', 'wf', '681'],
  ['Western Sahara', 'eh', '212'],
  ['Yemen', 'ye', '967'],
  ['Zambia', 'zm', '260'],
  ['Zimbabwe', 'zw', '263'],
  ['Åland Islands', 'ax', '358']
]

export default {
  name: 'SmsNotifications',

  components: {
    SavingAnimation,
    MazPhoneNumberInput,
  },

  props: {
    errorMessages: {
      type: Object,
      required: true,
    },
    saving: {
      type: Object,
      required: true,
    },
    user: {
      type: Object,
      required: true,
    },
    twilioEnabled: {
      type: Boolean,
      default: false,
    },
    availableCountryCodes: {
      type: Array,
      default: () => [],
    },
  },

  methods: {
    updatePhone(data) {
      if (this.user.phone_number !== data.nationalNumber && data.isValid) {
        // update, valid value
        this.user.phone_country_code = data.countryCallingCode
        this.user.phone_number = data.nationalNumber
        this.$emit('updateSetting', 'phone_number')
      } else if (this.user.phone_number && !data.nationalNumber && data.countryCode) {
        // update, empty phone
        this.user.phone_country_code = null
        this.user.phone_number = null
        this.$emit('updateSetting', 'phone_number')
      }
    }
  },

  computed: {
    onlyCountries() {
      let result = allCountries
      if (this.availableCountryCodes.length) {
        result = allCountries.filter(country => this.availableCountryCodes.includes(parseInt(country[2])))
      }
      return result
    },
    countryCode() {
      if (this.user.phone_country_code) {
        const countries = this.onlyCountries.filter(country => country[2] === this.user.phone_country_code.replace('+', ''))

        if (countries.length > 1) {
          // can't identify country
          return null
        } else if (countries.length === 1) {
          // identify country by country code
          return countries[0][1].toUpperCase()
        }
      }
      return null
    },
  },
}
</script>

<style lang="sass" scoped>
::v-deep .maz-phone-number-input
  --maz-text-color: rgb(var(--color-text-primary))
  --maz-icon-color: rgb(var(--color-divider))
  --maz-muted-color: rgb(var(--color-text-secondary))
  --maz-bg-color: rgb(var(--color-input-background))
  --maz-border-color: rgb(var(--color-divider))
  --maz-border-color-darken: rgb(var(--color-divider))
  --maz-border-radius: 0
  --maz-primary: rgb(var(--color-primary))
  --maz-primary-darken: rgb(var(--color-primary-variant))
  --maz-hover-color: rgb(var(--color-hover) / .075)
  --maz-hover-color-darken: rgb(var(--color-hover) / .05)
  --maz-success: rgb(var(--color-success))
  --maz-success-darker: rgb(var(--color-success-variant))

  button, .btn
    border-radius: 0

  .country-selector
    @media (max-width: 768px)
      $width: 7rem
      flex: 0 0 $width
      width: $width
      min-width: $width
      max-width: $width

      .maz-input__icon
        align-items: flex-end
</style>
