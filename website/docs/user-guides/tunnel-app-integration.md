---
id: tunnel-app-integration
title: Guide to integrate with OctoPrint/Klipper Tunnel
---

## Acquire user authorization to use the tunnel {#acquire-user-authorization-to-use-the-tunnel}

Example:

`https://app.obico.io/tunnels/new/?app=Great%20App&printer_id=12345&success_redirect_url=greatapp://callback`

### Address {#address}

`https://app.obico.io/tunnels/new/`

#### HTTP Verb {#http-verb}

`GET`

### Parameters {#parameters}

- `app`: Required. The name of your app.
- `platform`: Optional. It can be "OctoPrint" or "Klipper". Default to "OctoPrint" if absent.
- `printer_id`: Optional. If not provided, and the user has more than 1 printers linked to his/her Obico account, the page will list all printers for the user to choose from.
- `success_redirect_url`: Optional. If not provided, the page will be redirected to `https://app.obico.io/tunnels/succeeded/` on successful authorization.

### Redirect on success {#redirect-on-success}

On a successful authorization, the page will be redirect to `{success_redirect_url}/?tunnel_endpoint=https://basic_auth_username:basic_auth_password@tunnel-domain.tunnels.app.obico.io`

Use `https://basic_auth_username:basic_auth_password@tunnel-domain.tunnels.app.obico.io` as endpoint to connect to OctoPrint/Klipper.

This value will be designated as `TUNNEL_ENDPOINT` for the rest of this document.

## Special HTTP status code for tunnelled API calls {#special-http-status-code-for-tunnelled-api-calls}

- `481`: Over free tunnel monthly data cap.
- `482`: Obico for OctoPrint/Klipper is not connected to the Obico server.
- `483`: Obico for OctoPrint/Klipper is connected but timed out (30s)

## Other HTTP status code {#other-http-status-code}

- `401`: Unauthenticated request. This can be caused by:
  - User explicitly revoked the authorization.
  - User deleted the printer in Obico.
  - User account is deleted or suspended in Obico.

## Tunnel APIs {#tunnel-apis}

### Tunnel usage API {#tunnel-usage-api}

#### HTTP Verb {#http-verb-1}

`GET`

#### Endpoint {#endpoint}

`{TUNNEL_ENDPOINT}/_tsd_/tunnelusage/`

#### Response {#response}

- `total`: Month-to-date usage. In bytes.
- `monthly_cap`: In bytes. -1 when the cap is unlimited (for Pro users, including the free trial).
- `reset_in_seconds`: Remaining time (in seconds) until the usage is reset.

### Webcam snapshot API {#webcam-snapshot-api}

#### HTTP Verb {#http-verb-2}

`GET`

#### Endpoint {#endpoint-1}

`{TUNNEL_ENDPOINT}/_tsd_/webcam/0/`

#### Response {#response-1}

- `snapshot`: The url to fetch the most recent webcam snapshot (in JPEG). No authentication is required.

### Failure prediction API {#failure-prediction-api}

#### HTTP Verb {#http-verb-3}

`GET`

#### Endpoint {#endpoint-2}

`{TUNNEL_ENDPOINT}/_tsd_/prediction/`

#### Response {#response-2}

- `normalized_p`: The prediction value in the range of [0,1). < 0.33: Low. 0.33 - 0.66: Medium. > 0.66: High.

### Printer System Info {#printer-system-info}

#### HTTP Verb {#http-verb-4}

`GET`

#### Endpoint {#endpoint}

`{TUNNEL_ENDPOINT}/_tsd_/dest_platform_info/`

Currently only Moonraker is supported.

#### Response {#response}

- `server_ip`: The IP address of the Moonraker server.
- `server_port`: The port the Moonraker server listens on.
- `linked_name`: The name the user gave to the printer in Obico.
