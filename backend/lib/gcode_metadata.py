# Credit: Huge THANK-YOU to @Arksine for his work at: https://github.com/Arksine/moonraker

import tempfile
import random
from pathlib import Path
from io import BytesIO
from typing import BinaryIO


from moonraker.components.file_manager.metadata import *


def get_slicer(file_path: str, f: BinaryIO, size: int, encoding: str,) -> Tuple[BaseSlicer, Dict[str, str]]:
    header_data = footer_data = ""
    slicer: Optional[BaseSlicer] = None

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

def extract_metadata(file_path: str, check_objects: bool, f: BinaryIO, size: int, encoding: str,
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    slicer, ident = get_slicer(file_path, f, size, encoding)
    if check_objects and slicer.has_objects():
        name = ident.get("slicer", "unknown")
        if process_objects(file_path, slicer, name):
            slicer, ident = get_slicer(file_path, f, size, encoding)
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

def parse(f: BinaryIO, size: int, encoding: str):
    random_file_prefix = random.randint(0,1000000)
    stub_gcode_path = os.path.join(tempfile.gettempdir(), f'{random_file_prefix}.gcode')
    Path(stub_gcode_path).touch()   # extract_metadata needs a path to a real file, in addition to a BytesIO.
    metadata = extract_metadata(stub_gcode_path, False, f, size, encoding)

    # Clean up the stub g_code file s to free up disk space
    Path(stub_gcode_path).unlink()

    # Turn thumbnail files to bytes, and delete them to free up disk space
    thumbnails = []
    for thumbnail in metadata.pop('thumbnails', []):
        thumbnail_path = os.path.join(tempfile.gettempdir(), thumbnail['relative_path'])
        with open(thumbnail_path, 'rb') as thumbnail_file:
            thumbnails.append(BytesIO(thumbnail_file.read()))
        Path(thumbnail_path).unlink()

    # Remove the fields generated from the stub g_code file
    metadata.pop('modified', None)
    metadata.pop('size', None)
    metadata.pop('uuid', None)

    return metadata, thumbnails
    getbuffer().nbytes

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], 'rb') as f:
        print(parse(f, os.path.getsize(sys.argv[1]), 'utf-8'))