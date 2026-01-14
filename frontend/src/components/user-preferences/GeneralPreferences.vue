<template>
  <section class="personalization">
    <h2 class="section-title">{{ $t("General") }}</h2>
    <div class="form-group row mt-3">
      <label class="col-md-2 col-sm-3 col-form-label">{{ $t("Language") }}</label>
      <div class="col-sm-9 col-md-10">
        <b-form-select
          id="language-select"
          v-model="selectedLanguage"
          :options="languageOptions"
          class="form-control"
          @change="onLanguageChange"
        ></b-form-select>
        <div v-if="showLanguageChangeMessage" class="mt-2">
          <div class="alert alert-warning mb-0" role="alert">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            {{ $t("Language preference saved. Please refresh the page to apply the changes.") }}
          </div>
        </div>
      </div>
    </div>
    <div class="form-group row mt-3">
      <label class="col-md-2 col-sm-3 col-form-label">{{ $t("Printers") }}</label>
      <div class="col-sm-9 col-md-10 col-form-label">
        <div class="custom-control custom-checkbox form-check-inline system-theme-control">
          <input
            id="id_theme_system"
            v-model="redirectEnabled"
            type="checkbox"
            class="custom-control-input"
          />
          <label class="custom-control-label" for="id_theme_system">
            {{$t("Land directly on the printer control page if I have only 1 printer")}}
            <br />
            <span class="text-muted setting-description"
              >{{$t("This option will be ignored if you have multiple printers. In this case, you will always land on the printer overview page.")}}</span
            >
          </label>
        </div>
      </div>
      <a class="col-sm-9 col-md-10 col-form-label" href="/ent/printers/archived/"
        >{{ $t("View Archived Printers") }}</a
      >
    </div>
  </section>
</template>

<script>
import { getLocalPref, setLocalPref } from '@src/lib/pref'
import i18n from '@src/i18n/i18n.js'
import { language } from '@src/lib/page-context'

const normalizeLanguage = (lang) => {
  if (!lang) return 'en';

  // Normalize format (replace underscores with hyphens, lowercase for comparison)
  const normalized = lang.replace(/_/g, '-').toLowerCase();

  // Check if it's already one of our supported codes (case-insensitive)
  const supportedCodes = {
    'en': 'en',
    'zh-cn': 'zh-CN',
    'zh-tw': 'zh-TW',
    'ca': 'ca',
    'cs': 'cs',
    'de': 'de',
    'es': 'es',
    'fr': 'fr',
    'hu': 'hu',
    'it': 'it',
    'ja': 'ja',
    'ko': 'ko',
    'nl': 'nl',
    'pl': 'pl',
    'pt-br': 'pt-BR',
    'ru': 'ru',
    'sv': 'sv',
    'tr': 'tr',
    'uk': 'uk',
  };

  if (supportedCodes[normalized]) {
    return supportedCodes[normalized];
  }

  // Handle Chinese variants
  if (normalized.startsWith('zh')) {
    if (normalized.includes('hant') || normalized.includes('tw') || normalized.includes('traditional')) {
      return 'zh-TW';
    }
    return 'zh-CN';
  }

  // Extract base language code (e.g., "en-US" -> "en", "pt-BR" -> "pt")
  const baseLang = normalized.split('-')[0];

  // Map base language codes to our supported codes
  const langMap = {
    'en': 'en',
    'ca': 'ca',
    'cs': 'cs',
    'de': 'de',
    'es': 'es',
    'fr': 'fr',
    'hu': 'hu',
    'it': 'it',
    'ja': 'ja',
    'ko': 'ko',
    'nl': 'nl',
    'pl': 'pl',
    'pt': 'pt-BR', // Portuguese defaults to Brazilian Portuguese
    'ru': 'ru',
    'sv': 'sv',
    'tr': 'tr',
    'uk': 'uk',
  };

  return langMap[baseLang] || 'en';
};

const getCurrentLanguage = () => {
  // First check i18n's current language (which already handles localStorage)
  const i18nLang = i18n.language;
  if (i18nLang) {
    return normalizeLanguage(i18nLang);
  }

  // Fall back to saved preference
  const savedLanguage = getLocalPref('user-language', null);
  if (savedLanguage) {
    return normalizeLanguage(savedLanguage);
  }

  // Finally fall back to backend page context
  const backendLang = language();
  return normalizeLanguage(backendLang);
};

const LANGUAGE_OPTIONS = [
  { value: 'en', text: 'English' },
  { value: 'zh-CN', text: '简体中文 (Simplified Chinese)' },
  { value: 'zh-TW', text: '繁體中文 (Traditional Chinese)' },
  { value: 'ca', text: 'Català (Catalan)' },
  { value: 'cs', text: 'Čeština (Czech)' },
  { value: 'de', text: 'Deutsch (German)' },
  { value: 'es', text: 'Español (Spanish)' },
  { value: 'fr', text: 'Français (French)' },
  { value: 'hu', text: 'Magyar (Hungarian)' },
  { value: 'it', text: 'Italiano (Italian)' },
  { value: 'ja', text: '日本語 (Japanese)' },
  { value: 'ko', text: '한국어 (Korean)' },
  { value: 'nl', text: 'Nederlands (Dutch)' },
  { value: 'pl', text: 'Polski (Polish)' },
  { value: 'pt-BR', text: 'Português (Brasil) (Brazilian Portuguese)' },
  { value: 'ru', text: 'Русский (Russian)' },
  { value: 'sv', text: 'Svenska (Swedish)' },
  { value: 'tr', text: 'Türkçe (Turkish)' },
  { value: 'uk', text: 'Українська (Ukrainian)' },
];

export default {
  name: 'GeneralPreferences',

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
  },

  data() {
    return {
      redirectEnabled: true,
      selectedLanguage: getCurrentLanguage(),
      languageOptions: LANGUAGE_OPTIONS,
      showLanguageChangeMessage: false,
    }
  },

  watch: {
    redirectEnabled: function (newVal, prevVal) {
      setLocalPref('single-printer-redirect-enabled', newVal)
    },
  },

  created() {
    this.redirectEnabled = getLocalPref('single-printer-redirect-enabled', true)
    this.selectedLanguage = getCurrentLanguage()
  },

  methods: {
    onLanguageChange(newLanguage) {
      if (!newLanguage) return

      const previousLanguage = getLocalPref('user-language', null)

      // Only show message if language actually changed
      if (previousLanguage !== newLanguage) {
        setLocalPref('user-language', newLanguage)
        this.showLanguageChangeMessage = true

        // Hide message after 10 seconds
        setTimeout(() => {
          this.showLanguageChangeMessage = false
        }, 10000)
      }
    },
  },
}
</script>
