#!/bin/sh
# Stage the frontend bundle inside the web build context.
#
# The backend image expects the built Vue bundle at /frontend, which
# docker-compose supplies as a bind mount. An image has no such mount, so the
# bundle is copied into the build context and symlinked at the end of the
# Dockerfile.
#
# This lives in a script rather than inline in a workflow because both the
# release publisher and the pull request build need it. Two copies that drift
# mean the images tested before a merge are not the images published after it,
# and nothing would report the difference.
set -eu

stage() {
    root=$1
    if [ ! -d "$root/frontend" ]; then
        echo "no frontend/ in $root: nothing to stage" >&2
        return 1
    fi
    # Not just the directory: an empty one moves happily and produces an image
    # whose /frontend symlink points at nothing, which only a browser reports.
    if [ -z "$(ls -A "$root/frontend" 2>/dev/null)" ]; then
        echo "$root/frontend is empty: staging it would bake an image that serves nothing" >&2
        return 1
    fi
    if [ ! -f "$root/backend/Dockerfile" ]; then
        echo "no backend/Dockerfile in $root: wrong build context" >&2
        return 1
    fi
    # mv into an existing directory nests instead of replacing, which would
    # leave the bundle at backend/frontend/frontend and the symlink pointing
    # at a directory holding nothing but another directory. The image builds
    # and serves no UI, and only a browser would report it.
    if [ -e "$root/backend/frontend" ]; then
        echo "$root/backend/frontend already exists: staging would nest inside it" >&2
        return 1
    fi
    mv "$root/frontend" "$root/backend/frontend"
    echo 'RUN ln -s /app/frontend /frontend' >> "$root/backend/Dockerfile"
}

self_test() {
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT

    mkdir -p "$tmp/ok/frontend/dist" "$tmp/ok/backend"
    echo 'FROM python:3.8' > "$tmp/ok/backend/Dockerfile"
    echo 'built' > "$tmp/ok/frontend/dist/app.js"
    stage "$tmp/ok"
    [ -f "$tmp/ok/backend/frontend/dist/app.js" ] || { echo "the bundle did not move"; exit 1; }
    [ ! -e "$tmp/ok/frontend" ] || { echo "the bundle was left outside the context"; exit 1; }
    tail -n 1 "$tmp/ok/backend/Dockerfile" | grep --quiet '^RUN ln -s /app/frontend /frontend$' \
        || { echo "the symlink step is not the last instruction"; exit 1; }

    # A missing bundle has to stop the build rather than produce an image that
    # serves nothing: on the master branch frontend/ holds sources, and a
    # future reshuffle of that directory should fail here, not in a browser.
    mkdir -p "$tmp/nobundle/backend"
    echo 'FROM python:3.8' > "$tmp/nobundle/backend/Dockerfile"
    if stage "$tmp/nobundle" 2>/dev/null; then
        echo "a missing bundle was accepted"
        exit 1
    fi

    # And an empty one, which is what a reshuffle of that directory looks
    # like: the move succeeds, the image builds, and the page is blank.
    mkdir -p "$tmp/empty/frontend" "$tmp/empty/backend"
    echo 'FROM python:3.8' > "$tmp/empty/backend/Dockerfile"
    if stage "$tmp/empty" 2>/dev/null; then
        echo "an empty bundle was accepted"
        exit 1
    fi

    # An occupied destination, which is also what a second run looks like:
    # nesting the bundle and appending a second symlink instruction are both
    # silent, and neither shows up until someone loads the page.
    mkdir -p "$tmp/occupied/frontend/dist" "$tmp/occupied/backend/frontend"
    echo 'FROM python:3.8' > "$tmp/occupied/backend/Dockerfile"
    if stage "$tmp/occupied" 2>/dev/null; then
        echo "an occupied destination was accepted"
        exit 1
    fi
    [ ! -e "$tmp/occupied/backend/frontend/frontend" ] || { echo "the bundle nested inside the destination"; exit 1; }
    [ -d "$tmp/occupied/frontend" ] || { echo "the bundle was moved despite the refusal"; exit 1; }

    # Running twice is the way that happens in practice, on a re-run of a job
    # whose checkout survived.
    if stage "$tmp/ok" 2>/dev/null; then
        echo "a second run was accepted"
        exit 1
    fi
    [ "$(grep --count '^RUN ln -s /app/frontend /frontend$' "$tmp/ok/backend/Dockerfile")" -eq 1 ] \
        || { echo "the symlink instruction was appended twice"; exit 1; }

    # Half-applying is the outcome worth ruling out: the move must not happen
    # when the context is wrong, or a retry of the job finds no frontend/ left.
    mkdir -p "$tmp/nocontext/frontend"
    if stage "$tmp/nocontext" 2>/dev/null; then
        echo "a missing build context was accepted"
        exit 1
    fi
    [ -d "$tmp/nocontext/frontend" ] || { echo "the bundle was moved into a context that does not exist"; exit 1; }

    echo "self-test ok"
}

case "${1:-}" in
    --self-test) self_test ;;
    "") stage "${GITHUB_WORKSPACE:-.}" ;;
    *) echo "usage: $0 [--self-test]" >&2; exit 2 ;;
esac
