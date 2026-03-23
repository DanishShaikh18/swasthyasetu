export function checkNetwork() {
  const conn = navigator.connection || navigator.mozConnection
  const isSlow = conn?.effectiveType === '2g' || conn?.effectiveType === 'slow-2g'
  if (isSlow) document.body.classList.add('low-bandwidth')
  return { isOnline: navigator.onLine, isSlow }
}

export function watchNetwork(onStatusChange) {
  window.addEventListener('online', () => onStatusChange(true))
  window.addEventListener('offline', () => onStatusChange(false))
}
