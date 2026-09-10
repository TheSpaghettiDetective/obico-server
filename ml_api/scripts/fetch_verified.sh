#!/bin/sh
# Download a file and refuse to continue unless what arrived is plausibly it.
#
# Usage: fetch_verified.sh URL DEST MIN_BYTES SHA256
#
# Three failures this guards against, none of which a bare curl catches:
#
#   * a 3xx with an empty body, which leaves a zero-byte file and surfaces
#     later as an unreadable model or an uninstallable wheel;
#   * an error page served with a 200, which lands on disk looking like a
#     download and weighs a few hundred bytes;
#   * a connection dropped mid-transfer, which curl reports but which leaves
#     a partial file behind — the case a size floor alone lets through when
#     the truncation happens late.
#
# The checksum makes all three moot, so it is required rather than preferred:
# every caller reads it from a sidecar with a command substitution, and an
# optional argument turns a missing sidecar into "no checksum wanted". The
# size floor stays as a cheap first answer that names the size in the message,
# which a hash mismatch cannot.
#
# Run --self-test to exercise the accept and reject paths.
set -e

digest_of() {
    # Nothing here is inside a pipeline. A compound command piped into cut runs
    # in a subshell, so a return from within it exits that subshell and the
    # function reports cut's status — zero — with an empty result, which fetch
    # would then compare against the expected digest and reject while blaming
    # the file rather than the missing tool.
    if command -v sha256sum > /dev/null 2>&1; then
        line=$(sha256sum "$1") || return 1
    elif command -v shasum > /dev/null 2>&1; then
        line=$(shasum -a 256 "$1") || return 1
    else
        echo "no sha256 tool on PATH" >&2
        return 2
    fi
    echo "${line}" | cut -d' ' -f1
}

fetch() {
    url="$1"
    dest="$2"
    min_bytes="$3"
    want_sha="${4:-}"

    # Required, not optional. Every caller passes it as a command substitution
    # reading a .sha256 beside the .url; a missing or empty one of those makes
    # the substitution expand to nothing, and an optional argument turns that
    # into "no checksum wanted" instead of "the checksum could not be read".
    # A 200 MB download would then be accepted on the size floor alone, which
    # is the one thing this script exists to prevent.
    if [ -z "${want_sha}" ]; then
        echo "no sha256 given for ${url}: refusing to fetch it unverified" >&2
        return 1
    fi

    # A floor is only a floor if it is a number: [ "$size" -lt abc ] is an
    # error rather than a comparison, so the surrounding if takes the else
    # branch and the check silently stops checking — the same shape the
    # || echo 0 below guards against on the other operand.
    case "${min_bytes}" in
        ''|*[!0-9]*) echo "min_bytes must be a number, got '${min_bytes}'" >&2; return 2 ;;
    esac

    # --fail rejects a 4xx/5xx body, --location follows a real redirect, and
    # curl's own exit status covers the truncated transfer. || return 1 rather
    # than leaning on set -e: errexit is suppressed for a function called in a
    # condition, which is how the self-test calls this one.
    # rm on failure, not just on the checks below: a transfer cut off partway
    # is the one curl failure that leaves bytes at ${dest}, and it is the case
    # this script's header names. Not --remove-on-error, which arrived in curl
    # 7.83 — the amd64 base is Ubuntu 20.04 with 7.68.
    curl --fail --location --silent --show-error \
        --connect-timeout 30 --max-time 1800 --output "${dest}" "${url}" \
        || { rm -f "${dest}"; return 1; }

    # Both stat dialects, so this is runnable where it is written as well as
    # where it runs. || echo 0 matters: without it a failing stat leaves the
    # variable empty, and [ "" -lt N ] exits 2, which the caller reads as
    # "not less than" and waves the file through.
    size=$(stat -c %s "${dest}" 2>/dev/null || stat -f %z "${dest}" 2>/dev/null || echo 0)
    if [ "${size}" -lt "${min_bytes}" ]; then
        echo "${dest} is only ${size} bytes, expected at least ${min_bytes}" >&2
        # Removed rather than left behind: inside a RUN the failed layer is
        # discarded anyway, but this is installed as a general-purpose tool in
        # four images, and a caller that survives the failure must not find
        # something at that path that looks like the artifact.
        rm -f "${dest}"
        return 1
    fi

    # Computed and compared as strings rather than through --check: both tools
    # print the same format, but only the GNU one takes that flag. The
    # assignment is guarded because digest_of returns non-zero when neither
    # tool is present, and under set -e that would abort the function before
    # the rm below, leaving the unverified file exactly where the size check
    # above promises it will not be.
    if ! got=$(digest_of "${dest}"); then
        echo "cannot hash ${dest}: no sha256sum or shasum on this image" >&2
        rm -f "${dest}"
        return 1
    fi
    if [ "${got}" != "${want_sha}" ]; then
        echo "${dest} hashes to ${got}, expected ${want_sha}" >&2
        rm -f "${dest}"
        return 1
    fi

    echo "${dest}: ${size} bytes"
}

