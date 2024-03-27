self.addEventListener("push", (event) => {
  if (!(self.Notification && self.Notification.permission === "granted")) {
    return;
  }
  let data = event.data.json();
  const image = "https://www.obico.io/wwwimg/favicon.png";
  const options = {
    body: data.message,
    icon: image,
  };
  self.registration.showNotification(data.title, options);
});

// TODO
// self.addEventListener("notificationClick", (event) => {
//   event.notification.close();
//   event.waitUntil(self.clients.openWindow("https://app.obico.io"));
// });
