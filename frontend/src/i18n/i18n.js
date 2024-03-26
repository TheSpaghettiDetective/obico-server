import i18n from 'i18next';

import baseEn from './base/en.json';
import baseZh from './base/zh.json';
import yumiEn from './yumi/en.json';
import yumiZh from './yumi/zh.json';
import mintionEn from './mintion/en.json';
import mintionZh from './mintion/zh.json';
import { syndicate ,language} from '@src/lib/page-context'

import entBaseEn from './base/ent_en.json';
import entBaseZh from './base/ent_zh.json';

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
    ...baseEn,
    ...entBaseEn
  },
  'zh_base': baseZh,
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
    lng: `zh_base`,
    fallbackLng: `zh_base`,
    interpolation: {
      escapeValue: false,
    },
    debug: true,
  });

export default i18n;
