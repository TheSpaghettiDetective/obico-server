# Obico Server Helm Charts

These helm charts exist as a replacement/alternative to the Docker Compose Configuration. They were developed using
[Rancher Desktop 1.10.0](https://github.com/rancher-sandbox/rancher-desktop)

## Docker Compose Differences

### Accessing Software

By default, the helm charts are configured for [http://obico.localhost](http://obico.localhost). Note that the port number is not required.

### Admin Access

The Admin is not accessible by default. In order do access it, you have two options. The port-forward method is the more secure method.

#### Port Forward

The simplest way is to run `kubectl port-forward $(kubectl get pod -l obico.deployment=web -o jsonpath='{.items[0].metadata.name}') 3334:3334`.

After the above command is ran, you can use [http://obico.localhost:3334/admin/](http://obico.localhost:3334/admin/) to access the admin as normal.

Once you are done, `CTRL+C` the port forward command to disable admin access.

#### IP Whitelist

As with the Docker Compose, you can whitelist IPs by adding additional addresses to the `application.ipWhitelist` array.

### DB Persistence

The DB is handled through volume mounts. This allows you some persistence. When running with the defaults, the volumes will
be deleted when helm-stop is ran, and you will loose all data. Alternatively, you can set `web.dbPvc.name` after creating your own PVC.

## Installation

### Quick Start

*Requires GNU `make` and either `wget` or `curl`*

This will launch the software with all the default configurations.

1. Open a terminal and navigate to the project.
2. Execute `cd helm`
3. Execute `make`
4. Execute `make` a second time.

### General Usage

- `make` or `make helm-start` - Start the Charts
- `make helm-stop` - Stop the Charts
- `make helm-restart` - Stop the Charts, Wait For The Charts To Fully Exit, Then Start The Charts Again.

### Advanced Configuration

#### bin/values-local.yaml

The first time you run the helm charts via `make`, it will create `bin/values-local.yaml`. Use this file to modify
basic configurations without the need for additional changes.

#### Secrets

The default configuration is considered insecure, but is good enough to get started. If you wish to properly configure
secret variables, create the appropriate K8S secret and set the `secret` key in the appropriate key.

##### Email

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-email
data:
  EMAIL_HOST: ''
  EMAIL_HOST_USER: ''
  EMAIL_HOST_PASSWORD: ''
  EMAIL_PORT: ''
  EMAIL_USE_TLS: ''
  DEFAULT_FROM_EMAIL: ''
```

##### Pushover

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-pushover
data:
  PUSHOVER_APP_TOKEN: ''
```


##### Slack

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-pushover
data:
  SLACK_CLIENT_ID: ''
  SLACK_CLIENT_SECRET: ''
```

##### Telegram

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-pushover
data:
  TELEGRAM_BOT_TOKEN: ''
```

##### Twilio

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-pushover
data:
  TWILIO_ACCOUNT_SID: ''
  TWILIO_AUTH_TOKEN: ''
  TWILIO_FROM_NUMBER: ''
```
