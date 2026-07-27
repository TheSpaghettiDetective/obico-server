#!/bin/sh
# Point the Docker daemon at a pull-through cache for Docker Hub.
#
# Reaching Docker Hub from a runner is the most common way these jobs fail for
# reasons that have nothing to do with the change under review. mirror.gcr.io
# caches Hub content; dockerd asks it first and falls back to Hub on a miss or
# an error, so this can only reduce how often a build depends on Hub answering.
# It does not cover nvcr.io, which is a different registry and where the CUDA
# and L4T bases come from.
#
# The buildx container driver keeps its own registry config and does not read
# this one; workflows using it pass the same mirror through
# buildkitd-config-inline.
#
# This does add a party to a chain that ends in a cosign signature: the bases
# are addressed by tag, so the mirror resolves tag to digest for content that
# then gets signed. Accepted knowingly rather than by omission. A pull-through
# cache serves what the upstream registry gave it and dockerd falls back to Hub
# on any error, so the exposure is the cache serving a wrong digest for a tag
# that Hub would resolve differently. Pinning the FROM lines by digest would
# close it outright and is the better answer whenever the base images stop
# moving.
set -eu

MIRROR=https://mirror.gcr.io

# Merged, not overwritten: a runner may already carry daemon settings, and
# replacing the file would drop them silently.
merged() {
    existing='{}'
    [ -s "$1" ] && existing="$(cat "$1")"
    echo "${existing}" | jq --arg m "${MIRROR}" '. + {"registry-mirrors": [$m]}'
}

# Written through a temporary file, never straight back into the source: tee
# truncates its target when the pipeline starts while merged() is still reading
# that same file, and which wins is undefined. The comment above promised a
# merge; a pipe into tee would have delivered an empty file.
install_to() {
    target="$1"
    staged="$(mktemp)"
    merged "${target}" > "${staged}"
    sudo mkdir -p "$(dirname "${target}")"
    sudo cp "${staged}" "${target}"
    rm -f "${staged}"
}

self_test() {
    tmp="$(mktemp -d)"
    trap 'rm -rf "${tmp}"' EXIT

    got="$(merged "${tmp}/absent" | jq -r '."registry-mirrors"[0]')"
    [ "${got}" = "${MIRROR}" ] || { echo "self-test: no file gave '${got}'" >&2; return 1; }

    echo '{"log-driver":"json-file","registry-mirrors":["https://old"]}' > "${tmp}/existing"
    out="$(merged "${tmp}/existing")"
    [ "$(echo "${out}" | jq -r '."log-driver"')" = "json-file" ] \
        || { echo "self-test: an unrelated setting was dropped" >&2; return 1; }
    [ "$(echo "${out}" | jq -r '."registry-mirrors"[0]')" = "${MIRROR}" ] \
        || { echo "self-test: the existing mirror was not replaced" >&2; return 1; }

    # The real write path, not just the merge. What this pins is that the
    # write goes through a staged file: a race between reading and truncating
    # the same target is decided by the scheduler, so asserting on the
    # outcome of the racy form would pass most runs. Asserting on the shape
    # is what actually holds.
    # Read from the file rather than from `type`: only bash prints a
    # function's body, and /bin/sh on the runner is dash, where `type` says
    # "install_to is a shell function" and every pattern below would decide
    # whatever the first branch says. Shellcheck and actionlint see nothing
    # wrong either way, because this is what the shell does at run time.
    body="$(sed --quiet '/^install_to() {/,/^}/p' "$0")"
    [ -n "${body}" ] || { echo "self-test: could not read install_to from $0" >&2; return 1; }
    case "${body}" in
        *'staged'*) ;;
        *) echo "self-test: install_to no longer stages before writing" >&2; return 1 ;;
    esac
    case "${body}" in
        *'| sudo tee'*|*'|sudo tee'*|*'| tee'*)
            echo "self-test: install_to pipes into the file it is reading" >&2; return 1 ;;
    esac

    echo '{"log-driver":"json-file","insecure-registries":["x"]}' > "${tmp}/live"
    sudo() { "$@"; }   # the self-test writes to a temp path, no privileges needed
    install_to "${tmp}/live"
    unset -f sudo
    [ -s "${tmp}/live" ] || { echo "self-test: the target was emptied" >&2; return 1; }
    [ "$(jq -r '."log-driver"' < "${tmp}/live")" = "json-file" ] \
        || { echo "self-test: an unrelated setting was lost on write" >&2; return 1; }
    [ "$(jq -r '."registry-mirrors"[0]' < "${tmp}/live")" = "${MIRROR}" ] \
        || { echo "self-test: the mirror did not reach the file" >&2; return 1; }

    echo "self-test ok"
}

if [ "${1:-}" = "--self-test" ]; then
    self_test
    exit 0
fi

install_to /etc/docker/daemon.json
sudo systemctl restart docker

# Not optional: a daemon that came back without the setting would leave every
# build below going straight to Hub while this step reported success.
if ! docker info --format '{{json .RegistryConfig.Mirrors}}' | grep --quiet 'mirror.gcr.io'; then
    echo "::error::the daemon restarted without the registry mirror configured" >&2
    exit 1
fi
echo "docker will pull Docker Hub images through mirror.gcr.io"
