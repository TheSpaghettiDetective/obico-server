{{/*
Expand the name of the chart.
*/}}
{{- define "obico.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
Truncate at 56, not 63: templates append component suffixes (the longest is
"-ml-api", 7 chars) to this base name, and the result must stay within the
63-char Kubernetes DNS label limit. If the release name contains the chart
name it is used as the full name.
*/}}
{{- define "obico.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 56 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 56 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 56 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "obico.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "obico.labels" -}}
helm.sh/chart: {{ include "obico.chart" . }}
{{ include "obico.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels (shared across all components).
Per-component templates add app.kubernetes.io/component to disambiguate pods.
*/}}
{{- define "obico.selectorLabels" -}}
app.kubernetes.io/name: {{ include "obico.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "obico.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "obico.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Resolve the Redis URL: bundled service when redis.enabled, otherwise external.
*/}}
{{- define "obico.redisUrl" -}}
{{- if .Values.redis.enabled -}}
redis://{{ include "obico.fullname" . }}-redis:6379/0
{{- else if .Values.redis.externalUrl -}}
{{- .Values.redis.externalUrl -}}
{{- else -}}
{{- fail "redis.enabled is false: set redis.externalUrl to an external Redis connection string" -}}
{{- end -}}
{{- end }}

{{/*
Name of the Secret holding sensitive env (DJANGO_SECRET_KEY, ...).
Use a pre-created Secret when obico.existingSecret is set, otherwise the
chart-managed Secret named after the release.
*/}}
{{- define "obico.secretName" -}}
{{- if .Values.obico.existingSecret -}}
{{- .Values.obico.existingSecret -}}
{{- else -}}
{{- include "obico.fullname" . -}}
{{- end -}}
{{- end }}

{{/*
Resolve the Django SECRET_KEY for the chart-managed Secret.
Prefer an explicit value; otherwise reuse the key from an existing Secret so it
stays stable across live upgrades; otherwise generate a new random key.
NOTE: the lookup-based reuse only works during a live `helm install/upgrade`.
Render-only paths (helm template, --dry-run, helm diff, ArgoCD) cannot read the
cluster, so they regenerate the key on every render. For GitOps set
obico.secretKey explicitly or use obico.existingSecret.
*/}}
{{- define "obico.secretKey" -}}
{{- if .Values.obico.secretKey -}}
{{- .Values.obico.secretKey -}}
{{- else -}}
{{- $existing := lookup "v1" "Secret" .Release.Namespace (include "obico.fullname" .) -}}
{{- if and $existing $existing.data (index $existing.data "DJANGO_SECRET_KEY") -}}
{{- index $existing.data "DJANGO_SECRET_KEY" | b64dec -}}
{{- else -}}
{{- randAlphaNum 50 -}}
{{- end -}}
{{- end -}}
{{- end }}

{{/*
JSON-encoded CSRF_TRUSTED_ORIGINS for Django. Django 4+ rejects HTTPS POSTs
(login, signup, admin) whose origin is not listed here. Use an explicit
obico.csrfTrustedOrigins list when set; otherwise derive origins from the
ingress hosts and HTTPRoute hostnames, using the scheme implied by
obico.siteUsesHttps.
*/}}
{{- define "obico.csrfTrustedOrigins" -}}
{{- $scheme := ternary "https" "http" .Values.obico.siteUsesHttps -}}
{{- $origins := list -}}
{{- if .Values.obico.csrfTrustedOrigins -}}
{{- $origins = .Values.obico.csrfTrustedOrigins -}}
{{- else -}}
{{- if .Values.ingress.enabled -}}
{{- range .Values.ingress.hosts -}}
{{- $origins = append $origins (printf "%s://%s" $scheme .host) -}}
{{- end -}}
{{- end -}}
{{- if .Values.httpRoute.enabled -}}
{{- range .Values.httpRoute.hostnames -}}
{{- $origins = append $origins (printf "%s://%s" $scheme .) -}}
{{- end -}}
{{- end -}}
{{- end -}}
{{- $origins | toJson -}}
{{- end }}

{{/*
Shared environment wiring for every web-image container (collectstatic, migrate,
server, tasks). Keeping it in one place guarantees the containers stay identical
by construction — e.g. the DATABASE_URL override is never accidentally dropped
from one of them.
*/}}
{{- define "obico.podEnv" -}}
envFrom:
  - configMapRef:
      name: {{ include "obico.fullname" . }}
  - secretRef:
      name: {{ include "obico.secretName" . }}
{{- if .Values.database.existingSecret }}
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: {{ .Values.database.existingSecret }}
        key: {{ .Values.database.existingSecretKey }}
{{- else if .Values.database.host }}
env:
  # OBICO_DB_PASSWORD is read from the Secret, then referenced via the $(VAR)
  # dependent-env syntax so the password is assembled into DATABASE_URL at
  # runtime instead of being baked into the ConfigMap. Kubernetes only expands
  # $(VAR) for vars declared earlier in the same container's env list.
  - name: OBICO_DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ .Values.database.passwordSecret }}
        key: {{ .Values.database.passwordSecretKey }}
  - name: DATABASE_URL
    value: {{ printf "postgresql://%s:$(OBICO_DB_PASSWORD)@%s:%v/%s" .Values.database.user .Values.database.host .Values.database.port .Values.database.name | quote }}
{{- end }}
{{- end }}

{{/*
Validate the database configuration. existingSecret (full DSN from a Secret) and
host (DATABASE_URL composed from parts) are mutually exclusive; compose mode
requires user, name and passwordSecret. Rendered once from configmap.yaml.
*/}}
{{- define "obico.validateDatabase" -}}
{{- if and .Values.database.existingSecret .Values.database.host -}}
{{- fail "database.existingSecret and database.host are mutually exclusive: set one or the other" -}}
{{- end -}}
{{- if .Values.database.host -}}
{{- if not .Values.database.user -}}
{{- fail "database.host is set: database.user is required to compose DATABASE_URL" -}}
{{- end -}}
{{- if not .Values.database.name -}}
{{- fail "database.host is set: database.name is required to compose DATABASE_URL" -}}
{{- end -}}
{{- if not .Values.database.passwordSecret -}}
{{- fail "database.host is set: database.passwordSecret is required to source the password" -}}
{{- end -}}
{{- end -}}
{{- end }}

{{/*
Guard against overriding chart-managed environment variables through the
free-form extraEnv / extraSecretEnv maps, which would silently win via
later-key YAML semantics in the ConfigMap / Secret.
*/}}
{{- define "obico.checkReservedEnv" -}}
{{- $reserved := list "DEBUG" "WEBPACK_LOADER_ENABLED" "SITE_USES_HTTPS" "REDIS_URL" "ML_API_HOST" "INTERNAL_MEDIA_HOST" "DATABASE_URL" "OBICO_DB_PASSWORD" "DJANGO_SECRET_KEY" "CSRF_TRUSTED_ORIGINS" -}}
{{- range $key, $_ := .Values.obico.extraEnv -}}
{{- if has $key $reserved -}}
{{- fail (printf "obico.extraEnv must not set the chart-managed key %q; configure it via its dedicated value instead" $key) -}}
{{- end -}}
{{- end -}}
{{- range $key, $_ := .Values.obico.extraSecretEnv -}}
{{- if has $key $reserved -}}
{{- fail (printf "obico.extraSecretEnv must not set the chart-managed key %q; configure it via its dedicated value instead" $key) -}}
{{- end -}}
{{- end -}}
{{- end }}
