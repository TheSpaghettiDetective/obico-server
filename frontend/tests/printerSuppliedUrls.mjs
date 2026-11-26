import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

// Load this Vue ES module without changing the frontend package's module type.
const source = await readFile(new URL('../src/lib/printer-supplied-urls.js', import.meta.url), 'utf8')
const { discoverySecretUrl } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`)

// Discovered printers: OctoPrint announces its web port, moonraker-obico its handshake port (an int)
const device = { host_or_ip: '192.168.1.5', device_id: '9c55fc68df3183d371a00566447f01de', agent: 'Obico for OctoPrint' }
assert.equal(discoverySecretUrl({ ...device, port: 5000 }), 'http://192.168.1.5:5000/plugin/obico/grab-discovery-secret?device_id=9c55fc68df3183d371a00566447f01de')
assert.equal(discoverySecretUrl({ ...device, port: '46793' }), 'http://192.168.1.5:46793/plugin/obico/grab-discovery-secret?device_id=9c55fc68df3183d371a00566447f01de')
assert.equal(discoverySecretUrl({ ...device, port: undefined }), 'http://192.168.1.5:80/plugin/obico/grab-discovery-secret?device_id=9c55fc68df3183d371a00566447f01de')
assert.equal(discoverySecretUrl({ ...device, agent: undefined, port: 80 }), 'http://192.168.1.5:80/plugin/thespaghettidetective/grab-discovery-secret?device_id=9c55fc68df3183d371a00566447f01de')
assert.ok(discoverySecretUrl({ ...device, port: 80, device_id: 'a&b#c' }).endsWith('?device_id=a%26b%23c'))
// A port that would point the popup at another host, or put markup in the page
for (const port of ['80@attacker.example', '80/x?<img src=x onerror=alert(1)>', '99999', '-1', '80 ', 'abc']) {
  assert.equal(discoverySecretUrl({ ...device, port }), null, port)
}
console.log('printer-supplied-urls ok')
