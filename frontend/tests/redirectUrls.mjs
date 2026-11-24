import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

// Load this Vue ES module without changing the frontend package's module type.
const source = await readFile(new URL('../src/lib/redirect-urls.js', import.meta.url), 'utf8')
const { appOrSameOriginUrlOrNull, sameOriginUrlOrNull, webUrlOrNull } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`)
const page = 'https://app.obico.io/tunnels/new/?app=OctoApp'

// Where the tunnel authorization page may send the person: an app, or this site
for (const url of ['mobileraker://obico', 'greatapp://callback', 'octoapp:tunnel', '/tunnels/succeeded/', 'https://app.obico.io/x/']) {
  assert.equal(appOrSameOriginUrlOrNull(url, page), url)
}
// Web pages elsewhere, and addresses that would run script on this site, however they are written
for (const url of ['https://attacker.example/', 'HTTP://attacker.example', '//attacker.example/x', 'https://app.obico.io.attacker.example/',
  'http://app.obico.io/', 'https://app.obico.io:8443/', 'javascript:alert(1)', ' JavaScript:alert(1)', 'java\tscript:alert(1)',
  'data:text/html,<script>1</script>', 'vbscript:x', 'blob:https://attacker.example/1', null]) {
  assert.equal(appOrSameOriginUrlOrNull(url, page), null, String(url))
}

const tunnelPage = '/tunnels/new/?app=OctoApp&success_redirect_url=greatapp%3A%2F%2Fcallback'
assert.equal(sameOriginUrlOrNull(tunnelPage, page), tunnelPage)
for (const url of ['javascript:alert(1)', 'https://attacker.example/', '//attacker.example/x', null]) {
  assert.equal(sameOriginUrlOrNull(url, page), null, String(url))
}

// Printer event links: the plugins send documentation pages on other sites
for (const url of ['https://obico.io/docs/user-guides/webcam-feed-is-not-showing/', 'http://192.168.1.5/']) {
  assert.equal(webUrlOrNull(url), url)
}
for (const url of ['javascript:alert(1)', ' JavaScript:alert(1)', 'java\tscript:alert(1)', 'data:text/html,<script>1</script>', 'mobileraker://obico', '/printer_events/', '', null, undefined]) {
  assert.equal(webUrlOrNull(url), null, String(url))
}
console.log('redirect-urls ok')
