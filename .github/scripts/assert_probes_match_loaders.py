#!/usr/bin/env python3
"""Each weights download is gated on a probe; the probe has to ask what the
loader asks.

`ml_api/Dockerfile` downloads a 200 MB model only when the base can use it,
and decides that with a shell test per format. The decision is only as good as
what it looks for: probing for a directory while the loader dlopens a file
inside it, or for a shared library while the loader imports a Python package,
passes on a base where the model is unreadable and 200 MB is wasted, or skips
on one where it would have worked.

The names cannot be compared automatically to a loader's behaviour, so this
compares them to the loader's source: whatever the probe names must appear in
the module that does the loading.

    assert_probes_match_loaders.py DOCKERFILE MODULE_DIR
    assert_probes_match_loaders.py --self-test
"""
import re
import sys
from pathlib import Path

# (format, what the probe must name, the module that loads it). The probe line
# is found by the format's model path, which is what the download writes.
PAIRS = (
    ("darknet", ("libdarknet_gpu.so", "libdarknet_cpu.so"), "darknet.py"),
    ("onnx", ("onnxruntime",), "onnx.py"),
    ("rknn", ("rknnlite",), "rknn.py"),
)


def probe_for(dockerfile_text, fmt):
    """The `if` line guarding this format's download, or None."""
    lines = dockerfile_text.splitlines()
    for number, line in enumerate(lines):
        if f"/model_cache/ml_api/{fmt}/model-weights.{fmt}" not in line:
            continue
        # The guard is the nearest `if` above the download it guards.
        for candidate in reversed(lines[:number]):
            if re.search(r"(^|&&)\s*if\s", candidate):
                return candidate
    return None


def mismatched(dockerfile_text, module_text_by_name):
    """(format, name) for every probe naming something its loader does not."""
    found = []
    for fmt, names, module in PAIRS:
        probe = probe_for(dockerfile_text, fmt)
        if probe is None:
            found.append((fmt, "no probe guards this download"))
            continue
        source = module_text_by_name.get(module, "")
        for name in names:
            if name in probe and name not in source:
                found.append((fmt, f"{name} is not in {module}"))
        if not any(name in probe for name in names):
            found.append((fmt, f"names none of {list(names)}, which {module} uses"))
    return found


def self_test():
    def dockerfile(darknet_probe):
        return (
            "RUN mkdir -p /model_cache \\\n"
            f" && if {darknet_probe}; then \\\n"
            "      fetch_verified x /model_cache/ml_api/darknet/model-weights.darknet 1 y; \\\n"
            "    fi \\\n"
            " && if python3 -c 'import onnxruntime'; then \\\n"
            "      fetch_verified x /model_cache/ml_api/onnx/model-weights.onnx 1 y; \\\n"
            "    fi \\\n"
            " && if python3 -c 'import rknnlite.api'; then \\\n"
            "      fetch_verified x /model_cache/ml_api/rknn/model-weights.rknn 1 y; \\\n"
            "    fi\n"
        )

    modules = {
        "darknet.py": "so_path = os.path.join('/darknet', 'libdarknet_gpu.so')\nlibdarknet_cpu.so\n",
        "onnx.py": "import onnxruntime\n",
        "rknn.py": "from rknnlite.api import RKNNLite\n",
    }
    good = dockerfile("[ -e /darknet/libdarknet_gpu.so ] || [ -e /darknet/libdarknet_cpu.so ]")
    assert mismatched(good, modules) == [], mismatched(good, modules)

    # The shape that shipped: a directory test standing in for the library the
    # loader opens. An empty or half-copied /darknet passes it.
    directory = dockerfile("[ -d /darknet ]")
    assert [f for f, _ in mismatched(directory, modules)] == ["darknet"], mismatched(directory, modules)

    # And the other direction: probing for a library while the loader imports
    # a package. This is what made the rk3588 download land on a base that
    # could not read it.
    library = (
        "RUN mkdir -p /model_cache \\\n"
        " && if [ -e /usr/lib/librknnrt.so ]; then \\\n"
        "      fetch_verified x /model_cache/ml_api/rknn/model-weights.rknn 1 y; \\\n"
        "    fi\n"
    )
    # Only the rknn download is present here, so the other two report as
    # unguarded; what this case pins is the reason given for rknn.
    assert ("rknn", "names none of ['rknnlite'], which rknn.py uses") in mismatched(library, modules), mismatched(library, modules)

    # A download with no guard at all is the same failure without the excuse.
    ungated = "RUN fetch_verified x /model_cache/ml_api/onnx/model-weights.onnx 1 y\n"
    assert ("onnx", "no probe guards this download") in mismatched(ungated, modules)

    # main() itself: without driving it, replacing its sys.exit(1) with a
    # return leaves every case above green while CI prints the errors and
    # passes. Every sibling checker here drives main() for this reason.
    import os
    import tempfile

    previous = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            os.makedirs("lib")
            for name, body in modules.items():
                open(f"lib/{name}", "w").write(body)
            open("Dockerfile", "w").write(good)
            main(["Dockerfile", "lib"])
            open("Dockerfile", "w").write(directory)
            try:
                main(["Dockerfile", "lib"])
            except SystemExit:
                pass
            else:
                raise AssertionError("a probe that asks the wrong question did not stop main()")
    finally:
        os.chdir(previous)

    print("self-test ok")


def main(argv):
    if len(argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} DOCKERFILE MODULE_DIR | --self-test")
    dockerfile, module_dir = Path(argv[0]), Path(argv[1])
    modules = {name: (module_dir / name).read_text() for _, _, name in PAIRS}
    bad = mismatched(dockerfile.read_text(), modules)
    for fmt, why in bad:
        print(
            f"::error::the {fmt} probe in {dockerfile} {why}. It decides "
            "whether to download 200 MB, so asking a different question than "
            "the loader means the answer is right by luck."
        )
    if bad:
        sys.exit(1)
    print(f"all {len(PAIRS)} weight probes name what their loader uses")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main(sys.argv[1:])
