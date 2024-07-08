---
title: Super Detection API
---

The APIs documented on this page are called "super APIs" because they are authenticated by partner's "super auth token".

## Authentication {#authentication}

All APIs are authenticated by the authentication token in the HTTP request header:

`Authorization: Token XXX`

![](/img/developer-guides/super-api-token.png)

:::tip
Please contact Obico team to obtain your super auth token.
:::

## Endpoint {#endpoint}

- `https://app.obico.io/`. Production endpoint. Please use this endpoint unless instructed by the Obico team differently.
- `https://app-stg.obico.io/`. Staging endpoint. Please don't use unless instructed by the Obico team.

## POST `/ent/partners/api/predict/` {#post-entpartnersapipredict}

### Request {#request}

This POST request should be sent as `multipart/form-data` format.

![](/img/developer-guides/postman-form-data-format.png)


#### Query parameters {#query-parameters}

- `printer_id`: A id that can uniquely identify the printer within your system. Max 256 characters.
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

#### Status code: `401` {#status-code-401}

Super auth_token is not valid. Contact Obico team member.

#### Body {#body-3}

```
{
  "error": "Invalid or Inactive Token",
  "is_authenticated": "False"
}
```

#### Status code: `429` {#status-code-429}

API request was NOT processed successfully because of rate throttling. Contact Obico team member to increase your rate limit.

#### Body {#body-2}

```
{
  "error": "You are running too hot! Take it easy buddy..."
}
```
