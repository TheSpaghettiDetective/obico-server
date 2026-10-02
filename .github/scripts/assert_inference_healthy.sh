#!/usr/bin/env bash
# Start an ml_api image and wait for it to report a loaded model.
#
# Usage: assert_inference_healthy.sh IMAGE_REF [COMMAND...]
#
# The failure this exists for is quiet: lib/detection_model.py swallows an
# ImportError from the inference backend, load_net() then raises at import
# time, and the gunicorn worker dies at boot. A build that merely finished
# proves nothing.
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $(basename "$0") IMAGE_REF [COMMAND...]" >&2
  exit 2
fi

ref="$1"
shift

# Overridable so the failing path can be exercised without waiting out the
# real deadline. The cases that do live in the workflow rather than here,
# because both of them need a container to run: see the two negative-path
# steps in .github/workflows/ci.yaml.
attempts="${ATTEMPTS:-45}"

# No --rm: a container that dies at boot would be gone before the trap could
# show why, which is the one case this script exists for.
cid="$(docker run --detach --publish 3333:3333 "${ref}" "$@")"
trap 'docker rm --force "${cid}" > /dev/null 2>&1 || true' EXIT

for _ in $(seq "${attempts}"); do
  # A worker that dies at import takes the container with it. Waiting out the
  # full deadline for that reads as slowness rather than as the failure it is.
  if [ "$(docker inspect --format '{{.State.Running}}' "${cid}")" != "true" ]; then
    echo "::error::${ref} exited before answering on /hc/"
    docker logs "${cid}" || true
    exit 1
  fi
  # --max-time matters more than it looks: a native crash inside the inference
  # runtime leaves gunicorn's master holding the listening socket while it
  # respawns workers forever, so the connection is accepted by the kernel and a
  # request without a deadline hangs until the job's own timeout. The body is
  # what is checked, not the status: /hc/ is a plain 200, and a worker that died
  # loading the model answers nothing at all.
  if [ "$(curl --silent --fail --connect-timeout 2 --max-time 5 http://127.0.0.1:3333/hc/ || true)" = "ok" ]; then
    echo "inference API is up"
    exit 0
  fi
  sleep 2
done

echo "::error::${ref} did not report a loaded model on /hc/ in time"
docker logs "${cid}" || true
exit 1
