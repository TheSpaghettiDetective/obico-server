import i18n from 'i18next';

import baseEn from './base/en.json';
import baseZh from './base/zh.json';
import yumiEn from './yumi/en.json';
import yumiZh from './yumi/zh.json';
import mintionEn from './mintion/en.json';
import mintionZh from './mintion/zh.json';
import { syndicate ,language} from '@src/lib/page-context'


const getCurrentSyndicate = () => {
  return syndicate().provider
};
const getCurrentLanguage = () => {
  return language().provider
};


const currentSyndicate = getCurrentSyndicate();
const currentLanguage = getCurrentLanguage()


const resources = {
  'en_base': {
    translation: baseEn,
  },
  'zh_base': {
    translation: baseZh,
  },
  'en_yumi': {
    translation: yumiEn,
  },
  'zh_yumi': {
    translation: yumiZh,
  },
  'en_mintion': {
    translation: mintionEn,
  },
  'zh_mintion': {
    translation: mintionZh,
  },
};

i18n
  .init({
    resources,
    lng: `${currentLanguage}_${currentSyndicate}`,
    fallbackLng: `${currentLanguage}_base`,
    interpolation: {
      escapeValue: false,
    },
    debug: false,
  });

export default i18n;
