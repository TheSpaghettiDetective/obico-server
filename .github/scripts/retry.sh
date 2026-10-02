#!/bin/sh
# Run a command until it succeeds, with backoff, and say something useful when
# it does not.
#
# Usage: retry.sh ATTEMPTS COMMAND [ARG...]
#
# Every job here that builds an image pulls its base from somebody else's
# registry, so a failure is as likely to be the network as the change under
# review. Retrying absorbs the common case; the message on the last failure
# exists so the uncommon one does not get blamed on the diff.
#
# Lives in a file rather than inline in the workflow for two reasons: the two
# call sites had already drifted apart while inline, and actionlint's shellcheck
# pass excludes SC2154 (unassigned variable) because run: blocks legitimately
# read from env:, so a typo'd variable name in a workflow is invisible to it.
# Here plain shellcheck sees it.
#
# RETRY_SLEEP_SCALE exists so the self-test does not wait out real backoff.
set -eu

retry() {
    attempts="$1"
    shift

    # Validated, not assumed: [ abc -le 3 ] is an error rather than a
    # comparison, the loop body never runs, and the failure message then
    # reports attempts that never happened and blames the registry for it.
    case "${attempts}" in
        # 0* rather than 0: `00` is all digits and not zero as a string, so a
        # bare 0 in the pattern lets it through, the loop runs no attempts and
        # the message then blames a registry nothing tried to reach.
        ''|*[!0-9]*|0*) echo "attempts must be a positive number without leading zeros, got '${attempts}'" >&2; return 2 ;;
    esac
    scale="${RETRY_SLEEP_SCALE:-30}"

    attempt=1
    while [ "${attempt}" -le "${attempts}" ]; do
        if "$@"; then
            return 0
        fi
        echo "::warning::attempt ${attempt} of ${attempts} failed: $*"
        if [ "${attempt}" -lt "${attempts}" ]; then
            echo "waiting before the next attempt"
            sleep $((attempt * scale))
        fi
        attempt=$((attempt + 1))
    done

    echo "::error::gave up after ${attempts} attempts: $*. Retrying that many times covers a network blip, so check whether the registries this build pulls from are reachable before assuming the change is at fault."
    return 1
}

self_test() {
    out="$(RETRY_SLEEP_SCALE=0 sh "$0" 3 false 2>&1 || true)"
    RETRY_SLEEP_SCALE=0 sh "$0" 3 false > /dev/null 2>&1 \
        && { echo "self-test: a command that always fails was reported as success" >&2; return 1; }

    for want in 'attempt 1 of 3' 'attempt 2 of 3' 'gave up after 3 attempts'; do
        case "${out}" in
            *"${want}"*) ;;
            *) echo "self-test: expected '${want}' in the output, got: ${out}" >&2; return 1 ;;
        esac
    done

    # The last attempt is reported, and it does not announce a wait it will
    # not take: only the two earlier ones may be followed by a sleep.
    case "${out}" in
        *'attempt 3 of 3'*) ;;
        *) echo "self-test: the last attempt was never reported" >&2; return 1 ;;
    esac
    sleeps="$(printf '%s\n' "${out}" | grep --count 'waiting before the next attempt' || true)"
    [ "${sleeps}" -eq 2 ] || { echo "self-test: announced ${sleeps} waits for 3 attempts, wanted 2" >&2; return 1; }

    RETRY_SLEEP_SCALE=0 sh "$0" 2 true > /dev/null 2>&1 \
        || { echo "self-test: a command that succeeds was reported as failure" >&2; return 1; }

    for bad in abc '' 0; do
        if RETRY_SLEEP_SCALE=0 sh "$0" "${bad}" true > /dev/null 2>&1; then
            echo "self-test: '${bad}' was accepted as an attempt count" >&2
            return 1
        fi
    done

    # The guard on the count. Without a case here it can be deleted and this
    # file still reports ok, while a non-numeric count makes [ -le ] an error
    # the surrounding if reads as false: no attempts, and a message blaming
    # the registry for it.
    # Asserted on the message, not the exit status: without the guard a bad
    # count makes [ -le ] an error, the loop runs nothing and the function
    # still returns non-zero — the same verdict for the opposite reason, and
    # the reason is what the operator reads.
    for bad in '' 'abc' '0' '00' '-1' '2x'; do
        said="$(retry "${bad}" true 2>&1 || true)"
        case "${said}" in
            *"attempts must be a positive number"*) ;;
            *) echo "self-test: '${bad}' was not rejected as a count, got: ${said}" >&2; return 1 ;;
        esac
    done
    for good in 1 3 10; do
        retry "${good}" true > /dev/null 2>&1 \
            || { echo "self-test: '${good}' was rejected" >&2; return 1; }
    done

    echo "self-test ok"
}

if [ "${1:-}" = "--self-test" ]; then
    self_test
else
    [ "$#" -ge 2 ] || { echo "usage: $(basename "$0") ATTEMPTS COMMAND [ARG...]" >&2; exit 2; }
    retry "$@"
fi
