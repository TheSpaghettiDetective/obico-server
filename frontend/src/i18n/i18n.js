import i18n from 'i18next';

import baseEn from './locales/en.json';
import baseZh from './locales/zh.json';
import baseptbr from './locales/ptbr.json';
import entBaseEn from './locales/ent_en.json';
import entBaseZh from './locales/ent_zh.json';
import entBaseptbr from './locales/ent_ptbr.sjon';

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
  'zh': {
    translation: {
      ...baseZh,
      ...entBaseZh
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
