import i18n from 'i18next';

import baseEn from './locales/en.json';
import baseZhCN from './locales/zh-CN.json';
import baseZhTW from './locales/zh-TW.json';
import baseCa from './locales/ca.json';
import baseCs from './locales/cs.json';
import baseDe from './locales/de.json';
import baseEs from './locales/es.json';
import baseFr from './locales/fr.json';
import baseHu from './locales/hu.json';
import baseIt from './locales/it.json';
import baseJa from './locales/ja.json';
import baseKo from './locales/ko.json';
import baseNl from './locales/nl.json';
import basePl from './locales/pl.json';
import basePtBR from './locales/pt-BR.json';
import baseRu from './locales/ru.json';
import baseSv from './locales/sv.json';
import baseTr from './locales/tr.json';
import baseUk from './locales/uk.json';

import entBaseEn from './locales/ent_en.json';
import entBaseZhCN from './locales/ent_zh-CN.json';
import entBaseZhTW from './locales/ent_zh-TW.json';
import entBaseCa from './locales/ent_ca.json';
import entBaseCs from './locales/ent_cs.json';
import entBaseDe from './locales/ent_de.json';
import entBaseEs from './locales/ent_es.json';
import entBaseFr from './locales/ent_fr.json';
import entBaseHu from './locales/ent_hu.json';
import entBaseIt from './locales/ent_it.json';
import entBaseJa from './locales/ent_ja.json';
import entBaseKo from './locales/ent_ko.json';
import entBaseNl from './locales/ent_nl.json';
import entBasePl from './locales/ent_pl.json';
import entBasePtBR from './locales/ent_pt-BR.json';
import entBaseRu from './locales/ent_ru.json';
import entBaseSv from './locales/ent_sv.json';
import entBaseTr from './locales/ent_tr.json';
import entBaseUk from './locales/ent_uk.json';

import {language} from '@src/lib/page-context'
import { getLocalPref } from '@src/lib/pref'

const getCurrentLanguage = () => {
  // Check for saved language preference first
  const savedLanguage = getLocalPref('user-language', null)
  if (savedLanguage) {
    return savedLanguage
  }

  // Fall back to backend page context
  const lang = language().replace(/_/g, '-');
  if (lang === 'zh') return 'zh-CN';
  if (lang === 'zh_Hans' || lang === 'zh-Hans') return 'zh-CN';
  if (lang === 'zh_Hant' || lang === 'zh-Hant') return 'zh-TW';
  return lang;
};

const currentLanguage = getCurrentLanguage()

const resources = {
  'en': {
    translation: {
      ...baseEn,
      ...entBaseEn
    }
  },
  'zh-CN': {
    translation: {
      ...baseZhCN,
      ...entBaseZhCN
    }
  },
  'zh-TW': {
    translation: {
      ...baseZhTW,
      ...entBaseZhTW
    }
  },
  'ca': {
    translation: {
      ...baseCa,
      ...entBaseCa
    }
  },
  'cs': {
    translation: {
      ...baseCs,
      ...entBaseCs
    }
  },
  'de': {
    translation: {
      ...baseDe,
      ...entBaseDe
    }
  },
  'es': {
    translation: {
      ...baseEs,
      ...entBaseEs
    }
  },
  'fr': {
    translation: {
      ...baseFr,
      ...entBaseFr
    }
  },
  'hu': {
    translation: {
      ...baseHu,
      ...entBaseHu
    }
  },
  'it': {
    translation: {
      ...baseIt,
      ...entBaseIt
    }
  },
  'ja': {
    translation: {
      ...baseJa,
      ...entBaseJa
    }
  },
  'ko': {
    translation: {
      ...baseKo,
      ...entBaseKo
    }
  },
  'nl': {
    translation: {
      ...baseNl,
      ...entBaseNl
    }
  },
  'pl': {
    translation: {
      ...basePl,
      ...entBasePl
    }
  },
  'pt-BR': {
    translation: {
      ...basePtBR,
      ...entBasePtBR
    }
  },
  'ru': {
    translation: {
      ...baseRu,
      ...entBaseRu
    }
  },
  'sv': {
    translation: {
      ...baseSv,
      ...entBaseSv
    }
  },
  'tr': {
    translation: {
      ...baseTr,
      ...entBaseTr
    }
  },
  'uk': {
    translation: {
      ...baseUk,
      ...entBaseUk
    }
  }
};

i18n
  .init({
    resources,
    lng: currentLanguage,
    fallbackLng: ['en'],
    interpolation: {
      escapeValue: false,
    },
    debug: true,
    nsSeparator:false
  });

export default i18n;
