#!/usr/bin/env python3
"""Every values key that carries a helm-docs comment must reach the table.

helm-docs parses `# -- description` with a greedy group, so a second
whitespace-preceded `--` anywhere in that line steals the separator: the key
name becomes garbage and the row silently vanishes from the generated README.
`--timeout` in a comment did exactly that here and removed mlApi.command.

The existing "generated README is current" check cannot see this. It compares
the generated file against the committed one, and both lose the row together.
It compares output to output; this compares output to input.

The same file also holds the schema to the one-line style the other 79 of its
80 descriptions already follow. A key described at length in two hand-edited
places gets corrected in one of them and left stale in the other; the values
comment is the copy that reaches readers, through the generated table.

    assert_values_documented.py VALUES README [SCHEMA]
    assert_values_documented.py --self-test
"""
import json
import re
import sys
from pathlib import Path

import yaml

# The helm-docs marker. Anything on that line after the marker is description.
MARKER = re.compile(r"^\s*#\s*--\s")
# A mapping key at any indent: `  someKey:` possibly followed by a value.
KEY = re.compile(r"^(\s*)([A-Za-z_][\w.-]*):")


def documented_keys(values_text):
    """Dotted paths whose definition is preceded by a helm-docs comment block.

    Dotted, not bare: a bare name like `command` appears inside other rows of
    the table, so a missing row would still look present.
    """
    marked = False
    keys = []
    stack = []  # (indent, name) of the enclosing mappings
    for line in values_text.splitlines():
        if MARKER.match(line):
            marked = True
            continue
        if line.strip().startswith("#") or not line.strip():
            continue
        match = KEY.match(line)
        if not match:
            marked = False
            continue
        indent, name = len(match.group(1)), match.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([n for _, n in stack] + [name])
        if marked:
            keys.append(path)
            marked = False
        stack.append((indent, name))
    return keys


# A values file this project would ship always documents far more than this.
# Without a floor, a changed marker or a reindent makes documented_keys() return
# nothing, missing() return nothing, and the check pass while checking nothing —
# the same degradation assert_imports.py carries check_floor() to prevent.
FLOOR = 20


def missing(values_text, readme_text, floor=None):
    keys = documented_keys(values_text)
    if len(keys) < (FLOOR if floor is None else floor):
        sys.exit(
            f"only {len(keys)} documented keys found, expected at least "
            f"{FLOOR if floor is None else floor}. "
            "The scan is not reading this file the way it expects, so it is "
            "proving nothing."
        )
    # Matched as a whole table cell. A bare substring test cannot see a
    # missing row for any key that is a prefix of another documented key —
    # image.mlApi would be "found" inside the row for image.mlApi.cpu — and on
    # this chart that is 19 keys out of 82, including every parent.
    return [key for key in keys if f"| {key} |" not in readme_text]


# Long enough for any of these keys, short enough that a rationale does not fit.
SENTENCE_LIMIT = 120
# The schema describes most of what it validates, so a scan finding almost
# nothing is reading the wrong shape rather than reporting a clean file.
SCHEMA_FLOOR = 40
SECOND_SENTENCE = re.compile(r"\.\s+[A-Z]")


def schema_descriptions(schema):
    """(path, description) for every described node, at any depth."""
    found = []

    def walk(node, path):
        if isinstance(node, dict):
            text = node.get("description")
            if isinstance(text, str):
                found.append((path, text))
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key)
        elif isinstance(node, list):
            for value in node:
                walk(value, path)

    walk(schema, "")
    return found


def schema_properties(schema, path=""):
    """Dotted paths the schema claims to validate, at any depth."""
    found = []
    properties = schema.get("properties") if isinstance(schema, dict) else None
    if isinstance(properties, dict):
        for name, node in properties.items():
            here = f"{path}.{name}" if path else name
            found.append(here)
            found.extend(schema_properties(node, here))
    return found


