{{/*
The boot deadline gunicorn was given in mlApi.command, or nothing when the
command names none. Read once here, because two places need it: the deployment
sizes the startup probe against this number and NOTES warns on its absence.

Matched against the joined command rather than element by element, because the
deadline does not have to be its own argv entry. Some of the gunicorn
invocations this repository ships sit inside a `bash -c "..."` wrapper —
docker-compose.yml and the Jetson symlink workaround in docs/model_development.md
both take that shape, and a Jetson user copying that workaround into
mlApi.command is exactly who this chart now documents. To an argv walk the whole
invocation is one opaque element, so whatever deadline it carries is invisible,
which is wrong twice over: NOTES calls a working config broken, and the pairing
below stops guarding the one command that most needs it.

Bounded on both sides. On the left, because a wrapped command has a prelude and
preludes carry flags: `wait-for-it -t 30`, `docker run -t`, `curl --timeout 5`.
On the right, because what follows a `&&` or a `&` is a different command, and
start-then-poll is the ordinary shape — `gunicorn ... & ./wait-for-it.sh -t 30
...`. Read either boundary wrong and a neighbour's flag becomes this command's
deadline, so a gunicorn started bare looks covered and the pairing below stops
holding on the one command that needed it most.

The first program name inside a command, not the last: `--chdir /opt/gunicorn`
is a path argument that ends at a space, and splitting there would put the
deadline that follows it outside the invocation it belongs to.

Both spellings gunicorn accepts, `--timeout` and `-t`, and only where the flag
names a number.

A command that names a config file yields nothing here, and NOTES stays quiet
for it. `timeout = 120` in gunicorn.conf.py is a deliberate way to set this and
the chart cannot read that file, so calling the deadline missing would send
someone to add a flag they moved on purpose.
*/}}
{{/*
One command, and whether it starts gunicorn. Two ways to qualify, because the
container's command and a shell wrapper are different shapes. A command whose
own program is gunicorn is an invocation whatever flags follow. Inside a
wrapper the word can also be a mention — `echo starting gunicorn` — so there a
flag only an invocation carries is required. A bare mention stays a mention;
one written next to a gunicorn-looking flag does not.

What that costs depends on which flag. `echo starting gunicorn -w 2` is read as
an invocation and prints one NOTES line nobody needed, which is cheap. A
mention carrying the deadline flag is not: `echo about to start gunicorn -t 600`
hands 600 to the pairing check as this command's boot deadline, and any value
above startupBudgetSeconds refuses the render outright, naming a deadline no
process here has. Both are the price of deciding invocation from a flag rather
than from a running program, and the second one is what anyone loosening or
tightening this heuristic later is really trading against.

Both spellings of that flag, for the same reason the deadline is read in both:
gunicorn documents `-b` and `-w` alongside `--bind` and `--workers`, and a
check that knows only the long ones judges a command it cannot read. Wrapped
plus short-flagged is a real shape — it is what fits on one `bash -c` line —
and missing it costs twice, since the deadline pairing stops guarding that
command and NOTES stops warning when it has no deadline at all.

Value attached or separated, because argparse takes a short option's value
either way and `-b0.0.0.0:3333 -w1` is the terser habit. Insisting on a
separator here while the deadline below reads `-t600` attached would leave one
half of the same check unable to read what the other half accepts.

The deadline flag counts as a marker too, and it is the one that matters most.
`exec gunicorn --timeout=600 wsgi` is an ordinary thing to write inside a
wrapper — `exec` is how the server ends up as PID 1 — and a command carrying
`--timeout` is no less an invocation than one carrying `--bind`. Left out, the
pairing skips exactly the command that named a deadline to be paired against,
which is the one case values.yaml promises will fail the render rather than
kill the pod early.
*/}}
{{- define "obico.isGunicornCommand" -}}
{{- if regexMatch "^[[:space:]]*([^[:space:]]*/)?gunicorn[0-9]*([^0-9A-Za-z_./-]|$)" . -}}yes
{{- else if and (regexMatch "(^|[^0-9A-Za-z_])gunicorn[0-9]*([^0-9A-Za-z_./-]|$)" .) (regexMatch "--bind|--workers|--timeout|(^|[[:space:]])-[btw][=[:space:]]*[^[:space:]=]" .) -}}yes
{{- end -}}
{{- end }}

