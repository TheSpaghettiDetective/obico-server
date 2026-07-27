#!/usr/bin/env python3
"""Import every module in an image that ships compiled code.

A build proves pip exited zero. It does not prove the result loads: an
extension can install cleanly and then fail at import against the base
image's C library. Nothing else in CI would notice, because the app is
never started without a database behind it.

Written for the web image: it also imports that container's entrypoints, which
ship no compiled code of their own. Run it inside the image under test, naming
packages that image is known to have compiled code for — the scan silently
derives nothing if it looks at the wrong directory, and those names are what
turns that into a failure:

    docker run --rm -v "$PWD/.github/scripts:/s:ro" IMAGE python /s/assert_imports.py psycopg2 PIL

Run --self-test on the runner to check the derivation itself.
"""
import importlib
import pathlib
import sys
import sysconfig
import tempfile

# The packages the web container's entrypoints live in — gunicorn, daphne and
# celery all import their way here. Pure Python, so they ship no compiled
# object of their own and the scan below would miss them. Web-specific, which
# is why the docstring says which image this script is for.
ENTRYPOINTS = {"django", "channels", "celery", "daphne"}

# Directories a wheel places beside its package. For .libs and .dist-info the
# name is simply not a module and attributing anything to it would be wrong.
# .data is different and worth knowing: a real importable extension can live
# under it, so skipping it is a false negative — the scan then reports a clean
# pass on a module it never imported. Name such a package in the caller's
# expected list if an image ever grows one. Sidecar libraries observed in practice carry a soname
# (libjpeg-ad9713a2.so.62.4.0) and so would not match *.so anyway, but .data
# layouts do produce a bare directory name, and relying on a naming habit of
# one packaging tool is not the same as excluding by construction.
NOT_PACKAGES = (".libs", ".dist-info", ".data")

# A bare .so at the root of site-packages is treated as a module, which is
# correct for extensions like _cffi_backend and zmq.abi3.so. A wheel that
# instead drops a loader shim there (libtorch_global_deps.so is the canonical
# example) would make this try to import it and fail loudly. Nothing in the
# current dependency set does that; the next compiled dependency might. The
# same applies to a package whose import has side effects — importing every
# extension is the point, but a dependency that talks to the network or reads
# a config at import time would fail here for reasons unrelated to the change
# being reviewed.


def derive(site_packages):
    """Top-level importable names that own a compiled extension."""
    names = set()
    for so in pathlib.Path(site_packages).rglob("*.so"):
        top = so.relative_to(site_packages).parts[0]
        if top.endswith(NOT_PACKAGES):
            continue
        names.add(top.split(".")[0])
    return names


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for path in (
            "PIL/_imaging.cpython-310-x86_64-linux-gnu.so",
            "pillow.libs/libjpeg.so",
            "psycopg2_binary.libs/libpq.so",
            "psycopg2/_psycopg.cpython-310.so",
            "opencv_python-4.9.0.data/purelib/cv2/cv2.so",
            "numpy-1.26.3.dist-info/whatever.so",
            # Extensions living directly in site-packages rather than inside a
            # package directory, which is what the split on "." is for.
            "_cffi_backend.cpython-38-x86_64-linux-gnu.so",
            "zmq.abi3.so",
        ):
            f = root / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.touch()
        got = derive(root)
    want = {"PIL", "psycopg2", "_cffi_backend", "zmq"}
    assert got == want, f"derived {sorted(got)}, wanted {sorted(want)}"

    # A directory with nothing to find must be a failure, not a quiet pass.
    with tempfile.TemporaryDirectory() as empty:
        assert derive(empty) == set(), "an empty tree should derive nothing"
        try:
            check_floor(set(), {"psycopg2"})
        except SystemExit:
            pass
        else:
            raise AssertionError("an empty derivation should have been rejected")
    # And that a satisfied floor passes: the reject case alone would be met by
    # a check_floor that always failed.
    check_floor({"psycopg2", "PIL", "numpy"}, {"psycopg2", "PIL"})

    # main() itself. Deriving the names proves nothing if nothing imports
    # them, and this is the only thing between a wheel whose compiled half
    # does not load on arm64 and a published image.
    previous_path = list(sys.path)
    original = sysconfig.get_paths
    # The entrypoints are the real image's pure-Python modules; the fixture
    # has none of them and importing them here would fail for a reason this
    # case is not about.
    global ENTRYPOINTS
    previous_entrypoints = ENTRYPOINTS
    ENTRYPOINTS = frozenset()
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "site-packages"
        for name, body in (("importable", ""), ("broken", "raise ImportError('compiled half missing')\n")):
            (root / name).mkdir(parents=True)
            (root / name / "__init__.py").write_text(body)
            (root / name / "_ext.cpython-310-x86_64-linux-gnu.so").write_bytes(b"")
        sys.path.insert(0, str(root))
        sysconfig.get_paths = lambda *a, **k: {"platlib": str(root)}
        try:
            try:
                main(["importable", "broken"])
            except (SystemExit, ImportError):
                pass
            else:
                raise AssertionError("a module that cannot import was reported as loaded")
            # And the healthy one on its own still passes, so the case above
            # is about the import and not about main() refusing everything.
            (root / "broken" / "__init__.py").write_text("")
            main(["importable", "broken"])
        finally:
            sysconfig.get_paths = original
            sys.path[:] = previous_path
            ENTRYPOINTS = previous_entrypoints

    print("self-test ok:", sorted(got))


def check_floor(names, expected):
    """Fail unless the scan found what the caller says the image contains.

    An unreadable or wrong site-packages path yields an empty set rather than
    an error, which would otherwise leave this asserting nothing beyond the
    pure-Python entrypoints.
    """
    missing = set(expected) - names
    if missing:
        sys.exit(
            f"found {len(names)} modules with compiled code, but not "
            f"{sorted(missing)} — the scan is looking at the wrong place, so "
            f"it is proving nothing"
        )


def main(expected):
    if not expected:
        sys.exit(f"usage: {sys.argv[0]} MODULE [MODULE...] | --self-test")
    # platlib, not purelib: compiled extensions belong to the platform-
    # specific scheme. The two are the same directory on these images, which
    # is exactly why reading the wrong one would go unnoticed.
    site_packages = pathlib.Path(sysconfig.get_paths()["platlib"])
    native = derive(site_packages)
    check_floor(native, expected)
    modules = sorted(native | ENTRYPOINTS)
    for name in modules:
        importlib.import_module(name)
    print("loaded", len(modules), "modules:", " ".join(modules))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main(sys.argv[1:])
