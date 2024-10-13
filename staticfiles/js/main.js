if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js');
  });
}

Notification.requestPermission().then((result) => {
  if (result === 'granted') {
    // Setup push notification subscription
  }
});

navigator.serviceWorker.ready.then((registration) => {
  return registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
  });
});

let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  // Show your custom "Add to Home Screen" button here
});

// When your custom button is clicked:
btnAdd.addEventListener('click', (e) => {
  deferredPrompt.prompt();
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('User accepted the A2HS prompt');
    }
    deferredPrompt = null;
  });
});