def orphaned(schema_text, values_text, floor=None):
    """Schema paths that name nothing in values.yaml.

    A key nested under the wrong parent validates a path nobody sets, and the
    path people do set goes unvalidated. Nothing reports it: the schema is
    still valid JSON, the chart still renders, and the description reads as
    if it applies to the real key. The one that prompted this sat under `web`
    while documenting the ml-api container.
    """
    schema = json.loads(schema_text)
    values = yaml.safe_load(values_text) or {}
    paths = schema_properties(schema)
    if len(paths) < (SCHEMA_FLOOR if floor is None else floor):
        sys.exit(
            f"only {len(paths)} schema properties found, expected at least "
            f"{SCHEMA_FLOOR if floor is None else floor}. The scan is not "
            "reading this file the way it expects, so it is proving nothing."
        )

    def present(path):
        node = values
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return True

    return [path for path in paths if not present(path)]


def overlong(schema_text, floor=None):
    described = schema_descriptions(json.loads(schema_text))
    if len(described) < (SCHEMA_FLOOR if floor is None else floor):
        sys.exit(
            f"only {len(described)} described schema nodes found, expected at "
            f"least {SCHEMA_FLOOR if floor is None else floor}. The scan is not "
            "reading this file the way it expects, so it is proving nothing."
        )
    return [
        (path, text)
        for path, text in described
        if len(text) > SENTENCE_LIMIT or SECOND_SENTENCE.search(text)
    ]


def self_test():
    values = (
        "mlApi:\n"
        "  # -- Command for the server. The `--timeout` flag matters.\n"
        "  command:\n"
        "    - gunicorn\n"
        "  # -- Replica count\n"
        "  replicaCount: 1\n"
    )
    assert documented_keys(values) == ["mlApi.command", "mlApi.replicaCount"], documented_keys(values)
    assert missing(values, "| mlApi.command | ... |\n| mlApi.replicaCount | ... |", floor=2) == []

    # A parent key must not be considered present just because a child's row
    # mentions it. This is the shape a bare substring test cannot see.
    nested = (
        "# -- the parent\n"
        "a:\n"
        "  # -- the child\n"
        "  b: 1\n"
    )
    assert documented_keys(nested) == ["a", "a.b"], documented_keys(nested)
    assert missing(nested, "| a.b | ... |", floor=2) == ["a"]
    # The shape the trap produces: one documented key never reaches the table.
    # The floor: a file the scan cannot read must fail, not pass quietly.
    try:
        missing("nothing: here\n", "", floor=2)
    except SystemExit:
        pass
    else:
        raise AssertionError("a values file with no documented keys was accepted")

    # The schema rule. A one-line description passes; the shape that started
    # this, a rationale restated next to the validator, does not.
    clean = json.dumps({"properties": {"a": {"description": "Replica count"}}})
    assert overlong(clean, floor=1) == [], overlong(clean, floor=1)
    wordy = json.dumps(
        {"properties": {"a": {"description": "Replica count. Raising it needs a shared cache."}}}
    )
    assert [p for p, _ in overlong(wordy, floor=1)] == ["properties.a"], overlong(wordy, floor=1)
    long_one = json.dumps({"properties": {"a": {"description": "x" * (SENTENCE_LIMIT + 1)}}})
    assert [p for p, _ in overlong(long_one, floor=1)] == ["properties.a"]
    # Nested descriptions have to be reached, or the rule covers only the top
    # level while reporting on the whole file.
    deep = json.dumps(
        {"properties": {"a": {"properties": {"b": {"description": "One. Two more here."}}}}}
    )
    assert [p for p, _ in overlong(deep, floor=1)] == ["properties.a.properties.b"]
    try:
        overlong(json.dumps({"type": "object"}), floor=1)
    except SystemExit:
        pass
    else:
        raise AssertionError("a schema with no descriptions was accepted")

    # The schema-to-values rule. A key under the wrong parent is the shape
    # that started this: valid JSON, plausible description, validating a path
    # nobody sets.
    matching = json.dumps({"properties": {"a": {"properties": {"b": {"type": "integer"}}}}})
    assert orphaned(matching, "a:\n  b: 1\n", floor=1) == [], orphaned(matching, "a:\n  b: 1\n", floor=1)
    misplaced = json.dumps(
        {"properties": {"a": {"properties": {"b": {"type": "integer"}}}, "c": {"type": "string"}}}
    )
    assert orphaned(misplaced, "a:\n  b: 1\n", floor=1) == ["c"], orphaned(misplaced, "a:\n  b: 1\n", floor=1)
    # A null value is set, not absent: values.yaml uses null to mean "delete
    # this on merge", and treating it as missing would flag every such key.
    assert orphaned(json.dumps({"properties": {"a": {}}}), "a: null\n", floor=1) == []
    try:
        orphaned(json.dumps({"type": "object"}), "a: 1\n", floor=1)
    except SystemExit:
        pass
    else:
        raise AssertionError("a schema with no properties was accepted")

    # main() itself. Each detector is reported from its own loop there, so
    # unwiring one leaves every case above passing while the check it names
    # stops running. One fixture per rule, each breaking only that rule.
    #
    # Generated rather than written out because main() applies the real
    # floors, and a fixture small enough to read would trip them instead of
    # reaching the detector under test.
    import os
    import pathlib
    import tempfile

    keys = [f"key{n}" for n in range(FLOOR + 5)]
    good_values = "mlApi:\n" + "".join(f"  # -- What {k} does\n  {k}: 1\n" for k in keys)
    good_readme = "".join(f"| mlApi.{k} | int | `1` | What {k} does |\n" for k in keys)
    described = {k: {"description": f"What {k} does"} for k in keys}
    # Described, because overlong() counts descriptions while orphaned()
    # counts properties, and both floors have to clear.
    padding = {f"pad{n}": {"description": f"Padding {n}"} for n in range(SCHEMA_FLOOR)}
    good_values += "".join(f"  pad{n}: 1\n" for n in range(SCHEMA_FLOOR))
    good_schema = json.dumps({"properties": {"mlApi": {"properties": {**described, **padding}}}})

    def schema_with(properties):
        return json.dumps({"properties": {"mlApi": {"properties": properties}}})

    broken = {
        "missing row": (
            good_values,
            good_readme.replace(f"| mlApi.{keys[0]} |", "| something.else |", 1),
            good_schema,
        ),
        "wordy description": (
            good_values,
            good_readme,
            schema_with({**described, **padding, keys[0]: {"description": "What it does. Raising it needs a shared cache."}}),
        ),
        "orphaned property": (
            good_values,
            good_readme,
            schema_with({**described, **padding, "absent": {"description": "Names nothing"}}),
        ),
    }
    previous = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            names = ("values.yaml", "README.md", "values.schema.json")
            for name, text in zip(names, (good_values, good_readme, good_schema)):
                pathlib.Path(name).write_text(text)
            main(list(names))
            for rule, texts in broken.items():
                for name, text in zip(names, texts):
                    pathlib.Path(name).write_text(text)
                try:
                    main(list(names))
                except SystemExit:
                    continue
                raise AssertionError(f"the {rule} rule did not reach main()")
    finally:
        os.chdir(previous)

    print("self-test ok")


