// Addresses built from values a printer sends, so whoever controls the printer, or
// announces a fake one on the user's network, chooses them.

// The page on a discovered printer that hands the printer-setup wizard the device secret,
// or null when the device announced a port that is not a number. Only a port number is
// accepted, so the address stays on the device's private address and never names another host.
export const discoverySecretUrl = (device) => {
  const port = String(device.port || '80')
  if (!/^[0-9]{1,5}$/.test(port) || Number(port) > 65535) {
    return null
  }
  const pluginName = device.agent ? 'obico' : 'thespaghettidetective'
  const deviceId = encodeURIComponent(device.device_id)
  return `http://${device.host_or_ip}:${port}/plugin/${pluginName}/grab-discovery-secret?device_id=${deviceId}`
}
