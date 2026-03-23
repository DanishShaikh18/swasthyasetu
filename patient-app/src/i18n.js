import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import hi from './locales/hi.json'
import ta from './locales/ta.json'
import te from './locales/te.json'
import mr from './locales/mr.json'
import gu from './locales/gu.json'
import kn from './locales/kn.json'
import ml from './locales/ml.json'
import pa from './locales/pa.json'
import or_lang from './locales/or.json'

i18n.use(LanguageDetector).use(initReactI18next).init({
  resources: {
    en: { translation: en }, hi: { translation: hi },
    ta: { translation: ta }, te: { translation: te },
    mr: { translation: mr }, gu: { translation: gu },
    kn: { translation: kn }, ml: { translation: ml },
    pa: { translation: pa }, or: { translation: or_lang },
  },
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