def main(argv):
    if len(argv) not in (2, 3):
        sys.exit(f"usage: {sys.argv[0]} VALUES README [SCHEMA] | --self-test")
    values_path, readme_path = (Path(p) for p in argv[:2])
    gone = missing(values_path.read_text(), readme_path.read_text())
    if gone:
        for key in gone:
            print(
                f"::error::{key} carries a helm-docs comment in {values_path} but has "
                f"no row in {readme_path}. A second ` --` in the comment line is the "
                f"usual cause; wrap flags in backticks."
            )
        sys.exit(1)
    print(f"all {len(documented_keys(values_path.read_text()))} documented keys reach the table")
    if len(argv) == 3:
        schema_path = Path(argv[2])
        wordy = overlong(schema_path.read_text())
        for path, text in wordy:
            print(
                f"::error::{path} in {schema_path} carries more than a one-line "
                f"description: {text!r}. The rationale belongs in {values_path}, "
                "which is the copy the generated table shows."
            )
        if wordy:
            sys.exit(1)
        print("every schema description is a single line")
        stray = orphaned(schema_path.read_text(), values_path.read_text())
        for path in stray:
            print(
                f"::error::{path} in {schema_path} validates nothing: "
                f"{values_path} has no such key. A property nested under the "
                "wrong parent leaves the real key unvalidated while reading "
                "as though it covers it."
            )
        if stray:
            sys.exit(1)
        print(f"all {len(schema_properties(json.loads(schema_path.read_text())))} schema properties name a real value")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main(sys.argv[1:])
