import i18n from 'i18next';

import baseEn from './base/en.json';
import baseZh from './base/zh.json';
import yumiEn from './yumi/en.json';
import yumiZh from './yumi/zh.json';
import mintionEn from './mintion/en.json';
import mintionZh from './mintion/zh.json';
import { syndicate } from '@src/lib/page-context'


const getCurrentSyndicate = () => {
  return syndicate().provider
};

const getLocalizationlanguage = () => {
  let language = 'en'
  if(window){
    let stragety = {
      'en': 'en',
      'zh-CN': 'zh',
    };
    const userLanguage = navigator.language || navigator.userLanguage ||'en';
    language = stragety[userLanguage] || 'en'
  }
  return language

}

const currentSyndicate = getCurrentSyndicate();
const language = getLocalizationlanguage()

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
    lng: `${language}_${currentSyndicate}`,
    fallbackLng: `${language}_base`,
    interpolation: {
      escapeValue: false,
    },
    debug: true,
  });

export default i18n;
