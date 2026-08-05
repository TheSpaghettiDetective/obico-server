#!/usr/bin/env python3
"""Check that the Rockchip runtime and the toolkit that drives it agree.

Dockerfile.base_rk3588 pins librknnrt.so to a commit and
requirements_rk3588.txt pins rknn-toolkit-lite2 to the version that runtime
reports. Nothing enforces that, and the mismatch does not surface until
RKNNLite.init_runtime() talks to real NPU hardware, which no runner has.

The runtime carries its own version as a literal inside the binary, so the
two halves can be compared without a device. Run inside the image:

    docker run --rm -v "$PWD/.github/scripts:/s:ro" IMAGE python3 /s/assert_rknn_pair.py

Run --self-test on the runner to check the parsing.
"""
import importlib.metadata
import os
import pathlib
import re
import subprocess
import sys
import tempfile

# Found wherever the base put it. This checks the runtime against the toolkit
# that wraps it, so it needs the file itself rather than the import the
# Dockerfile probes for, and CI deliberately builds a base with the library
# moved off the literal path — a lookup that knew one location would die
# there on a missing file rather than reporting on the pair.
RUNTIME_NAME = "librknnrt.so"
TOOLKIT = "rknn-toolkit-lite2"
# The literal the runtime embeds, e.g. "librknnrt version: 2.3.2 (429f97ae6b@...)"
VERSION = re.compile(rb"librknnrt version: ([0-9]+(?:\.[0-9]+)+)")


def find_runtime():
    literal = pathlib.Path("/usr/lib") / RUNTIME_NAME
    if literal.exists():
        return literal
    for entry in os.environ.get("LD_LIBRARY_PATH", "").split(":"):
        if entry and (pathlib.Path(entry) / RUNTIME_NAME).exists():
            return pathlib.Path(entry) / RUNTIME_NAME
    try:
        listing = subprocess.run(
            ["ldconfig", "-p"], capture_output=True, text=True, check=False
        ).stdout
    except FileNotFoundError:
        listing = ""
    for line in listing.splitlines():
        if RUNTIME_NAME in line and "=>" in line:
            candidate = pathlib.Path(line.split("=>")[-1].strip())
            if candidate.exists():
                return candidate
    sys.exit(
        f"{RUNTIME_NAME} is not on the library search path, so there is no "
        f"runtime to compare {TOOLKIT} against. This image is not one the pair "
        f"applies to."
    )


def runtime_version(path):
    try:
        blob = pathlib.Path(path).read_bytes()
    except OSError as problem:
        sys.exit(f"cannot read {path}: {problem}")
    match = VERSION.search(blob)
    if not match:
        sys.exit(f"{path} carries no recognisable version string")
    return match.group(1).decode()


def check_pair(runtime, toolkit):
    if runtime != toolkit:
        sys.exit(
            f"the runtime reports {runtime} but {TOOLKIT} is {toolkit}. "
            "These are one pair; a mismatch fails on real hardware, where "
            "nothing in CI can see it."
        )


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        good = pathlib.Path(tmp) / "good.so"
        good.write_bytes(b"\x7fELF\x00\x00librknnrt version: 2.3.2 (429f97ae6b@2025-04-09)\x00")
        assert runtime_version(good) == "2.3.2", "failed to parse the embedded version"

        blank = pathlib.Path(tmp) / "blank.so"
        blank.write_bytes(b"\x7fELF" + b"\x00" * 64)
        try:
            runtime_version(blank)
        except SystemExit:
            pass
        else:
            raise AssertionError("a binary with no version string should be rejected")

        # A missing runtime must say so, not raise pathlib's error at the caller.
        try:
            runtime_version(pathlib.Path(tmp) / "absent.so")
        except SystemExit:
            pass
        except FileNotFoundError:
            raise AssertionError("a missing runtime surfaced as a raw traceback")
        else:
            raise AssertionError("a missing runtime was accepted")
    # main() itself, because the handler for a missing toolkit is a formatted
    # string that no other case reaches — and that is precisely the branch this
    # file exists to report on. Only where the toolkit really is absent: with
    # it installed main() takes the comparison branch instead, and a case that
    # quietly changes which branch it lands on proves nothing.
    try:
        importlib.metadata.version(TOOLKIT)
    except importlib.metadata.PackageNotFoundError:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = pathlib.Path(tmp) / RUNTIME_NAME
            runtime.write_bytes(b"librknnrt version: 2.3.2 (test)\x00")
            previous = os.environ.get("LD_LIBRARY_PATH", "")
            os.environ["LD_LIBRARY_PATH"] = tmp
            try:
                main()
            except SystemExit as outcome:
                # The wording of the branch, not just the package name: the
                # mismatch message names the package too.
                assert "is not installed" in str(outcome), outcome
            except NameError as broken:
                raise AssertionError(f"the missing-toolkit diagnostic is broken: {broken}")
            else:
                raise AssertionError("a missing toolkit was accepted")
            finally:
                os.environ["LD_LIBRARY_PATH"] = previous
    else:
        print(f"skipping the missing-toolkit case: {TOOLKIT} is installed here")

    check_pair("2.3.2", "2.3.2")
    try:
        check_pair("2.3.2", "2.3.9")
    except SystemExit:
        pass
    else:
        raise AssertionError("a version mismatch should have been rejected")
    print("self-test ok")


def main():
    found = find_runtime()
    runtime = runtime_version(found)
    try:
        toolkit = importlib.metadata.version(TOOLKIT)
    except importlib.metadata.PackageNotFoundError:
        sys.exit(
            f"{TOOLKIT} is not installed, so there is nothing to compare "
            f"{found} against. This image is not one the pair applies to."
        )
    check_pair(runtime, toolkit)
    print(f"{found} and {TOOLKIT} both at {runtime}")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
