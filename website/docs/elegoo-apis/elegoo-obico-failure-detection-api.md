---
title: Elegoo-Obico Failure Detection API
unlisted: true
---

The APIs documented on this page are designed for Elegoo partners to detect print failures using Obico's AI-powered failure detection system.

## Authentication {#authentication}

Authentication is performed using device credentials passed as form data parameters:

- `serial_no`: The device serial number registered in the system
- `access_token`: The access token associated with the device

These credentials must be included in the POST request along with other parameters.

:::tip
Use the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) to manage device credentials before using the failure detection API.
:::

## Endpoint {#endpoint}

- `https://elegoo-app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://elegoo-app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.
- `https://elegoo-cn-app.elegoo.com.cn`. Production endpoint within China.
- `https://elegoo-cn-app-stg.elegoo.com.cn`. Staging endpoint within China.

## POST `/ent/partners/api/elegoo/predict/` {#post-entpartnersapielegoopredict}

### Request {#request}

This POST request should be sent as `multipart/form-data` format.

#### Form parameters {#form-parameters}

- `serial_no`: The device serial number. Required for authentication.
- `access_token`: The access token for the device. Required for authentication.
- `print_id`: A id that can uniquely identify the print within the printer it belongs. Max 256 characters.
- `img`: Snapshot from the webcam for failure detection. In JPEG format.

### Response {#response}

#### Status code: `200` {#status-code-200}

API request was processed successfully.

#### Body {#body}

```
{
  "result": {
    "p": 0,
    "temporal_stats": {
      "ewm_mean": 0,
      "rolling_mean_short": 0,
      "rolling_mean_long": 0,
      "prediction_num": 0,
      "prediction_num_lifetime": 0
    },
    "detections": [
        [0.541085422039032, [422.7984619140625, 236.30227661132812, 61.9364013671875, 74.49552917480469]],
        [0.43781569600105286, [426.05596923828125, 264.619140625, 42.386478424072266, 4.73854064941406]],
        [0.2545202076435089, [423.3209533691406, 238.6829071044922, 113.47953796386719, 135.73854064941406]],
        [0.20370429754257202, [456.3966369628906, 236.23785400390625, 39.029632568359375, 67.34481811523438]]
      ]
  }
}
```

- `p`: A number between 0 and 1.0. 0 means no failure is detected. 1 means the maximum confidence on predicting a print failure.
- `temporal_stats`: The temporal stats that may be useful in determining if a failure has actually occurred. These stats are important for smoothening the noises in failure detection. See the tip below for details.
    - `ewm_mean`: Exponentially weighted mean for `p`. EWM window span = 12.
    - `rolling_mean_short`: Short-term rolling mean for `p`. Rolling window span = 310. This rolling mean is reset to 0 when a new print starts.
    - `rolling_mean_long`: Long-term rolling mean for `p`. Rolling window span = 7200. This rolling mean is accumulated over the lifetime of the printer.
    - `prediction_num`: The number of predictions for the current print so far.
    - `prediction_num_lifetime`: The number of predictions for the life-time of the printer.
  - `detections`: A list of tuples. Each tuple is `[confidence, [xc, yc, w, h]]`.
    - `confidence`: Range: [0, 1], where 0 means not failure and 1.0 means the maximum confidence on predicting a print failure.
    - `[xc, yc, w, h]`: Rectangle of the detected area. `xc` and `yc` are the X and Y coordinates of the **center** of the rectangle. `w` and `h` are the width and hight of the rectangle.

:::tip
It's a good practice to use the temporal stats to smoothen out the noises in failure detection. Otherwise there may be excessive amount of false alarms.

In Obico open-source server, the way these temporal stats are used can be simplistically described as below:


- If `ewm_mean - rolling_mean_long < 0.36`: no failure.
- Else if `ewm_mean - rolling_mean_long > 0.99`: failure.
- Else if `ewm_mean - rolling_mean_long > 0.78`: maybe failure.
- Else if `ewm_mean > (rolling_mean_short - rolling_mean_long) * 3.8`: maybe failure.

:::

:::tip
All these "magic numbers", such as the rolling window sizes, or thresholds such as 0.36 or 0.78, should be considered as hyper-parameters. You are highly recommended to go through the hyper-parameters tuning process to find the optimal values for them.
:::

#### Status code: `400` {#status-code-400}

API request was NOT processed successfully for other reasons, such as missing required parameters.

#### Body {#body-1}

```
{
  "error": "Detailed error message"
}
```

Examples of error messages:
- `"Missing or invalid image"`
- `"print_id is required"`

#### Status code: `401` {#status-code-401}

Authentication failed. This can occur when:
- Missing `serial_no` or `access_token`
- Invalid credentials (including expired access tokens)

#### Body {#body-2}

```
{
  "error": "serial_no and access_token are required"
}
```

or

```
{
  "error": "Invalid credentials"
}
```


#### Status code: `429` {#status-code-429}

API request was NOT processed successfully because of rate throttling.

#### Body {#body-3}

```
{
  "error": "You are running too hot! Take it easy buddy..."
}
```

## Usage Example {#usage-example}

```bash
curl -X POST https://elegoo-app.obico.io/ent/partners/api/elegoo/predict/ \
  -F "serial_no=ELEGOO_DEVICE_001" \
  -F "access_token=your_access_token_here" \
  -F "print_id=print_456" \
  -F "img=@/path/to/snapshot.jpg"
```

:::tip
Make sure to register your device credentials using the [Elegoo-Obico Access Token API](./elegoo-obico-access-token.md) before calling the failure detection API.
:::