{{/*
Whether any command in mlApi.command starts gunicorn, deferring to
obico.isGunicornCommand for what that means. A command that hands gunicorn a
config file of its own does not count: the deadline may well be set in that
file, and NOTES has nothing to warn about.

A trailing digit is still the program: Debian ships the binary as `gunicorn3`,
and rejecting that name skipped the pairing check for a real invocation, so a
140s budget rendered against a 600s deadline — the check answering wrong in the
one direction it exists to prevent. Widened at all four anchors together, since
the tail split has to agree with the test that decided there was a tail.

gunicorn as a program name, not as part of a path. A trailing / . _ - or word
character means this is a file: --access-logfile /var/log/gunicorn/access.log
and -c gunicorn.conf.py are the spellings gunicorn's own documentation uses,
and the first is already in this chart's default command with a `-` where a
path would go. Treating one as the invocation puts everything real before the
anchor, and the deadline stops being found at all.
*/}}
{{/*
Whether mlApi.command is handed to a shell, which decides whether `&&`, `;`,
`|` and `&` in it mean anything.

They only mean something to a shell. mlApi.command is a list, and when its
program is not a shell each element is one argv entry that execve hands over
untouched — `--access-logformat=%(h)s|%(t)s` is gunicorn's own documented
syntax for a log format, and the pipe in it is a character in a value, not a
command boundary. Splitting on it anyway threw away the rest of the command,
`--timeout` included, and rendered a 140s budget against a 600s deadline.

So the question is answered from the argv rather than from the joined text,
because joining is exactly what destroys the distinction.

What is looked for is the script flag, not the program. A `-c` is what says
some element of this argv is a script rather than an argument, and whoever
ends up handing that script to a shell — `sh`, `bash`, `tini -- sh`,
`busybox sh`, `dumb-init`, `gosu` — does not change what the string is. Asking
instead which program sits at the front means keeping a list of every runner
anyone might put in front of it, and every name missing from that list read a
poller's deadline past an `&` as gunicorn's own and refused the render over a
number nothing had set.

Matched as a cluster rather than as the word `-c`, because a shell takes its
short options joined: `bash -lc` and `sh -ec` run a script exactly as `-c`
does, and `-cl` puts the letter in the middle rather than at the end.

And required to introduce something multi-word, because `-c` is gunicorn's own
config-file flag as well as the shell's script flag, and only one of the two
is followed by a script. `gunicorn -c /etc/g.conf.py` is a path; treating it
as a script turned metacharacter splitting on for a direct argv command, so
`--access-logformat=%(h)s|%(t)s` beside it silently dropped the `--timeout`
that came after — the same command refusing the render without the pipe and
rendering with it.

Whitespace is the discriminator, and it is safe in both directions. It cannot
bring back the inventing case: a script able to carry someone else's deadline
needs a second command in it — a poller past an `&`, a prelude before `&&` —
and a single word has no room for a command and a flag. So `tini -- sh -c`
and `busybox sh -c` stay shells. What it can still lose is a config path that
contains both a space and a metacharacter, and losing leaves the budget as the
ceiling, which values.yaml promises for every command shape.

That asymmetry is the whole rule. Splitting can only lose a deadline; not
splitting can invent one, and a fabricated deadline fails the render outright
on a command that is perfectly valid. Between losing and inventing, lose.
*/}}
{{/* Accumulated rather than emitted in the loop: two matching elements would
     otherwise print "yesyes", and the caller compares against "yes". */}}
{{- define "obico.mlApiUsesShell" -}}
{{- $argv := .Values.mlApi.command -}}
{{- $script := false -}}
{{- range $i, $arg := $argv -}}
  {{- if and (regexMatch "^-[a-zA-Z]*c[a-zA-Z]*$" $arg) (lt (add $i 1) (len $argv)) -}}
    {{- if regexMatch "[[:space:]]" (index $argv (add $i 1)) -}}
      {{- $script = true -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- if $script -}}yes{{- end -}}
{{- end }}

