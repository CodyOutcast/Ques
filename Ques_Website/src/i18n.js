import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './i18n/en.json';
import cnTranslations from './i18n/cn.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: enTranslations,
      cn: cnTranslations
    },
    lng: 'en', // Default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
