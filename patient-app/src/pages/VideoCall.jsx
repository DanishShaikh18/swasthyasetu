import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { joinVideoCall } from '../api/doctors'
import DailyIframe from '@daily-co/daily-js'

export default function VideoCall() {
  const { appointmentId } = useParams()
  const [status, setStatus] = useState('connecting')
  const [error, setError] = useState('')
  const containerRef = useRef(null)
  const callRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    startCall()
    return () => { callRef.current?.destroy() }
  }, [])

  const startCall = async () => {
    try {
      const res = await joinVideoCall(appointmentId)
      const { token, room_url } = res.data.data

      const callFrame = DailyIframe.createFrame(containerRef.current, {
        showLeaveButton: true, showFullscreenButton: true,
        iframeStyle: { width: '100%', height: '100%', border: 'none', borderRadius: '12px' },
      })
      callRef.current = callFrame
      callFrame.on('left-meeting', () => { setStatus('ended'); navigate(-1) })
      await callFrame.join({ url: room_url, token })
      setStatus('connected')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not join the call')
      setStatus('error')
    }
  }

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {status === 'connecting' && (
        <div className="flex-1 flex items-center justify-center text-white">
          <div className="text-center">
            <div className="text-4xl mb-4">📹</div>
            <p className="text-lg">Connecting to video call...</p>
          </div>
        </div>
      )}
      {status === 'error' && (
        <div className="flex-1 flex items-center justify-center text-white">
          <div className="text-center px-6">
            <p className="text-lg mb-2">Unable to join call</p>
            <p className="text-sm text-gray-400 mb-4">{error}</p>
            <button onClick={() => navigate(-1)} className="px-6 py-3 bg-primary rounded-xl min-h-[48px]">Go Back</button>
          </div>
        </div>
      )}
      <div ref={containerRef} className="flex-1" style={{ display: status === 'connected' ? 'block' : 'none' }} />
    </div>
  )
}
