import i18n from 'i18next';

import baseEn from './locales/en.json';
import baseZhCN from './locales/zh-CN.json';
import baseZhTW from './locales/zh-TW.json';
import entBaseEn from './locales/ent_en.json';
import entBaseZhCN from './locales/ent_zh-CN.json';
import entBaseZhTW from './locales/ent_zh-TW.json';

import {language} from '@src/lib/page-context'

const getCurrentLanguage = () => {
  return language()
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
