self.addEventListener("push", (event) => {
  if (!(self.Notification && self.Notification.permission === "granted")) {
    return;
  }
  let data = event.data.json();
  const icon = "https://obico.io/img/favicon.png";
  const options = {
    body: data.message,
    icon,
    image: data.image,
    tag: data.tag,
    renotify: true,
    requireInteraction: true,
    data: {
      url: data.url
    }
  };
  self.registration.showNotification(data.title, options);
});

self.addEventListener("notificationClick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow(event.notification.data.url));
});
