// Addresses that arrive in a page's query string, so anyone who sends the link chooses them.

// Opening one of these runs script in this page, or shows content the link's sender chose.
const SCRIPT_SCHEMES = ['javascript:', 'data:', 'vbscript:', 'blob:', 'filesystem:']
const WEB_SCHEMES = ['http:', 'https:']

// The address if it opens an app (such as mobileraker://obico) or a page on the same site as
// base; null otherwise. A web page elsewhere could belong to anyone who sent the link.
export const appOrSameOriginUrlOrNull = (url, base) => {
  try {
    const { protocol, origin } = new URL(url, base)
    if (SCRIPT_SCHEMES.includes(protocol)) {
      return null
    }
    if (WEB_SCHEMES.includes(protocol)) {
      return origin === new URL(base).origin ? url : null
    }
    return url
  } catch (e) {
    return null
  }
}

// The address if it is on the same site as base; null otherwise.
export const sameOriginUrlOrNull = (url, base) => {
  try {
    return new URL(url, base).origin === new URL(base).origin ? url : null
  } catch (e) {
    return null
  }
}