{{/*
The command split into the pieces a shell would run, or the whole thing as one
piece when no shell is involved.

Unquoted, this agrees with the shell by construction: a metacharacter a shell
would act on is one this cuts at too, so what gets lost is what a shell would
have put in another command anyway. Often the shell is stricter still —
`bash -c 'gunicorn --access-logformat=%(h)s|%(t)s ...'` is a syntax error near
`(`, so that container never starts and there is no deadline to miss.

Quoted is the real gap. The shell hands the whole value to gunicorn, so a
deadline after it is genuinely in force, and this still cuts at the
metacharacter inside the quotes and loses it. The pairing check is then
skipped, leaving the budget as the only ceiling — which is what values.yaml
promises for every command shape. A quote-aware split is the fix that would
close that too, and is deliberately not attempted here.

What this costs the operator is bounded by what NOTES claims. It reports that
no deadline could be READ, never that none was set, so the sentence stays true
whether the command names one this cannot parse or names none at all. An
earlier version asserted the stronger thing and needed a second heuristic to
guess when it was lying; the weaker claim is one the parser can always make
honestly, and it needed no heuristic at all.
*/}}
{{- define "obico.mlApiCommandSegments" -}}
{{- $joined := join " " .Values.mlApi.command -}}
{{- if eq (include "obico.mlApiUsesShell" .) "yes" -}}
{{- join "\x00" (regexSplit "&&|\\|\\||[\n;&|]" $joined -1) -}}
{{- else -}}
{{- $joined -}}
{{- end -}}
{{- end }}

{{/* Accumulated rather than emitted in the loop, for the same reason
     obico.mlApiUsesShell is: a command with two gunicorn segments matched
     twice and printed "yesyes". Only truthiness is read today, so nothing
     was wrong yet — but the answer is a word, and the first caller to
     compare it against one would have got a silently false negative. */}}
{{- define "obico.mlApiRunsGunicorn" -}}
{{- $runs := false -}}
{{- range $command := splitList "\x00" (include "obico.mlApiCommandSegments" .) -}}
  {{- if include "obico.isGunicornCommand" $command -}}
    {{/* The tail, not the whole command: `bash -c` carries a -c of its own,
         and a wrapper's flag is not what gunicorn was configured with. */}}
    {{- $tail := index (regexSplit "gunicorn[0-9]*([^0-9A-Za-z_./-]|$)" $command 2) 1 -}}
    {{- if not (regexMatch "(^|[^0-9A-Za-z_-])(-c|--config)[ =]" $tail) -}}
      {{- $runs = true -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- if $runs -}}yes{{- end -}}
{{- end }}


{{- define "obico.mlApiBootDeadline" -}}
{{- $deadline := "" -}}
{{- $answered := false -}}
{{- range $command := splitList "\x00" (include "obico.mlApiCommandSegments" .) -}}
  {{/* The first invocation answers, whether or not it names a deadline.
       Scanning on would credit a later command's flag to this one. */}}
  {{- if and (not $answered) (include "obico.isGunicornCommand" $command) -}}
    {{- $answered = true -}}
    {{- $tail := index (regexSplit "gunicorn[0-9]*([^0-9A-Za-z_./-]|$)" $command 2) 1 -}}
    {{/* Every occurrence of either spelling, then the last one, because a
         repeated option wins from the right in argparse and gunicorn is
         argparse. Taking the first is wrong in both directions at once: it
         renders `--timeout=120 --timeout=600` against a budget that only
         covers 120 while the worker really gets 600, and it refuses
         `--timeout=600 -t 120`, whose real deadline the budget does cover.
         One pattern rather than one per spelling, because the answer is
         positional and two searches cannot compare positions — trying the
         long form first is what made the mixed case answer by spelling
         instead of by order.

         Quotes are among the separators because argv written as JSON puts
         them between the flag and its value. */}}
    {{- $hits := regexFindAll "(--timeout[= \"']+|(^|[[:space:]])-t[= \"']*)0*[0-9]+" $tail -1 -}}
    {{- if $hits -}}
      {{- $named := regexFind "[0-9]+$" (last $hits) -}}
      {{/* Zero is matched above rather than excluded from the pattern, so that
           it can win as the last word. gunicorn reads 0 as no arbiter deadline
           at all, so there is nothing to pair against and NOTES has something
           to warn about — but an earlier number must not be left standing as
           the answer once a later flag switched the deadline off. */}}
      {{- if not (regexMatch "^0+$" $named) -}}
        {{- $deadline = $named -}}
      {{- end -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- $deadline -}}
{{- end }}

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
