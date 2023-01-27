# Credit: Huge THANK-YOU to @Arksine for his work at: https://github.com/Arksine/moonraker

import tempfile
import random
from pathlib import Path

from components.file_manager.metadata import *


def get_slicer(file_path: str, f: bytes, encoding: str,) -> Tuple[BaseSlicer, Dict[str, str]]:
    header_data = footer_data = ""
    slicer: Optional[BaseSlicer] = None
    size = os.path.getsize(file_path)

    # read the default size, which should be enough to
    # identify the slicer
    header_data = f.read(READ_SIZE).decode('utf-8')
    for impl in SUPPORTED_SLICERS:
        slicer = impl(file_path)
        ident = slicer.check_identity(header_data)
        if ident is not None:
            break
    else:
        slicer = UnknownSlicer(file_path)
        ident = slicer.check_identity(header_data)
    if size > READ_SIZE * 2:
        f.seek(size - READ_SIZE)
        footer_data = f.read().decode('utf-8')
    elif size > READ_SIZE:
        remaining = size - READ_SIZE
        footer_data = header_data[remaining - READ_SIZE:] + f.read().decode('utf-8')
    else:
        footer_data = header_data
    slicer.set_data(header_data, footer_data, size)
    if ident is None:
        ident = {"slicer": "unknown"}
    return slicer, ident

def extract_metadata(file_path: str, check_objects: bool, f: bytes, encoding: str,
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    slicer, ident = get_slicer(file_path, f, encoding)
    if check_objects and slicer.has_objects():
        name = ident.get("slicer", "unknown")
        if process_objects(file_path, slicer, name):
            slicer, ident = get_slicer(file_path, f, encoding)
    metadata['size'] = os.path.getsize(file_path)
    metadata['modified'] = os.path.getmtime(file_path)
    metadata['uuid'] = str(uuid.uuid4())
    metadata.update(ident)
    for key in SUPPORTED_DATA:
        func = getattr(slicer, "parse_" + key)
        result = func()
        if result is not None:
            metadata[key] = result
    return metadata

def parse(f: bytes, encoding: str):
    random_file_prefix = random.randint(0,1000000)
    stub_gcode_path = os.path.join(tempfile.gettempdir(), f'{random_file_prefix}.gcode')
    Path(stub_gcode_path).touch()   # extract_metadata needs a path to a real file, in addition to a BytesIO.
    metadata = extract_metadata(stub_gcode_path, False, f, encoding)

    # Clean up the stub g_code file s to free up disk space
    Path(stub_gcode_path).unlink()

    # Clean up thumbnail to free up disk space
    for thumbnail in metadata.pop('thumbnails', []):
        thumbnail_path = os.path.join(tempfile.gettempdir(), thumbnail['relative_path'])
        Path(thumbnail_path).unlink()

    # Remove the fields generated from the stub g_code file
    metadata.pop('modified', None)
    metadata.pop('size', None)
    metadata.pop('uuid', None)

    return metadata

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], 'rb') as f:
        print(parse(f, 'utf-8'))