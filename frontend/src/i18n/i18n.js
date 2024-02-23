import i18n from 'i18next';

import baseEn from './base/en.json';
import yumiEn from './yumi/en.json';
import { syndicate } from '@src/lib/page-context'


const getCurrentSyndicate = () => {
  return syndicate().provider
};

const currentSyndicate = getCurrentSyndicate();


const resources = {
  'en_base': {
    translation: baseEn,
  },
  'en_yumi': {
    translation: yumiEn,
  },
};

i18n
  .init({
    resources,
    lng: `en_${currentSyndicate}`,
    fallbackLng: 'en_base',
    interpolation: {
      escapeValue: false,
    },
    debug: true,
  });

export default i18n;
