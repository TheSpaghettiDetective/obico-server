from typing import List, Tuple
from dataclasses import dataclass, field
import os
import re

@dataclass
class Meta:
    names: List[str] = field(default_factory=list)

    def __init__(self, meta_path: str):
        names = None
        with open(meta_path) as f:
            meta_contents = f.read()
            match = re.search("names *= *(.*)$", meta_contents, re.IGNORECASE | re.MULTILINE)
            if match:
                names_path = match.group(1)
                try:
                    if os.path.exists(names_path):
                        with open(names_path) as namesFH:
                            names_list = namesFH.read().strip().split("\n")
                            names = [x.strip() for x in names_list]
                except TypeError:
                    pass
        if names is None:
            names = ['failure']

        self.names = names
