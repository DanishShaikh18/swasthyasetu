import { useState } from 'react'
import { useTranslation } from 'react-i18next'

const langCodeMap = {
  hi: 'hi-IN', en: 'en-IN', ta: 'ta-IN', te: 'te-IN',
  mr: 'mr-IN', gu: 'gu-IN', kn: 'kn-IN', ml: 'ml-IN',
  pa: 'pa-IN', or: 'or-IN',
}

export default function VoiceInput({ onResult, language = 'hi' }) {
  const [listening, setListening] = useState(false)
  const { t } = useTranslation()
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

  const startListening = () => {
    if (!SpeechRecognition) {
      alert('Voice input not supported in this browser')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang = langCodeMap[language] || 'hi-IN'
    recognition.continuous = false
    recognition.interimResults = false
    recognition.onstart = () => setListening(true)
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      onResult(transcript)
      setListening(false)
    }
    recognition.onerror = () => setListening(false)
    recognition.onend = () => setListening(false)
    recognition.start()
  }

  return (
    <button onClick={startListening} disabled={listening}
      className={`w-full py-4 rounded-xl text-base font-medium flex items-center justify-center gap-2 min-h-[52px] transition-all ${
        listening
          ? 'bg-urgency-red text-white animate-pulse'
          : 'bg-primary text-white hover:bg-primary-dark active:scale-95'
      }`}>
      {listening ? `🎤 ${t('symptoms.listening')}` : `🎤 ${t('symptoms.speak')}`}
    </button>
  )
}
