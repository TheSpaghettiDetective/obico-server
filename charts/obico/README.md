# obico

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 2026.1.20](https://img.shields.io/badge/AppVersion-2026.1.20-informational?style=flat-square)

Self-hosted Obico server for AI-powered 3D printer monitoring (OctoPrint/Klipper)

**Homepage:** <https://www.obico.io/>

## About

[Obico](https://www.obico.io/) (formerly The Spaghetti Detective) is a self-hosted server that adds remote access, webcam streaming and AI-powered failure detection to OctoPrint and Klipper 3D printers.

This chart deploys the full stack:

* **web** — Django application served by Daphne (API, frontend, websockets)
* **tasks** — Celery worker + beat scheduler (runs in the same pod as web)
* **ml-api** — Flask/Gunicorn AI inference service for print-failure detection
* **redis** — bundled Celery broker / Django Channels layer / cache

## Images

Obico's docker-compose builds the server images from source. This chart consumes prebuilt, tagged equivalents produced by the repository's own workflow (`.github/workflows/build-images.yaml`), which builds from the release branch and publishes to GHCR:

* `obico-web` — Django/Daphne app + Celery worker
* `obico-ml-api-cpu` — slim CPU inference image (chart default)
* `obico-ml-api-gpu` — CUDA inference image for GPU nodes

By default the chart pulls the `release` moving tag — the latest images built from the release branch at deploy time. Because that tag moves and `pullPolicy` defaults to `IfNotPresent`, already-running pods keep their pulled image until they restart. For a reproducible deployment, pin `image.*.tag`: `sha-<short>` is immutable per commit, while a CalVer like `2026.7.1` is day-granular (it moves if two commits land the same UTC day). Alternatively set the image `pullPolicy` to `Always` to re-pull on every pod start.

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| lexfrei | <f@lex.la> | <https://github.com/lexfrei> |

## Source Code

* <https://github.com/TheSpaghettiDetective/obico-server/>

## Requirements

Kubernetes: `>=1.21.0-0`

## Installing the Chart

```bash
# From a checkout of this repository
helm install obico ./charts/obico

# With custom values
helm install obico ./charts/obico --values my-values.yaml
```

## Uninstalling the Chart

```bash
helm uninstall obico
```

The data and media PVCs are annotated with `helm.sh/resource-policy: keep` and survive uninstall. Delete them manually if you no longer need the data.

## Secret key (read before using GitOps)

Obico needs a stable Django `SECRET_KEY`. Rotating it logs every user out and breaks signed tokens. Leaving `obico.secretKey` empty is only safe for a throwaway `helm install`: the empty-value fallback reuses the live Secret on upgrades, but **regenerates the key on every render-only path** — `helm template`, `--dry-run`, `helm diff` and ArgoCD (which renders with `helm template` and never reads the cluster). Under ArgoCD this rotates the key on every sync.

For GitOps, do one of the following:

```yaml
# Set a stable key directly (e.g. openssl rand -base64 48)
obico:
  secretKey: "your-long-random-string"
```

```yaml
# Or reference a Secret you manage (sealed-secrets, external-secrets, ...)
# It must contain DJANGO_SECRET_KEY and any other sensitive env vars.
obico:
  existingSecret: obico-secrets
```

## Database

The default configuration uses SQLite on the data volume so the chart installs with no external dependencies. **SQLite is for evaluation only:** the web server and the Celery worker are separate processes writing the same database file, so under real load they hit `database is locked` errors. Upstream Obico ships PostgreSQL only. For anything beyond a quick try-out, point `database.url` at an external PostgreSQL, reference a Secret holding the full DSN, or compose the DSN from parts with the password kept in a Secret:

```yaml
# Plain connection string
database:
  url: "postgresql://obico:password@postgres:5432/obico"
```

```yaml
# Connection string from an existing Secret
database:
  existingSecret: obico-db
  existingSecretKey: DATABASE_URL
```

```yaml
# Compose the DSN from parts, with the password kept in a Secret. Point host at a
# connection pooler (e.g. a CloudNativePG Pooler / PgBouncer) to multiplex many
# app connections onto a few server connections. Mutually exclusive with
# existingSecret; the password is used verbatim and must be URL-safe.
database:
  host: obico-db-pooler
  port: 5432
  name: obico
  user: obico
  passwordSecret: obico-db-app
  passwordSecretKey: password
```

When `host` points at a connection pooler, run the pooler in **transaction** pooling mode, not session. Obico keeps connections open (Django `CONN_MAX_AGE=600`), so in session mode every idle connection pins one server connection and the pool is exhausted at zero query load — the app then stalls waiting for a connection that never frees. Transaction mode holds a server connection only for the duration of a transaction, so idle clients cost nothing. Obico is safe in transaction mode for the workloads this chart runs: its Channels layer runs on Redis (no PostgreSQL `LISTEN`/`NOTIFY`), and the web server and Celery worker issue no server-side cursors. (The only `QuerySet.iterator()` caller in the codebase is the `extract_prints_from_hist` management command, which this chart never runs; if you run it by hand against the pooler, expect cursor errors.) For a CloudNativePG `Pooler` this is `spec.pgbouncer.poolMode: transaction`.

## Exposing the Web UI

Either classic Ingress or Gateway API (HTTPRoute) can be used. Remember to set `obico.siteUsesHttps=true` when serving over HTTPS — Django 4 rejects HTTPS form posts (login, signup, admin) from untrusted origins. The chart derives `CSRF_TRUSTED_ORIGINS` automatically from the enabled ingress hosts / HTTPRoute hostnames using that scheme; override with `obico.csrfTrustedOrigins` if you front the app with a different hostname.

```yaml
# Ingress
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: obico.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: obico-tls
      hosts:
        - obico.example.com
obico:
  siteUsesHttps: true
```

```yaml
# Gateway API
httpRoute:
  enabled: true
  parentRefs:
    - name: my-gateway
      namespace: gateway-system
  hostnames:
    - obico.example.com
obico:
  siteUsesHttps: true
```

## Scaling notes

The web pod runs a single replica because the default SQLite database lives on a ReadWriteOnce volume. It uses the `Recreate` update strategy, so every upgrade or config change tears the pod down before starting the new one — expect a brief outage on each rollout. To run multiple replicas, use an external PostgreSQL and a ReadWriteMany media volume (NFS, Longhorn RWX, CephFS, EFS, ...).

## Bundled Redis

The bundled Redis (`redis.enabled: true`) is a minimal, **unauthenticated** single instance intended for in-cluster use only. Do not expose it outside the cluster. For a hardened or shared Redis, set `redis.enabled: false` and point `redis.externalUrl` at your own instance.

## ML inference image (CPU / GPU)

The `ml-api` service ships as two images built from the same source:

* **CPU (default)** — `obico-ml-api-cpu`, a slim image that runs failure detection on the CPU via ONNX Runtime. No CUDA layers and no NVIDIA toolchain, an order of magnitude smaller than the GPU image. This is what the chart deploys by default and it runs on any node.
* **GPU** — `obico-ml-api-gpu`, the CUDA image for NVIDIA GPU inference. Much larger, since the CUDA / cuDNN runtime ships inside it.

Most self-hosted deployments run CPU inference and should keep the default. Enable the GPU image only if you have an NVIDIA GPU with the device plugin configured:

```yaml
mlApi:
  gpu: true
  # Adjust for non-NVIDIA / MIG / time-sliced GPUs.
  gpuResources:
    nvidia.com/gpu: 1
```

When `gpu` is true the chart uses the CUDA image and adds `gpuResources` to the container limits, so the scheduler places the pod on a GPU node.

To skip AI failure detection entirely, set `mlApi.enabled: false`. Obico still calls the ML API for any printer that has detection enabled, so when you disable the bundled ml-api either turn detection off on every printer or point `mlApi.externalHost` at an external instance — otherwise those picture uploads will error.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| database | object | `{"existingSecret":"","existingSecretKey":"DATABASE_URL","host":"","name":"","passwordSecret":"","passwordSecretKey":"password","port":5432,"url":"sqlite:////data/db.sqlite3","user":""}` | Database configuration. Defaults to SQLite on the data volume. WARNING: SQLite is for evaluation only. The server and the Celery worker run as separate processes writing the same file, so under load they will hit "database is locked" errors. Upstream ships PostgreSQL only. For any real use set url to an external postgresql:// DSN, or reference a Secret via existingSecret/existingSecretKey. |
| database.existingSecret | string | `""` | Use a key from an existing Secret for the full DATABASE_URL instead of url |
| database.existingSecretKey | string | `"DATABASE_URL"` | Key inside existingSecret holding the DATABASE_URL value |
| database.host | string | `""` | PostgreSQL host. When set, DATABASE_URL is composed from the fields below and the password is injected from passwordSecret at runtime (so it never lands in the ConfigMap or in git). Mutually exclusive with existingSecret. Point this at a connection pooler service (e.g. a CloudNativePG Pooler / PgBouncer) to multiplex many app connections onto few server connections. Run the pooler in TRANSACTION mode: Obico keeps connections open (CONN_MAX_AGE=600), so session mode pins idle connections and exhausts the pool (see the Database section of the README). The password must be URL-safe; the chart does not URL-encode it. |
| database.name | string | `""` | PostgreSQL database name (compose mode; required when host is set) |
| database.passwordSecret | string | `""` | Name of an existing Secret holding the PostgreSQL password (compose mode; required when host is set) |
| database.passwordSecretKey | string | `"password"` | Key inside passwordSecret holding the password |
| database.port | int | `5432` | PostgreSQL port (compose mode) |
| database.url | string | `"sqlite:////data/db.sqlite3"` | Database connection string (Django DATABASE_URL). Used only when neither existingSecret nor host is set. |
| database.user | string | `""` | PostgreSQL user (compose mode; required when host is set) |
| fullnameOverride | string | `""` |  |
| httpRoute | object | `{"annotations":{},"enabled":false,"hostnames":["obico.example.com"],"parentRefs":[{"name":"gateway","namespace":"gateway-system"}],"rules":[{"matches":[{"path":{"type":"PathPrefix","value":"/"}}]}]}` | HTTPRoute configuration (Gateway API) |
| httpRoute.hostnames | list | `["obico.example.com"]` | Hostnames for the route |
| httpRoute.parentRefs | list | `[{"name":"gateway","namespace":"gateway-system"}]` | Parent Gateway references |
| httpRoute.rules | list | `[{"matches":[{"path":{"type":"PathPrefix","value":"/"}}]}]` | Routing rules |
| image | object | `{"mlApi":{"cpu":{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-cpu","tag":""},"gpu":{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-gpu","tag":""},"pullPolicy":"IfNotPresent"},"web":{"pullPolicy":"IfNotPresent","repository":"ghcr.io/thespaghettidetective/obico-web","tag":""}}` | Container images. Built from obico-server source by the in-repo workflow (.github/workflows/build-images.yaml) and published to GHCR under the repository owner's namespace (ghcr.io/thespaghettidetective/* upstream). Each tag defaults to the "release" moving tag the workflow publishes on the release branch; pin a specific tag (a CalVer like 2026.7.1 or sha-<short>) for reproducibility. |
| image.mlApi | object | `{"cpu":{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-cpu","tag":""},"gpu":{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-gpu","tag":""},"pullPolicy":"IfNotPresent"}` | ML inference API images. Two variants are published from the same source: a slim CPU-only image (default) and a CUDA image for GPU inference. mlApi.gpu selects which one runs; configure each variant independently. |
| image.mlApi.cpu | object | `{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-cpu","tag":""}` | CPU-only inference image (slim). Used when mlApi.gpu is false. |
| image.mlApi.cpu.tag | string | `""` | Overrides the CPU image tag whose default is the "release" moving tag |
| image.mlApi.gpu | object | `{"repository":"ghcr.io/thespaghettidetective/obico-ml-api-gpu","tag":""}` | CUDA inference image (large). Used when mlApi.gpu is true. |
| image.mlApi.gpu.tag | string | `""` | Overrides the GPU image tag whose default is the "release" moving tag |
| image.web | object | `{"pullPolicy":"IfNotPresent","repository":"ghcr.io/thespaghettidetective/obico-web","tag":""}` | Web application image (Django + Celery) |
| image.web.tag | string | `""` | Overrides the image tag whose default is the "release" moving tag |
| imagePullSecrets | list | `[]` |  |
| ingress | object | `{"annotations":{},"className":"","enabled":false,"hosts":[{"host":"obico.example.com","paths":[{"path":"/","pathType":"Prefix"}]}],"tls":[{"hosts":["obico.example.com"],"secretName":"obico-tls"}]}` | Ingress configuration |
| mlApi | object | `{"command":["gunicorn","--bind=0.0.0.0:3333","--workers=1","--access-logfile=-","wsgi"],"enabled":true,"externalHost":"","gpu":false,"gpuResources":{"nvidia.com/gpu":1},"replicaCount":1,"resources":{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"1Gi"}},"securityContext":{}}` | ML inference API (AI failure detection). Can be disabled. |
| mlApi.command | list | `["gunicorn","--bind=0.0.0.0:3333","--workers=1","--access-logfile=-","wsgi"]` | Command for the gunicorn inference server |
| mlApi.enabled | bool | `true` | Deploy the ML inference API |
| mlApi.externalHost | string | `""` | External ML inference API URL, used when enabled is false. Obico still calls the ML API for prints that have AI detection on, so if you disable the bundled ml-api, either point this at an external instance (e.g. http://ml-api:3333) or make sure AI detection is off on every printer — otherwise picture uploads that request detection will error. |
| mlApi.gpu | bool | `false` | Run the CUDA (GPU) inference image instead of the slim CPU default. When true the ml-api container uses image.mlApi.gpu and requests the accelerator from gpuResources; requires an NVIDIA GPU and device plugin on the node. The CPU image works everywhere and is far smaller, so leave this false unless you actually have a GPU. |
| mlApi.gpuResources | object | `{"nvidia.com/gpu":1}` | Accelerator resources merged into the ml-api container limits when gpu is true. Adjust for non-NVIDIA or MIG / time-sliced GPUs (e.g. nvidia.com/mig-1g.5gb: 1). |
| mlApi.replicaCount | int | `1` | Number of ml-api replicas |
| mlApi.resources | object | `{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"500m","memory":"1Gi"}}` | Resource requests/limits for the ml-api container |
| mlApi.securityContext | object | `{}` | Security context for the ml-api container. Left empty (image default = root) because the upstream CUDA-based ml-api image is not validated to run unprivileged (model cache and runtime expect root). Harden here once confirmed it runs as non-root in your environment. |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| obico | object | `{"csrfTrustedOrigins":[],"debug":false,"existingSecret":"","extraEnv":{},"extraSecretEnv":{},"secretKey":"","siteUsesHttps":false}` | Obico application configuration (rendered into the env ConfigMap/Secret) |
| obico.csrfTrustedOrigins | list | `[]` | CSRF trusted origins (Django 4+ rejects HTTPS POSTs from untrusted origins). Leave empty to auto-derive from the enabled ingress hosts / HTTPRoute hostnames using the scheme implied by siteUsesHttps. Set explicitly to override, e.g. ["https://obico.example.com"]. |
| obico.debug | bool | `false` | Enable Django debug mode (never enable in production) |
| obico.existingSecret | string | `""` | Reference a pre-created Secret for sensitive env (must contain DJANGO_SECRET_KEY and any other secret keys). When set, the chart does not create its own Secret and extraSecretEnv is ignored. Recommended for GitOps. |
| obico.extraEnv | object | `{}` | Extra non-sensitive environment variables (key/value) for web and tasks. Chart-managed keys (DATABASE_URL, REDIS_URL, ...) are rejected here. Example: EMAIL_HOST: smtp.example.com |
| obico.extraSecretEnv | object | `{}` | Extra sensitive environment variables (key/value) stored in the Secret. Example: EMAIL_HOST_PASSWORD: s3cr3t |
| obico.secretKey | string | `""` | Django SECRET_KEY. IMPORTANT: leave empty only for a quick `helm install` test. The empty-value fallback reuses the live Secret on upgrades but REGENERATES the key on any render-only path (helm template, --dry-run, helm diff, ArgoCD) — rotating it logs every user out and rolls the pod on every sync. For GitOps set a stable value here (e.g. `openssl rand -base64 48`) or use existingSecret below. |
| obico.siteUsesHttps | bool | `false` | Set to true when the site is served over HTTPS (behind a TLS ingress/gateway) |
| persistence | object | `{"data":{"accessMode":"ReadWriteOnce","enabled":true,"existingClaim":"","retain":true,"size":"1Gi","storageClassName":""},"media":{"accessMode":"ReadWriteOnce","enabled":true,"existingClaim":"","retain":true,"size":"10Gi","storageClassName":""}}` | Persistence configuration |
| persistence.data | object | `{"accessMode":"ReadWriteOnce","enabled":true,"existingClaim":"","retain":true,"size":"1Gi","storageClassName":""}` | Data volume (SQLite database and persistent data) |
| persistence.data.accessMode | string | `"ReadWriteOnce"` | Access mode |
| persistence.data.existingClaim | string | `""` | Use an existing PVC instead of creating one |
| persistence.data.retain | bool | `true` | Keep the PVC when the release is uninstalled |
| persistence.data.size | string | `"1Gi"` | Size of the volume |
| persistence.data.storageClassName | string | `""` | Storage class name |
| persistence.media | object | `{"accessMode":"ReadWriteOnce","enabled":true,"existingClaim":"","retain":true,"size":"10Gi","storageClassName":""}` | Media volume (user uploads, webcam frames, timelapses) |
| persistence.media.accessMode | string | `"ReadWriteOnce"` | Access mode |
| persistence.media.existingClaim | string | `""` | Use an existing PVC instead of creating one |
| persistence.media.retain | bool | `true` | Keep the PVC when the release is uninstalled |
| persistence.media.size | string | `"10Gi"` | Size of the volume |
| persistence.media.storageClassName | string | `""` | Storage class name |
| podAnnotations | object | `{}` | Pod annotations |
| podLabels | object | `{}` | Pod labels |
| podSecurityContext | object | `{"fsGroup":65534}` | Security context for the pod. fsGroup is load-bearing, not cosmetic: the server, tasks and migrate containers run as non-root (65534, see securityContext below), so the data and media volumes must be group-owned by that gid for them to write the SQLite DB and media files. It also lets the non-root server read the static assets generated by the root collectstatic init container. Keep them aligned. |
| redis | object | `{"enabled":true,"externalUrl":"","image":{"pullPolicy":"IfNotPresent","repository":"redis","tag":"8.8-alpine"},"resources":{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"50m","memory":"64Mi"}},"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]},"runAsNonRoot":true,"runAsUser":999}}` | Bundled Redis (Celery broker + Django Channels + cache) |
| redis.enabled | bool | `true` | Deploy a minimal in-cluster Redis. Disable to use an external Redis. |
| redis.externalUrl | string | `""` | External Redis URL, used when redis.enabled is false |
| redis.image | object | `{"pullPolicy":"IfNotPresent","repository":"redis","tag":"8.8-alpine"}` | Redis image (pinned; not tied to the chart appVersion) |
| redis.resources | object | `{"limits":{"cpu":"200m","memory":"256Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}` | Resource requests/limits for the redis container |
| redis.securityContext | object | `{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]},"runAsNonRoot":true,"runAsUser":999}` | Security context for the redis container |
| securityContext | object | `{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]},"runAsGroup":65534,"runAsNonRoot":true,"runAsUser":65534}` | Security context for the server, tasks and migrate containers |
| service | object | `{"mlApi":{"annotations":{},"port":3333,"type":"ClusterIP"},"web":{"annotations":{},"port":3334,"type":"ClusterIP"}}` | Service configuration |
| service.mlApi | object | `{"annotations":{},"port":3333,"type":"ClusterIP"}` | ML inference API service (internal) |
| service.mlApi.annotations | object | `{}` | Annotations for the ml-api service |
| service.mlApi.port | int | `3333` | HTTP port |
| service.mlApi.type | string | `"ClusterIP"` | Service type for the ml-api |
| service.web | object | `{"annotations":{},"port":3334,"type":"ClusterIP"}` | Web UI / API service (ClusterIP for Ingress/HTTPRoute) |
| service.web.annotations | object | `{}` | Annotations for the web service |
| service.web.port | int | `3334` | HTTP port |
| service.web.type | string | `"ClusterIP"` | Service type for the web UI |
| serviceAccount | object | `{"annotations":{},"create":true,"name":""}` | Service account configuration |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `""` | The name of the service account to use |
| tasks | object | `{"command":["celery","-A","config","worker","--beat","--schedule","/data/celerybeat-schedule","-l","info","-c","2","-Q","realtime,celery"],"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}}}` | Celery worker (runs in the same pod as the web server) |
| tasks.command | list | `["celery","-A","config","worker","--beat","--schedule","/data/celerybeat-schedule","-l","info","-c","2","-Q","realtime,celery"]` | Command for the Celery worker with the embedded beat scheduler. The beat schedule DB is written under /data (a writable, persistent volume) because the container runs as non-root and the image's /app is not writable; the default (celerybeat-schedule in the working directory) would crash beat. |
| tasks.resources | object | `{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"256Mi"}}` | Resource requests/limits for the tasks container |
| tolerations | list | `[]` |  |
| web | object | `{"command":["daphne","-b","0.0.0.0","-p","3334","config.routing:application"],"resources":{"limits":{"cpu":"1","memory":"1Gi"},"requests":{"cpu":"250m","memory":"512Mi"}}}` | Web pod configuration (server + tasks containers, plus init containers) |
| web.command | list | `["daphne","-b","0.0.0.0","-p","3334","config.routing:application"]` | Command for the Daphne ASGI server (serves API, frontend and websockets) |
| web.resources | object | `{"limits":{"cpu":"1","memory":"1Gi"},"requests":{"cpu":"250m","memory":"512Mi"}}` | Resource requests/limits for the server container |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
