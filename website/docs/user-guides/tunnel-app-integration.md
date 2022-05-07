---
id: tunnel-app-integration
title: Guide to integrate with OctoPrint Tunneling
---

## Acquire user authorization to use the tunnel

Example:

`https://app.obico.io/tunnels/new/?app=Great%20App&printer_id=12345&success_redirect_url=greatapp://callback`

### Address

`https://app.obico.io/tunnels/new/`

### Parameters

* `app`: Required. The name of your app.
* `printer_id`: Optional. If not provided, and the user has more than 1 printers in The Spaghetti Detective, the page will list all printers for the user to choose from.
* `success_redirect_url`: Optional. If not provided, the page will be redirected to `https://app.obico.io/tunnels/succeeded/` on successful authorization.

### Redirect on success

On a successful authorization, the page will be redirect to `{success_redirect_url}/?tunnel_endpoint=https://basic_auth_username:basic_auth_password@tunnel-domain.tunnels.app.obico.io`

Use `https://basic_auth_username:basic_auth_password@tunnel-domain.tunnels.app.obico.io` as endpoint to connect to OctoPrint.

This value will be designated as `TUNNEL_ENDPOINT` for the rest of this document.

## Special HTTP status code for tunnelled API calls

* `481`: Over free tunneling monthly cap.
* `482`: OctoPrint is not connected to The Spaghetti Detective server.
* `483`: OctoPrint is connected but timed out (30s)

## Other HTTP status code

* `401`: Unauthenticated request. This can be caused by:
    * User explicitly revoked the authorization.
    * User deleted the printer in The Spaghetti Detective.
    * User account is deleted or suspended in The Spaghetti Detective.


## Tunnel APIs

### Tunnel usage API

#### Endpoint

`{TUNNEL_ENDPOINT}/_tsd_/tunnelusage/`

#### Response

* `total`: Month-to-date usage. In bytes.
* `monthly_cap`: In bytes. -1 when the cap is unlimited (for Pro users, inculding the free trial).
* `reset_in_seconds`: Remaining time (in seconds) until the usage is reset.

### Webcam snapshot API

#### Endpoint

`{TUNNEL_ENDPOINT}/_tsd_/webcam/0/`

#### Response

* `snapshot`: The url to fetch the most recent webcam snapshot (in JEPG). No authentication is required.