self_test() {
    tmp=$(mktemp -d)
    trap 'rm -rf "${tmp}"' EXIT
    printf 'x%.0s' $(seq 1 100) > "${tmp}/source"
    sha=$(digest_of "${tmp}/source")
    # Without this the checksum cases below are vacuous: an empty digest makes
    # fetch skip the comparison entirely and report success.
    case "${sha}" in
        [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]) ;;
        *) echo "self-test: digest_of returned '${sha}', not a sha256" >&2; return 1 ;;
    esac

    fetch "file://${tmp}/source" "${tmp}/a" 50 "${sha}" > /dev/null \
        || { echo "self-test: a large-enough file was rejected" >&2; return 1; }

    if fetch "file://${tmp}/source" "${tmp}/b" 500 "${sha}" > /dev/null 2>&1; then
        echo "self-test: a file below the floor was accepted" >&2
        return 1
    fi
    if [ -e "${tmp}/b" ]; then
        echo "self-test: a rejected file was left on disk" >&2
        return 1
    fi

    fetch "file://${tmp}/source" "${tmp}/c" 50 "${sha}" > /dev/null \
        || { echo "self-test: a matching checksum was rejected" >&2; return 1; }

    if fetch "file://${tmp}/source" "${tmp}/d" 50 "0000000000000000000000000000000000000000000000000000000000000000" > /dev/null 2>&1; then
        echo "self-test: a mismatched checksum was accepted" >&2
        return 1
    fi
    if [ -e "${tmp}/d" ]; then
        echo "self-test: a file with the wrong hash was left on disk" >&2
        return 1
    fi

    if fetch "file://${tmp}/does-not-exist" "${tmp}/e" 1 "${sha}" > /dev/null 2>&1; then
        echo "self-test: a failed download was accepted" >&2
        return 1
    fi

    # An image with neither hasher must fail loudly rather than return an
    # empty digest that reads as a content mismatch.
    stub="${tmp}/stub"
    mkdir -p "${stub}"
    for tool in cut echo; do
        command -v "${tool}" > /dev/null 2>&1 && ln -sf "$(command -v "${tool}")" "${stub}/${tool}"
    done
    if PATH="${stub}" digest_of "${tmp}/source" > /dev/null 2>&1; then
        echo "self-test: digest_of succeeded with no sha256 tool available" >&2
        return 1
    fi

    # The truncated transfer, which is the only curl failure that leaves bytes
    # behind — a 404 or a missing file never creates one, so neither would
    # exercise the cleanup. Needs a server that promises more than it sends.
    if command -v python3 > /dev/null 2>&1; then
        python3 -c '
import socket, sys
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 0)); s.listen(1)
open(sys.argv[1], "w").write(str(s.getsockname()[1]))
c, _ = s.accept(); c.recv(4096)
c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 1000\r\n\r\n" + b"x" * 200)
c.close(); s.close()' "${tmp}/port" &
        server=$!
        # Bounded, and watching the helper: without this a python that never
        # binds turns into the job's own timeout with nothing said about why.
        waited=0
        while [ ! -s "${tmp}/port" ]; do
            if ! kill -0 "${server}" 2>/dev/null; then
                echo "self-test: the truncating helper exited before binding" >&2
                return 1
            fi
            waited=$((waited + 1))
            if [ "${waited}" -gt 100 ]; then
                echo "self-test: the truncating helper never bound a port" >&2
                kill "${server}" 2>/dev/null
                return 1
            fi
            sleep 0.1
        done
        if fetch "http://127.0.0.1:$(cat "${tmp}/port")/x" "${tmp}/h" 1 "${sha}" > /dev/null 2>&1; then
            echo "self-test: a truncated transfer was accepted" >&2
            kill "${server}" 2>/dev/null
            return 1
        fi
        wait "${server}" 2>/dev/null || true
        if [ -e "${tmp}/h" ]; then
            echo "self-test: a truncated transfer was left on disk" >&2
            return 1
        fi
    else
        # Not a skip. This is the failure the header names as the reason the
        # script exists, and reporting ok without having run it tells the CI
        # step that called us something that is not true.
        echo "self-test: no python3, so the truncated-transfer case cannot run" >&2
        return 1
    fi

    if fetch "file://${tmp}/source" "${tmp}/f" not-a-number "${sha}" > /dev/null 2>&1; then
        echo "self-test: a non-numeric floor was accepted" >&2
        return 1
    fi

    # The case this script exists for. Callers read the digest out of a
    # sidecar file with a command substitution, so a missing or empty sidecar
    # arrives here as an empty string rather than as an error, and treating
    # that as "no checksum wanted" accepts whatever the server sent.
    if fetch "file://${tmp}/source" "${tmp}/i" 50 "" > /dev/null 2>&1; then
        echo "self-test: an empty checksum was accepted" >&2
        return 1
    fi
    [ ! -e "${tmp}/i" ] || { echo "self-test: an unverified file was left behind" >&2; return 1; }

    if fetch "file://${tmp}/source" "${tmp}/g" "" "${sha}" > /dev/null 2>&1; then
        echo "self-test: an empty floor was accepted" >&2
        return 1
    fi

    if sh "$0" "file://${tmp}/source" > /dev/null 2>&1; then
        echo "self-test: a call with too few arguments was accepted" >&2
        return 1
    fi

    echo "self-test ok"
}

if [ "${1:-}" = "--self-test" ]; then
    self_test
else
    [ "$#" -eq 4 ] || { echo "usage: $(basename "$0") URL DEST MIN_BYTES SHA256" >&2; exit 2; }
    fetch "$@"
fi
